<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_isharp_filters.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_isharp_filters.h

## Purpose

`dc_spl_isharp_filters.h` defines iSHARP filter helper types and public lookup/generation APIs used by the SPL core.

## Important APIs, Types, And Functions

- `NUM_SHARPNESS_ADJ_LEVELS`.
- `struct scale_ratio_to_sharpness_level_adj`: ratio threshold to sharpness down-adjust mapping.
- `struct isharp_1D_lut_pregen`: cached sharpness numerator/denominator and generated LUT values.
- `enum system_setup`: `SDR_NL`, `SDR_L`, `HDR_NL`, `HDR_L`, and `NUM_SHARPNESS_SETUPS`.
- Public APIs: `spl_set_blur_scale_data`, `spl_build_isharp_1dlut_from_reference_curve`, `spl_get_pregen_filter_isharp_1D_lut`, `spl_dscl_get_blur_scale_coeffs_64p`, and `spl_dscl_get_blur_scale_coeffs_64p_s1_10`.

## Control Flow

No executable control flow exists in the header. It defines the shape of lookup tables and declares functions implemented by `dc_spl_isharp_filters.c`.

## State And Persistence Behavior

The header stores no state. The implementation has static LUT cache state represented by `struct isharp_1D_lut_pregen`.

## Dependencies And Integration Points

It includes `dc_spl_types.h` for `dscl_prog_data`, `spl_scaler_data`, `adaptive_sharpness`, fixed-point types, and policy enums. It is included by `dc_spl.c` to configure iSHARP during scaler parameter calculation.

## Risks And Edge Cases

Changing enum order changes the cache index and setup interpretation. The public APIs assume caller-selected tap values are supported by iSHARP tables. The LUT size must match `ISHARP_LUT_TABLE_SIZE`.

## Test Signals

Build coverage validates API compatibility. Functional tests should include every `system_setup`, supported tap count, sharpness policy, and integration with `spl_calculate_scaler_params` when iSHARP is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_isharp_filters.h -->
