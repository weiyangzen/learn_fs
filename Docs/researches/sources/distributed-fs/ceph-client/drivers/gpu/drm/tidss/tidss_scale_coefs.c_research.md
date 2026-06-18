# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_scale_coefs.c

## Purpose

`tidss_scale_coefs.c` provides the FIR scaler coefficient tables used by TIDSS DISPC video plane scaling. It maps a computed FIR increment to one of several 3-tap or 5-tap coefficient sets.

## Important APIs, Types, and Functions

- Static `coef5_m*` tables define 5-tap coefficient arrays for scaling-factor buckets.
- Static `coef3_m*` tables define 3-tap coefficient arrays for wider-input or lower-resource paths.
- `tidss_get_scale_coefs(struct device *dev, u32 firinc, bool five_taps)` converts `firinc` into `inc = firinc / 0x40000`, selects the matching bucket, and returns either the 3-tap or 5-tap table.
- Upscaling more than 2x intentionally maps to M11/M16/M19 tables instead of the M8 table to reduce observed blockiness/outlines.

## Control Flow

`tidss_dispc.c` calculates FIR increments from input/output dimensions in `dispc_vid_calc_scaling()`. For horizontal, vertical, and UV scaling paths it calls `tidss_get_scale_coefs()`, then `dispc_vid_write_fir_coefs()` writes the returned coefficient arrays into hardware phase registers during plane setup.

## State and Persistence Behavior

All coefficient tables are static constant data. Returned pointers are stable for the kernel lifetime. Hardware persistence occurs only after DISPC writes the selected table into plane registers.

## Dependencies and Integration Points

The file depends on Linux device logging and fixed-width types from the header. It is tightly coupled to DISPC FIR register programming and the scaling-limit calculations in `tidss_dispc.c`.

## Risks and Edge Cases

- If `firinc` falls outside all buckets, the function logs an error and returns NULL; the DISPC writer logs another error and skips writing coefficients.
- Bucket boundaries encode empirical quality choices; changing them can affect visible scaler output.
- Tables come from an interpolation script noted in comments, but the script is not present here for regeneration or verification.
- 3-tap tables leave `c2` zero-initialized through struct initialization, which is intentional but easy to misread.

## Test Signals

Tests should cover bucket selection at every boundary, 3-tap versus 5-tap selection, upscaling special buckets, invalid `firinc` error logging, and visual/hardware validation for representative scaler ratios including NV12 chroma scaling.
