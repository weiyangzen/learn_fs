# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/dcn30_fpu.c

## Purpose

This file contains DCN 3.0 Display Mode Library routines that require floating-point execution in the AMD display driver. It defines the DCN 3.0 IP and SOC bounding boxes used to initialize DML, translates runtime display/writeback state into DML structures, calculates watermarks and DLG parameters, updates bandwidth bounding boxes from clock tables and BIOS data, and builds power-management watermark range tables.

The file is part of the DCN30 resource/DML integration layer. It is not a generic math library: each function asserts floating-point access with `dc_assert_fp_enabled()` and either reads or mutates `struct dc`, `struct dc_state`, `struct clk_mgr`, DML pipe arrays, or global DCN30 bounding-box structures.

## Important APIs, Types, and Functions

Two global model structures anchor the file. `dcn3_0_ip` is a `_vcs_dpi_ip_params_st` describing DCN 3.0 display IP limits and capacities: DET/ROB sizes, DPP/OTG/DSC counts, chunk sizes, buffer sizes, scaler limits, DCC support, cursor capacity, ODM capability, and clock delay constants. `dcn3_0_soc` is a `_vcs_dpi_soc_bounding_box_st` describing initial clock limits, latency assumptions, bandwidth percentages, return bus widths, DRAM behavior, urgent latency adjustment, and related SOC parameters.

The exported functions are:

- `dcn30_fpu_populate_dml_writeback_from_context()` walks active pipe contexts, finds enabled writeback targets attached to the pipe plane, computes writeback source/destination dimensions, taps, ratios, format, and worst-case writeback DISPCLK, then stores the selected writeback model in the matching DML pipe.
- `dcn30_fpu_set_mcif_arb_params()` fills MCIF writeback urgent and pstate watermarks for all client slots and computes the DRAM speed change duration in refclk cycles.
- `dcn30_fpu_update_soc_for_wm_a()` updates the context DML SOC latencies from clock-manager WM_A table entries, with special handling for firmware-based mclk switching and zero pstate latency.
- `dcn30_fpu_calculate_wm_and_dlg()` is the main watermark/DLG orchestration routine for DCN30 validation. It handles pstate support, firmware-based vblank stretch fallback, DCFCLK selection, watermark sets B/C/A/D, dummy pstate latency selection, display and DPP clock assignment, FPO workarounds, DLG calculation through `dcn20_calculate_dlg_params()`, and final mclk-switch setup.
- `dcn30_fpu_update_dram_channel_width_bytes()` patches the global SOC bounding box from BIOS VRAM info.
- `dcn30_fpu_update_max_clk()` fills missing max clock values from the current global SOC clock limit.
- `dcn30_fpu_get_optimal_dcfclk_fclk_for_uclk()` derives optimal DCFCLK and FCLK from UCLK, channel count, channel width, DRAM bandwidth limits, fabric return width, and DCF return bus width.
- `dcn30_fpu_update_bw_bounding_box()` updates global clock-limit states from validated DCFCLK and DRAM-speed arrays, refreshes VCO speed from the dentist clock, and reinitializes DML instances.
- `dcn30_find_dummy_latency_index_for_fw_based_mclk_switch()` searches dummy pstate latency table entries until DML allows self-refresh plus mclk switch in vblank.
- `dcn3_fpu_build_wm_range_table()` initializes watermark sets A, C, and D plus dummy pstate table defaults for the clock manager.
- `patch_dcn30_soc_bounding_box()` reads BIOS SOC bounding-box latency information and patches the global SOC latency fields.

## Control Flow

Writeback population is a per-active-stream scan. For each pipe context with a stream, it clears writeback enable/count in the current DML pipe, scans `stream->writeback_info`, filters for enabled writebacks whose source plane matches the pipe plane, builds a `writeback_st`, calculates required writeback DISPCLK with `dml30_CalculateWriteBackDISPCLK()`, and keeps only the worst-case writeback because DML models one writeback parameter set per pipe.

The main `dcn30_fpu_calculate_wm_and_dlg()` flow starts from DML VBA outputs: selected voltage level, `maxMpcComb`, DCFCLK state, and DRAM clock-change support. It clears firmware pstate optimization flags on all streams. If natural pstate switching is unsupported, it tests whether firmware-based vblank stretch can support mclk switching, finds a dummy latency index if so, restores original latency state, and revalidates bandwidth. It then selects at least `soc.min_dcfclk`, programs pipe clock config fields, computes watermark set B when valid, computes set C with dummy pstate latency, maps set A to C when pstate is unsupported, or recalculates set A from normal WM_A latencies when pstate is supported. Set D is currently copied from set A after a disabled code block.

