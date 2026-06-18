# subset-b-001415 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/display_mode_vba_314.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/display_mode_vba_314.h

Purpose: declares the public DCN 3.14 Display Mode Library VBA entry points used to recalculate mode support, run full mode/system configuration, and calculate writeback DISPCLK requirements. This header is the small ABI surface for the spreadsheet-derived DCN314 VBA implementation.

Important APIs/types/functions: exports `dml314_recalculate(struct display_mode_lib *mode_lib)`, `dml314_ModeSupportAndSystemConfigurationFull(struct display_mode_lib *mode_lib)`, and `dml314_CalculateWriteBackDISPCLK(...)`. The function signatures depend on `struct display_mode_lib` and `enum source_format_class`, which are defined by the surrounding DML headers included by users of this header.

Control flow: the header itself has no executable control flow. Consumers call `dml314_ModeSupportAndSystemConfigurationFull` to populate mode-support and system-configuration VBA state, `dml314_recalculate` to recompute after parameter changes, and `dml314_CalculateWriteBackDISPCLK` as a helper for writeback scaling and line-buffer constraints.

State and persistence: no state is stored in this header. All persistent calculation state is owned by the caller-provided `display_mode_lib` instance. The writeback helper returns a `double` and does not expose mutable state in the signature.

Dependencies and integration: guarded by `__DML314_DISPLAY_MODE_VBA_H__` and intended to be paired with the DCN314 DML implementation and common `display_mode_lib`/VBA structures. It integrates with resource validation code through function tables that select generation-specific DML callbacks.

Risks: the header forward-declares through parameter usage rather than including all defining headers, so compilation order must ensure `struct display_mode_lib` and `enum source_format_class` are visible where needed. Any signature drift from the implementation or function-table assignments would break DCN314 validation.

Test signals: compile coverage for AMD display DML is the primary signal. Runtime confidence comes from modeset/bandwidth validation paths that exercise DCN314 mode support, recalculation, and writeback clock calculations under scaled writeback formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/display_mode_vba_314.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/display_rq_dlg_calc_314.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/display_rq_dlg_calc_314.c

Purpose: implements DCN 3.14 request queue, display logic generator, and TTU register calculations for AMD Display Mode Library. It converts pipe source/timing/scaling data and VBA-calculated timing values into `display_rq_regs_st`, `display_dlg_regs_st`, and `display_ttu_regs_st` fields programmed by the display driver.

Important APIs/functions: public entry points are `dml314_rq_dlg_get_rq_reg` and `dml314_rq_dlg_get_dlg_reg`. Key internal helpers are `CalculateBytePerPixelAnd256BBlockSizes`, `is_dual_plane`, `get_refcyc_per_delivery`, `get_blk_size_bytes`, `extract_rq_sizing_regs`, `extract_rq_regs`, `handle_det_buf_split`, `get_meta_and_pte_attr`, `get_surf_rq_param`, `dml_rq_dlg_get_rq_params`, `calculate_ttu_cursor`, and `dml_rq_dlg_get_dlg_params`.

Control flow: RQ calculation starts in `dml314_rq_dlg_get_rq_reg`, clears the output register struct, builds `display_rq_params_st` with `dml_rq_dlg_get_rq_params`, then encodes it with `extract_rq_regs`. `dml_rq_dlg_get_rq_params` detects dual-plane/YUV/RGBE-alpha formats, gathers luma and optional chroma surface attributes via `get_surf_rq_param`, and calls `handle_det_buf_split` to decide full 256-byte versus reduced 128-byte request behavior when the full two-swath footprint does not fit in DET.

Control flow for surface attributes: `get_surf_rq_param` derives viewport, pitch, meta pitch, and surface height for luma/chroma/alpha, adjusts viewport width or height for ODM combine, sets fixed chunk/meta chunk defaults, selects MPTE group size based on host VM, then delegates to `get_meta_and_pte_attr`. `get_meta_and_pte_attr` computes bytes per element, 256B block dimensions, swath width/request count, meta request shape, meta chunking, meta PTE bytes per frame, GPUVM page shape, dPTE request dimensions, dPTE row height, dPTE group size, and row upper bounds. It has separate paths for linear versus tiled surfaces and horizontal versus vertical scan.

