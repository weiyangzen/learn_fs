# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/dcn20_fpu.c

## Purpose

`dcn20_fpu.c` centralizes floating-point display mode and bandwidth logic for DCN2.0, DCN2.01, and DCN2.1. It owns DCN2 hardware bounding-box defaults, watermark tables, DML pipe population, DML-based bandwidth validation, watermark/DLG/RQ/TTU calculation, writeback modeling, bounding-box patching from firmware/SMU/debug overrides, and selected DCN2.1 clock-table initialization.

Like `dcn10_fpu.c`, it follows AMD DC's kernel FPU isolation convention: callers must enter the FPU critical section outside this file, and every public function asserts FPU access with `dc_assert_fp_enabled()`.

## Important APIs, Types, And Data

Major global data:

- `dcn2_0_ip`, `dcn2_0_nv14_ip`, `dcn2_1_ip`: DML IP parameter tables for DCN2.0/Navi variants and DCN2.1. They describe DPP/OTG/DSC/writeback counts, VM/PTE capabilities, buffers, chunks, scaler capabilities, cursor buffers, delay values, DCC/XFC support, and cursor count.
- `dcn2_0_soc`, `dcn2_0_nv14_soc`, `dcn2_0_nv12_soc`, `dcn2_1_soc`: DML SoC bounding boxes with clock-limit arrays, voltage states, latency values, bandwidth policy, DRAM/channel configuration, bus widths, clock-change latencies, XFC parameters, and urgent-burst behavior.
- `ddr4_wm_table_gs`, `lpddr4_wm_table_gs`, `lpddr4_wm_table_with_disabled_ppt`, `ddr4_wm_table_rn`, `ddr4_1R_wm_table_rn`, `lpddr4_wm_table_rn`: watermark tables for different platforms/memory configurations.
- `LPDDR_MEM_RETRAIN_LATENCY`: latency constant used for DCN2.1 watermark set D retraining.

Primary exported functions:

- `dcn20_populate_dml_writeback_from_context`: populates one writeback model per active stream, using stream writeback info slot 0.
- `dcn20_fpu_set_wb_arb_params`: calculates MCIF writeback urgent and pstate watermarks and time-per-pixel.
- `dcn20_calculate_dlg_params`: applies DML results to clocks, pipe DLG timing, DET/unbounded request state, MCIF arbitration, RQ/DLG registers, pstate support, compbuf size, and zstate support.
- `dcn20_populate_dml_pipes_from_context`: translates active `pipe_ctx` entries into DML `display_e2e_pipe_params_st`.
- `dcn20_calculate_wm`: calculates DCN2.0 watermarks A-D and required pipe clocks for the selected voltage.
- `dcn20_update_bounding_box`: rebuilds SoC clock limits from SMU max clocks and UCLK states.
- `dcn20_cap_soc_clocks`: caps a bounding box to SMU-reported max clocks and removes duplicate states.
- `dcn20_patch_bounding_box`: applies debug/BB latency overrides to a SoC bounding box.
- `dcn20_validate_bandwidth_fp`: full DCN2.0 validation entry point with dummy-pstate fallback behavior.
- `dcn20_fpu_set_wm_ranges`: fills SMU watermark range fill-clock bounds for a table entry.
- `dcn20_fpu_adjust_dppclk`: doubles or halves a required DPPCLK entry around validation.
- `dcn21_populate_dml_pipes_from_context`: DCN2.1 wrapper over the DCN2.0 pipe population path that enables hostvm/gpuvm fields.
- `dcn21_validate_bandwidth_fp`: DCN2.1 validation entry point.
- `dcn21_update_bw_bounding_box_fpu`: reconstructs DCN2.1 DML clock limits from `clk_bw_params`, inserts a low DF pstate, updates resource counts, and reinitializes DML.
- `dcn21_clk_mgr_set_bw_params_wm_table`: sets watermark set D as a retraining entry.
- `dcn201_populate_dml_writeback_from_context_fpu`: DCN2.01 writeback population supporting multiple writebacks and selecting worst-case writeback DISPCLK.

Important internal helpers:

- `is_dtbclk_required`: detects DP 128b/132b links and requests DTBCLK.
- `decide_zstate_support`: determines Z8/Z9/Z10 support from plane count, eDP link index, PSR/replay, and DML stutter period.
- `dcn20_adjust_freesync_v_startup`: patches `vstartup_start` for adaptive sync timing on pre-DCN3.1.
- `swizzle_to_dml_params`: maps DC swizzle modes to DML swizzle enums.
- `dcn20_validate_bandwidth_internal`: common DCN2.0 fast-validate plus programming calculation path.
- `patch_bounding_box`, `calculate_wm_set_for_vlevel`, `dcn21_calculate_wm`, and `construct_low_pstate_lvl`: DCN2.1-specific watermark and clock-table helpers.

