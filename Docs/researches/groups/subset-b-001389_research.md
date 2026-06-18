# Research: subset-b-001389

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_hw_sequencer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_hw_sequencer.c

## Purpose

`dc_hw_sequencer.c` is a shared AMD Display Core hardware sequencing utility file. It provides color-space helpers, visual-confirmation color selection, wait/synchronization helpers, and a generic block-sequence mechanism that lets higher-level DCN code build ordered hardware programming steps and execute them through the HWSS, HWSEQ, HUBP, DPP, MPC, OPP, DSC, DCCG, ABM, DWBC, MCIF, timing-generator, and DMUB function tables.

The file is intentionally broad. Most exported `hwss_*` functions are small adapters from `union block_sequence_params` to lower-level block-specific callbacks. The substantive logic is in default CSC/black-color mapping, visual-confirmation state derivation, fast flip sequence assembly, outstanding-update waits, DSC configuration calculation, and the consistent block-sequence add/dispatch pattern.

## Important APIs, Types, And Functions

- `enum black_color_format`, `black_color_format[]`: local mapping from output color format/range to TG black values.
- `enum dc_color_space_type`, `struct out_csc_color_matrix_type`, `output_csc_matrix[]`: local normalized color-space categories and static 3x4 output CSC coefficient tables.
- `find_color_matrix(color_space, array_size)`: returns a 12-entry default output CSC coefficient array selected by `get_color_space_type`.
- `color_space_to_black_color(dc, colorspace, black_color)`: maps DC color spaces to RGB or YUV black TG values.
- `hwss_wait_for_blank_complete(tg)`: polls `tg->funcs->is_blanked` up to 100 ms and reports failure through `dm_error`.
- Visual-confirmation helpers: `get_mpctree_visual_confirm_color`, `get_surface_visual_confirm_color`, `get_hdr_visual_confirm_color`, `get_smartmux_visual_confirm_color`, `get_vabc_visual_confirm_color`, `get_subvp_visual_confirm_color`, `get_mclk_switch_visual_confirm_color`, `get_cursor_visual_confirm_color`, `get_dcc_visual_confirm_color`, `get_surface_tile_visual_confirm_color`, `get_fams2_visual_confirm_color`, and `get_refresh_rate_confirm_color`.
- `set_p_state_switch_method(dc, context, pipe_ctx)`: classifies a pipe into `P_STATE_*` visual/debug categories using DML DRAM clock support, vactive margin, FW-based MCLK switching, SubVP pairing, and FreeSync.
- `set_drr_and_clear_adjust_pending(pipe_ctx, stream, params)`: programs DRR through the timing generator and clears `stream->adjust.timing_adjust_pending`.
- `hwss_build_fast_sequence(...)`: builds a `struct block_sequence[]` for fast updates/flips from update flags, DMUB commands, lock requirements, SubVP state, and pipe topology.
- `hwss_execute_sequence(dc, block_sequence, num_steps)`: central dispatcher from `enum block_sequence_func` values to the wrapper or direct lower-level function call that performs each step.
- `hwss_add_*` helpers: append one step to a `struct block_sequence_state` if `*num_steps < MAX_HWSS_BLOCK_SEQUENCE_SIZE`.
- `hwss_wait_for_all_blank_complete`, `hwss_wait_for_odm_update_pending_complete`, `hwss_wait_for_no_pipes_pending`, `hwss_wait_for_outstanding_hw_updates`, `hwss_process_outstanding_hw_updates`: synchronization around pending flips, ODM double-buffer updates, OPP blank updates, MPCC disconnects, and post-update programming.
- Wrapper families: DPP setup/gamut/bias/scaler/cursor/HDR, HUBP surface/config/clock/VM/viewport/blank/SubVP/MALL, MPC output CSC/blending/plane insertion/DWB mux/MPCC idle, OPP format/dynamic expansion/blank/test-pattern, DSC config/enable/disable/read-state/clock, TG/OPTC sync/GSL/DSC/manual trigger/wait, DCCG DTO/ref DSC clock, ABM, MCIF writeback, DWBC, HUBBUB p-state/self-refresh/reset, and DMUB command/SubVP address forwarding.

## Control Flow

Color helpers normalize public `enum dc_color_space` values into internal color-space categories. `find_color_matrix` uses that category to scan `output_csc_matrix`, while `color_space_to_black_color` explicitly switches over every known color space to select TG black levels.

