## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_dc_resource_mgmt.c

### Purpose
`dml2_dc_resource_mgmt.c` maps DML2 display-configuration pipe requirements onto DC `pipe_ctx` topology. It creates or updates ODM and MPC combine trees, preserves preferred existing pipe choices when possible, supports DML2.0 and DML2.1 result formats, and rebuilds scaling/test-pattern state after mapping.

### Important APIs, Types, And Functions
The exported API is `dml2_map_dc_pipes()`. Internal structures are `dc_plane_pipe_pool` and `dc_pipe_mapping_scratch`. Important helpers compute plane IDs, find display-config indexes by stream or plane ID, locate master stream/plane pipes, gather assigned pipes, find preferred and last-resort candidates, allocate free pipes, sort pipe groups, calculate ODM slices, build ODM and blend trees, free unused pipes, derive source/target ODM/MPC factors, and choose either callback-driven or legacy direct mapping.

### Control Flow
If `ctx->config.map_dc_pipes_with_callbacks` is set, the file populates source and target ODM/MPC factors, first unmaps streams or planes that need fewer slices, then maps those that need more slices through DC callbacks. Otherwise it uses the legacy mapper. The legacy path converts DML2.1 programming outputs or DML2.0 `disp_cfg->hw` arrays into ODM and DPP-per-surface arrays, then iterates streams. For each stream it computes the target ODM factor and slice boundaries; blank streams still get ODM pipe mapping. For each plane it computes plane ID, target MPC factor, assigns/reuses enough pipes, sorts them, links bottom/top blend trees and prev/next ODM chains, calls `acquire_secondary_pipe_for_mpc_odm()`, frees unused plane pipes, then rebuilds scaling and test pattern parameters.

### State, Persistence, And Dependencies
The function mutates the caller's `dc_state->res_ctx.pipe_ctx` graph in memory. It uses `ctx->v20.scratch.dml_to_dc_pipe_mapping` or the supplied mapping to translate between DML and DC identifiers, and `ctx->pipe_combine_scratch` for callback mapping. Dependencies include DC resource/core types, DML wrapper/internal types, `dml2_utils.h`, `dml2_mall_phantom.h`, and many callback hooks in `ctx->config.callbacks` and `ctx->config.svp_pstate.callbacks`.

### Integration Points
This is the bridge from DML-calculated ODM/DPP requirements to actual DC hardware resource topology. It consumes DML2.0 `dml_display_cfg_st` or DML2.1 `mode_programming.programming`, handles SubVP phantom-to-main stream mapping, and calls DC resource callbacks for pipe acquisition, slice-count updates, scaling params, and test pattern params.

### Risks
The direct mapper relies heavily on preexisting master pipes and asserts rather than returning failures in many bad states. `remove_pipes_from_blend_trees()` assigns `pipe->bottom_pipe = pipe->top_pipe` when updating the lower neighbor, which is suspicious because it does not write through `pipe->bottom_pipe->top_pipe`. The mcache/pipe arrays are fixed-size and assume pipe counts never exceed `MAX_PIPES`. Plane duplicate handling depends on `dml_pipe_idx_to_plane_index` being valid. `validate_pipe_assignment()` is effectively stubbed, so final topology correctness depends on external callbacks and later hardware programming paths.

### Test Signals
Tests should cover DML2.0 and DML2.1 mappings, callback and legacy paths, ODM increase/decrease, MPC increase/decrease, stereo forced two-way split, SubVP phantom stream mapping, blank stream ODM setup, preserving preferred existing pipes, avoiding last-resort OTG/OPP-change pipes until needed, duplicate plane IDs, and topology validation of top/bottom and prev/next ODM links after mapping.
