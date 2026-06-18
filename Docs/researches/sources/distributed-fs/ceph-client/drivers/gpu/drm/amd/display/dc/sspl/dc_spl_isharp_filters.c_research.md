<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_isharp_filters.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_isharp_filters.c

## Purpose

`dc_spl_isharp_filters.c` owns iSHARP reference LUTs, blur-and-scale coefficient tables, sharpness-level adaptation, and helper APIs that attach iSHARP filter data to DSCL programming output.

## Important APIs, Types, And Functions

- Static tables: `filter_isharp_1D_lut_3p0x`, S1.10 and S1.12 blur-scale tables for 3-tap, 4-tap, and 6-tap-in-4-tap-layout cases.
- Mutable cache: `filter_isharp_1D_lut_pregen[NUM_SHARPNESS_SETUPS]`.
- Sharpness helpers: `spl_calculate_sharpness_level_adj`, `spl_calculate_sharpness_level`, and `spl_build_isharp_1dlut_from_reference_curve`.
- Public lookup helpers: `spl_get_pregen_filter_isharp_1D_lut`, `spl_dscl_get_blur_scale_coeffs_64p`, `spl_dscl_get_blur_scale_coeffs_64p_s1_10`, and `spl_set_blur_scale_data`.

## Control Flow

Sharpness LUT generation maps a discrete requested sharpness level through setup-specific min/mid/max ranges, optionally reduces it based on scale ratio, converts the selected level to fixed point, scales each byte of the base 3.0x LUT, clamps values to `0x7f`, and stores a cached pre-generated table per `enum system_setup`. Repeated calls with the same setup and sharpness skip recomputation.

Blur-scale lookup selects static coefficient tables by tap count. Supported taps are 3, 4, and 6; unsupported values break to debugger and return NULL. `spl_set_blur_scale_data` assigns horizontal and vertical blur-scale filter pointers from current scaler taps.

## State And Persistence Behavior

Most data is static read-only. `filter_isharp_1D_lut_pregen` is static mutable cache state storing the last generated sharpness table for each setup. There is no locking in this file, so concurrent callers can race while updating the same setup's cached LUT.

## Dependencies And Integration Points

It depends on SPL fixed-point math, `spl_debug.h`, filter helper definitions, and `dc_spl_isharp_filters.h`. `dc_spl.c` calls it when iSHARP is enabled to generate the delta LUT, retrieve the cached LUT, and attach blur-scale filters to `dscl_prog_data`.

## Risks And Edge Cases

- Only taps 3, 4, and 6 are valid for iSHARP blur-scale lookup.
- The mutable pre-generated LUT cache is not synchronized; parallel commits with different sharpness levels could interleave.
- The cached key ignores the full sharpness range and policy, using only resulting numerator/denominator per setup.
- Byte-level LUT scaling assumes the packed DWORD layout of `filter_isharp_1D_lut_3p0x`.
- S1.10 and S1.12 tables must remain numerically paired.

## Test Signals

Tests should validate sharpness reduction thresholds, min/mid/max interpolation for SDR/HDR and linear/nonlinear setups, LUT clamping, cache reuse, blur-scale table selection for 3/4/6 taps, NULL/debug behavior for invalid taps, and `dscl_prog_data->filter_blur_scale_h/v` pointer assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_isharp_filters.c -->