Visual-confirmation helpers derive debug colors from runtime pipe state. Some use pipe-chain traversal: MPCTree confirmation walks to the top pipe, HDR uses the top-most desktop plane, and tile confirmation walks to the bottom-most plane. Others inspect stream transfer functions, pixel formats, Smart Mux config, backlight control type, SubVP/p-state classification, cursor enable state, DCC/mcache assignment, FAMS2 enablement, or refresh-rate range.

`hwss_build_fast_sequence` is the key sequence builder. It returns immediately if the pipe has no plane or stream. It then conditionally appends DCC meta propagation waits, SubVP pipe-control locks, DMUB hardware locks, OPTC pipe-control locks, queued DMUB commands, and per-pipe update work. For each ODM pipe and each MPC pipe in the stack, it checks plane and stream update flags and appends only the needed steps: flip-control GSL, triple buffering, SubVP surface-address save, plane address programming, input/output transfer functions, gamut remap, DPP input CSC setup, bias/scale, CM histogram, visual-confirmation update, and output CSC programming. It unlocks in reverse-style trailing steps, then appends cursor offload and manual-trigger steps for the final pipe when an address update needs a manual trigger.

`hwss_execute_sequence` is a large switch over the block function enum. It unpacks the matching `union block_sequence_params` member and either directly invokes a low-level function pointer or calls a `hwss_*` wrapper. The default branch asserts false, so adding a new enum without dispatcher support is caught in debug builds.

Most `hwss_add_*` helpers are deliberately uniform: populate one union member, set the block function enum, and increment `num_steps`. This file relies on callers and the dispatcher to keep parameter lifetimes valid until execution.

Synchronization helpers walk `MAX_PIPES` or the resource pool pipe count and skip inactive/phantom pipes. They wait for blank completion, ODM/OTG double-buffer drain, no pending flips, all pending updates on OTG masters, and MPCC disconnect idleness before allowing full updates or post-update programming to continue.

## State And Persistence Behavior

This file does not persist data outside the in-memory DC structures and hardware registers it programs. It mutates:

- `pipe_ctx->p_state_type` for debug/visual confirmation.
- `stream->adjust.timing_adjust_pending` after DRR programming.
- `pipe_ctx->visual_confirm_color` in refresh-rate confirmation.
- `hubp->power_gated` in surface config and HUBP clock-control wrappers.
- `plane_state->status.is_flip_pending` while polling flip state.
- `opp->mpcc_disconnect_pending[mpcc_inst]` after waiting for MPC idle.
- Optional caller-owned booleans such as `disallow_self_refresh_applied`, frame-count outputs, and DSC power-gate state outputs.

The durable side effects are hardware-facing: MMIO/register writes and DMUB messages performed through function tables. `hwss_build_fast_sequence` stores pointers into a caller-provided block-sequence array, so referenced objects must remain alive until `hwss_execute_sequence` completes.

## Dependencies And Integration Points

The file depends heavily on AMD DC internals:

- Core DC structures: `struct dc`, `struct dc_state`, `struct pipe_ctx`, `struct dc_stream_state`, `struct dc_plane_state`.
- Hardware abstraction function tables: `dc->hwss`, `dc->hwseq->funcs`, and block-specific `funcs` under TG, HUBP, DPP, MPC, OPP, DSC, DCCG, ABM, MCIF, DWBC, and HUBBUB.
- Resource/topology helpers: `resource_is_pipe_type`, `dc_state_get_pipe_subvp_type`, `dc_state_get_paired_subvp_stream`, `dc_state_is_fams2_in_use`.
- DMUB integration: `dc_wake_and_execute_dmub_cmd`, `dc_dmub_srv_subvp_save_surf_addr`, and `dmub_hw_lock_mgr_does_link_require_lock`.
- DML/DML2 structures for bandwidth, p-state classification, HUBP programming, mcache, and global-sync data.

It is integrated by generation-specific HWSS code that constructs block sequences during commits, fast updates, power transitions, DSC changes, writeback setup, cursor updates, and pipe topology changes. The wrapper layer allows sequence construction to be shared while the actual register programming stays ASIC-specific behind function tables.

## Risks And Edge Cases

