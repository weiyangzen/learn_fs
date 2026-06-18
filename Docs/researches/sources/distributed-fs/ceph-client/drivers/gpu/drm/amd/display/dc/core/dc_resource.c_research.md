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
