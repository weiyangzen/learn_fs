<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper_fpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper_fpu.c

Purpose: implements the floating-point DML2.0 validation/programming engine. It initializes DML core data, maps DC state into DML config, runs mode-support and optional optimization, programs DML, maps hardware resources, verifies DET allocations, and publishes clocks, watermarks, and pipe register parameters back to DC.

Important APIs/types/functions: exports `initialize_dml2_ip_params()`, `initialize_dml2_soc_bbox()`, `initialize_dml2_soc_states()`, `dml2_validate_and_build_resource()`, `dml2_validate_only()`, `dml2_apply_debug_options()`, `dml2_extract_dram_and_fclk_change_support()`, `dml2_prepare_mcache_programming()`, `dml2_copy()`, and `dml2_create_copy()`. Internal helpers include `map_hw_resources()`, `pack_and_call_dml_mode_support_ex()`, `optimize_configuration()`, `calculate_lowest_supported_state_for_temp_read()`, `dml_mode_support_wrapper()`, and `call_dml_mode_support_and_programming()`.

Control flow: full validation clears scratch/policy/mode state, initializes DET scratch, copies dummy p-state latency data, optionally calculates a G6 temp-read state, maps DC streams/planes to DML, applies DET policy, calls `dml_mode_support_ex()`, filters software policy such as windowed MPO+ODM, tries ODM optimization to reduce dispclk, maps DML hardware output back to pipe mappings, calls `dml_mode_programming()`, maps DC pipes, verifies DET totals and reruns once if needed, then emits final clocks, RQ/DLG params, watermarks, writeback settings, MALL sizes, and zstate watermark adjustments.

State and persistence behavior: mutates `dml2_context->v20.scratch`, `dml_core_ctx.policy/ms/mp`, `dc_state->res_ctx`, `dc_state->bw_ctx`, and copied context memory. No disk persistence exists.

Dependencies and integration points: depends on DML core APIs, DML2 policy/translation/utils/SubVP/resource-management helpers, DML2.1 wrappers for delegated paths, DC clock manager dummy p-state tables, and ASIC capability flags such as APU versus dGPU.

Risks and test signals: this path is highly stateful and assumes `context->streams[0]`, sink, link, and clock manager data are valid when stream_count is nonzero. Recalculation after DET overflow must leave mapping scratch coherent. ODM optimization may change policy and needs rollback on failure. Test signals include mode-only versus full validation, empty state handling, APU/dGPU watermark differences, default clock table forcing, DET overflow rerun, MPO+ODM policy rejection, ODM 2:1/4:1 optimization, DML2.1 delegation, and copy/create-copy correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper_fpu.c -->