- Bounds safety depends on every add/build path respecting `MAX_HWSS_BLOCK_SEQUENCE_SIZE`. The `hwss_add_*` helpers check capacity, but `hwss_build_fast_sequence` appends directly without local capacity checks.
- Many wrappers only null-check the block object and function pointer, not every nested pointer. Callers must pass fully populated, generation-appropriate params.
- `get_dcc_visual_confirm_color` indexes `id_colors[assigned_id]` for mcache IDs other than `0xF`; IDs outside `0..7` would be unsafe if upstream mcache programming violates expectations.
- The color-space type function contains an unreachable duplicated `COLOR_SPACE_YCBCR709` check before `COLOR_SPACE_YCBCR709_BLACK`; behavior is still correct for black because the explicit black case follows.
- Static CSC tables contain a TODO for limited YCbCr values, so color correctness depends on later validation elsewhere.
- Wait loops can block commit paths for up to 100 ms per pipe/operation; missed pending-status updates or hardware that never drains can produce asserts or boot/update stalls.
- DSC config calculation divides horizontal slices by `opp_cnt`; callers must avoid zero and ensure stream DSC config is divisible for the topology.
- Sequence params often hold raw pointers to stack or context objects from the caller. Deferring execution beyond those lifetimes would corrupt hardware programming.
- Debug visual confirmation changes output border/colors intentionally and must be gated by `dc->debug.visual_confirm`.

## Test Signals

- Kernel build coverage for AMDGPU display catches missing enum cases, function declarations, and union member mismatches.
- Unit or simulator tests should validate `find_color_matrix`, `color_space_to_black_color`, and visual-confirmation helpers for representative RGB/YUV/HDR/SubVP/DCC paths.
- Sequence tests can construct mock `dc`, `pipe_ctx`, and function tables, set update flags, run `hwss_build_fast_sequence`, and verify ordered function enums and params.
- Dispatcher tests should ensure every block function enum has a non-default `hwss_execute_sequence` case.
- Hardware or emulation tests should cover fast flips, SubVP immediate flips, FAMS2/DMUB lock paths, output CSC changes, DCC metadata propagation, cursor offload/manual trigger, DSC enable/disable/reconfigure, ODM combine/bypass changes, MPCC disconnects, writeback enable/update/disable, and p-state/self-refresh transitions.
- Runtime debug signals include `dm_error("failed to blank crtc")`, asserts in pending-flip and dispatcher paths, visual-confirm colors, link/DMUB command failures outside this file, and stalls around wait loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_hw_sequencer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_link_enc_cfg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_link_enc_cfg.c

## Purpose

`dc_link_enc_cfg.c` owns Display Core link encoder assignment state. It decides which DIG link encoder should drive each active stream, with special handling for fixed physical endpoints, flexible/mappable endpoints such as DPIA/USB4, retained assignments across state transitions, and MST streams sharing the same link. It also exposes query, validation, copy, init, unassign, and transient-mode helpers for the resource pool and link code.

## Important APIs, Types, And Functions

- `struct link_enc_assignment`: stored in `state->res_ctx.link_enc_cfg_ctx.link_enc_assignments[]` and `transient_assignments[]`; includes validity, endpoint id, engine id, and retained stream pointer.
- `link_enc_cfg_init(dc, state)`: clears assignments, initializes available encoder pool, and sets steady mode.
- `link_enc_cfg_copy(src_ctx, dst_ctx)`: raw-copies the link encoder config context between DC states.
- `link_enc_cfg_link_encs_assign(dc, state, streams, stream_count)`: primary assignment algorithm.
- `link_enc_cfg_link_enc_unassign(state, stream)`: removes a stream assignment and returns the encoder to the availability pool only when no stream still uses it.
- `link_enc_cfg_get_stream_using_link_enc`, `link_enc_cfg_get_link_using_link_enc`, `link_enc_cfg_get_link_enc_used_by_link`, `link_enc_cfg_get_link_enc_used_by_stream_current`: query current/transient assignment state.
- `link_enc_cfg_get_next_avail_link_enc(dc)`: finds the first unassigned encoder in the resource pool.
- `link_enc_cfg_get_link_enc(link)`: public convenience resolver for fixed and flexible links.
- `link_enc_cfg_is_transmitter_mappable(dc, link_enc)` and `link_enc_cfg_is_link_enc_avail(dc, eng_id, link)`: policy checks for dynamic mapping.
- `link_enc_cfg_validate(dc, state)`: verifies assignment count, stream pointer matching, endpoint/encoder uniqueness, availability-pool consistency, and stream `link_enc` pointers.
- `link_enc_cfg_set_transient_mode(dc, current_state, new_state)`: switches current state lookup to transient assignments when a pending new state has a matching assignment count.

Private helpers include `is_dig_link_enc_stream`, `get_assignment`, `get_stream_using_link_enc`, `add_link_enc_assignment`, `remove_link_enc_assignment`, `find_first_avail_link_enc`, `is_avail_link_enc`, `are_ep_ids_equal`, `get_link_enc_used_by_link`, and `clear_enc_assignments`.

