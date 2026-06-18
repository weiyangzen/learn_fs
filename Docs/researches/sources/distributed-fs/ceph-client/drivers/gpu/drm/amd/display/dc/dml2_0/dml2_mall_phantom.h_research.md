<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_mall_phantom.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_mall_phantom.h

Purpose: declares the DML2 SubVP/MALL phantom-pipe helper interface used by wrapper/resource code to create phantom pipes, remove them, compute MALL way requirements, and validate SubVP timing schedules.

Important APIs/types/functions: defines `struct dml2_svp_helper_select_best_svp_candidate_params`, which packages DML config, mode-support info, a blacklist, and output candidate index for candidate selection. It forward-declares `struct dml2_context` and exports `dml2_helper_calculate_num_ways_for_subvp()`, `dml2_svp_add_phantom_pipe_to_dc_state()`, `dml2_svp_remove_all_phantom_pipes()`, `dml2_svp_validate_static_schedulability()`, and `dml2_svp_drr_schedulable()`.

Control flow: no runtime control flow in the header. It establishes the callable surface used after DML mode support has produced SubVP line and p-state data and before/after DC state resource programming.

State and persistence behavior: no state is stored here. The declared functions mutate `dc_state` and read `dml2_context` configuration.

Dependencies and integration points: includes `dml2_dc_types.h` and `display_mode_core_structs.h`, so users must already be in the AMD DC/DML type universe. It is consumed by `dml2_mall_phantom.c` and the FPU validation wrapper.

Risks and test signals: ABI risk is callback/type coupling rather than data layout. Build coverage should include SubVP-capable and force-disabled configurations, and call-site tests should verify null/unsupported states return false without mutating pipe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_mall_phantom.h -->