Control flow for DLG/TTU: `dml314_rq_dlg_get_dlg_reg` first gathers system watermark/latency inputs from DML getter functions, recomputes per-pipe RQ params, then calls `dml_rq_dlg_get_dlg_params`. The DLG helper initializes outputs, pulls OTG/scaler/source parameters, converts refclk/pixel-clock ratios into fixed-point fields, imports VBA prefetch/vblank/flip timing values, handles interlace and ODM hblank offset adjustments, computes line/request delivery reference cycles for luma/chroma/cursor, and encodes nominal/vblank/flip PTE/meta delivery, VM request timing, QoS, vratio prefetch, and TTU fields.

State and persistence: all calculations are stack-local except writes to caller-provided output structs. Persistent input state is read from `struct display_mode_lib`, its `ip` and `soc` substructures, and the passed pipe arrays. Debug printing and assertions are the only side effects besides populating register structs.

Dependencies and integration: includes `display_mode_lib.h`, `display_mode_vba.h`, `dml_inline_defs.h`, and its public header. It depends on DML math helpers such as `dml_log2`, `dml_floor`, `dml_ceil`, `dml_round_to_multiple`, `dml_min`, and `dml_pow`; register/type definitions from `display_rq_dlg_helpers.h`; and many VBA getter functions such as `get_dst_y_prefetch`, `get_refcyc_per_vm_group_vblank_in_us`, `get_wm_urgent`, and `get_vstartup`. Driver integration happens through DML callback tables that call the DCN314 RQ/DLG functions during bandwidth and watermark programming.

Risks: the code is dense fixed-point hardware math with many register-width assertions; small rounding changes can cause underflow, mode rejection, or register overflow. Linear dPTE row height asserts `log2_dpte_row_height_linear >= 3`, so unusual pitch/page inputs can trip assumptions. Several comments flag uncertainty or legacy behavior, including luma/chroma chunk-size selection, cursor handling, 4:2:0 chroma meta timing, and hard-coded QoS values. ODM and split-pipe cases rely on consistent `pipe_idx` ordering between DML pipes and DC pipe resources.

Test signals: build coverage catches signature/type drift. Functional signals are DC modeset validation, high-resolution tiled and linear surfaces, dual-plane formats including 4:2:0 and RGBE alpha, GPUVM/hostVM combinations, ODM/MPC split modes, cursor-enabled planes, interlaced timings, immediate flip, and debug assertion coverage for register field bounds. Underflow-free display operation during pstate, vblank, and flip stress is the practical end-to-end signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/display_rq_dlg_calc_314.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/display_rq_dlg_calc_314.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/display_rq_dlg_calc_314.h

Purpose: declares the DCN314 RQ/DLG register-calculation interface used by DML consumers and tests. It exposes one entry point for request-queue register extraction and one for DLG/TTU register extraction.

Important APIs/types/functions: includes `../display_rq_dlg_helpers.h` for `display_rq_regs_st`, `display_dlg_regs_st`, `display_ttu_regs_st`, `display_pipe_params_st`, and `display_e2e_pipe_params_st`. It forward-declares `struct display_mode_lib`. Public functions are `dml314_rq_dlg_get_rq_reg(...)` and `dml314_rq_dlg_get_dlg_reg(...)`.

Control flow: this header has no executable flow. Callers pass a mode library, source or end-to-end pipe params, and output register structs. The DLG entry also carries pipe count/index plus policy booleans for cstate, pstate, VM, viewport-position ignoring, and immediate-flip support, even though the DCN314 implementation currently relies mostly on VBA getter state for those policy outcomes.

State and persistence: no state is declared. Outputs are written through caller-owned register structs by the implementation. Inputs are borrowed and must remain valid for the duration of calculation.

Dependencies and integration: guarded by `__DML314_DISPLAY_RQ_DLG_CALC_H__`. This header is part of the generation-specific DML callback surface and pairs with `display_rq_dlg_calc_314.c`. The comments identify `dml314_rq_dlg_get_rq_reg` as the main test entry for extracting register values.

Risks: ABI compatibility is important because resource code and tests call through these exact signatures. Boolean policy parameters can be misleading if future code expects them to directly drive all paths; the implementation presently marks several as unused in the lower-level DLG helper. Comments contain minor typos but no behavioral issue.

Test signals: compile coverage, unit-style RQ/DLG register extraction tests, and generation-specific DML validation that calls these functions for active pipe configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/display_rq_dlg_calc_314.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/dcn32_fpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/dcn32_fpu.c

Purpose: provides DCN 3.2 floating-point bandwidth, watermark, SubVP/FPO, pipe topology, and bounding-box support for AMD display resource validation. It owns the static DCN3.2 IP/SOC tables, synthesizes clock states from firmware/VBIOS data, validates DML bandwidth, applies pipe split/merge decisions, and computes final watermarks, DLG/RQ registers, MALL allocations, and clock requirements.

