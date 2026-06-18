# subset-b-001390 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_resource.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_resource.c

## Purpose

`dc_resource.c` is the Display Core resource orchestration layer for AMDGPU DC. It maps ASIC identifiers to DCE/DCN resource-pool constructors, constructs common pool objects, assigns stream, link, audio, clock, OTG, OPP, DPP, ODM, MPC, DSC, and HPO/DIO encoder resources into a `dc_state`, computes scaler/test-pattern/infoframe programming parameters, validates proposed display states, and exposes topology helpers used by DML2 and other DC modules.

## Important APIs, types, and functions

- Resource-pool creation and teardown: `resource_parse_asic_id`, `dc_create_resource_pool`, `dc_destroy_resource_pool`, and `resource_construct` select version-specific `dce*`/`dcn*` constructors and build common audio, stream encoder, HPO encoder, 3DLUT, virtual link, and hwseq resources.
- Clock and sync helpers: `resource_reference_clock_source`, `resource_unreference_clock_source`, `resource_get_clock_source_reference`, `resource_find_used_clk_src_for_sharing`, `dc_resource_find_first_free_pll`, `resource_are_streams_timing_synchronizable`, and `resource_are_vblanks_synchronizable` manage PLL sharing and determine timing compatibility.
- Scaler geometry: `calculate_plane_rec_in_timing_active`, `calculate_mpc_slice_in_timing_active`, `resource_get_odm_slice_dst_rect`, `resource_get_odm_slice_src_rect`, `calculate_recout`, `calculate_scaling_ratios`, `calculate_init_and_vp`, `calculate_inits_and_viewports`, and `resource_build_scaling_params` translate stream/plane rectangles into per-pipe viewport, recout, line-buffer, tap, and SPL/scaler programming data.
- Pipe topology queries: `resource_is_pipe_type`, `resource_get_otg_master_for_stream`, `resource_get_opp_head`, `resource_get_otg_master`, `resource_get_primary_dpp_pipe`, `resource_get_opp_heads_for_otg_master`, `resource_get_dpp_pipes_for_opp_head`, `resource_get_dpp_pipes_for_plane`, `resource_get_mpc_slice_index/count`, and `resource_get_odm_slice_index/count` abstract the `pipe_ctx` graph.
- Pipe allocation and mutation: `resource_add_otg_master_for_stream_output`, `resource_remove_otg_master_for_stream_output`, `resource_append_dpp_pipes_for_plane_composition`, `resource_remove_dpp_pipes_for_plane_composition`, `resource_update_pipes_for_stream_with_slice_count`, `resource_update_pipes_for_plane_with_slice_count`, and legacy `dc_resource_acquire_secondary_pipe_for_mpc_odm_legacy` create and tear down OTG masters, ODM slices, and MPC slices.
- Encoder allocation: `resource_map_pool_resources`, `add_hpo_dp_link_enc_to_ctx`, `remove_hpo_dp_link_enc_from_ctx`, `add_dio_link_enc_to_ctx`, `remove_dio_link_enc_from_ctx`, `get_temp_dp_link_res`, and `update_dp_encoder_resources_for_test_harness` maintain stream encoder, HPO DP link encoder, DIO link encoder, and reference-count arrays in `resource_context`.
- State validation: `dc_validate_with_context`, `dc_validate_global_state`, `dc_validate_stream`, and `dc_validate_plane` apply stream/plane deltas, rebuild scaling, patch unknown tiling, decide DP clock use, and call ASIC-specific global/bandwidth/timing validators.
- Packet and output helpers: `resource_build_info_frame`, `set_avi_info_frame`, `set_vendor_info_packet`, `set_spd_info_packet`, `set_hdr_static_info_packet`, `set_vsc_info_packet`, `set_adaptive_sync_info_packet`, `set_vtem_info_packet`, `resource_build_bit_depth_reduction_params`, `resource_build_test_pattern_params`, and `pipe_need_reprogram`.
- DML2 integration: `resource_init_common_dml2_callbacks` registers resource, topology, scaling, phantom SubVP, flickerless refresh, and mcache callbacks into `dml2_configuration_options`.

