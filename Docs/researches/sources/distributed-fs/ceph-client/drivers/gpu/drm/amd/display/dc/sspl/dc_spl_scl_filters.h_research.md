# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_scl_filters.h

Purpose: this header exposes the legacy DSCL 64-phase scaler coefficient selector. It is intentionally narrow: callers provide a tap count and fixed-point scale ratio and receive a pointer to a static coefficient table.

Important API: `spl_dscl_get_filter_coeffs_64p(int taps, struct spl_fixed31_32 ratio)` returns `const uint16_t *`. The tap count determines table width, and the ratio determines which precomputed ModifiedLanczos band the implementation uses. The symbol is wrapped in `SPL_NAMESPACE`, making it compatible with SPL prefixing.

Control flow and state: the header defines no state. Control is delegated entirely to `dc_spl_scl_filters.c`; callers must not assume ownership of the returned pointer. A `NULL` result is meaningful for one-tap/bypass-style operation in the implementation.

Dependencies and integration: it includes `dc_spl_types.h`, which provides `struct spl_fixed31_32` and the SPL namespace macro through included OS types. It is included by EASF selection code as the fallback path and by scaler programming code that emits raw DSCL filter pointers.

Risks and tests: this API has no output length parameter, so consumers must know that tables are stored as `33 * taps` entries. Invalid taps assert in the implementation, so tests should cover valid tap values and the `taps == 1` `NULL` behavior. Build tests should also confirm declarations remain synchronized with the implementation when `SPL_PFX_` is defined.
