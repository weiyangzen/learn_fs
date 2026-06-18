# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_cm_common.c

## Purpose
Provides shared DCN1 color-management helpers for programming color matrices and transfer-function LUT region metadata. It converts software transfer-function samples into the fixed/custom-float formats consumed by DCN hardware.

## Important APIs, Types, And Functions
`cm_helper_program_color_matrices()` writes paired CSC matrix coefficients across a contiguous register range. `cm_helper_read_color_matrices()` reads the same layout back. `cm_helper_program_xfer_func()` programs start/end points and per-region LUT offsets/segment counts into transfer-function registers. `cm_helper_convert_to_custom_float()` converts corner points and optional PWL base/delta values into hardware custom-float or fixed-point fields. `cm_helper_translate_curve_to_hw_format()` builds regamma/shaper PWL parameters from `dc_transfer_func`. `cm_helper_translate_curve_to_degamma_hw_format()` builds the degamma-specific 12-region format.

## Control Flow
Matrix helpers linearly walk register pairs from `csc_c11_c12` through `csc_c33_c34`. Transfer-function programming writes three color channels of start controls, start slopes, end controls, and then walks `region_start..region_end` two regions per hardware register. Translation first rejects null or bypass transfer functions, clears `pwl_params`, chooses region distribution based on transfer-function type, samples `output_tf->tf_pts`, appends a duplicate terminal point for delta math, computes corner points and slopes, fills `arr_curve_points`, computes deltas, optionally clamps fixed-point values for shaper LUTs, then converts to custom float.

## State And Persistence
The helpers mutate caller-provided `struct pwl_params` and write hardware registers through `REG_SET*` macros. No heap allocation or static mutable state is used. The programmed register state persists in DPP/OPP color blocks until replaced by later color programming.

## Dependencies And Integration Points
Depends on `dc.h`, `reg_helper.h`, `dcn10_dpp.h`, `custom_float.h`, fixed-point helpers, logger macros, and the transfer-function data model. Integrated by DPP/OPP code that needs common LUT and matrix register programming.

## Risks
Boundary math is sensitive: `TRANSFER_FUNC_POINTS`, `MAX_LOW_POINT`, and `NUMBER_SW_SEGMENTS` must stay consistent with table sizes. `seg_distr[k] != -1` compares unsigned values against `-1`; it works as all-bits-one but is easy to misread. Failed custom-float conversion triggers debug breaks and returns false, so callers must handle translation failure. Fixed-point mode warns when delta precision is lost.

## Test Signals
Signals include correct LUT programming for PQ, gamma 2.2, sRGB-like curves, and degamma paths; no out-of-bounds log errors; stable color output under regamma/de-gamma changes; and readback matching matrix values written by `cm_helper_program_color_matrices()`.
