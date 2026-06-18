# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_cm_common.c

## Purpose
Provides DCN3 color-management helper logic for gamcor transfer-function programming and DCN3-specific software-curve translation, including 257-point behavior for non-shaper LUTs.

## Important APIs, Types, And Functions
`cm_helper_program_gamcor_xfer_func()` writes gamcor start controls, start slopes, end base/slope/end controls, and region metadata. `cm3_helper_translate_curve_to_hw_format()` converts `dc_transfer_func` samples into `pwl_params` for DCN3 hardware. `cm3_helper_convert_to_custom_float()` converts corner points and PWL base values to custom float or fixed point. `is_rgb_equal()` checks if all programmed RGB register values are equal across a PWL array.

## Control Flow
Translation rejects null/bypass inputs, clears params, chooses 32-region distribution for PQ, gamma 2.2, and HLG or compact 13-segment distribution otherwise, computes total hardware points, adjusts point count for fixed-point shaper LUTs, samples `tf_pts`, writes terminal duplicates, computes corner points and slopes, fills region offsets/segment counts, computes fixed-point deltas only in shaper mode, converts to custom float, and returns success/failure. Programming walks region registers two curve regions per register after writing per-channel start/end controls.

## State And Persistence
The helpers mutate caller-provided `pwl_params` and program hardware registers. There is no static mutable state. DCN3 register state persists until later color updates.

## Dependencies And Integration Points
Depends on `dcn30_dpp.h`, `dcn30_cm_common.h`, `custom_float`, fixed-point conversion helpers, and logger macros. Integrated by DCN3 DPP/OPP color programming paths.

## Risks
DCN3 point-count behavior differs from DCN1: non-fixpoint paths use 257 points because there are no separate slope registers. Off-by-one errors around `hw_points`, `hw_points + 1`, and terminal duplicates can corrupt LUT output. HLG is treated like PQ/gamma22 for region distribution. Fixed-point precision loss is logged as error.

## Test Signals
Regamma/gamcor tests for PQ, gamma 2.2, HLG, and SDR curves; shaper-LUT fixed-point tests; RGB equality checks; boundary coverage for `TRANSFER_FUNC_POINTS`; and visual/colorimetric validation.
