# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_dwb_cm.c

## Purpose

`dcn30_dwb_cm.c` implements DWB color-processing programming for DCN3.0: OGAM transfer functions, gamut remap matrices, and HDR multiplier. It translates DC color parameters into DWB register writes.

## Important APIs, Types, And Functions

Public functions are `dwb3_ogam_set_input_transfer_func`, `dwb3_set_gamut_remap`, and `dwb3_program_hdr_mult`. Private helpers map OGAM register fields, program RAM A/B region settings, determine current OGAM RAM, configure LUT writes, write PWL LUT data, program LUT selection, and program gamut remap coefficient banks.

## Control Flow

OGAM programming allocates `pwl_params`, converts the transfer function with `cm_helper_translate_curve_to_hw_format`, selects the inactive RAM bank based on current mode, writes region metadata and LUT samples, then switches `DWB_OGAM_SELECT`. Equal RGB curves use a single write mask; non-equal curves program red, green, and blue separately. Gamut remap bypasses unless software adjustment is requested, converts a 3x4 matrix to register values, and ping-pongs between remap A and B coefficient banks.

## State, Dependencies, Risks, And Test Signals

Software state is temporary allocation only. Hardware state includes OGAM mode/select/LUT contents, region metadata, gamut remap coefficient banks/mode, and HDR multiplier. Dependencies include `fixed31_32`, conversion helpers, `dwb.h`, `dcn30_dwb.h`, `dcn30_cm_common.h`, and DCN10 color helpers. Risks include allocation failure silently skipping OGAM, inactive-bank selection errors, LUT point assumptions, equal-RGB optimization hiding channel bugs, and bypassing non-software gamut adjustments. Tests should cover null transfer functions, PWL curves, RGB-equal and per-channel curves, gamut ping-pong, HDR multiplier writes, and update while capture is enabled.