## Control Flow

Initialization calls `clear_enc_assignments`, which invalidates all assignment slots, releases retained stream references, and fills `link_enc_avail[]` for existing resource-pool link encoder objects. The mode starts as `LINK_ENC_CFG_STEADY`.

Assignment begins with assertions that the caller's stream count matches `state->stream_count` and that current state is steady. It asks the resource pool to unassign each stream from the current state, then asserts the new state's assignment table is empty.

The assignment algorithm has three phases:

1. Fixed physical endpoints are handled first. Streams whose links are not `is_dig_mapping_flexible` and are supported by a DIG encoder receive `stream->link->eng_id`.
2. Flexible endpoints try to retain previous assignments when assigning a non-current state. For each new stream that matches a previous stream/link and had a valid previous assignment, the previous engine is reused if `is_avail_link_enc` permits it.
3. Remaining flexible endpoints receive either the encoder already used by the same link/MST endpoint, a preferred DPIA engine (`dpia_preferred_eng_id`) when set, or the first available encoder.

`add_link_enc_assignment` writes the table entry matching the stream index in `state->streams[]`, retains the stream, removes the engine from `link_enc_avail[]`, and writes `stream->link_enc`. MST sharing is handled because streams on the same link can be considered available for the same engine and `get_link_enc_used_by_link` can reuse an endpoint's encoder.

After assignment, `link_enc_cfg_validate` asserts invariants, transient assignments in `dc->current_state` are updated to mirror the new state's steady assignments, debug logs print current/new endpoint-engine mappings, and the new state is marked steady.

Lookup functions use `get_assignment`, which reads either `current_state->transient_assignments[]` or `current_state->link_enc_assignments[]` depending on mode. This is how transient mode lets callers resolve encoders during an in-flight transition.

## State And Persistence Behavior

State is held entirely in `struct dc_state`:

- `res_ctx.link_enc_cfg_ctx.link_enc_assignments[]`: steady assignment table.
- `res_ctx.link_enc_cfg_ctx.transient_assignments[]`: staged table used during transient state.
- `res_ctx.link_enc_cfg_ctx.link_enc_avail[]`: available DIG engine pool.
- `res_ctx.link_enc_cfg_ctx.mode`: steady vs transient lookup mode.

The file also mutates `stream->link_enc` and manages stream reference counts with `dc_stream_retain` and `dc_stream_release`. Incorrect assignment/removal can therefore leak stream references, prematurely release streams, or leave streams with stale encoder pointers.

No on-disk persistence exists. Assignment state lives across atomic DC state construction/commit by being copied with `link_enc_cfg_copy` and updated during resource assignment.

## Dependencies And Integration Points

The code depends on `link_enc_cfg.h`, `resource.h`, and `link_service.h`, plus core structures such as `struct dc`, `struct dc_state`, `struct dc_stream_state`, `struct dc_link`, `struct link_encoder`, `enum engine_id`, and `struct display_endpoint_id`.

It integrates with:

- The DC resource pool (`dc->res_pool->link_encoders`, `res_cap->num_dig_link_enc`, `funcs->link_enc_unassign`, `funcs->link_encs_assign`).
- Link objects (`connector_signal`, `output_signals`, `is_dig_mapping_flexible`, `eng_id`, `dpia_preferred_eng_id`, `link_id`, `ep_type`).
- Stream lifecycle management (`dc_stream_retain`, `dc_stream_release`).
- Logging and debug assertions through `DC_LOG_DEBUG`, `DC_LOG_ERROR`, and `ASSERT`.

This is a policy layer between high-level stream/resource planning and lower-level link encoder hardware objects. Other link code calls it to resolve encoders for training, transmitter setup, link resource mapping, or HPD/link operations.

## Risks And Edge Cases

