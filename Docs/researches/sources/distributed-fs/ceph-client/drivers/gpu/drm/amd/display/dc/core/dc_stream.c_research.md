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
