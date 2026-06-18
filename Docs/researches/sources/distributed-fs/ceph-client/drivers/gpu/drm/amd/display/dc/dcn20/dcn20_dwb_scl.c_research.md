# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_dwb_scl.c

## Purpose
Programs DCN2 writeback scaler ratios, phases, tap counts, and coefficient RAM for horizontal and vertical luma/chroma scaling.

## Important APIs, Types, And Functions
The file contains static 16-phase coefficient tables for 3 through 12 taps, with variants for upscale, ratios below 4/3, below 5/3, and higher downscale. `wbscl_get_filter_*tap_16p()` selects the table for a tap count and fixed-point ratio. `wbscl_get_filter_coeffs_16p()` dispatches by tap count and supports 2-tap through `get_filter_2tap_16p()` and 1-tap with no coefficients. `wbscl_set_scaler_filter()` writes coefficient RAM by phase and tap pair. Exported `dwb_program_horz_scalar()` and `dwb_program_vert_scalar()` compute ratios, taps, phases, and load coefficient sets.

## Control Flow
Horizontal and vertical programming compute `src/dest` fixed-point ratios, convert ratios to hardware U3.19-left-shifted format with an all-ones special case at floor 8, program tap counts as `taps - 1`, compute luma and chroma initial phases, split signed phase into integer and fractional fields, program init registers, choose luma/chroma filter tables, and write coefficient RAM. Vertical chroma phase adds a quarter-pixel offset only for co-sited subsampling.

## State And Persistence
The coefficient tables are static read-only data. Hardware state persists in WBSCL scale-ratio, tap-control, init-phase, and coefficient RAM registers. No software state is retained.

## Dependencies And Integration Points
Depends on `fixed31_32.h`, common DWB scaling params, `dcn20_dwb.h`, and `reg_helper`. Called by `dwb2_set_scaler()` from DCN2 writeback enable/update flows.

## Risks
Tap values outside 1..12 trigger debugger break in coefficient dispatch. Zero destination dimensions would divide by zero through fixed-point helpers. Chroma filter selection passes `dc_fixpt_from_int(h_ratio_luma * 2)`/`v_ratio_luma * 2`, which uses the encoded register ratio rather than the original fixed ratio and is sensitive to overflow/semantic assumptions. Coefficient arrays encode signed coefficients as unsigned 14-bit style values, so accidental reinterpretation would break filtering.

## Test Signals
Validate register programming for tap counts 1..12, upscale and downscale threshold ratios, co-sited vs non-co-sited vertical subsampling, zero/invalid dimensions rejection at higher layers, coefficient RAM writes, and capture quality/resampling correctness.
