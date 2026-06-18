# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn401/dcn401_dpp_dscl.c

## Purpose
`dcn401_dpp_dscl.c` is the DCN401 scaler implementation. It programs DSCL line-buffer configuration, scale ratios and initial phases, recout/MPC geometry, coefficient RAMs, scaler mode, EASF sharpening/filter blocks, iSharp, blur/scale coefficients, and scaler memory power control.

## Important APIs, types, and functions
- `dpp401_dscl_set_scaler_manual_scale()` is the exported scaler programming entry used by the DCN401/42 DPP function table.
- `dpp401_dscl_get_dscl_mode()` maps scaler ratios and pixel format to `enum dcn401_dscl_mode_sel`.
- `dpp401_power_on_dscl()` handles DSCL LUT memory power state and deferred low-power shutdown.
- `dpp401_dscl_set_lb()`, `dpp401_dscl_find_lb_memory_config()`, and `dpp401_dscl_is_lb_conf_valid()` configure line-buffer memory and validate tap/partition needs.
- `dpp401_dscl_get_filter_coeffs_64p()`, `dpp401_dscl_set_scaler_filter()`, and `dpp401_dscl_set_scl_filter()` select and program 64-phase scaler filter coefficients.
- `dpp401_dscl_set_manual_ratio_init()` writes scale ratios and filter initial phases, using SPL precomputed values when enabled.
- `dpp401_dscl_program_easf()`, `_easf_v()`, `_easf_h()`, and `_disable_easf()` program or disable edge adaptive scaler functions.
- `dpp401_dscl_program_isharp()` and `dpp401_dscl_set_isharp_filter()` program iSharp mode, noise detection, LBA PWL, delta LUT, soft clip, and blur/scale coefficient filters.

## Control flow
The main entry first compares the new `scaler_data` with the cached copy and returns if unchanged. If iSharp is enabled and only the sharpness level changed, it writes only the iSharp 1D delta LUT, updates the cached sharpness/LUT, and returns if the whole structure now matches. Otherwise it caches the full scaler data, optionally replaces computed geometry/mode/taps with SPL-provided programmed data, powers on DSCL memory when needed, disables AutoCal, clears boundary mode, programs recout and MPC size, and writes `DSCL_MODE`.

If DSCL is fully bypassed, it may schedule memory power-down and returns. For active modes it chooses the smallest line-buffer memory config satisfying vertical tap and ratio requirements, programs line-buffer format/memory control, handles 444 bypass as a special case for EASF disable/iSharp-only programming, writes black offsets for YCbCr versus RGB, writes manual ratios and init phases, writes tap counts, programs iSharp, programs scaler filter coefficients with possible coefficient-RAM toggle, and finally programs EASF when `prefer_easf` is enabled.

Filter programming obtains SPL-provided filters when SPL is enabled and not disabled; otherwise it selects built-in 64-phase filters based on taps and ratios. It uses hardware hardcoded 2-tap coefficients when both luma and chroma taps are two, otherwise it detects changed filter pointers or forced updates, writes luma/chroma coefficient RAMs, caches pointers, reads current coefficient RAM select, and flips to the alternate coefficient RAM.

## State and persistence behavior
`struct dcn401_dpp` caches the last `struct scaler_data` and filter pointers to avoid redundant register programming and to detect coefficient updates. Hardware state persists in DSCL, EASF, iSharp, line-buffer, coefficient RAM, recout, and MPC registers until reprogrammed. Low-power state is coordinated through DC debug flags, `ctx->dc->optimized_required`, and `deferred_reg_writes.bits.disable_dscl`. There is no durable storage.

## Dependencies and integration points
The file depends on DC fixed-point conversion, scaler data structures, filter-table providers such as `get_filter_8tap_64p()`, DC config/debug flags (`use_spl`, `disable_spl`, `prefer_easf`, `always_scale`, `enable_mem_low_power.bits.dscl`), DC caps (`ips_v2_support`), and the DCN401 register/field tables. It integrates through `dpp401_dscl_set_scaler_manual_scale()` in DCN401/DCN42 function tables and through line-buffer partition caps from `dcn401_dpp.c`.

## Risks and edge cases
The early `memcmp()` cache depends on `struct scaler_data` being fully initialized and stable; padding or transient pointers can cause missed or redundant programming. The sharpness-only fast path copies `ISHARP_LUT_TABLE_SIZE` entries and assumes `isharp_delta` storage is valid. Filter pointer caching treats pointer identity as coefficient identity for built-in filters and SPL-provided filters, which can miss in-place updates unless `force_coeffs_update` is set. The iSharp 1D LUT skip condition appears inverted in `dpp401_dscl_program_isharp()` (`if (!program_isharp_1dlut)` writes the LUT), so sharpness-only paths need careful validation. Many register writes consume SPL `dscl_prog_data` directly; invalid SPL data can program unsupported modes, taps, or PWL values. Power transitions use longer waits for IPS v2 and deferred shutdown for low-power debug, so sequencing bugs can leave memories in light sleep during coefficient writes.

## Test signals
Scaler validation should cover identity, RGB/YCbCr 444, 420 luma-only/chroma-only/full scaling, FP16 fixed-format bypass, SPL and non-SPL paths, all tap counts 1-8, 2-tap hardcoded coefficient paths, coefficient RAM flips, line-buffer config selection under high downscale ratios, EASF enabled/disabled and 1:1 behavior, iSharp enabled/disabled and sharpness-only updates, blur/scale coefficient updates, memory low-power transitions, and visual CRC/quality tests for scaling and sharpening.