Important data/APIs: global `dcn3_2_ip` describes hardware limits such as DET size, chunk sizes, buffer depths, scaler limits, DSC/writeback capability, and pipe/output counts. Global `dcn3_2_soc` contains default clock, latency, bandwidth, memory-channel, and fabric parameters. Public functions include `dcn32_build_wm_range_table_fpu`, `dcn32_find_dummy_latency_index_for_fw_based_mclk_switch`, `dcn32_helper_populate_phantom_dlg_params`, `dcn32_set_phantom_stream_timing`, `dcn32_internal_validate_bw`, `dcn32_calculate_wm_and_dlg_fpu`, `dcn32_patch_dpm_table`, `dcn32_update_bw_bounding_box_fpu`, `dcn32_zero_pipe_dcc_fraction`, `dcn32_allow_subvp_with_active_margin`, `dcn32_allow_subvp_high_refresh_rate`, `dcn32_determine_max_vratio_prefetch`, `dcn32_assign_fpo_vactive_candidate`, `dcn32_find_vactive_pipe`, `dcn32_set_clock_limits`, and `dcn32_override_min_req_memclk`.

Control flow for validation: `dcn32_internal_validate_bw` is the central bandwidth path. It clears phantom pipes, updates SoC state for watermark set A, normalizes stream slice counts, populates DML pipes, logs pipe params, sets max prefetch vratio, and for full validation calls `dcn32_full_validate_bw_helper`. It then falls back to voltage-favoring prefetch policy when needed, validates mode support, rejects unsupported ODM/window MPO cases, applies merge/split flags, validates DSC, repopulates DML pipes after topology changes, and returns final `pipe_cnt` and `vlevel`.

Control flow for SubVP/FPO: `dcn32_full_validate_bw_helper` first asks DML for voltage level and split/merge flags, applies topology updates, then attempts SubVP when debug/capability/pipeline constraints permit. It repeatedly selects a SubVP candidate with `dcn32_assign_subvp_pipe`, adds phantom pipes, repopulates DML pipes, recalculates voltage, chooses a pstate-supporting level, and checks static schedulability with `subvp_validate_static_schedulability`. Static checks cover SubVP+SubVP, SubVP+VBLANK, and SubVP+DRR; SubVP+VACTIVE is rejected. On failure it removes phantom state and retries without SubVP; on success it populates phantom DLG params and assigns SubVP indexes.

Control flow for topology: split/merge handling is split between the newer slice-table path enabled by `enable_windowed_mpo_odm` and the older direct pipe-link manipulation path. The slice-table path converts DML split/merge flags into ODM/MPC slice-count updates by stream or plane. The legacy path unlinks merged ODM/MPC pipes, finds available split pipes, clones primary pipe state into secondary pipes, acquires DSC for ODM when needed, rebuilds mapped stream resources, and rebuilds scaling/test-pattern params.

Control flow for watermarks and DLG: `dcn32_calculate_wm_and_dlg_fpu` handles SubVP and firmware-based vblank stretch by finding dummy pstate latency indices, temporarily adjusting FCLK/pstate latency when needed, rerunning validation, and choosing whether FPO improves voltage level. It computes watermark sets B and C from DML getters under different latency/clock assumptions, derives set A either from set C when full pstate is unsupported or from normal latencies, mirrors set D to set A, clamps DISPCLK/DPPCLK to forced/debug minima, then calls `dcn32_calculate_dlg_params`. `dcn32_calculate_dlg_params` writes selected clocks into `context->bw_ctx.bw.dcn`, updates vstartup/vupdate/vready/det/unbounded request state per pipe, computes MALL storage sizes, compbuf remaining size, and invokes generation-specific DML RQ/DLG callback functions for each active pipe.

Control flow for clock tables/bounding boxes: `dcn32_patch_dpm_table` fills missing critical DPM entries from defaults. `build_synthetic_soc_states` constructs sorted voltage states from DCFCLK STA targets, UCLK/FCLK DPMs, DC-mode limits, optimal bandwidth tuples, and duplicate/inconsistent-entry cleanup. `dcn32_update_bw_bounding_box_fpu` applies debug/config overrides, VBIOS latency and channel-width data, dentist/xtal/dpref clocks, legacy or synthetic clock table construction, reinitializes DML instances, and mirrors clock-table overrides into DML2 options.

