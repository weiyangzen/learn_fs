# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp_dscl.c

## Purpose
`dcn10_dpp_dscl.c` implements the DCN 1.0 DPP scaler and line-buffer programming path. It selects scaler mode based on format and ratios, powers DSCL LUT memory, chooses line-buffer partitioning, programs manual scale ratios and initial phases, loads filter coefficients, and caches scaler state to avoid redundant programming.

## Important APIs, types, and functions
- The primary entry point is `dpp1_dscl_set_scaler_manual_scale()`.
- Public helpers are `dpp1_dscl_calc_lb_num_partitions()` and `dpp1_dscl_is_lb_conf_valid()`.
- Mode and format helpers include `dpp1_dscl_get_pixel_depth_val()`, `dpp1_dscl_is_video_format()`, `dpp1_dscl_is_420_format()`, and `dpp1_dscl_get_dscl_mode()`.
- Filter helpers include `dpp1_dscl_get_filter_coeffs_64p()`, `dpp1_dscl_set_scaler_filter()`, and `dpp1_dscl_set_scl_filter()`.
- Line-buffer helpers include `dpp1_dscl_set_lb()`, `dpp1_dscl_get_lb_depth_bpc()`, and `dpp1_dscl_find_lb_memory_config()`.
- Geometry helpers are `dpp1_dscl_set_manual_ratio_init()` and `dpp1_dscl_set_recout()`.

## Control flow
`dpp1_dscl_set_scaler_manual_scale()` first compares the incoming `scaler_data` to the cached `dpp->scl_data`; if unchanged, it returns immediately. It derives a DSCL mode from scaling ratios, pixel format, `always_scale`, and fixed/float data-processing capability. If low-power DSCL memory is enabled and the mode is not full bypass, it powers the DSCL block on.

The function disables AutoCal, clears boundary mode, programs RECOUT and MPC size, writes `DSCL_MODE`, and exits early for full DSCL bypass. Otherwise it finds a line-buffer memory configuration by testing configs 1, 2, optionally 3 for 4:2:0, and finally config 0 against vertical ratio/tap requirements. It programs the line buffer, returns for 4:4:4 bypass, sets black offsets for RGB or YCbCr, writes manual scale ratios and initial phases, programs tap counts, and finally calls `dpp1_dscl_set_scl_filter()`.

The filter path enables hardcoded 2-tap coefficients when both luma/chroma tap counts qualify, otherwise it fetches 64-phase filter tables for luma and optional chroma. It compares table pointers against cached pointers in `struct dcn10_dpp`; when any table changed, it writes coefficient RAM and toggles `SCL_COEF_RAM_SELECT` to swap RAMs.

## State and persistence behavior
State is volatile and split between MMIO registers and the `struct dcn10_dpp` cache. `dpp->scl_data` records the last programmed scaler request. `filter_h`, `filter_v`, `filter_h_c`, and `filter_v_c` record the last coefficient table pointers. Low-power behavior can defer DSCL disable by setting `dpp->base.deferred_reg_writes.bits.disable_dscl` and `dc->optimized_required` instead of immediately forcing memory power off. No state survives driver unload or reboot.

## Dependencies and integration points
The file depends on `reg_helper.h`, `dcn10_dpp.h`, fixed-point conversion helpers (`dc_fixpt_*`), scaler filter tables (`get_filter_*tap_64p()`), display core debug flags, `struct scaler_data`, `struct line_buffer_params`, pixel-format enums, and `dpp_caps` callbacks. `dcn20_dpp.c` and `dcn201_dpp.c` reuse this DCN10 scaler entry point while providing generation-specific line-buffer partition calculations through their caps.

## Risks and edge cases
Line-buffer calculations rely on hardware-specific memory constants and clamp partitions to 64. Incorrect pixel depth, alpha, 4:2:0, or recout/viewport handling can select an insufficient buffer configuration. Exact zero widths are coerced to one to avoid division by zero. Ratios and taps must be consistent with hardware limits; invalid tap counts trigger debugger breaks in filter selection. The `memcmp()` cache assumes all relevant scaler state is represented deterministically in `struct scaler_data`, including no uninitialized padding.

## Test signals
Useful tests include identity scaling, RGB scaling, YCbCr 4:4:4 scaling, 4:2:0 luma/chroma bypass combinations, high downscale ratios requiring 8 taps, 1-tap and 2-tap paths, sharpness programming, alpha-enabled line-buffer partitioning, low-power DSCL enable/disable flows, and register trace or CRC validation across repeated modesets to confirm cache hits do not skip needed programming.
