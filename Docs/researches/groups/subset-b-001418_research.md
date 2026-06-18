# Research: subset-b-001418

Grouped research for AMD DC Display Mode Library files in the Ceph client source mirror. Each section preserves the source path and is intended for deterministic splitting into the mapped source-tree-aligned research files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/display_mode_vba_util_32.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/display_mode_vba_util_32.h

## Purpose
This header declares the DCN32 Display Mode Library utility surface used by the VBA-derived mode validation and bandwidth calculators. It is a broad math/API contract rather than an implementation file: callers feed SoC/IP limits, pipe geometry, timing, tiling, compression, VM, MALL, and link parameters, and receive derived clocks, swath/DET layout, request sizing, prefetch timings, watermarks, bandwidth support decisions, and register-facing timing quantities.

## Important APIs, Types, And Functions
The file depends on `display_mode_enums.h`, `dc_features.h`, `display_mode_structs.h`, and `display_mode_vba.h`, especially `DmlPipe`, `SOCParametersList`, `soc_bounding_box_st`, and `vba_vars_st`. API clusters are:

- DSC/link: `dml32_dscceComputeDelay`, `dml32_dscComputeDelay`, `dml32_CalculateOutputLink`, `dml32_TruncToValidBPP`, `dml32_RequiredDTBCLK`, and `dml32_DSCDelayRequirement`.
- Format and swath geometry: `IsVertical`, `dml32_CalculateBytePerPixelAndBlockSizes`, `dml32_CalculateSwathAndDETConfiguration`, `dml32_CalculateSwathWidth`, `dml32_UnboundedRequest`, `dml32_CalculateDETBufferSize`, and `dml32_CalculateDCCConfiguration`.
- Clock calculation: `dml32_CalculateSinglePipeDPPCLKAndSCLThroughput`, `dml32_CalculateODMMode`, `dml32_CalculateRequiredDispclk`, `dml32_RoundToDFSGranularity`, `dml32_CalculateDPPCLK`, `dml32_CalculateDCFCLKDeepSleep`, `dml32_UseMinimumDCFCLK`, and `dml32_CalculateWriteBackDISPCLK`.
- VM/PTE/meta timing: `dml32_CalculateSurfaceSizeInMall`, `dml32_CalculateVMRowAndSwath`, `dml32_CalculateVMAndRowBytes`, `dml32_CalculatePrefetchSourceLines`, `dml32_CalculateRowBandwidth`, `dml32_CalculateMetaAndPTETimes`, and `dml32_CalculateVMGroupAndRequestTimes`.
- Latency, prefetch, flip, and bandwidth gates: `dml32_CalculateUrgentLatency`, `dml32_CalculateUrgentBurstFactor`, `dml32_CalculateExtraLatencyBytes`, `dml32_CalculateExtraLatency`, `dml32_CalculateVUpdateAndDynamicMetadataParameters`, `dml32_CalculateTWait`, `dml32_CalculatePrefetchSchedule`, `dml32_CalculateFlipSchedule`, `dml32_CalculateWatermarksMALLUseAndDRAMSpeedChangeSupport`, `dml32_CalculateVActiveBandwithSupport`, `dml32_CalculatePrefetchBandwithSupport`, `dml32_CalculateBandwidthAvailableForImmediateFlip`, `dml32_CalculateImmediateFlipBandwithSupport`, and `dml32_CalculateDETSwathFillLatencyHiding`.

## Control Flow And State
There is no local control flow or persistent state in this header. The declared functions are called by DCN32 DML validation and recalculation code to populate `vba_vars_st` and per-pipe derived arrays, then downstream RQ/DLG code reads those derived values to pack hardware register fields. Most APIs follow a large input-array plus output-pointer pattern, with array dimensions tied to `DC__NUM_DPP__MAX`, `DC__NUM_PIPES__MAX`, or active surface counts.

## Dependencies And Integration Points
The contract bridges high-level display validation and low-level hardware programming. It consumes enums for source/output formats, rotations, MALL policy, ODM policy, prefetch modes, flip requirements, and clock-change support. It integrates with `dcn32/display_rq_dlg_calc_32.c`, which reads VBA helper values produced by these calculations; with `display_mode_lib.c`, which binds DCN32 validation/recalculation; and with ASIC FPU files that seed `soc_bounding_box_st`/`ip_params_st`.

## Risks
The risk surface is high because the APIs encode hardware timing and register assumptions through untyped arrays and many parallel output buffers. Dimension mismatches, wrong enum families, stale SoC limits, or caller-provided arrays in the wrong pipe/surface order can silently produce invalid bandwidth or register values. Many outputs are fixed-point or hardware-limited quantities used later with asserts/clamps, so precision and rounding changes require hardware-oriented regression coverage.