## Control flow

Startup flows from ASIC detection through `dc_create_resource_pool`, then version-specific resource-pool construction, then `resource_construct` for common objects. Proposed modes are evaluated through `dc_validate_with_context`: it compares the proposed validation set against the current context, builds deletion/addition/unchanged stream lists, removes changed planes, removes deleted streams, adds new streams, reattaches planes, clears SubVP cursor limits, then invokes `dc_validate_global_state`. Global validation delegates to ASIC-specific `validate_global`, adjusts DP clock-source selection, rebuilds scaler params for every active pipe, and finally calls ASIC-specific bandwidth validation.

Stream mapping is split by resource kind. `resource_map_pool_resources` calculates physical pixel clocks, marks seamless boot candidates, reuses boot-time hardware state when possible, otherwise acquires an OTG master pipe, then assigns stream encoders, DP link settings, HPO stream/link encoders for 128b/132b DP, DIO link encoders when unified assignment is enabled, audio, ABM, and stream status instances. Clock resources are mapped separately by `resource_map_clock_resources`.

Plane and slice changes mutate the linked `pipe_ctx` topology. Adding a first plane fills all OPP heads for the stream; adding later planes acquires secondary DPP pipes under each OPP head. Increasing ODM slices duplicates the current MPC blending tree into a new OPP head linked by `next_odm_pipe`/`prev_odm_pipe`. Increasing MPC slices inserts a new DPP pipe into the vertical `top_pipe`/`bottom_pipe` chain. Each successful topology change rebuilds scaling params and, for ODM changes, test pattern/pixel clock params.

## State and persistence behavior

The persistent state is the in-memory `dc_state->res_ctx`. It contains `pipe_ctx` graphs, clock-source refcounts, audio/stream-encoder acquisition arrays, DIO/HPO link-encoder refcounts and link-index ownership, and per-stream status fields such as `primary_otg_inst`, `stream_enc_inst`, and `audio_inst`. This file never writes durable storage; persistence is across DC atomic-check/commit state objects. Many helpers directly zero or copy `pipe_ctx` records, then restore pool object pointers and `pipe_idx`, so pointer consistency in the graph is critical.

Topology history is also persisted in `dc->debug_data.topology_history` by `resource_log_pipe_topology_update`, which starts a circular snapshot, logs visible and phantom pipe lines, and records DPP/OPP/TG instances. Seamless boot state can be reconstructed from enabled hardware by `acquire_resource_from_hw_enabled_state`; if successful, the stream records `apply_boot_odm_mode`.

## Dependencies and integration points

This file is tightly coupled to resource pool function tables, hardware object classes (`timing_generator`, `stream_encoder`, `link_encoder`, `hpo_dp_*`, `audio`, `opp`, `dpp`, `hubp`, `mpc`, `dwbc`, `clock_source`), DC link services, DML2, SPL, DSC, DMUB-facing packet structures, and DC state/stream/plane private APIs. Version-specific resource headers from DCE 6.x through DCN 4.2 provide pool constructors and ASIC-specific callbacks. External users include `dc_state.c` for stream/plane attach and detach, DML2 through callback registration, mode validation paths, and link test harness code.

## Risks and edge cases

- Pipe graph mutation is high-risk: errors in `top_pipe`/`bottom_pipe` or `prev_odm_pipe`/`next_odm_pipe` relinking can orphan resources, create inconsistent topology classifications, or break later deletes.
- `resource_remove_otg_master_for_stream_output` relies on assertions that ODM count is one and plane state is NULL; callers must remove planes/slices first.
- Encoder reference counts must stay balanced across failure paths. Several allocation paths set acquired flags before later resource checks can fail, so callers need context rollback semantics.
- Scaler math depends on nonzero stream/plane rectangles, 3D view formats, rotation, mirror, borders, 4:2:0 chroma division, ODM edge pixels, and visual confirm offsets. Off-by-one or rounding changes can cause visible corruption.
- `resource_build_scaling_params` temporarily mutates `stream->dst` for borders and must always restore it before returning.
- DP clock selection and HPO/DIO link resource decisions are policy-heavy and interact with link-service encoding choices. The comment in `get_link_hwss` explicitly notes a loose coupling between 128b/132b settings and HPO encoder presence.
- Functions named `recource_*` appear misspelled but are part of the compiled API in this file; renaming them would require header/caller coordination.