- `clear_enc_assignments` stores `(enum engine_id)i` for availability rather than `ENGINE_ID_DIGA + i`; this must match enum layout expectations in this tree or assignments can be invalid. Other code subtracts `ENGINE_ID_DIGA` when indexing.
- `link_enc_cfg_validate` loops over `MAX_PIPES` and calls `is_dig_link_enc_stream(state->streams[i])`; correctness depends on unused entries being NULL-safe, which `is_dig_link_enc_stream` is.
- `remove_link_enc_assignment` only clears the first matching stream assignment. MST sharing relies on availability not being restored until no stream uses the engine.
- Pointer equality is used for retaining previous stream assignments (`stream == prev_stream`), so recreated but equivalent streams will not retain prior encoders.
- `link_enc_cfg_copy` memcpy-copies retained stream pointers and reference ownership semantics; callers must understand whether copy creates an owned state or a staged clone to avoid release imbalance.
- Transient mode is enabled solely by assignment count matching `new_state->stream_count`; if transient assignments are stale but count-compatible, lookups may return wrong encoders.
- Several helpers compute `eng_idx = eng_id - ENGINE_ID_DIGA`; callers must not pass `ENGINE_ID_UNKNOWN` to paths that index before guarding.
- Validation asserts in debug builds but only logs and returns false in non-debug; callers that ignore the result may continue with invalid mappings.

## Test Signals

- Unit tests with mock DC states should cover fixed PHY assignment, flexible DPIA assignment, preferred DPIA engine selection, previous assignment retention, MST stream sharing, unassign/reassign, and exhausted encoder pools.
- Validate reference counts by assigning and clearing states with multiple streams, including MST streams that share an encoder.
- Exercise transient mode by assigning a new state, switching current state to transient, and verifying lookup functions read `transient_assignments`.
- Negative tests should create duplicate endpoint-to-engine or engine-to-endpoint mappings and ensure `link_enc_cfg_validate` reports failures and logs the bitmap.
- Runtime signals are `DC_LOG_DEBUG` assignment dumps, `DC_LOG_ERROR` invalid assignment logs, and assertions around unexpected non-empty state, missing streams, or invalid validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_link_enc_cfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_link_exports.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_link_exports.c

## Purpose

`dc_link_exports.c` is the public Display Core link API shim. Its file policy says it should be a single entrance to link functionality declared in DC public headers and should not add new functional behavior. Nearly every function forwards to `dc->link_srv` or `link->dc->link_srv`, with a few local convenience helpers for link lookup, eDP enumeration, I2C submission, and highest-encoding-format classification.

## Important APIs, Types, And Functions

- Link lookup and eDP enumeration: `dc_get_link_at_index`, `dc_get_edp_links`, `dc_get_edp_link_panel_inst`.
- Detection/status/capability exports: `dc_link_detect`, `dc_link_detect_connection_type`, `dc_link_get_status`, `dc_link_is_hdcp14`, `dc_link_is_hdcp22`, `dc_link_get_link_cap`, `dc_link_get_highest_encoding_format`, `dc_link_is_dp_sink_present`, `dc_link_is_fec_supported`, `dc_link_should_enable_fec`.
- Link resource map/DSC/link bandwidth: `dc_get_cur_link_res_map`, `dc_restore_link_res_map`, `dc_link_update_dsc_config`, `dc_link_bandwidth_kbps`, `dc_link_required_hblank_size_bytes`, `dc_link_dp_get_max_link_enc_cap`, `dc_link_decide_edp_link_settings`.
- I2C/AUX exports: `dc_get_oem_i2c_device`, `dc_is_oem_i2c_device_present`, `dc_submit_i2c`, `dc_submit_i2c_oem`, `dc_link_aux_transfer_raw`.
- DP test/training/trace exports: `dc_link_dp_handle_automated_test`, `dc_link_dp_set_test_pattern`, `dc_link_set_drive_settings`, `dc_link_set_preferred_link_settings`, `dc_link_set_preferred_training_settings`, `dc_dp_trace_*`, `dc_link_dp_mst_decide_link_encoding_format`, `dc_link_check_link_loss_status`, `dc_link_dp_allow_hpd_rx_irq`, `dc_link_dp_handle_link_loss`, `dc_link_dp_read_hpd_rx_irq_data`, `dc_link_handle_hpd_rx_irq`, `dc_link_decide_lttpr_mode`.
- Remote sink management: `dc_link_add_remote_sink`, `dc_link_remove_remote_sink`.
- eDP/embedded panel features: `dc_link_edp_panel_backlight_power_on`, backlight get/set functions, PSR setup/state/allow-active, Replay allow/state, PR enable/update/general command/state, T12 wait, ALPM support.
- HPD and bandwidth validation: `dc_link_get_hpd_state`, `dc_link_enable_hpd`, `dc_link_disable_hpd`, `dc_link_enable_hpd_filter`, `dc_link_validate_dp_tunneling_bandwidth`.

## Control Flow

Most functions are one-line pass-throughs. The common pattern is to extract `link->dc->link_srv` or `dc->link_srv` and call the corresponding service operation. Return values are returned unchanged.

