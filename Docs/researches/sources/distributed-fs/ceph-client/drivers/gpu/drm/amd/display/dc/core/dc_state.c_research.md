# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_state.c

## Purpose

`dc_state.c` owns lifecycle and high-level mutation of `struct dc_state`, the Display Core state object that carries streams, planes, resource context, bandwidth context, power source, SubVP phantom entities, and per-stream status. It provides copy/retain/release primitives and attaches/removes streams and planes by delegating low-level pipe topology work to `dc_resource.c`.

## Important APIs, types, and functions

- State lifecycle: `dc_state_create`, `dc_state_copy`, `dc_state_create_copy`, `dc_state_copy_current`, `dc_state_create_current_copy`, `dc_state_construct`, `dc_state_destruct`, `dc_state_retain`, and `dc_state_release`.
- Deep-copy helper: `dc_state_copy_internal` copies the struct, rewrites intra-array pipe pointers (`top_pipe`, `bottom_pipe`, `prev_odm_pipe`, `next_odm_pipe`) to the destination `pipe_ctx` array, and retains referenced streams and planes.
- Stream mutation: `dc_state_add_stream` appends a retained stream and calls `resource_add_otg_master_for_stream_output`; `dc_state_remove_stream` collapses ODM slice count to one, removes the OTG master resource, releases 3DLUT, releases the stream, and compacts arrays.
- Plane mutation: `dc_state_add_plane`, `dc_state_remove_plane`, `dc_state_rem_all_planes_for_stream`, and `dc_state_add_all_planes_for_stream` manage `stream_status[].plane_states` and delegate DPP pipe allocation/removal to resource helpers.
- SubVP/phantom helpers: `dc_state_create_phantom_stream`, `dc_state_release_phantom_stream`, `dc_state_create_phantom_plane`, `dc_state_release_phantom_plane`, `dc_state_add_phantom_stream`, `dc_state_remove_phantom_stream`, `dc_state_add_phantom_plane`, `dc_state_remove_phantom_plane`, `dc_state_remove_phantom_streams_and_planes`, and `dc_state_release_phantom_streams_and_planes`.
- Query and flags: `dc_state_get_stream_status`, `dc_state_get_pipe_subvp_type`, `dc_state_get_stream_subvp_type`, `dc_state_get_paired_subvp_stream`, `dc_state_get_stream_from_id`, `dc_state_is_fams2_in_use`, cursor-limit setters/getters, `dc_state_can_clear_stream_cursor_subvp_limit`, and `dc_state_is_subvp_in_use`.

## Control flow

Creating a state allocates with `kvzalloc_obj`, initializes the DML bandwidth context from `dc->dml`, constructs link encoder config, sets power source, optionally creates DML2 contexts under `CONFIG_DRM_AMD_DC_FP`, then initializes `kref`. Copying preserves the destination refcount, duplicates DML2 context contents into already-owned DML2 objects for `dc_state_copy`, or creates DML2 copies for `dc_state_create_copy`.

Adding a stream checks timing generator capacity, retains the stream, increments `stream_count`, then asks the resource layer to add an OTG master. Removing a stream finds its OTG master, reduces ODM to one slice, removes stream output resources, locates the stream in the compact stream array, releases any RMCM 3DLUT, releases the stream, and trims `streams[]` and `stream_status[]`.

Adding a plane finds the stream status and OTG master, attempts to append DPP pipes, then falls back by first removing MPC combine from all streams and then gradually reducing ODM slice count to free pipes. On success it appends and retains the plane. Removing a plane removes its DPP pipe composition, releases the retained plane reference, and compacts `plane_states[]`.

Phantom stream/plane flow creates normal stream/plane objects, tracks them in bounded phantom arrays, marks them phantom, then adds them to regular state structures with SubVP metadata linking main and phantom streams. Removal resets SubVP metadata and delegates through normal stream/plane removal paths.

## State and persistence behavior

`dc_state` owns retained references to all `streams[]`, per-stream `plane_states[]`, `phantom_streams[]`, and `phantom_planes[]`. Destruction releases those references, zeros resource and bandwidth substructures, clears DMUB/block-sequence/perf fields, and destroys DML2 contexts. The state has no durable persistence; it is an in-memory candidate or committed DC state. Copy operations must preserve graph consistency by rebasing embedded `pipe_ctx` pointers onto the copied `res_ctx.pipe_ctx` array.

## Dependencies and integration points

The file depends on DC type/private headers, `resource.h`, `link_enc_cfg.h`, stream and plane retain/release APIs, and DML2 when floating point support is enabled. It is called by higher-level atomic validation and commit code to build candidate states, while resource helpers call back into `dc_state_get_stream_status` through DML2 callback registration.

## Risks and edge cases

- `dc_state_copy_internal` uses `memcpy` of the whole state; every pointer field that points inside the state must be fixed up. New embedded pointers added to `dc_state` or `pipe_ctx` require audit.
- `dc_state_add_stream` increments `stream_count` before checking `resource_add_otg_master_for_stream_output` result and does not locally roll back on failure; callers rely on candidate-state disposal or higher-level rollback.
- `dc_state_remove_stream` indexes `state->streams[i]` after a search; correctness relies on the stream being present after the OTG master lookup succeeds.
- Plane add fallback mutates slice topology to free pipes, so failed add attempts can have broad effects unless the containing validation context is discarded.
- Phantom tracking arrays are bounded by `MAX_PHANTOM_PIPES`; failed tracking is not always propagated by callers.
- Cursor SubVP limit state is stored in `stream_status` and must be reset when stream roles change.

## Test signals

Coverage should include state create/copy/release with DML2 enabled and disabled, stream add/remove at capacity, failed resource-map paths, plane add/remove with MPO, ODM reduction fallback, removal of all planes, SubVP main/phantom pairing and cleanup, cursor limit set/clear behavior, FAMS2 detection across current and candidate states, and leak/refcount instrumentation for copied states. Assertions, `dm_error`, and `DC_LOG_WARNING/ERROR` paths are important diagnostics.