## Test Signals
Useful test signals are DML validation pass/fail status, RQ/DLG register dumps, display underflow/flip failures, DSC link-mode selection, MALL/pstate/stutter decisions, and comparisons against known spreadsheet/VBA reference vectors for DCN32 modes. Edge cases should include dual-plane 4:2:0/RGBE alpha, rotated surfaces, ODM combine, DSC, immediate flip, HostVM/GPUVM, MALL static and pstate-change modes, and low-vblank/high-refresh timings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/display_mode_vba_util_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/display_rq_dlg_calc_32.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/display_rq_dlg_calc_32.c

## Purpose
This file converts DCN32 DML/VBA-derived pipe timing and request parameters into RQ, DLG, and TTU register field structures. It is the DCN32 implementation behind the `display_mode_lib` v2 request/dialog callbacks and is used after validation/recalculation has filled the helper-accessible VBA values.

## Important APIs, Types, And Functions
The private `is_dual_plane()` helper treats 4:2:0 formats and RGBE alpha as dual-plane. `dml32_rq_dlg_get_rq_reg()` fills `display_rq_regs_st` fields for luma and chroma/plane1 chunk sizes, meta chunk sizes, DPTE/MPTE group sizes, PTE row height, swath height, expansion modes, and detile plane split address. `dml32_rq_dlg_get_dlg_reg()` fills `display_dlg_regs_st` and `display_ttu_regs_st` with fixed-point refclk/pixel ratios, vblank/prefetch line counts, VM/PTE/meta timings, line/request delivery times, cursor delivery, QoS levels, min TTU vblank, and register-range guarded values.

## Control Flow And State
Both public functions clear output structs with `memset`, query many `get_*` helper values from `display_rq_dlg_helpers.h`/VBA state, pack those values into register encodings, print debug traces, then range-check with `ASSERT()` or saturate selected large fields to 23-bit maxima. `dml32_rq_dlg_get_rq_reg()` computes the DET plane1 base address differently for phantom pipes and for dual-plane luma/chroma storage ratios. `dml32_rq_dlg_get_dlg_reg()` handles ODM 2:1/4:1 grouping by discovering hsplit groups and offsetting horizontal blank end per ODM pipe index.

## State And Persistence Behavior
There is no persistence or global mutable state. The functions mutate only caller-provided register structs. They assume `mode_lib` and `e2e_pipe_param` already contain a coherent DML calculation for `num_pipes` and `pipe_idx`; stale or partially populated `vba` values will directly become register programming.

## Dependencies And Integration Points
Includes `display_mode_lib.h`, `display_mode_vba.h`, `dml_inline_defs.h`, and its own header. `display_mode_lib.c` installs these functions in `dml32_funcs` as `rq_dlg_get_dlg_reg_v2` and `rq_dlg_get_rq_reg_v2`. DCN32 FPU code calls those callbacks when programming pipe RQ/DLG registers. The file depends heavily on helper functions such as `get_pixel_chunk_size_in_kbyte`, `get_dst_y_prefetch`, `get_refcyc_per_*`, `get_swath_height_*`, and `print__*_regs_st`.

## Risks
Register packing is sensitive to helper units: some values are in us, some in refclk cycles, some are fixed-point with `2^2`, `2^8`, `2^10`, or `2^19` scaling. Assertions cover many hardware limits, but several fields are clamped instead, and chroma PTE row overflow logs only a warning. The file assumes at most one cursor, `ref_freq_to_pix_freq < 4.0`, valid linear PTE row height, and coherent ODM hsplit metadata. Divide-by-zero is possible if luma/chroma stored swath bytes are inconsistent.

## Test Signals
Regression signals include exact RQ/DLG/TTU register snapshots for known DCN32 modes, asserts in low-vblank or high-refclk cases, underflow during immediate flip, cursor corruption, ODM combine positioning errors, and dual-plane DET allocation errors. Tests should cover linear vs tiled, phantom pipes, RGBE alpha chunk sizing, 4:2:0 chroma paths, dynamic metadata with GPUVM, and one-cursor boundary behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/display_rq_dlg_calc_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/display_rq_dlg_calc_32.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/display_rq_dlg_calc_32.h

## Purpose
This header exposes the DCN32 request queue and display logic generator register calculation entry points. It documents that DCN32 uses the newer v2 interface shape: register functions receive the full compacted `display_e2e_pipe_params_st` array, active pipe count, and target pipe index rather than a single pipe-only structure.