After watermarks, it writes per-pipe calculated DISPCLK and DPPCLK, applies forced-clock and debug minimum overrides, applies a firmware pstate optimization workaround for a narrow DRAM speed/channel case, and calls `dcn20_calculate_dlg_params()` to populate DLG parameters using shared DCN20 logic. It then restores full pstate latency when needed and configures firmware-based vblank stretch if that path was selected.

Bounding-box update flow mutates globals before reinitializing DML. `dcn30_fpu_update_bw_bounding_box()` fills each SOC clock state with per-state DCFCLK/FCLK/DRAM speed and max display clocks, then calls `dml_init_instance()` for `dc->dml` and, when present, `dc->current_state->bw_ctx.dml`.

## State and Persistence Behavior

This file mutates both per-validation state and global model state. Per-validation mutations include `pipes[*].dout.wb`, `pipes[*].clks_cfg`, `context->bw_ctx.dml.soc` latencies, `context->bw_ctx.bw.dcn.watermarks`, `context->bw_ctx.bw.dcn.clk.fw_based_mclk_switching`, stream `fpo_in_use`, `context->perf_params.stutter_period_us`, and MCIF arbitration parameters.

Global mutable state includes `dcn3_0_soc` and `dcn3_0_ip` as DML initialization inputs. BIOS and clock-table patch functions update `dcn3_0_soc`, so subsequent DML initializations inherit those values. There is no file I/O, durable storage, or allocation in this file, but the global bounding-box mutations persist for the life of the driver instance.

## Dependencies and Integration Points

The file includes resource, clock manager, register helper, DCN calculation math, DCN20/DCN30 resource headers, the DCN30 SMU interface, DML VBA 3.0 declarations, and its own header. It is called from `resource/dcn30/dcn30_resource.c` for writeback population, MCIF arbitration, watermark/DLG calculation, DRAM channel width updates, max clock updates, optimal clock derivation, and bandwidth bounding-box refresh. `clk_mgr/dcn30/dcn30_clk_mgr.c` calls `dcn3_fpu_build_wm_range_table()`. Resource construction calls `patch_dcn30_soc_bounding_box()`.

The function set depends on several external DCN30/DCN20 helpers: `dcn30_can_support_mclk_switch_using_fw_based_vblank_stretch()`, `dcn30_internal_validate_bw()`, `dcn30_setup_mclk_switch_using_fw_based_vblank_stretch()`, `dcn20_calculate_dlg_params()`, DML watermark getters, DML clock getters, and DML instance initialization.

## Risks and Edge Cases

Global mutable bounding boxes are a major coupling point. BIOS-derived latency patches, DRAM channel width updates, and bandwidth-table updates change `dcn3_0_soc` globally and then reinitialize DML; incorrect ordering can leave current or future contexts using stale values. The code assumes FPU access is enabled; calling these functions without the FPU guard violates kernel FPU rules.

Watermark calculation is sensitive to pstate support. The fallback path temporarily changes `dram_clock_change_latency_us`, runs validation, restores latency, and may use dummy pstate latencies. A missed restore or stale `pipe_cnt`/`vlevel` after validation would affect watermarks and DLG. The dummy-latency search asserts if no valid index is found and then falls back to index 3, accepting possible underflows over crashes.

Writeback support compresses multiple writebacks attached to one plane into the worst writeback DISPCLK model, which is a deliberate workaround for DML's one-writeback-per-pipe assumption. This can be conservative but may hide per-writeback distinctions. The FPO workaround mutates `DRAMSpeed` for a narrow NV24 bandwidth issue, so tests should check that later calculations see the intended adjusted speed.

`dcn30_fpu_get_optimal_dcfclk_fclk_for_uclk()` performs floating-point bandwidth division and writes integer outputs without explicit rounding policy beyond assignment truncation. `dcn30_fpu_update_bw_bounding_box()` ignores its `bw_params` parameter and assumes input arrays are sized for `dcn3_0_soc.num_states`.

## Test Signals

Good test coverage includes DCN30 bandwidth validation modes with natural pstate support, unsupported pstate with and without firmware-based vblank stretch, dummy pstate table selection, forced clocks, debug minimum clocks, writeback enabled/disabled and multiple writeback targets, BIOS latency overrides, DRAM channel width override, and clock-table-driven bounding-box updates. Golden comparisons should verify watermark sets A/B/C/D, `fw_based_mclk_switching`, `stutter_period_us`, DLG register outputs after `dcn20_calculate_dlg_params()`, and MCIF arbitration watermarks.

Runtime signals include absence of FPU assertion violations, no display underflows during pstate/mclk transitions, correct PMFW watermark range table programming, stable DML validation after reinitialization, and no regression in DCN30 resource validation call sites.