## Control Flow

The DCN2.0 validation path is:

1. `dcn20_validate_bandwidth_fp` asserts FPU access, copies pstate latency, writes debug DRAM-clock-change policy into `context->bw_ctx.dml.soc`, and asserts it is not mutating `dc->current_state`.
2. Fast validation modes call `dcn20_validate_bandwidth_internal` directly.
3. Programming validation first tries the full DML pstate latency by calling the internal validator.
4. `dcn20_validate_bandwidth_internal` calls `dcn20_fast_validate_bw`, receives pipe count, split mapping, and voltage level, exits early on empty/failed/non-programming cases, and in programming mode calls `dcn20_calculate_wm` followed by `dcn20_calculate_dlg_params`.
5. If full pstate is unsupported and a dummy pstate latency exists, `dcn20_validate_bandwidth_fp` temporarily changes `dram_clock_change_latency_us`, clears the pipe array, reruns internal validation, and accepts the result with `p_state_change_support` forced false when the fallback succeeds.
6. It restores original pstate latency before returning.

`dcn20_populate_dml_pipes_from_context` is the translation front end used by validation:

1. It first determines whether all streams have synchronizable timing/vblank unless debug disables timing sync.
2. For each active pipe, it fills refclk, vblank/active timing, interlace, pixel rate, OTG instance, DSC state, dynamic metadata, vtotal min/max, ODM combine state, hsplit group, output type, output format/bpp, DSC bpp, audio sample rate, cursor count, and default cursor properties.
3. For no-plane pipes, it builds a conservative synthetic source capped to 1920x1080 and adjusts viewport/recout for ODM combine.
4. For real planes, it fills immediate flip, split status, stereo split exceptions, rotation, viewport/surface/pitch/DCC, recout/full recout including split-chain width, scaler ratios/taps, macro tile, DML swizzle, and source pixel format.
5. It delegates writeback population to the resource pool callback.

`dcn20_calculate_wm` uses DML fast-validation results to set per-pipe DISPCLK/DPPCLK and ODM combine, repopulating DML pipes if DML pipe count and pipe index diverge. It then evaluates watermark sets B, C, D, and A by temporarily changing pipe 0 voltage/DCF/SOC clocks and calling DML watermark helper functions.

`dcn20_calculate_dlg_params` applies programmed results: it sets MCIF writeback arbitration, writes selected DML clocks into `context->bw_ctx.bw.dcn.clk`, determines pstate and DTBCLK support, updates per-pipe DPP clocks and `pipe_dlg_param`, handles SubVP phantom DET/unbounded request requirements, computes compbuf size, generates RQ/DLG register values through DML callbacks, and decides zstate support.

DCN2.1 follows the same broad validation structure with `dcn21_fast_validate_bw`, `dcn21_calculate_wm`, and `dcn20_calculate_dlg_params`. Its watermark calculation uses `clk_mgr->bw_params->wm_table` entries and selected voltage levels rather than the DCN2.0 fixed B/C/D sequence.

Bounding-box update flows:

- `dcn20_update_bounding_box` clears clock limits and rebuilds them from UCLK states and SMU max clocks, choosing a minimum DCFCLK, deriving FCLK from UCLK ratio, capping SOCCLK/DCFCLK by SMU maxes, and duplicating the last state for DML.
- `dcn20_cap_soc_clocks` caps existing state clocks to SMU maxes and reduces `num_states` for trailing duplicates.
- `dcn21_update_bw_bounding_box_fpu` maps firmware clock-table entries onto the closest default DCN2.1 DCFCLK level for display-related clocks, inserts a reserved low pstate, duplicates the last level, updates global `dcn2_1_soc`, and reinitializes `dc->dml`.

## State And Persistence Behavior

There is no disk persistence. The file has extensive in-memory state effects:

- Global SoC/IP tables are mutable globals and can be updated, especially `dcn2_1_soc`, `dcn2_1_ip`, and their clock limits/resource counts.
- Validation writes `context->bw_ctx.dml.soc` policy flags and temporarily modifies `dram_clock_change_latency_us`.
- Validation writes `context->bw_ctx.bw.dcn.watermarks`, clock votes, pstate support, DTBCLK enable, zstate support, compbuf size, and bandwidth DPP/DISPCLK snapshots.
- DLG calculation writes each active `pipe_ctx`'s `pipe_dlg_param`, `plane_res.bw.dppclk_khz`, `det_buffer_size_kb`, `unbounded_req`, `dlg_regs`, `ttu_regs`, and `rq_regs`.
- Pipe population mutates only the caller-provided `pipes` array, except through delegated writeback callbacks.
- Bounding-box patch functions mutate passed bounding boxes and, for DCN2.1, `dc->clk_mgr->bw_params->wm_table`.
- `dcn21_update_bw_bounding_box_fpu` uses `dc->scratch.update_bw_bounding_box.clock_limits` as a staging buffer and calls `dml_init_instance` to reinitialize the display mode library.