## Test signals

Useful coverage includes atomic modesets that add/remove streams and planes, MPO plane changes on unchanged streams, ODM combine increase/decrease, MPC split/merge, SubVP phantom streams/planes, seamless boot takeover, DP 8b/10b versus 128b/132b resource assignment, flexible and fixed DIO encoder mapping, audio endpoint exhaustion, DSC and hblank-borrow modes, HDMI and DP infoframe generation, 4:2:0/4:2:2 timing, rotated and mirrored planes, visual confirm, and DML2 callback-driven topology changes. Kernel test signals are `DC_LOG_WARNING`, `DC_ERR`, topology debug snapshots, failed `dc_status` returns such as `DC_NO_*_RESOURCE`, and bandwidth/scaling validation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_sink.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_sink.c

## Purpose

`dc_sink.c` implements the lifetime and basic construction of `struct dc_sink`, the Display Core object representing a connected sink and its EDID-derived capabilities. It binds a sink to a `dc_link`, assigns a unique sink id from the DC context, and exposes retain/release semantics around a kernel `kref`.

## Important APIs, types, and functions

- `dc_sink_construct` validates `dc_sink_init_data->link`, copies sink signal, link, context, dongle pixel clock, converter audio-disable flag, initializes `dc_container_id` to NULL, assigns `sink_id`, and increments `ctx->dc_sink_id_count`.
- `dc_sink_create` allocates a zeroed `dc_sink`, constructs it, initializes the refcount, and cleans up on construction failure.
- `dc_sink_retain` and `dc_sink_release` wrap `kref_get` and `kref_put`.
- `dc_sink_free` is the `kref` finalizer; it frees the optional `dc_container_id` and the sink object itself.

## Control flow

Creation is allocation, construction, then `kref_init`. If allocation fails, `dc_sink_create` returns NULL. If construction fails, it frees the partially allocated sink and returns NULL. Runtime users retain the sink while streams or links hold references. Final release invokes `dc_sink_free`.

## State and persistence behavior

The sink stores pointers to `dc_link` and `dc_context`; it does not own those objects. It owns `dc_container_id` if one is later allocated. `sink_id` persists for the object's lifetime and is generated by incrementing `dc_sink_id_count`; the file comment notes the intent that two different sink objects should not share an id unless they represent the same sink. No on-disk persistence is involved.

## Dependencies and integration points

The file depends on `dm_services.h`, `dm_helpers.h`, and `core_types.h`, plus kernel allocation and `kref` primitives. `dc_stream.c` consumes sinks through `dc_create_stream_for_sink`, retains sinks in `dc_stream_construct`, copies EDID audio/display fields into streams, and releases sinks in stream destruction.

## Risks and edge cases

- `dc_sink_retain` assumes a non-NULL valid sink; callers must guard NULL.
- `dc_sink_construct` increments `dc_sink_id_count` without local locking. Correctness depends on the surrounding DC/link management serialization.
- `dc_container_id` is initialized to NULL here but freed later; any external assignment must allocate with compatible kernel allocation semantics.
- A failed constructor after future field additions must keep cleanup aligned with owned fields.

## Test signals

Relevant tests are hotplug/connect-disconnect cycles, stream creation and destruction against one sink, MST or dongle paths that exercise `sink_signal` and `dongle_max_pix_clk`, leak/refcount checks, and error injection for allocation or NULL link initialization. Expected failure behavior is NULL from `dc_sink_create` with no leaked allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_sink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_stat.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_stat.c

## Purpose

`dc_stat.c` provides lockless Display Core status accessors for DMUB notifications and GPINT dataout. The file-level documentation states these interfaces are called without DAL and DC locks, so they must avoid modifying shared DC state except variables exclusively owned by these interfaces.

## Important APIs, types, and functions