## Important APIs, Types, And Functions
`dml32_rq_dlg_get_rq_reg()` produces `display_rq_regs_st` for one pipe from `display_mode_lib`, the compacted pipe array, `num_pipes`, and `pipe_idx`. `dml32_rq_dlg_get_dlg_reg()` produces `display_dlg_regs_st` and `display_ttu_regs_st` for one pipe from the same multi-pipe context. The header forward declares `struct display_mode_lib` and imports `display_rq_dlg_helpers.h` for the register and pipe typedefs.

## Control Flow And State
The header has no control flow or state. Its comments define the intended flow: calculate RQ/DLG parameters from DML state, extract hardware register fields into output structs, and use cstate/pstate concepts indirectly through values already present in the DML calculation.

## Dependencies And Integration Points
`display_mode_lib.c` binds these symbols into `dml32_funcs`. DCN32 validation/programming code calls them through `context->bw_ctx.dml.funcs.rq_dlg_get_*_v2`. It is tightly coupled to `display_mode_structs.h` register structs and helper functions implemented outside this header.

## Risks
The v2 function signatures are intentionally different from earlier DML generations. Accidentally wiring them into legacy `rq_dlg_get_*` callback slots would corrupt call arguments. Since the header does not encode array lengths beyond `num_pipes`, callers must guarantee `pipe_idx < num_pipes` and that the compacted array order matches the resource pipe order expected by downstream programming.

## Test Signals
Compile-time coverage should ensure DCN32 binds the v2 callbacks. Runtime coverage should verify each active pipe receives nonzero RQ/DLG/TTU fields from the expected compacted index, especially with split or ODM-combined pipes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/display_rq_dlg_calc_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn321/dcn321_fpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn321/dcn321_fpu.c

## Purpose
This DCN3.21 FPU file defines the ASIC IP parameters and SoC bounding box used by DML, then updates that bounding box from runtime clock tables, BIOS data, debug overrides, and display-core configuration. It is responsible for producing usable voltage/clock states for DML and DML2 on DCN321 hardware.

## Important APIs, Types, And Functions
Global `dcn3_21_ip` describes hardware limits such as DPP/OTG/DSC counts, ROB/DET/config return buffer sizes, chunk sizes, line buffer size, writeback limits, cursor buffers, DCC support, DP2 outputs, and DML workarounds. Global `dcn3_21_soc` seeds latency, bandwidth percentage, channel, bus width, spread-spectrum, MALL, and default clock-limit data. Helpers include `get_optimal_ntuple()`, `calculate_net_bw_in_kbytes_sec()`, sorted-table insertion/removal/swap helpers, `sort_entries_with_same_bw()`, `remove_inconsistent_entries()`, `override_max_clk_values()`, `build_synthetic_soc_states()`, and `dcn321_get_optimal_dcfclk_fclk_for_uclk()`. The public entry point is `dcn321_update_bw_bounding_box_fpu()`.

## Control Flow And State
`dcn321_update_bw_bounding_box_fpu()` asserts FPU availability, applies `dc->config`, debug, `dc->bb_overrides`, BIOS SoC info, VRAM channel information, DSC and prefetch workarounds, PLL/refclk data, and then builds clock states. In legacy mode it constructs DCFCLK/UCLK states from PMFW tables and STA targets; otherwise `build_synthetic_soc_states()` creates sorted points of interest from DCFCLK targets, max DCFCLK, UCLK DPMs, and FCLK DPMs, removes unsupported/duplicate/inconsistent entries, rounds clocks to DPMs, and indexes states. It then calls `dml_init_instance()` for `dc->dml` and the current state's DML, and copies clock/latency overrides into `dc->dml2_options`.

## State And Persistence Behavior
The file mutates global `dcn3_21_ip` and `dcn3_21_soc` in place, plus `dc->dml`, `dc->current_state->bw_ctx.dml`, and `dc->dml2_options.bbox_overrides`. These are runtime driver state updates, not persistent storage, but because the globals are mutable, repeated calls accumulate the latest override values.

## Dependencies And Integration Points
Includes clock manager/resource headers, DCN32/DCN321 resource headers, and `display_mode_vba_util_32.h`. It depends on BIOS callbacks (`get_soc_bb_info`), VRAM info, `clk_bw_params`, `dc->debug`, `dc->bb_overrides`, `dc->clk_mgr`, and `dcn32_calc_num_avail_chans_for_mall()`. It initializes DML as `DML_PROJECT_DCN32`, reusing the DCN32 DML function table.

