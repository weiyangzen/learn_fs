# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_scl_easf_filters.h

Purpose: this header declares the public EASF scaler-filter interface and the small lookup-row type used by the EASF implementation. It is the contract between SPL scaler calculation code and the generated EASF coefficient/register tables in `dc_spl_scl_easf_filters.c`.

Important APIs and types: `struct scale_ratio_to_reg_value_lookup` stores a rational threshold (`numer`/`denom`) and the register value selected for ratios below that threshold; negative numerator rows are used by the implementation as a sentinel/default. `spl_set_filters_data()` populates `struct dscl_prog_data` filter pointers from `struct spl_scaler_data`, taking independent vertical and horizontal EASF enable flags. The `spl_get_*` functions expose EASF register values for BF3 mode, reducer gains, ring gains, and 3-tap tilt controls. `spl_dscl_get_easf_filter_coeffs_64p()` and `_s1_10()` expose coefficient tables for supported tap counts.

Control flow and state: the header has no executable state, but it defines a pull-based API: scaler setup computes ratios/taps, then calls these functions to obtain register-ready values or coefficient-array pointers. All state is held by caller-owned `spl_scaler_data` and `dscl_prog_data`.

Dependencies and integration: it includes `dc_spl_types.h`, so users inherit SPL fixed-point, scaler, and hardware-programming data structures. The symbols are wrapped in `SPL_NAMESPACE`, allowing optional compile-time prefixing. Primary consumers are SPL scaler parameter programming paths such as `dc_spl.c`; the implementation also coordinates with legacy `dc_spl_scl_filters`.

Risks and tests: callers must pass only supported tap counts for coefficient APIs, because invalid combinations assert in the implementation. Ratio values must use the same fixed31_32 convention expected by the generated tables. Tests should compile this header with namespace prefixing on/off, check all declarations match the implementation, and exercise 3-, 4-, and 6-tap EASF paths plus unsupported tap defensive behavior.
