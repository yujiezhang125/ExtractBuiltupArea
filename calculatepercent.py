# -*- coding: utf-8 -*-
# @Time    : 2020/04/27
# @Author  : yujiezhang125
# @FileName: calculatepercent.py
# @Description: The urban built-up area was extracted by calculating the proportion of impermeable area

import arcpy

arcpy.env.workspace = r'D:\CityDNA\Data\dikuaitest\guangzhou.gdb'
arcpy.env.overwriteOutput = True

city = "guangzhou"


def calculatepercent(city):
    # union building greenspace and river
    arcpy.Union_analysis(["building", "greenspace", "river"], "union_arch", "ONLY_FID")

    # intersect arch and block
    arcpy.Intersect_analysis(["union_arch", city + "_block"], "intersect_arch", "ONLY_FID")

    # dissolve by fid
    arcpy.Dissolve_management("intersect_arch", "intersect_arch_dis", ["FID_" + city + "_block"])

    # add field
    arcpy.AddField_management(city + "_block", "AreaAll", "DOUBLE")
    arcpy.AddField_management("intersect_arch_dis", "AreaPart", "DOUBLE")

    # calculate geometry
    arcpy.CalculateField_management("intersect_arch_dis", "AreaPart", "!shape.area@SQUAREMETERS!", "PYTHON_9.3")
    arcpy.CalculateField_management(city + "_block", "AreaAll", "!shape.area@SQUAREMETERS!", "PYTHON_9.3")

    # join table
    arcpy.MakeFeatureLayer_management(city + "_block", "tempLayer")
    arcpy.AddJoin_management("tempLayer", "OBJECTID_1", "intersect_arch_dis", "FID_" + city + "_block", "KEEP_ALL")
    arcpy.CopyFeatures_management("tempLayer", city + "_block_join")
    arcpy.Delete_management('tempLayer')

    # calculate field
    arcpy.AddField_management(city + "_block_join", "percent", "DOUBLE")

    fc = city + "_block_join"
    cursor = arcpy.UpdateCursor(fc)
    field1 = city + "_block_AreaAll"
    field2 = "intersect_arch_dis_AreaPart"

    for row in cursor:
        if row.getValue(field1) is not None and row.getValue(field2) is not None:
            row.setValue("percent", row.getValue(field2) / row.getValue(field1))
        else:
            row.setValue("percent", 0)
        cursor.updateRow(row)
    # Delete cursor and row objects
    del cursor, row