State and persistence: this file mutates global/static DCN3.2 bounding boxes (`dcn3_2_ip`, `dcn3_2_soc`) and per-context runtime state under `dc->dml`, `dc->current_state->bw_ctx.dml`, `context->bw_ctx`, `context->res_ctx.pipe_ctx`, `context->perf_params`, and stream status fields such as `fpo_in_use`. It also mutates pipe topology links (`top_pipe`, `bottom_pipe`, `prev_odm_pipe`, `next_odm_pipe`), phantom stream/plane state, DML `vba` fields, and clock-manager watermark tables. All exported functions assert floating point is enabled with `dc_assert_fp_enabled`.

Dependencies and integration: includes DCN32 resource headers, DCN20/DCN30 resource helpers, DML VBA utilities, SMU watermark definitions, link service, and DC state internals. It calls many cross-module helpers: resource pipe allocation/building functions, DML getters and `dml_get_voltage_level`, SubVP admission helpers from DCN32 resource code, DSC validation/acquisition, BIOS `get_soc_bb_info`, clock manager tables, and link-service DP 128b/132b checks. It is integrated into the DCN32 resource validation and clock programming pipeline.

Risks: the code is highly stateful and order-sensitive. Revalidation can overwrite VBA fields, so comments require phantom DLG getters before later split-flag application. SubVP scheduling uses timing arithmetic in microseconds and hard-coded policy lists for refresh/resolution; off-by-one or overflow issues can accept an unschedulable mode or reject a valid one. Legacy direct pipe topology manipulation is risky around ODM+MPO+DSC transitions. Global bounding-box mutation means SKU/VBIOS/debug overrides persist across later validations. Several fallback paths prefer underflow risk over crash, for example dummy latency index fallback, which is appropriate for display survival but a test target.

Test signals: compile and FP-guard coverage are basic signals. Strong runtime coverage should include bandwidth validation for no-pipe, single-display, multi-display, MPO, rotated-surface rejection, DSC, ODM/MPC 2:1 and 4:1 split, windowed MPO ODM, SubVP single/SubVP+SubVP/SubVP+VBLANK/SubVP+DRR, FPO vblank stretch, high-refresh and active-margin allowlists, PSR/MALL allocation, firmware clock tables with missing DPM fields, VBIOS latency/channel overrides, forced/debug clock minima, and underflow-free watermark/DLG programming across pstate and flip stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/dcn32_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/dcn32_fpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/dcn32_fpu.h

Purpose: declares the DCN32 floating-point helper surface used by resource validation, clock management, SubVP/FPO policy, watermark/DLG programming, and bounding-box updates.

Important APIs/types/functions: includes `clk_mgr_internal.h` and exposes functions operating on `struct clk_mgr_internal`, `struct dc`, `struct dc_state`, `struct pipe_ctx`, `struct dc_stream_state`, `struct clk_bw_params`, `display_e2e_pipe_params_st`, and `_vcs_dpi_soc_bounding_box_st`. Key exported routines are `dcn32_build_wm_range_table_fpu`, `dcn32_internal_validate_bw`, `dcn32_calculate_wm_and_dlg_fpu`, `dcn32_update_bw_bounding_box_fpu`, `dcn32_patch_dpm_table`, SubVP/FPO helpers, and clock-limit/memclk override helpers.

Control flow: the header has no executable flow, but its API order reflects the normal pipeline: build watermark ranges, populate phantom timing/DLG data when SubVP is used, validate bandwidth and pipe topology, compute watermarks/DLG registers, update bounding boxes from firmware/platform data, and apply policy helpers for FPO/SubVP and memory-clock constraints.

State and persistence: no storage is defined in the header. Implementations mutate caller-owned DC state, clock-manager bandwidth params, DML contexts, and static DCN32 bounding boxes.

Dependencies and integration: guarded by `__DCN32_FPU_H__`. This header is consumed by DCN32 resource and clock-management code that must run these functions with FPU access enabled. It bridges display core resource objects with DML pipe arrays and SoC/IP bounding-box structures.

Risks: these declarations expose many mutable state pointers; callers must pass arrays sized for active pipes and keep `pipe_cnt`/`vlevel` synchronized with the current DML context. Calling without the required FPU guard or before DML pipe population can corrupt validation results. Signature changes ripple into resource validation and clock-manager code.

Test signals: compile coverage for DCN32 resource integration, bandwidth-validation tests that call `dcn32_internal_validate_bw`, clock-table update tests for `dcn32_update_bw_bounding_box_fpu`, and modeset stress that exercises SubVP/FPO, DLG/RQ programming, and memory-clock override behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/dcn32_fpu.h -->