## Risks
Clock-table synthesis mixes MHz, MT/s, percentages, and channel widths, so unit errors are high impact. Several loops iterate backward with unsigned state counts and assume nonzero entries. The mutable global bounding box can leak override assumptions across contexts if not refreshed carefully. Legacy and synthetic paths can produce different state counts, and the `num_states > MAX_NUM_DPM_LVL` path asserts and returns early. Incorrect BIOS channel data changes MALL allocation and bandwidth limits.

## Test Signals
Useful checks include DML state count and monotonicity, clock-limit dumps after BIOS/debug override, successful `dml_init_instance()` with `DML_PROJECT_DCN32`, DML2 override table contents, and display validation across DC/AC clock tables. Edge tests should cover single-entry PMFW tables, missing FCLK/DPPCLK/PHYCLK data, DC-mode overwrite disabled/enabled, BIOS latency overrides, nondefault VRAM channel width/count, and legacy vs synthetic SoC bounding-box paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn321/dcn321_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn321/dcn321_fpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn321/dcn321_fpu.h

## Purpose
This header exposes the DCN321 FPU bounding-box update hook used by resource and clock-management code. It is intentionally narrow: DCN321 contributes only the bandwidth bounding-box update entry point here.

## Important APIs, Types, And Functions
The public API is `dcn321_update_bw_bounding_box_fpu(struct dc *dc, struct clk_bw_params *bw_params)`. The header includes `dml/display_mode_vba.h`, which provides DML-related type visibility used by the declaration path.

## Control Flow And State
There is no control flow or local state in the header. The implementation mutates `dc->dml`, current-state DML, DML2 bounding-box overrides, and DCN321 global IP/SOC bounding-box structures.

## Dependencies And Integration Points
Callers are expected to invoke this only inside FPU-protected display code paths because the implementation calls `dc_assert_fp_enabled()`. It integrates DCN321 resource setup with DML initialization and PMFW/BIOS clock data ingestion.

## Risks
The include guard name is `__DCN32_FPU_H__`, which is broader than the filename and could collide conceptually with DCN32 headers. The API does not indicate FPU requirements or mutation breadth, so call-site discipline is required.

## Test Signals
Compile coverage should verify the declaration is visible to DCN321 resource code. Runtime tests should verify calling the hook updates DML bounding-box state and does not run outside FPU-safe regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn321/dcn321_fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn35/dcn35_fpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn35/dcn35_fpu.c

## Purpose
This file supplies DCN3.5 DML FPU support: static IP/SOC bounding boxes, runtime bounding-box updates from clock tables and overrides, per-context DML pipe adjustment, and z-state support decisions. It adapts DCN31-era DML pipe population for DCN35-specific timing, DET, immediate-flip, DSC, and low-power policy.

## Important APIs, Types, And Functions
`dcn3_5_ip` defines DCN35 hardware limits and DML knobs, including HostVM/GPUVM, ROB/DET/config return buffer, chunk/meta sizes, DSC support, line buffer, DPP/OTG counts, scaler limits, DPTE buffers, delays, DCC, and default vblank target. `dcn3_5_soc` defines default clock states, latency, bandwidth percentage, page size, bus width, and spread values. Public functions are `dcn35_build_wm_range_table_fpu()` (currently TODO/no-op), `dcn35_update_bw_bounding_box_fpu()`, `dcn35_populate_dml_pipes_from_context_fpu()`, and `dcn35_decide_zstate_support()`. Private helpers detect dual-plane formats and convert microseconds to vertical lines/back porch.

## Control Flow And State
The bounding-box update asserts FPU availability, adjusts DPP/OTG counts from the resource pool, sets channel count from `bw_params`, derives max DISPCLK/DPPCLK from the SMU clock table, maps each runtime entry to the closest static voltage level, copies voltage-dependent and independent clocks into scratch `clock_limits`, applies latency overrides, reinitializes DML as `DML_PROJECT_DCN31`, and mirrors clock/latency data into DML2 override structures when enough clock entries exist. Pipe population first calls `dcn31_populate_dml_pipes_from_context()`, then clamps `vblank_nom`, detects upscaling, forces immediate flip support, disables unbounded request by default, zeros DCC fractions, sets vfront porch/DCC rate/GPUVM min page size, derives DSC input bpc from timing color depth, adjusts DET size, optionally enables unbounded request for a single non-dual-plane <=5K surface, and applies seamless boot ODM policy. Z-state policy counts planes and allows deeper states primarily for no-plane cases or single eDP with PSR/replay and sufficient stutter residency.

