# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_scl_filters.c

Purpose: this file provides the legacy/non-EASF DSCL scaler coefficient tables and the public selector `spl_dscl_get_filter_coeffs_64p()`. The data covers 2 through 8 taps, 64 phases represented as 33 stored symmetric phases, and several ModifiedLanczos ratio bands.

Important APIs and control flow: static arrays such as `filter_3tap_64p_upscale`, `filter_3tap_64p_116`, `filter_3tap_64p_149`, and `filter_3tap_64p_183` repeat for 3 through 8 taps. Selection helpers choose an upscale table when `ratio < 1`, then downscale bands split at `4/3` and `5/3`, with the final table used for larger ratios. `spl_get_filter_2tap_64p()` always returns the 2-tap table. `spl_dscl_get_filter_coeffs_64p()` dispatches by tap count, returns `NULL` for one tap, and asserts for impossible tap counts.

State and persistence: the implementation is stateless. It returns pointers to static const tables and does not allocate, copy, or retain caller data. Runtime behavior depends only on the `taps` integer and the raw `value` field in `struct spl_fixed31_32`.

Dependencies and integration: it depends on `spl_debug.h` for assertions and `dc_spl_scl_filters.h` for the public prototype. It is used indirectly by `spl_set_filters_data()` when EASF is disabled, and directly by scaler programming code that needs raw DSCL coefficient pointers. The fixed-point comparison thresholds depend on `spl_fixpt_from_fraction()`.

Risks and tests: threshold equality selects the higher ratio band because all comparisons are strict `<`. Invalid tap counts are treated as programming bugs rather than soft failures. Array lengths must remain `33 * taps`; a malformed generated table would corrupt hardware programming downstream. Test signals should validate the dispatch matrix for taps 1-8, exact 1.0/4:3/5:3 boundaries, pointer identity for each selected table, and coefficient sum/format expectations for representative phases.
