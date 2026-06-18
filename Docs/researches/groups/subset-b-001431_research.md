# subset-b-001431 research

This grouped report covers DML2.0 MALL/SubVP phantom-pipe handling, DML2 policy and translation helpers, wrapper validation flow, RQ/DLG register extraction, DML logging/dependency headers, and DCN10 DPP build/runtime plumbing under the assigned Ceph-client source mirror. Each source file section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_mall_phantom.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_mall_phantom.c

Purpose: implements DML2.0 SubVP/MALL phantom-pipe support. It estimates MALL cache ways for SubVP surfaces, decides whether a display state can use SubVP, creates/removes phantom streams and planes, and performs static schedulability checks for SubVP+SubVP, SubVP+VBLANK, and SubVP+DRR cases.

Important APIs/types/functions: exported entry points are `dml2_helper_calculate_num_ways_for_subvp()`, `dml2_svp_add_phantom_pipe_to_dc_state()`, `dml2_svp_remove_all_phantom_pipes()`, `dml2_svp_validate_static_schedulability()`, and `dml2_svp_drr_schedulable()`. Internal helpers include `merge_pipes_for_subvp()`, `assign_subvp_pipe()`, `enough_pipes_for_subvp()`, `subvp_subvp_schedulable()`, `subvp_vblank_schedulable()`, `set_phantom_stream_timing()`, `enable_phantom_stream()`, `enable_phantom_plane()`, and `add_phantom_pipes_for_main_pipe()`.

Control flow: `dml2_svp_add_phantom_pipe_to_dc_state()` rejects disabled SubVP, null state, stream-only pipes, and MPO. It merges existing split/ODM pipes, rebuilds scaling params, checks available free pipes, chooses the best main pipe by refresh/frame timing and active p-state margin, reads SubViewport and vstartup data from DML, then creates a paired phantom stream/plane chain through DC callbacks. Validation later counts SubVP and VACTIVE-capable pipes and dispatches to the appropriate static timing analysis.

State and persistence behavior: the file mutates in-memory `dc_state` pipe topology, stream/plane lists, phantom flags, DSC references, scaling params, and MALL sizing fields. There is no persistent storage; state lasts for the candidate DC state and is released through callback-provided phantom stream/plane cleanup.

Dependencies and integration points: depends on `dml2_context`, `dc_state`, `pipe_ctx`, DML mode support outputs, MALL configuration in `dml2_configuration_options`, and many `svp_pstate.callbacks` hooks supplied by DC resource code. It integrates with `dml2_utils` for DML pipe lookup and with the DML core for `dml_get_vstartup_calculated()`.

Risks and test signals: pipe-chain mutation is fragile: ODM/MPC merges clear stream and plane resources and must not leak DSC or leave stale links. `assign_subvp_pipe()` currently uses a fixed `free_pipes = 2` rather than the helper, which is a policy risk. Timing arithmetic mixes integer and double conversions and assumes valid pixel clocks and paired phantom streams. Test signals include SubVP add/remove on single and dual display, MPO rejection, pipe split/ODM merge behavior, DRR/VBLANK/SubVP schedulability boundaries, MALL way estimates with DCC, and cleanup leaving no phantom planes or stale `is_phantom` flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_mall_phantom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_mall_phantom.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_mall_phantom.h

Purpose: declares the DML2 SubVP/MALL phantom-pipe helper interface used by wrapper/resource code to create phantom pipes, remove them, compute MALL way requirements, and validate SubVP timing schedules.

Important APIs/types/functions: defines `struct dml2_svp_helper_select_best_svp_candidate_params`, which packages DML config, mode-support info, a blacklist, and output candidate index for candidate selection. It forward-declares `struct dml2_context` and exports `dml2_helper_calculate_num_ways_for_subvp()`, `dml2_svp_add_phantom_pipe_to_dc_state()`, `dml2_svp_remove_all_phantom_pipes()`, `dml2_svp_validate_static_schedulability()`, and `dml2_svp_drr_schedulable()`.