## State And Persistence Behavior
The file mutates global `dcn3_5_ip` and `dcn3_5_soc`, `dc->scratch.update_bw_bounding_box.clock_limits`, `dc->dml`, `dc->dml2_options.bbox_overrides`, `context->bw_ctx.dml.ip`, `pipes[]`, `context->bw_ctx.dml.vba.ODMCombinePolicy`, and `context->bw_ctx.bw.dcn.clk.zstate_support`. These updates are runtime state and may vary with clock table, debug flags, stream timing, plane format, and boot optimization flags.

## Dependencies And Integration Points
The file includes resource headers for DCN31/DCN32/DCN35, `dml/dcn31/dcn31_fpu.h`, `dml_inline_defs.h`, and `link_service.h`. It depends on `clk_bw_params`, `dc_state`, `pipe_ctx`, stream timing, debug settings, PSR/replay link state, and DML structs from `display_mode_structs.h`. Resource-layer function tables call these hooks for DCN35 validation and bandwidth setup.

## Risks
`dcn35_build_wm_range_table_fpu()` is a TODO, so callers must not rely on it for real watermark range construction. The update path asserts clock entries exist and copies into fixed-size global arrays; invalid SMU table counts can be dangerous. `pipe` is used after the population loop for single-pipe DET decisions and assumes at least one active pipe. Immediate flip is forced for all active pipes to avoid intermittent underflow, which can raise bandwidth requirements. Z-state behavior depends on stutter period, link index, PSR/replay flags, and debug residency thresholds.

## Test Signals
Important signals include DML/DML2 clock table contents, DET size selected per context, `vblank_nom` clamping, DSC input bpc selection, immediate flip validation, unbounded request enablement for single 5K-or-less RGB surfaces, seamless boot ODM selection, and z-state support logged against stutter period. Tests should cover one SMU clock entry, multiple clock entries, latency overrides, eDP PSR/replay, no-plane/no-stream cases, multi-display with upscaling, dual-plane formats, and DSC color depths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn35/dcn35_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn35/dcn35_fpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn35/dcn35_fpu.h

## Purpose
This header declares the DCN35 FPU hooks for watermark table setup, bandwidth bounding-box update, DML pipe population, and z-state policy. It is the public interface used by DCN35 resource code to enter the FPU-heavy DML support routines.

## Important APIs, Types, And Functions
Exports `dcn35_build_wm_range_table_fpu(struct clk_mgr *clk_mgr)`, `dcn35_update_bw_bounding_box_fpu(struct dc *dc, struct clk_bw_params *bw_params)`, `dcn35_populate_dml_pipes_from_context_fpu(struct dc *dc, struct dc_state *context, display_e2e_pipe_params_st *pipes, enum dc_validate_mode validate_mode)`, and `dcn35_decide_zstate_support(struct dc *dc, struct dc_state *context)`.

## Control Flow And State
The header has no behavior. Its declarations map to implementation routines that mutate global DCN35 IP/SOC state, DML/DML2 bounding boxes, DML pipe arrays, DET policy, and `context->bw_ctx.bw.dcn.clk.zstate_support`.

## Dependencies And Integration Points
It includes `clk_mgr.h`, which supplies clock manager and display-core type declarations. Resource code wraps these functions in FPU entry/exit helpers before calling them.

## Risks
All declared functions are FPU-sensitive by implementation convention, but the header itself does not enforce that. The watermark table function is declared publicly despite being a no-op/TODO in the implementation.

## Test Signals
Compile-time integration should ensure DCN35 resource tables bind these declarations. Runtime checks should confirm callers enter FPU-safe regions, and that the no-op watermark function is not the only source of required watermark programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn35/dcn35_fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn351/dcn351_fpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn351/dcn351_fpu.c

## Purpose
This file is the DCN3.51 variant of the DCN35 FPU support layer. It defines DCN351-specific IP/SOC bounding boxes, updates DML and DML2 bounding-box data from runtime clock tables and overrides, customizes DML pipe inputs, and decides z-state support with DCN351-specific restrictions.

## Important APIs, Types, And Functions
`dcn3_51_ip` is closely aligned with DCN35 IP settings: HostVM/GPUVM enabled, ROB/DET/config return buffer sizing, chunk/meta sizes, DSC and line-buffer capabilities, DPP/OTG limits, scaler limits, DPTE buffers, delay values, DCC, and `VBlankNomDefaultUS`. `dcn3_51_soc` differs materially from DCN35 by providing eight default clock states with DCFCLK/FCLK/SOCCLK/DRAM/DISPCLK/DPPCLK values, default four channels, and a 2400 MHz VCO. Public functions are `dcn351_update_bw_bounding_box_fpu()`, `dcn351_populate_dml_pipes_from_context_fpu()`, and `dcn351_decide_zstate_support()`. Private helpers mirror DCN35 dual-plane detection, microsecond-to-line conversion, and vertical back porch calculation.

