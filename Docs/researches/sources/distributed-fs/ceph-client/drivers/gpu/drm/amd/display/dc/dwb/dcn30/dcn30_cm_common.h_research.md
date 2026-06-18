# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_cm_common.h

## Purpose

`dcn30_cm_common.h` extends DCN10 color-management helper register descriptions for DCN3 transfer function programming. It supports DWB OGAM curve programming with additional region start base and offset fields.

## Important APIs, Types, And Functions

It defines `TF_HELPER_REG_FIELD_LIST_DCN3`, `struct DCN3_xfer_func_shift`, `struct DCN3_xfer_func_mask`, `struct dcn3_xfer_func_reg`, and declares `cm_helper_program_gamcor_xfer_func`, `cm3_helper_translate_curve_to_hw_format`, `cm3_helper_convert_to_custom_float`, and `is_rgb_equal`.

## Control Flow

The header has no execution. DWB color-management code populates a `dcn3_xfer_func_reg` with RAM A/B register addresses and shift/mask fields, then passes it to common helpers that program piecewise-linear transfer functions.

## State, Dependencies, Risks, And Test Signals

It defines register mapping containers only. Runtime state is in caller-owned `pwl_params` and hardware OGAM registers. It includes `dcn10/dcn10_cm_common.h` and is consumed by `dcn30_dwb_cm.c`. Risks include mismatch between helper field expectations and DWB register mapping, especially region start/base/offset fields. Tests should verify OGAM LUT programming for equal RGB and per-channel curves.
