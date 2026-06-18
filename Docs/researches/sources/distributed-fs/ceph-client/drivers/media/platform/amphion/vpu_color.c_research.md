<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_color.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_color.c

Purpose: converts color metadata between V4L2 enum values and firmware integer table indices for color primaries, transfer functions, matrix coefficients, and quantization range.

Important APIs: `vpu_color_cvrt_primaries_v2i/i2v()`, `vpu_color_cvrt_transfers_v2i/i2v()`, `vpu_color_cvrt_matrix_v2i/i2v()`, and `vpu_color_cvrt_full_range_v2i/i2v()`.

Control flow and state: conversion is table-driven using static arrays and `vpu_helper_find_in_array_u8()` for V4L2-to-index lookup. Unknown or unsupported mappings usually convert to 0 or V4L2 LAST/default-like placeholders. No mutable state exists.

Dependencies and integration: used by Malone sequence-header unpacking and parameter packing paths to expose firmware color metadata through decoder formats and controls.

Risks: lossy mappings can collapse unsupported V4L2 values to index 0, and firmware indices outside the table become 0. Color metadata regressions are visible only when userspace checks format colorimetry or decoded streams include VUI.

Test signals: decode streams with Rec.709, SMPTE170M, BT.2020, full/limited range, and unknown VUI values; assert V4L2 `G_FMT` color fields and firmware parameter tables round-trip correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_color.c -->