## Control Flow And State
The update function asserts FPU availability, sets IP DPP/OTG counts and channel count, derives max display clocks, maps SMU clock entries to closest static clock-limit rows, copies clock data into scratch/global SOC tables, applies debug and `bb_overrides` latencies, reinitializes DML as `DML_PROJECT_DCN31`, and mirrors clocks/latencies into DML2 override tables. Pipe population calls the DCN31 base population, adjusts `vblank_nom`, forces immediate flip, disables unbounded request by default, zeros DCC fractions, sets DCC rate/DSC input bpc/GPUVM page size, changes DET size based on single-pipe, CRB policy, or upscaled multi-display cases, and applies eDP seamless boot ODM policy. Z-state logic explicitly notes DCN351 does not support z9/z10 and should allow at most Z8.

## State And Persistence Behavior
The file mutates global `dcn3_51_ip` and `dcn3_51_soc`, `dc->scratch.update_bw_bounding_box.clock_limits`, `dc->dml`, DML2 bounding-box overrides, per-context DML IP state, `pipes[]`, ODM policy in `context->bw_ctx.dml.vba`, and final z-state support. It has no persistent storage but carries mutable global runtime defaults.

## Dependencies And Integration Points
Includes DCN31/DCN32/DCN35/DCN351 resource headers, `dml/dcn31/dcn31_fpu.h`, `dml/dcn35/dcn35_fpu.h`, `dml_inline_defs.h`, and `link_service.h`. DCN351 resource code calls `dcn351_update_bw_bounding_box_fpu()` and `dcn351_populate_dml_pipes_from_context_fpu()`; the resource search also showed DCN351 init paths may reuse DCN35 z-state decisions in places, so naming and call-site choice matter.

## Risks
The z-state function contains a suspicious assignment-like ternary result: `support = allow_z8 ? allow_z8 : DCN_ZSTATE_SUPPORT_DISALLOW;`, which stores boolean `true` rather than an explicit `DCN_ZSTATE_SUPPORT_ALLOW_Z8_ONLY` enum value if `allow_z8` is true. That may only be safe if enum value `1` matches Z8-only. Like DCN35, the code assumes valid clock-table counts, uses a post-loop `pipe` pointer for single-pipe logic, and globally mutates bounding-box tables. DML is initialized as `DML_PROJECT_DCN31`, so DCN351 remains dependent on older DML function selection while feeding DML2 overrides separately.

## Test Signals
Tests should verify the eight-state default table is replaced correctly by SMU clocks, DML2 override clocks include DRAM speed and DTBCLK, latency overrides propagate, DET and unbounded request decisions match DCN351 policy, DSC input bpc is correct, and z-state outputs never allow unsupported z9/z10. A focused test should validate the `allow_z8` ternary maps to the intended enum.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn351/dcn351_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn351/dcn351_fpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn351/dcn351_fpu.h

## Purpose
This compact header declares DCN351 FPU hooks for bandwidth bounding-box update, DML pipe population, and z-state policy. It exposes the DCN351-specific counterparts to the DCN35 FPU routines.

## Important APIs, Types, And Functions
Exports `dcn351_update_bw_bounding_box_fpu(struct dc *dc, struct clk_bw_params *bw_params)`, `dcn351_populate_dml_pipes_from_context_fpu(struct dc *dc, struct dc_state *context, display_e2e_pipe_params_st *pipes, enum dc_validate_mode validate_mode)`, and `dcn351_decide_zstate_support(struct dc *dc, struct dc_state *context)`.

## Control Flow And State
The header has no local behavior. Implementations update mutable DCN351 global IP/SOC bounding boxes, DML/DML2 clock and latency state, per-context DML pipe fields, DET policy, and z-state support.

## Dependencies And Integration Points
It includes `clk_mgr.h` for the display and clock type declarations needed by the prototypes. DCN351 resource code uses these declarations inside FPU-safe wrappers.

## Risks
The interface does not advertise that the implementation initializes DML as `DML_PROJECT_DCN31` or that z-state support is DCN351-restricted. Callers must pick the DCN351 functions rather than the similar DCN35 functions when SoC-specific clocks and z-state policy matter.

