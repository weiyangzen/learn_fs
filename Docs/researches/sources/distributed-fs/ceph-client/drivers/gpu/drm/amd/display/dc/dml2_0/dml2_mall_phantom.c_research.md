<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_mall_phantom.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_mall_phantom.c

Purpose: implements DML2.0 SubVP/MALL phantom-pipe support. It estimates MALL cache ways for SubVP surfaces, decides whether a display state can use SubVP, creates/removes phantom streams and planes, and performs static schedulability checks for SubVP+SubVP, SubVP+VBLANK, and SubVP+DRR cases.

Important APIs/types/functions: exported entry points are `dml2_helper_calculate_num_ways_for_subvp()`, `dml2_svp_add_phantom_pipe_to_dc_state()`, `dml2_svp_remove_all_phantom_pipes()`, `dml2_svp_validate_static_schedulability()`, and `dml2_svp_drr_schedulable()`. Internal helpers include `merge_pipes_for_subvp()`, `assign_subvp_pipe()`, `enough_pipes_for_subvp()`, `subvp_subvp_schedulable()`, `subvp_vblank_schedulable()`, `set_phantom_stream_timing()`, `enable_phantom_stream()`, `enable_phantom_plane()`, and `add_phantom_pipes_for_main_pipe()`.

Control flow: `dml2_svp_add_phantom_pipe_to_dc_state()` rejects disabled SubVP, null state, stream-only pipes, and MPO. It merges existing split/ODM pipes, rebuilds scaling params, checks available free pipes, chooses the best main pipe by refresh/frame timing and active p-state margin, reads SubViewport and vstartup data from DML, then creates a paired phantom stream/plane chain through DC callbacks. Validation later counts SubVP and VACTIVE-capable pipes and dispatches to the appropriate static timing analysis.

State and persistence behavior: the file mutates in-memory `dc_state` pipe topology, stream/plane lists, phantom flags, DSC references, scaling params, and MALL sizing fields. There is no persistent storage; state lasts for the candidate DC state and is released through callback-provided phantom stream/plane cleanup.

Dependencies and integration points: depends on `dml2_context`, `dc_state`, `pipe_ctx`, DML mode support outputs, MALL configuration in `dml2_configuration_options`, and many `svp_pstate.callbacks` hooks supplied by DC resource code. It integrates with `dml2_utils` for DML pipe lookup and with the DML core for `dml_get_vstartup_calculated()`.

Risks and test signals: pipe-chain mutation is fragile: ODM/MPC merges clear stream and plane resources and must not leak DSC or leave stale links. `assign_subvp_pipe()` currently uses a fixed `free_pipes = 2` rather than the helper, which is a policy risk. Timing arithmetic mixes integer and double conversions and assumes valid pixel clocks and paired phantom streams. Test signals include SubVP add/remove on single and dual display, MPO rejection, pipe split/ODM merge behavior, DRR/VBLANK/SubVP schedulability boundaries, MALL way estimates with DCC, and cleanup leaving no phantom planes or stale `is_phantom` flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_mall_phantom.c -->