Control flow: no runtime control flow in the header. It establishes the callable surface used after DML mode support has produced SubVP line and p-state data and before/after DC state resource programming.

State and persistence behavior: no state is stored here. The declared functions mutate `dc_state` and read `dml2_context` configuration.

Dependencies and integration points: includes `dml2_dc_types.h` and `display_mode_core_structs.h`, so users must already be in the AMD DC/DML type universe. It is consumed by `dml2_mall_phantom.c` and the FPU validation wrapper.

Risks and test signals: ABI risk is callback/type coupling rather than data layout. Build coverage should include SubVP-capable and force-disabled configurations, and call-site tests should verify null/unsupported states return false without mutating pipe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_mall_phantom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_policy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_policy.c

Purpose: builds DML2.0 policy defaults and synthesizes a sorted SoC state table from PMFW-derived clocks and DCFCLK STAs. It translates sparse clock entries into complete DCFCLK/FCLK/UCLK tuples that DML mode support can evaluate.

Important APIs/types/functions: exported functions are `dml2_policy_build_synthetic_soc_states()` and `build_unoptimized_policy_settings()`. Internal helpers include `get_optimal_ntuple()`, `calculate_net_bw_in_mbytes_sec()`, `insert_entry_into_table_sorted()`, and `remove_entry_from_table_at_index()`.

Control flow: synthetic state construction scans input states for max display, PHY, fabric, DCFCLK, SOC, and UCLK limits, seeds an entry from state 0, inserts all DCFCLK STAs, UCLK DPMs, and FCLK DPMs or max FCLK into a bandwidth-sorted table, removes unsupported entries, rounds UCLK/FCLK to available DPMs, clamps minimum FCLK/DCFCLK, and removes neighboring duplicates. `build_unoptimized_policy_settings()` initializes all planes to as-needed MPC/ODM, required immediate flip, and permissive p-state/stutter policy, then adjusts DCN35/DCN36/DCN351 policy flags.

State and persistence behavior: state is written only to caller-provided `soc_states_st`, scratch entry, and `dml_mode_eval_policy_st`. There is no static mutable state.

Dependencies and integration points: consumes `display_mode_core_structs.h` structures and constants such as `__DML_MAX_STATE_ARRAY_SIZE__`. It is called from `dml2_translation_helper.c` for native SoC-state construction and from `dml2_wrapper_fpu.c` before each mode-support evaluation.

Risks and test signals: the code assumes at least one input state and enough output-table capacity; insert operations do not enforce a hard bounds check. `num_fclk_dpms - 1` is used in the coarse-FCLK path, so missing FCLK entries would underflow. Floating bandwidth comparisons and integer truncation can change state ordering. Test signals include synthetic table generation with 1, 2, and many FCLK/UCLK entries, duplicate removal, override tables, max-clock rejection, and DCN35/DCN36 policy deltas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_policy.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_policy.h

Purpose: declares the DML2.0 policy construction interface and scratch/parameter structures for synthetic SoC-state generation.

Important APIs/types/functions: `struct dml2_policy_build_synthetic_soc_states_params` carries input bounding box, input states, output states, DCFCLK STA list, and STA count. `struct dml2_policy_build_synthetic_soc_states_scratch` stores one temporary `soc_state_bounding_box_st` entry. Public functions are `dml2_policy_build_synthetic_soc_states()` and `build_unoptimized_policy_settings()`.

Control flow: no runtime flow in the header. The API separates scratch from inputs so callers can keep large temporary state inside `dml2_context` rather than on the stack.

State and persistence behavior: no direct state. The declared builder mutates the supplied output state table and policy struct.

Dependencies and integration points: includes `display_mode_core_structs.h` and is used by translation and FPU wrapper code before DML mode support.