## Test Signals
Compile integration should verify DCN351 resource tables bind these hooks. Runtime checks should confirm the DCN351 update path uses `dcn3_51_soc`/`dcn3_51_ip` and that z-state policy differs from DCN35 where required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn351/dcn351_fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_enums.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_enums.h

## Purpose
This header centralizes DML enum contracts for display formats, tiling, validation results, power-state policies, output links, and mode-support decisions. These values are shared across DML calculators, pipe population code, SoC bounding-box setup, and register packing.

## Important APIs, Types, And Functions
The file defines enums for output encoders/formats/BPC, source formats, scan direction, swizzle modes, line-buffer depth, voltage states, macro tile size, cursor BPP, DRAM clock-change support, output standards, MPC affinity, request type, self-refresh affinity, validation status, writeback config, ODM combine modes/policies, immediate flip requirement, unbounded requesting policy, rotation angle, MALL use, DP link rate, FCLK-change support, prefetch modes, output type, and output rate.

## Control Flow And State
There is no control flow or state. The numeric values form ABI-like contracts inside the driver: DML calculations, resource policy, and status logging all assume stable enum meanings. Some enums alias values intentionally, such as mono formats mapping to 444 formats.

## Dependencies And Integration Points
Included by `display_mode_structs.h`, `display_mode_lib.h`, DCN utility headers, and numerous generated DML implementations. `display_mode_lib.c` maps `dm_validation_status` to user-readable strings. DCN32 RQ/DLG code uses format, rotation, swizzle, ODM, and output enums to choose register packing behavior.

## Risks
Changing numeric order can break table indexing, validation status mapping, and hardware policy interpretation. The status-to-string mapper in `display_mode_lib.c` does not cover all enum values in this file, so new statuses can appear as "Unknown Status" unless kept in sync. Some enum names are historical and cross-generation, increasing risk of using the wrong policy enum in newer DCN paths.

## Test Signals
Compile coverage catches missing enum names, but behavior tests should verify DML validation messages, ODM policy behavior, MALL and prefetch mode selection, output link selection, and immediate flip requirements. Static review should flag new enum values that need logging or DML2 translation updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_enums.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_lib.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_lib.c

## Purpose
This file is the generation dispatch and logging core for DML. It binds `display_mode_lib` instances to the correct generation-specific validate/recalculate/RQ/DLG functions, maps validation statuses to messages, and provides verbose logging for pipe inputs and mode-support results.

## Important APIs, Types, And Functions
Static `dml_funcs` tables exist for DML20, DML20v2, DML21, DML30, DML31, DML314, and DML32. `dml_init_instance()` copies SoC/IP bounding boxes into a `display_mode_lib`, stores the project enum, and selects the function table. `dml_get_status_message()` translates selected `dm_validation_status` values. `dml_log_pipe_params()` prints source, destination, scaler, output, and clock config for each pipe. `dml_log_mode_support_params()` prints per-voltage-state support booleans from `mode_lib->vba`.

## Control Flow And State
Initialization is a switch on `enum dml_project`; most projects use legacy `rq_dlg_get_*` callbacks, while `DML_PROJECT_DCN32` binds `rq_dlg_get_*_v2` because DCN32 requires multi-pipe arguments. Logging loops over provided pipe count or `vba.soc.num_states` and emits `dml_print()` diagnostics.

## State And Persistence Behavior
`dml_init_instance()` mutates the caller-owned `display_mode_lib` by value-copying the SoC/IP structs and replacing the callback table. There is no global mutable state in this file. Logging reads current `vba` and pipe structures without persisting data.

## Dependencies And Integration Points
The file includes generation-specific DML and RQ/DLG headers from DCN20 through DCN32 plus `dml_logger.h`. ASIC FPU files call `dml_init_instance()` after constructing bounding boxes. DCN FPU validation code calls `mode_lib->funcs.validate`, `recalculate`, and RQ/DLG callbacks through this dispatch layer.

## Risks
Unsupported or unrecognized `project` values leave `funcs` unchanged, which can produce stale callbacks if the struct was previously initialized. The validation status message switch covers only a subset of enum values. DCN35/DCN351 currently initialize as `DML_PROJECT_DCN31`, which is intentional in the read code but means they depend on DCN31 DML behavior unless DML2 paths override it. Logging assumes populated pointers and valid pipe counts.

## Test Signals
Tests should verify each project selects the expected callback table, especially DCN32 v2 RQ/DLG callbacks. Status-message tests should catch unmapped validation failures. Debug logging tests can compare key pipe fields and mode-support flags when diagnosing bandwidth validation regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_lib.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_lib.h

