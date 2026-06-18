# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn10/dcn10_hwseq.h

## Purpose

`dcn10_hwseq.h` declares the DCN10 hardware sequencer interface used by the AMD Display Core hardware sequencing layer. It is the public local contract for DCN10 implementations and for later DCN generations that reuse DCN10 functions.

The header exposes initialization, timing, bandwidth, plane, pipe, color, cursor, power-gating, stream, synchronization, logging, and status helper routines implemented mostly in `dcn10_hwseq.c`, with several DCE110 routines declared because the DCN10 function table composes DCE-era stream/link/audio/backlight helpers.

## Important APIs, Types, And Functions

The central constructor is `dcn10_hw_sequencer_construct(struct dc *dc)`, which installs DCN10 function tables into a `struct dc`.

Timing and update synchronization declarations include `dcn10_get_vupdate_offset_from_vsync`, `dcn10_calc_vupdate_position`, `dcn10_setup_vupdate_interrupt`, `dcn10_enable_stream_timing`, `dcn10_wait_for_pipe_update_if_needed`, `dcn10_set_wait_for_update_needed_for_pipe`, `dcn10_enable_timing_synchronization`, `dcn10_enable_vblanks_synchronization`, `dcn10_enable_per_frame_crtc_position_reset`, `dcn10_set_drr`, `dcn10_get_position`, `dcn10_set_static_screen_control`, and `dcn10_setup_periodic_interrupt`.

Plane and pipe declarations include `dcn10_program_pipe`, `dcn10_update_plane_addr`, `dcn10_update_mpcc`, `dcn10_disable_plane`, `dcn10_plane_atomic_disconnect`, `dcn10_plane_atomic_disable`, `dcn10_plane_atomic_power_down`, `dcn10_disconnect_pipes`, `dcn10_lock_all_pipes`, `dcn10_pipe_control_lock`, `dcn10_cursor_lock`, `dcn10_blank_pixel_data`, `dcn10_post_unlock_program_front_end`, and `dcn10_wait_for_pending_cleared`.

Color declarations include `dcn10_program_gamut_remap`, `dcn10_program_output_csc`, `dcn10_set_output_transfer_func`, `dcn10_set_input_transfer_func`, `dcn10_set_hdr_multiplier`, `dcn10_update_visual_confirm_color`, and `dcn10_reset_surface_dcc_and_tiling`.

Initialization/power declarations include `dcn10_init_hw`, `dcn10_init_pipes`, `dcn10_power_down_on_boot`, `dcn10_reset_hw_ctx_wrap`, `dcn10_hubp_pg_control`, `dcn10_dpp_pg_control`, `dcn10_enable_power_gating_plane`, `dcn10_disable_vga`, `dcn10_bios_golden_init`, `dcn10_dummy_display_power_gating`, `dcn10_update_dchub`, and DCE110 power/audio/link/backlight helpers.

Diagnostics and status declarations include `dcn10_log_hw_state`, `dcn10_get_hw_state`, `dcn10_clear_status_bits`, `dcn10_did_underflow_occur`, `dcn10_wait_for_mpcc_disconnect`, `dcn10_update_pending_status`, `dcn10_get_clock`, `dcn10_set_clock`, `dcn10_get_dcc_en_bits`, and `dcn10_verify_allow_pstate_change_high`.

## Control Flow

The header does not implement control flow, but it shows the expected sequencing surface. Higher layers construct the hw sequencer, then invoke init/power hooks, prepare bandwidth, lock pipes, program stream timing and front-end pipe state, unlock and post-program, optimize bandwidth, and use status/logging hooks around those transitions.

The header also exposes DCE110 functions that are wired into the DCN10 function table, which shows that DCN10 sequencing is not isolated: stream enable/disable, audio, infoframes, link outputs, backlight, and eDP power control are inherited integration points.

## State And Persistence Behavior

All declared functions operate through pointer arguments, primarily `struct dc`, `struct dc_state`, `struct pipe_ctx`, `struct dce_hwseq`, `struct resource_pool`, `struct dc_stream_state`, `struct dc_plane_state`, and link/audio structs. State persistence is therefore in the caller-owned DC state graph, hardware block objects, and hardware registers programmed by the implementation. The header itself has no static data and no storage.

## Dependencies And Integration Points

The header includes `core_types.h` and `hw_sequencer_private.h`, forward declares `struct dc`, and uses many Display Core types from those headers. It is included by DCN10 implementation files and by DCN20 code that reuses DCN10 declarations.

It is tightly integrated with the function-table contracts `struct hw_sequencer_funcs` and `struct hwseq_private_funcs` from the private hw sequencer layer. Any signature change here must match the function table slots and the concrete implementations in DCN10/DCN20/DCE files.

## Risks And Edge Cases

Because this header exposes a broad hardware sequencing ABI inside the driver, signature drift can break multiple generations. The same symbol names are reused in function tables and by later DCN code, so compatibility across DCN10, DCN20, and DCE110 helpers matters.

Several declarations expose low-level operations that assume a valid, fully populated `pipe_ctx`; callers must respect top/bottom pipe and ODM/phantom rules enforced in implementations. The header cannot express those preconditions, so misuse is a runtime risk.

## Test Signals

Build coverage is the first signal: all function declarations must match definitions and function-table assignments. Runtime signals come from mode-set, plane update, stream enable/disable, bandwidth, cursor, color, and power-gating tests that call these functions through `dc->hwss`/`dc->hwseq->funcs`.