- `dc_stat_get_dmub_notification` obtains `dc->ctx->dmub_srv->dmub`, calls `dmub_srv_stat_get_notification`, asserts success, and normalizes certain notification instances from DPIA port index to DC link index with `get_link_index_from_dpia_port_index`.
- `dc_stat_get_dmub_dataout` calls `dmub_srv_get_gpint_dataout` and asserts success.
- Key types are `struct dc`, `struct dmub_notification`, `struct dmub_srv`, and `enum dmub_status`.

## Control flow

Both functions are thin pass-throughs to DMUB service routines. Notification retrieval has one post-processing branch: for HPD, HPD IRQ, AUX reply, DPIA notification, and SET_CONFIG_REPLY notification types, `notify->link_index` is overwritten with the DC link index derived from `notify->instance`.

## State and persistence behavior

The functions do not allocate memory or persist state. They read DC context pointers and write only caller-provided output buffers (`notify` or `dataout`). The notification helper mutates the returned notification structure after DMUB fills it.

## Dependencies and integration points

Includes are `dc/dc_stat.h`, `dmub/dmub_srv_stat.h`, and `dc_dmub_srv.h`. The code integrates DC with DMUB firmware status queues and the DPIA/link-index mapping helper used by USB4/DPIA display paths. It is likely consumed by higher-level interrupt, HPD, AUX, or DM status polling code that cannot take the normal DC locks.

## Risks and edge cases

- The code assumes `dc`, `dc->ctx`, `dc->ctx->dmub_srv`, and `dmub` are valid. There is no defensive NULL check.
- Because the functions are explicitly lockless, adding access to mutable DC fields would be risky.
- `ASSERT(status == DMUB_STATUS_OK)` may catch firmware/service failures in debug builds, but non-debug behavior depends on ASSERT semantics; callers still receive whatever data the DMUB layer produced.
- Notification instance remapping is type-gated. New DMUB notification types that carry DPIA port indexes must be added here or consumers may see the wrong index namespace.

## Test signals

Exercise DMUB notification retrieval for HPD, HPD IRQ, AUX reply, DPIA notification, SET_CONFIG_REPLY, and unrelated notification types. Check that DPIA instances map to expected `link_index` values and that non-remapped types preserve DMUB-provided fields. Also cover GPINT dataout reads and DMUB failure injection where ASSERT diagnostics are expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_state.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_stream.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_stream.c

## Purpose

`dc_stream.c` implements lifecycle, sink-derived initialization, cursor programming, writeback control, status queries, metadata programming, 3DLUT ownership, logging, and flickerless refresh calculations for `struct dc_stream_state`. A stream is the DC representation of one display timing/signal path attached to a sink.

## Important APIs, types, and functions

- Lifecycle and identity: `update_stream_signal`, `dc_stream_construct`, `dc_stream_destruct`, `dc_stream_assign_stream_id`, `dc_stream_retain`, `dc_stream_release`, `dc_create_stream_for_sink`, and `dc_copy_stream`.
- Status and pipe lookup: `dc_stream_get_status`, `dc_stream_get_status_const`, and `dc_stream_get_pipe_ctx`.
- Cursor paths: `dc_stream_check_cursor_attributes`, `dc_stream_set_cursor_attributes`, `dc_stream_program_cursor_attributes`, `program_cursor_attributes`, `dc_stream_set_cursor_position`, `dc_stream_program_cursor_position`, and `program_cursor_position`.
- Writeback paths: `dc_stream_add_writeback`, `dc_stream_fc_disable_writeback`, and `dc_stream_remove_writeback`.
- Hardware/status helpers: `dc_stream_get_vblank_counter`, `dc_stream_send_dp_sdp`, `dc_stream_get_scanoutpos`, `dc_stream_dmdata_status_done`, `dc_stream_set_dynamic_metadata`, and `dc_stream_add_dsc_to_resource`.
- Color resources and diagnostics: `dc_stream_log`, `dc_stream_get_3dlut_for_stream`, `dc_stream_release_3dlut_for_stream`, and `dc_stream_init_rmcm_3dlut`.
- Flickerless VRR/luminance helpers: interpolation routines over `stream->lumin_data`, `dc_stream_calculate_max_flickerless_refresh_rate`, `dc_stream_calculate_min_flickerless_refresh_rate`, `dc_stream_is_refresh_rate_range_flickerless`, `dc_stream_get_max_flickerless_instant_vtotal_decrease`, `dc_stream_get_max_flickerless_instant_vtotal_increase`, `dc_stream_is_cursor_limit_pending`, and `dc_stream_can_clear_cursor_limit`.