## Purpose
This header defines the main DML instance object, project enum, callback table, and public utility functions for initialization and logging. It is the core interface between resource/FPU code and the generated DML implementations.

## Important APIs, Types, And Functions
`enum dml_project` identifies supported DML generations up to `DML_PROJECT_DCN32`. `struct dml_funcs` contains callbacks for validation, recalculation, legacy RQ/DLG register calculation, and DCN32 v2 RQ/DLG register calculation. `struct display_mode_lib` stores IP params, SoC bounding box, selected project, `vba_vars_st`, logger pointer, callback table, a six-pipe DML pipe state array, and `validate_max_state`. Public functions are `dml_init_instance()`, `dml_get_status_message()`, `dml_log_pipe_params()`, and `dml_log_mode_support_params()`.

## Control Flow And State
The header has no implementation behavior, but it defines the state shape that all DML calculations mutate. Callers initialize the struct with a project-specific bounding box, call `validate`/`recalculate`, and then call the appropriate RQ/DLG callback family for hardware register derivation.

## Dependencies And Integration Points
Includes `dm_services.h`, `dc_features.h`, `display_mode_structs.h`, `display_mode_enums.h`, and `display_mode_vba.h`. It is consumed by `display_mode_lib.c`, generation-specific DML code, and ASIC FPU/resource code. The six-element `dml_pipe_state` reflects a fixed display pipe capacity assumption in this tree.

## Risks
The callback table contains both legacy and v2 RQ/DLG signatures; calling the wrong family for a project would corrupt arguments. The project enum currently ends at DCN32, so newer DCN35/DCN351 code initializing as DCN31 is a compatibility choice rather than a first-class project entry. Struct size and embedded generated VBA state make copying and initialization order important.

## Test Signals
Compile-time tests should catch callback signature mismatches. Runtime validation should ensure initialized `funcs` pointers are non-null for every active project and that DCN32 uses v2 callbacks. New DML projects should add enum values, dispatch table entries, and initialization tests together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_structs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_structs.h

## Purpose
This header defines the data model used by the Display Mode Library and its VCS-DPI heritage. It contains the SoC/IP bounding boxes, pipe input/output structures, request/dialog calculation structures, hardware register field containers, watermark/latency structs, and DML helper pipe snapshots.

## Important APIs, Types, And Functions
Key typedefs alias `_vcs_dpi_*` structs to shorter names such as `voltage_scaling_st`, `soc_bounding_box_st`, `ip_params_st`, `display_pipe_source_params_st`, `display_output_params_st`, `display_e2e_pipe_params_st`, `display_rq_regs_st`, `display_dlg_regs_st`, and `display_ttu_regs_st`. `Watermarks`, `Latencies`, `DmlPipe`, and `SOCParametersList` provide higher-level DML calculation containers. Major structs include `_vcs_dpi_soc_bounding_box_st`, `_vcs_dpi_ip_params_st`, source/output/scaler/destination pipe params, RQ sizing/misc/dialog params, DLG/TTU/RQ register structs, DLG system params, and arbitration params.

## Control Flow And State
There is no executable flow. These structs are mutable state containers passed through DML validation, recalculation, RQ/DLG packing, FPU bounding-box update, and resource programming. Many fields are arrays or scalar hardware parameters whose units are implied by field name and calling convention.

## Dependencies And Integration Points
Includes `dc_features.h` and `display_mode_enums.h`. ASIC-specific FPU files populate `_vcs_dpi_ip_params_st` and `_vcs_dpi_soc_bounding_box_st`; resource code populates `display_e2e_pipe_params_st`; DML utility functions read and write these fields; RQ/DLG code emits `display_rq_regs_st`, `display_dlg_regs_st`, and `display_ttu_regs_st` for hardware programming.

## Risks
The file is a shared contract with little type-level unit safety. Fields mix MHz, MT/s, bytes, kbytes, microseconds, nanoseconds-derived values, fixed-point register encodings, booleans, and enum-backed ints. Many newer fields are appended for DCN32+ behavior, so older generation code may ignore them. Incorrect initialization, stale values, or partial struct copies can cause validation failures or hardware underflow.

## Test Signals
Tests should focus on end-to-end struct population rather than this header alone: bounding-box dumps, pipe parameter logs, RQ/DLG register dumps, validation statuses, and DML2 translation output. Static checks should verify new fields are initialized by relevant ASIC bounding boxes and pipe population paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_structs.h -->