Local control flow exists in a few helpers:

- `dc_get_link_at_index` returns NULL when `link_index >= MAX_LINKS`; otherwise it returns `dc->links[link_index]`.
- `dc_get_edp_links` iterates `dc->links[0..link_count)`, skips NULL entries, records every link whose `connector_signal == SIGNAL_TYPE_EDP`, and stops at `MAX_NUM_EDP`.
- `dc_get_edp_link_panel_inst` returns false for non-eDP links; otherwise it enumerates eDP links and counts how many precede the target pointer.
- `dc_is_oem_i2c_device_present` and `dc_submit_i2c_oem` return false when no OEM DDC service exists.
- `dc_link_set_drive_settings` first obtains current link resources into a local `struct link_resource`, then forwards drive settings with that resource.
- `dc_link_get_highest_encoding_format` inspects signal type, dongle type, and verified DP encoding to map to public `DC_LINK_ENCODING_*` values; non-DP/unsupported cases return `DC_LINK_ENCODING_UNSPECIFIED`.

## State And Persistence Behavior

This file owns no persistent state. It exposes and triggers stateful behavior owned by other subsystems:

- Detection, MST topology reset, DPRX state clear, link loss handling, link training preferences, HPD filters, FEC decisions, USB4 bandwidth allocation, PSR/Replay/PR state, ALPM support, and backlight control are all delegated to `link_srv`.
- I2C functions send commands through DDC pins and may affect external devices.
- Remote sink add/remove mutates link-managed sink lists through the service layer.
- `dc_get_edp_links` writes caller-provided output arrays and counts; `dc_get_edp_link_panel_inst` writes `inst_out`.

Because it is an API shim, it assumes passed `dc`, `link`, `pipe_ctx`, `ddc`, and output pointers are valid unless a local guard is explicitly present.

## Dependencies And Integration Points

The file includes `link_service.h` for the internal service interface and `dce/dce_i2c.h` for I2C helpers. It integrates public DC APIs with the `link_srv` implementation installed on `struct dc`.

Primary integration boundaries:

- Public display manager / DRM-facing DC callers use these `dc_link_*` exports.
- Link service implements the real DP, HDMI, eDP, AUX, HPD, HDCP, DSC, FEC, LTTPR, USB4, PSR, Replay, PR, ALPM, and bandwidth policies.
- Resource pool supplies `dc->links[]`, `link_count`, `oem_device`, and DDC pins.
- DCE I2C helpers perform OEM and per-link I2C transactions.

The file's policy makes it a stable facade: new public link functions should be declared in `dc.h`, documented there, and forwarded here to the service layer.

## Risks And Edge Cases

- `dc_get_link_at_index` checks `MAX_LINKS` but not `dc->link_count`, so callers can receive NULL or stale/uninitialized slots for indexes below `MAX_LINKS` but outside active count.
- `dc_submit_i2c` does not bounds-check `link_index` or null-check `dc->links[link_index]`, `link->ddc`, or `ddc->ddc_pin`; callers must validate before use.
- `dc_get_edp_link_panel_inst` returns true for an eDP link even if the pointer was not found in the enumerated eDP list; in that case `inst_out` ends as `edp_num`.
- Service table function pointers are assumed present. Any incomplete `link_srv` implementation can crash through a null function pointer.
- `dc_link_get_highest_encoding_format` has an empty HDMI branch and only classifies DP dongle/TMDS and DP 8b/10b or 128b/132b encodings; HDMI native links return unspecified here.
- The shim should not grow policy. Adding behavior here can split responsibility with `link_srv` and make public API behavior inconsistent.

## Test Signals

- API-level tests can mock `link_srv` and assert each export forwards the exact arguments and returns service results unchanged.
- Boundary tests should cover `dc_get_link_at_index` with `MAX_LINKS`, inactive slots, and valid links; eDP enumeration with NULL links and `MAX_NUM_EDP`; and `dc_get_edp_link_panel_inst` for non-eDP, found eDP, and missing eDP pointer.
- I2C tests should cover OEM-device absent/present and invalid per-link DDC inputs if the caller layer can provide them.
- Encoding tests should cover DP-to-DVI/HDMI dongles, DP 8b/10b, DP 128b/132b, non-DP signals, and native HDMI returning unspecified.
- Runtime signals are mostly service-layer logs/traces: DP trace initialization/logging state, LT timestamps/counts, link-loss counts, HPD IRQ results, FEC decisions, backlight/PSR/Replay/PR state, and bandwidth validation statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_link_exports.c -->