## Control flow

Stream construction retains the sink, copies context/link/sink patches/audio modes/display identity/quantization bits from EDID caps, initializes default DSC timing config, derives the signal from sink or connector signal, sets transfer function bypass, and assigns a unique stream id. Copying uses `kmemdup`, allocates fresh update scratch, retains the sink, assigns a new stream id, and optionally clears dynamic link encoder assignment until commit.

Cursor attribute programming validates stream and cursor address, optionally rejects oversized hardware cursors when SubVP/software fallback rules require it, stores attributes, exits low-power state, temporarily disables idle optimizations, programs all matching pipes through HWSS, sends DMUB cursor updates, and restores idle optimizations. Cursor position programming follows the same pattern and additionally updates visual confirm color and may trigger manual DRR events.

Writeback add/update stores `dc_writeback_info` in the stream, binds the stream transfer function to DWB params, updates bandwidth, and calls HWSS enable/update. Removal marks matching writeback entries disabled, compacts the array, updates bandwidth, and disables the hardware DWB pipe if enabled.

Flickerless refresh control uses luminance tables to interpolate brightness for refresh rates, find safe min/max refresh rates within static or gaming flicker criteria, and convert safe refresh bounds to instantaneous vtotal deltas.

## State and persistence behavior

A stream owns its `update_scratch` allocation and a retained `dc_sink`. It stores copied EDID/audio information, timing, DSC defaults, cursor attributes/position, writeback array and count, dynamic metadata address, assigned stream id, luminance data, and flags such as `is_phantom`, `dpms_off`, and cursor/SubVP requests. RMCM 3DLUT ownership is persisted in `dc->res_pool->rmcm_3dlut[]`, keyed by stream pointer and `isInUse`.

## Dependencies and integration points

The file depends on DC core types, resource helpers, IPP/timing generator/HWSS hooks, DMUB cursor and metadata services, state private APIs, and stream private APIs. It is integrated with `dc_sink.c` for sink refcounts, `dc_state.c` for stream status lookups and cursor limit state, `dc_resource.c` for DSC/resource addition, and hardware sequencer callbacks for cursor, writeback, bandwidth, dynamic metadata, and visual confirm programming.

## Risks and edge cases

- Cursor programming iterates all pipes for the stream; ODM and pipe-split configurations must lock/update the correct set of pipes to avoid inconsistent cursor state.
- `old_position` in `dc_stream_program_cursor_position` points to `stream->cursor_position` before `dc_stream_set_cursor_position`; because the setter overwrites the struct, comparisons using `old_position` observe the updated value rather than a snapshot. This may affect idle-optimization gating logic.
- Writeback add updates stream state before bandwidth update and hardware enable; callers need to handle false returns with candidate-state rollback or cleanup.
- Dynamic metadata requires HDMI/DP signal, HWSS support, a matching current pipe, and a HUBP. Missing any of these returns false.
- Luminance interpolation uses integer division and assumes valid sorted luminance tables when `is_valid` is true; duplicate refresh entries are partially handled.
- `dc_create_stream_for_sink` uses `GFP_ATOMIC` under a preemption macro, so allocation failures are expected under pressure and must be handled by callers.

## Test signals

Useful tests include stream create/copy/release refcount checks, DVI dual-link signal selection, EDID audio copy, dynamic encoder assignment copies, cursor attribute rejection for zero address and oversized SubVP cursors, cursor programming across ODM/MPC split pipes with DMUB cursor offload on and off, writeback add/update/remove and bandwidth failure injection, DP SDP sending, dynamic metadata programming, RMCM 3DLUT exhaustion/release, vblank/scanout queries, and luminance table edge cases for min/max flickerless refresh and vtotal delta.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_stream.c -->