Risks and test signals: callers must provide valid arrays and at least one initialized input state. Build/test coverage should validate the header remains synchronized with scratch members stored in `dml2_internal_types.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_translation_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_translation_helper.c

Purpose: converts AMD DC state and legacy DML data into DML2.0 structures, initializes native IP/SOC defaults, applies bounding-box overrides, maps stream/plane identities between DC and DML indexes, and copies calculated DML RQ/DLG/TTU register fields back into DC pipe contexts.

Important APIs/types/functions: exported entry points are `dml2_init_ip_params()`, `dml2_init_socbb_params()`, `dml2_init_soc_states()`, `dml2_translate_ip_params()`, `dml2_translate_socbb_params()`, `dml2_translate_soc_states()`, `map_dc_state_into_dml_display_cfg()`, and `dml2_update_pipe_ctx_dchub_regs()`. Internal mapping helpers populate timing, output, surface, plane, writeback, HPO encoder, stream id, plane id, and pipe-to-plane-index tables.

Control flow: initialization chooses project-specific hardcoded IP/SOC values for DCN32/DCN321/DCN35/DCN351/DCN36/DCN401, applies override clock tables and latency overrides, then either copies independent DCN35-style states or calls the synthetic-state policy builder. Runtime mapping clears DML/DC mapping arrays, sets VM policy flags, builds scaling data, creates one DML timing per stream or per duplicated plane when needed, emits dummy planes for plane-less streams, maps surfaces from `dc_plane_state`, sets MALL policy for SubVP main/phantom streams, and records stream/plane ids for reverse lookup.

State and persistence behavior: writes persistent-for-validation data into `dml2->v20.dml_core_ctx`, `dml2->v20.scratch`, and caller-provided `dml_display_cfg_st`. `dml2_update_pipe_ctx_dchub_regs()` zeroes and repopulates `pipe_ctx` RQ, DLG, and TTU register caches.

Dependencies and integration points: depends on `display_mode_core.h`, `dml2_internal_types.h`, DC stream/plane/writeback/scaler/resource helpers, HPO DP encoder instances, DML struct layouts, and SubVP stream-type helpers. It is central to the wrapper FPU validation path.

Risks and test signals: many defaults are hardcoded and project-specific; wrong DCN version selection changes bandwidth support. Mapping arrays are size-limited by `__DML2_WRAPPER_MAX_STREAMS_PLANES__`; duplicated planes and MPO require exact plane-id handling. Some functions assume stream audio mode pointers, pipe state, and pixel clocks are valid. Test signals include DCN32/DCN35/DCN401 default initialization, override clock table ingestion, plane-less streams, MPO plane duplicates, SubVP main/phantom MALL flags, DP2/HPO encoder mapping, writeback mapping, and register-copy parity with DML getters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_translation_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_translation_helper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_translation_helper.h

Purpose: exposes the DML2.0 translation boundary between DC state and DML structures.

Important APIs/types/functions: declares native initializers for IP params, SOC bounding box, and SOC states; legacy translators from `dc->dml`; `map_dc_state_into_dml_display_cfg()` for runtime stream/plane conversion; `dml2_update_pipe_ctx_dchub_regs()` for copying calculated RQ/DLG/TTU registers into a `pipe_ctx`; and `is_dp2p0_output_encoder()`.

Control flow: no direct runtime flow. Callers choose native construction versus translation through wrapper functions in `dml2_wrapper_fpu.c`.

State and persistence behavior: no state in the header. Declared functions mutate `dml2_context`, `dml_display_cfg_st`, and `pipe_ctx` data passed by the caller.

Dependencies and integration points: intentionally relies on surrounding includes for DC/DML type declarations. It is included by DML2 wrapper, utility, and translation implementation files.

Risks and test signals: since the header does not include all dependent type definitions, include ordering matters. Build signals should cover all translation users, especially when adding fields to DML register structs or DC pipe contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_translation_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_utils.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_utils.c

Purpose: provides DML2.0 utility routines for copying DML config arrays, deriving output/clock constraints, mapping DML pipe indexes back to DC pipes, calculating RQ/DLG params, extracting watermarks/writeback settings, applying DET buffer policy, and recognizing stereo timings.

Important APIs/types/functions: exports copy helpers for timing/plane/surface/output arrays, `dml2_util_get_maximum_odm_combine_for_output()`, `is_dp2p0_output_encoder()`, `is_dtbclk_required()`, `dml2_copy_clocks_to_dc_state()`, `dml2_helper_find_dml_pipe_idx_by_stream_id()`, `dml2_calculate_rq_and_dlg_params()`, `dml2_extract_watermark_set()`, `dml2_calc_max_scaled_time()`, `dml2_extract_writeback_wm()`, `dml2_initialize_det_scratch()`, `dml2_apply_det_buffer_allocation_policy()`, `dml2_verify_det_buffer_configuration()`, and `dml2_is_stereo_timing()`.

Control flow: the most important path is `dml2_calculate_rq_and_dlg_params()`: it updates deep-sleep/fclk support, clamps dispclk to debug minimum, resolves each DC pipe to a DML pipe through stream or plane id mappings, populates DLG params, applies phantom-pipe DET/unbounded-request rules, reads DPPCLK/DET/MALL sizes from DML, calls RQ/DLG calculators, and copies register values into the output resource context. DET policy splits the available DET pool across streams, planes, and DPPs per surface, then verification triggers recalculation when DML allocates more than the hardware total.

State and persistence behavior: mutates `dc_state->bw_ctx`, `pipe_ctx` register caches, MALL size counters, DET helper scratch, and DML display config overrides. It does not keep independent static state.

Dependencies and integration points: depends on DML getters, `dml_display_rq_dlg_calc`, DC pipe/resource structs, DP2 HPO encoder fields, writeback structures, and mapping tables populated by `dml2_translation_helper.c` and `dml2_wrapper_fpu.c`.

Risks and test signals: DML/DC pipe index mismatches can write registers or DET sizes to the wrong pipe. `dml2_extract_writeback_wm()` iterates DMB slots and references `pipe_ctx[i].stream`, so writeback-only or sparse pipe layouts need coverage. DET rounding masks with `~0x3F`, assuming 64 KB segment alignment. Test signals include DP2 `dtbclk_en`, phantom DET zeroing, MALL size accounting, RQ/DLG register population, DET recalculation, writeback watermark extraction, and forced clock/debug minimum interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_utils.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_utils.h

Purpose: declares shared DML2.0 helper routines for DML config copying, clock/watermark extraction, RQ/DLG calculation, DET policy, pipe construction hooks, and timing predicates.

Important APIs/types/functions: public functions include DML array copy helpers, `dml2_util_get_maximum_odm_combine_for_output()`, `dml2_copy_clocks_to_dc_state()`, `dml2_extract_watermark_set()`, `dml2_extract_writeback_wm()`, `dml2_helper_find_dml_pipe_idx_by_stream_id()`, `is_dtbclk_required()`, `dml2_is_stereo_timing()`, `dml2_calc_max_scaled_time()`, `dml2_calculate_rq_and_dlg_params()`, DET allocation/verification helpers, and declarations for resource-building helpers such as `dml2_dc_construct_pipes()`, `dml2_predict_pipe_split()`, and `dml2_build_mapped_resource()`.

Control flow: no direct control flow, but comments document how DML validation maps hardware resources and then calls these helpers to build DC pipe programming.

State and persistence behavior: no header-owned state. The declared functions mutate DC state, DML context scratch, clocks, watermarks, and pipe register caches.

Dependencies and integration points: includes `os_types.h` and `dml2_dc_types.h`, forward-declares core DC/DML structs, and is used by wrapper, translation, resource-management, and SubVP code.

Risks and test signals: several declared resource helpers are not implemented in this specific file, so link coverage must include the companion DML2 resource-management sources. Header comments contain older DML1 phrasing and should be kept aligned with the actual validation flow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper.c

Purpose: provides the non-FPU public lifecycle and validation dispatch wrapper for DML2, including allocation, create, destroy, reinit, and routing between DML2.0 and DML2.1 implementations.

Important APIs/types/functions: exports `dml2_allocate_memory()`, `dml2_validate()`, `dml2_create()`, `dml2_destroy()`, and `dml2_reinit()`. Internal `dml2_init()` stores configuration, maps DCN version to DML project id, and initializes IP, SOC bounding box, and SOC states through FPU helper entry points.

Control flow: creation checks whether DML2.1 is enabled for DCN 4.01 or newer and delegates to `dml21_create()` when needed. Otherwise it allocates a zeroed `dml2_context`, initializes project-specific DML2.0 state, and returns it. Validation applies debug overrides, delegates to DML2.1 for DML2.1 contexts, calls `dml2_validate_only()` for mode-only/state-index validation, or calls `dml2_validate_and_build_resource()` for full programming validation.

State and persistence behavior: owns `dml2_context` allocation via `vzalloc`/`vfree`, with optional `DC_RUN_WITH_PREEMPTION_ENABLED` wrapping. It persists a copy of configuration in the context and refreshes DML core IP/SOC/state data on reinit.

Dependencies and integration points: depends on `dml2_internal_types.h`, DML2.0 and DML2.1 wrapper/FPU headers, and `dc_fpu.h`. It is the external DML2 API used by DC state creation and validation.

Risks and test signals: architecture dispatch must match `in_dc->debug.using_dml21`, `dce_version`, and `dml2->architecture`. Destroy delegates to DML2.1 cleanup but still frees the context afterward, so DML2.1 must not independently free the same pointer. Test signals include DCN32/35/401 create, DML2.1 create/reinit path, null validation rejection, validate-mode dispatch, and repeated reinit without stale project data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper.h

Purpose: defines the DML2 public configuration, callback, clock, MALL, bounding-box override, and lifecycle/validation interface shared with AMD DC.

Important APIs/types/functions: key structs are `dml2_soc_mall_info`, `dml2_dcn_clocks`, `dml2_dc_callbacks`, `dml2_dc_svp_callbacks`, `dml2_clks_limit_table`, `dml2_soc_bbox_overrides`, and `dml2_configuration_options`. Public functions include `dml2_create()`, `dml2_destroy()`, `dml2_copy()`, `dml2_create_copy()`, `dml2_reinit()`, `dml2_validate()`, `dml2_extract_dram_and_fclk_change_support()`, `dml2_prepare_mcache_programming()`, debug/validate helpers, and `dml2_allocate_memory()`.

Control flow: no direct flow, but the callback tables define how DML2 requests DC operations: build scaling params, allocate secondary MPC/ODM pipes, query stream/plane topology, create/release phantom SubVP resources, and allocate MCACHE.

State and persistence behavior: the configuration struct is copied into `dml2_context` and persists across validation until reinit or destroy. Callback function pointers are trusted runtime integration state.

Dependencies and integration points: includes `os_types.h` and forward-declares DC resource types. It bridges DML2 with resource pool, pipe, stream, plane, DSC, MALL/SubVP, PMO, GPUVM/HOSTVM, and DML2.1 debug data.

Risks and test signals: most failures come from incomplete callback initialization or mismatched pipe counts. `DML2_MAX_NUM_DPM_LVL` bounds override clock tables. Test signals should verify callback tables are fully populated per ASIC, SubVP callbacks are null-safe when disabled, clock override tables do not exceed limits, and DML2.0/DML2.1 callers share compatible lifecycle semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper_fpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper_fpu.c

Purpose: implements the floating-point DML2.0 validation/programming engine. It initializes DML core data, maps DC state into DML config, runs mode-support and optional optimization, programs DML, maps hardware resources, verifies DET allocations, and publishes clocks, watermarks, and pipe register parameters back to DC.

Important APIs/types/functions: exports `initialize_dml2_ip_params()`, `initialize_dml2_soc_bbox()`, `initialize_dml2_soc_states()`, `dml2_validate_and_build_resource()`, `dml2_validate_only()`, `dml2_apply_debug_options()`, `dml2_extract_dram_and_fclk_change_support()`, `dml2_prepare_mcache_programming()`, `dml2_copy()`, and `dml2_create_copy()`. Internal helpers include `map_hw_resources()`, `pack_and_call_dml_mode_support_ex()`, `optimize_configuration()`, `calculate_lowest_supported_state_for_temp_read()`, `dml_mode_support_wrapper()`, and `call_dml_mode_support_and_programming()`.

Control flow: full validation clears scratch/policy/mode state, initializes DET scratch, copies dummy p-state latency data, optionally calculates a G6 temp-read state, maps DC streams/planes to DML, applies DET policy, calls `dml_mode_support_ex()`, filters software policy such as windowed MPO+ODM, tries ODM optimization to reduce dispclk, maps DML hardware output back to pipe mappings, calls `dml_mode_programming()`, maps DC pipes, verifies DET totals and reruns once if needed, then emits final clocks, RQ/DLG params, watermarks, writeback settings, MALL sizes, and zstate watermark adjustments.

State and persistence behavior: mutates `dml2_context->v20.scratch`, `dml_core_ctx.policy/ms/mp`, `dc_state->res_ctx`, `dc_state->bw_ctx`, and copied context memory. No disk persistence exists.

Dependencies and integration points: depends on DML core APIs, DML2 policy/translation/utils/SubVP/resource-management helpers, DML2.1 wrappers for delegated paths, DC clock manager dummy p-state tables, and ASIC capability flags such as APU versus dGPU.

Risks and test signals: this path is highly stateful and assumes `context->streams[0]`, sink, link, and clock manager data are valid when stream_count is nonzero. Recalculation after DET overflow must leave mapping scratch coherent. ODM optimization may change policy and needs rollback on failure. Test signals include mode-only versus full validation, empty state handling, APU/dGPU watermark differences, default clock table forcing, DET overflow rerun, MPO+ODM policy rejection, ODM 2:1/4:1 optimization, DML2.1 delegation, and copy/create-copy correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper_fpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper_fpu.h

Purpose: declares the FPU-required DML2.0 initialization helpers used by the non-FPU wrapper to populate IP, SOC bounding box, and SOC state data.

Important APIs/types/functions: forward-declares `struct dml2_context`, `struct dc`, `struct ip_params_st`, `struct soc_bounding_box_st`, and `struct soc_states_st`. Exports `initialize_dml2_ip_params()`, `initialize_dml2_soc_bbox()`, and `initialize_dml2_soc_states()`.

Control flow: no direct flow. The implementation chooses native construction or legacy translation based on `dml2->config.use_native_soc_bb_construction`.

State and persistence behavior: no header state. Declared functions initialize persistent fields inside the DML core context supplied by the caller.

Dependencies and integration points: includes `os_types.h` and is included by `dml2_wrapper.c` and `dml2_wrapper_fpu.c`.

Risks and test signals: this header intentionally exposes only initialization helpers; validation helpers live in `dml2_wrapper.h`. Build coverage should ensure FPU separation rules remain valid for AMD DC build configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper_fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_assert.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_assert.h

Purpose: placeholder DML assertion header for this DML2.0 subtree.

Important APIs/types/functions: it includes `os_types.h` and defines no assertion macro of its own. Assertion behavior used by these sources appears to come from other AMD DC/DML includes.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: provides a stable include target for DML code that expects `dml_assert.h` while relying on shared OS/DC type and assertion definitions elsewhere.

Risks and test signals: because it is effectively empty, adding a local `ASSERT` definition here could change build behavior across the subtree. Test signal is successful compilation of all DML2.0 sources that include or indirectly expect this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_assert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_depedencies.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_depedencies.h

Purpose: dependency aggregation header for DML2.0 code, intentionally without an include guard.

Important APIs/types/functions: declares no functions or types itself. It includes `os_types.h` and `cmntypes.h` to provide standard AMD display/DML type definitions.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: used as a compatibility include target for DML code that expects shared standard types to be pulled in. The lack of guard is documented as intentional because the header is just an include bundle.

Risks and test signals: the filename contains the misspelling `depedencies`, so include paths must match exactly. Repeated inclusion is expected; adding declarations with side effects would be risky. Test signal is build coverage for files that include this compatibility header more than once or through generated DML sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_depedencies.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_display_rq_dlg_calc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_display_rq_dlg_calc.c

Purpose: converts programmed DML mode results into display request queue, DLG, TTU, and arbitration register structures for DCN programming.

Important APIs/types/functions: exports `dml_rq_dlg_get_rq_reg()`, `dml_rq_dlg_get_dlg_reg()`, and `dml_rq_dlg_get_arb_params()`. Internal `is_dual_plane()` recognizes 420 and RGBE-alpha formats that require luma/chroma or alpha-plane handling.

Control flow: RQ calculation reads plane/source format, swizzle, chunk sizes, group sizes, DET size, row heights, swath heights, stored swath sizes, and phantom status from DML getters. It encodes register fields with log2/floor conversions and chooses DET chroma base split, including a fixed half-MALL split for phantom dual-plane pipes. DLG/TTU calculation reads timing, plane, hardware, ODM mode, prefetch, VM/PTE/meta delivery, cursor, and watermark-related values, adjusts hblank reference cycles for ODM combine position, writes fixed-point register fields, clamps selected VM/PTE/meta values, and asserts register width constraints.

State and persistence behavior: no persistent state. It zeroes caller-provided register structs and fills them from `display_mode_lib_st` cached mode-programming outputs.

Dependencies and integration points: depends on `display_mode_core.h`, `display_mode_util.h`, DML getter APIs, DML math helpers, and `dml_print` logging macros. Called by `dml2_calculate_rq_and_dlg_params()` before copying results into DC pipe contexts.

Risks and test signals: many fields rely on DML getters having valid data after `dml_mode_programming()`. Register-width asserts can fire for unusual timings, high refclk ratios, or unsupported scaling. The code assumes at most one cursor and contiguous DML pipe indexes for ODM combine. Test signals include linear and tiled surfaces, dual-plane formats, RGBE alpha, phantom SubVP pipes, ODM 2:1/4:1, interlace, cursor enabled/disabled, low htotal magic path, and clamp behavior near 13/17/23/24-bit register limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_display_rq_dlg_calc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_display_rq_dlg_calc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_display_rq_dlg_calc.h

Purpose: declares DML2.0 RQ/DLG/TTU calculation entry points used to turn DML mode-programming results into hardware register structs.

Important APIs/types/functions: exports `dml_rq_dlg_get_rq_reg()`, `dml_rq_dlg_get_dlg_reg()`, and `dml_rq_dlg_get_arb_params()`. It forward-declares `struct display_mode_lib_st` and uses DML display register types from `display_mode_core_structs.h`.

Control flow: no direct flow. Comments document that callers must have already run mode programming before requesting register values.

State and persistence behavior: no header state. Functions fill caller-provided output structs.

Dependencies and integration points: included by `dml2_utils.c` and the implementation. It bridges DML core outputs to DC pipe register caches.

Risks and test signals: callers must pass the correct DML pipe index; otherwise RQ/DLG fields are copied to the wrong DC pipe. Build coverage should catch struct type drift between DML core and DC-facing register containers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_display_rq_dlg_calc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_logging.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_logging.h

Purpose: provides a no-op logging macro for DML2.0 code.

Important APIs/types/functions: defines `dml_print(...)` as `((void)0)`.

Control flow: logging calls compile away and produce no runtime side effects.

State and persistence behavior: none.

Dependencies and integration points: included by DML code through common headers so verbose debug print calls can remain in source without requiring an active logging backend.

Risks and test signals: no-op logging means diagnostic paths in RQ/DLG and validation code are silent unless another build overrides logging before inclusion. Test signal is that debug-print-heavy sources compile cleanly and do not evaluate expensive or side-effecting logging arguments in unexpected ways.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_logging.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/Makefile

Purpose: adds Display Pipe Processor object files for multiple DCN generations to the AMD display build when floating-point DC support is enabled.

Important APIs/types/functions: Kbuild variables include `DPP_DCN10`, `AMD_DAL_DPP_DCN10`, `DPP_DCN20`, `DPP_DCN201`, `DPP_DCN30`, `DPP_DCN32`, `DPP_DCN35`, `DPP_DCN401`, and `DPP_DCN42`. Each generation uses `$(addprefix $(AMDDALPATH)/dc/dpp/<generation>/,...)` and appends to `AMD_DISPLAY_FILES`.

Control flow: no runtime flow. Under `ifdef CONFIG_DRM_AMD_DC_FP`, the Makefile lists the generation-specific DPP C objects that become part of the AMD DC build.

State and persistence behavior: no runtime state. It affects build artifacts and object inclusion only.

Dependencies and integration points: depends on the top-level AMD display Kbuild variables `AMDDALPATH`, `AMD_DISPLAY_FILES`, and `CONFIG_DRM_AMD_DC_FP`. It integrates DPP implementations for DCN10 through DCN42.

Risks and test signals: missing an object here can silently omit generation-specific DPP functionality; adding one without the corresponding source breaks builds. Test signals are allmodconfig and ASIC-specific builds with `CONFIG_DRM_AMD_DC_FP` enabled, plus link coverage for DCN401/42 additions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.c

Purpose: implements the DCN1.0 Display Pipe Processor front-end object: state readback, scaler tap selection, color conversion setup, degamma/regamma control, cursor programming, DPP clock control, function-table registration, and construction.

Important APIs/types/functions: exported functions include `dpp_read_state()`, `dpp1_get_optimal_number_of_taps()`, `dpp_reset()`, `dpp1_cnv_setup()`, `dpp1_set_cursor_attributes()`, `dpp1_set_cursor_position()`, `dpp1_cnv_set_optional_cursor_attributes()`, `dpp1_dppclk_control()`, `dpp_force_disable_cursor()`, and `dpp1_construct()`. Static helpers include `dpp1_cm_set_regamma_pwl()`, `dpp1_setup_format_flags()`, and `dpp1_set_degamma_format_float()`. `dcn10_dpp_funcs` and `dcn10_dpp_cap` publish the implementation through the generic `struct dpp` interface.

Control flow: construction wires context, instance, registers, shifts, masks, caps, and line-buffer constants. Setup maps surface pixel formats to CNVC pixel format codes, alpha behavior, float output, degamma format, default/input CSC selection, and cursor disable requirements for some YCrCb formats. Cursor positioning transforms coordinates for rotation/mirror/hotspot, clips against viewport, and writes enable state unless cursor offload is active. Regamma PWL uses double-buffered LUT RAM selection and skips reprogramming when cached PWL data matches.

State and persistence behavior: caches scaler filters, PWL data, cursor position/attributes, cursor offload, LUT RAM safety toggle, line-buffer caps, and register descriptors in `struct dcn10_dpp`. Hardware register state persists in the DPP block until reprogrammed or reset.

Dependencies and integration points: depends on DC register helper macros, `dcn10_dpp.h`, color-management helpers from DCN10 DPP CM/DSCL files, fixed-point conversion helpers, and generic DPP function-table consumers in AMD DC resource code.

Risks and test signals: format-to-register mappings and cursor rotation math are user-visible. FP16 scaling is rejected on fixed-format DSCL hardware only when both horizontal and vertical ratios differ from one, which should match hardware limits. Regamma cache comparison assumes `pwl_params` is fully initialized. Test signals include format setup for RGB/YUV/FP16, CSC adjustment/default paths, cursor clipping and rotation, regamma LUT A/B toggling, dppclk enable/divider, state readback, and scaler tap defaults with identity-ratio collapse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.c -->