All public functions assume caller-managed FPU lifetime. They do not call `DC_FP_START` or `DC_FP_END`.

## Dependencies And Integration Points

Direct dependencies include:

- Display resource/clock/link/core state: `resource.h`, `clk_mgr.h`, `dchubbub.h`, `link_service.h`, `dc_state_priv.h`.
- DCN2.0/DCN2.1 resource headers for platform-specific pools and fast validation.
- `dcn20_fpu.h` for exported prototypes.
- DML helpers such as `get_wm_urgent`, `get_wm_stutter_exit`, `get_wm_dram_clock_change`, `get_vstartup`, `CalculateWriteBackDISPCLK`, `dml_get_status_message`, and DML RQ/DLG callbacks through `context->bw_ctx.dml.funcs`.
- Resource pool callbacks: `set_mcif_arb_params`, `populate_dml_writeback_from_context`, and optional `populate_dml_pipes`.
- Link service callback `dp_is_128b_132b_signal`, audio helper `get_audio_check`, resource helper `resource_get_odm_slice_count`, and SubVP helper `dc_state_get_pipe_subvp_type`.
- SMU/firmware clock structures: `pp_smu_nv_clock_table`, `clk_bw_params`, `clk_limit_table`, `wm_table`, and `pp_smu_wm_range_sets`.

Repository call sites show these functions are integrated from DCN20/DCN21 resource validation and bounding-box update code, and newer DCN resource files reuse `dcn20_patch_bounding_box`.

## Risks And Edge Cases

- Every public entry point requires active kernel FPU protection. Runtime assertions catch misuse, but the type system does not.
- The validation code asserts `context != dc->current_state` because current pipe merge/split logic is unsafe for in-place current-state mutation. Violating this can corrupt live display state.
- `dcn20_populate_dml_writeback_from_context` takes `&res_ctx->pipe_ctx[i].stream->writeback_info[0]` before checking `stream` for null, which is a latent null-deref risk if evaluated by the compiler before the later guard. The DCN2.01 version avoids this by checking `stream` first.
- DML pipe population assumes several nested resource pointers exist for active streams and planes, including timing generator, scaler data, link/sink for eDP zstate logic, and plane size/pitch metadata.
- Many calculations use pipe index and DML pipe index mappings (`pipe_split_from`, `pipe_idx`, `pipe_cnt`). Off-by-one or split-chain divergence can assign clocks or ODM combine settings to the wrong pipe.
- DCN2.0 watermark set D uses clock limit index 2 when `vlevel < 3`, which may be intentional but is fragile around low `num_states`.
- Bounding-box updates assume `num_states > 0`; they guard zero in `dcn20_update_bounding_box`, but duplicate-last-state logic depends on arrays sized for one extra state.
- `dcn20_cap_soc_clocks` reduces only `num_states` for duplicates; stale entries remain in the array but should be ignored. Consumers must honor `num_states`.
- DCN2.1 updates mutate global `dcn2_1_soc` and `dcn2_1_ip`, so multi-device or reinitialization scenarios must ensure the globals are safe for the driver architecture.
- `construct_low_pstate_lvl` increments `clk_table->num_entries` and shifts entries in place; callers must ensure capacity in the clock table.
- Several platform tables encode hard-coded latency and clock values. Wrong ASIC/memory table selection causes validation errors, underflow, flicker, or excessive power.

## Test Signals

Useful validation signals include:

- Mode validation coverage for DCN2.0, DCN2.01, and DCN2.1 in fast and programming modes.
- Regression tests for full pstate support, dummy pstate fallback, no-stream/no-plane cases, and empty `pipe_cnt`.
- DML pipe population tests across DP, DP2 128b/132b, eDP, HDMI/DVI, virtual outputs, DSC, dynamic metadata, RGB/YUV420/YUV422, high bpc, immediate flip, DCC, rotations, ODM 2:1/4:1, MPC splits, stereo exceptions, SubVP phantom pipes, and video planes with cursor disabled.
- Writeback tests for single writeback, multiple writebacks on DCN2.01, crop versus source dimensions, YUV420 8/10 bpc, and worst-case writeback DISPCLK selection.
- Bounding-box tests with zero UCLK states, capped SMU clocks, duplicate clock states, Navi12 min DCFCLK behavior, debug latency overrides, and DCN2.1 low-pstate insertion.
- Watermark tests comparing A-D watermark fields against known DML reference outputs for DDR4/LPDDR4/Renoir/green sardine tables.
- Runtime assertions for FPU protection and `context != dc->current_state`.
- Display bring-up and power-management tests checking pstate switch support, zstate support, DTBCLK enable for DP2, and FreeSync vstartup adjustment.
