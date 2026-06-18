# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn10/dcn10_hwseq.c

## Purpose

`dcn10_hwseq.c` is the DCN 1.0 hardware sequencing implementation for AMD Display Core. It programs the display pipeline at the boundary between abstract `dc_state`/`pipe_ctx` state and hardware blocks such as HUBP, DPP, MPC/MPCC, OPP, OTG timing generators, DCCG, DCHUBBUB, link encoders, audio, ABM, DMCU/DMUB locks, and BIOS display power-gating tables. The file provides the concrete routines installed by `dcn10_init.c` into public `dc->hwss` and private `dc->hwseq->funcs` function tables.

The file covers boot/reset sequencing, plane enable/disable, pipe lock/unlock, bandwidth watermark transitions, transfer-function/color programming, surface flips, cursor programming, timing synchronization, hardware state logging, underflow handling, and several DCN10-specific workarounds.

## Important APIs, Types, And Functions

Primary entry points include `dcn10_init_hw`, `dcn10_init_pipes`, `dcn10_power_down_on_boot`, `dcn10_reset_hw_ctx_wrap`, `dcn10_enable_stream_timing`, `dcn10_program_pipe`, `dcn10_post_unlock_program_front_end`, `dcn10_prepare_bandwidth`, and `dcn10_optimize_bandwidth`.

Plane lifecycle APIs include `dcn10_plane_atomic_disconnect`, `dcn10_plane_atomic_disable`, `dcn10_plane_atomic_power_down`, `dcn10_disable_plane`, and the internal `dcn10_enable_plane`. These manipulate MPC trees, MPCC instances, DPP/HUBP clocks and power gates, HUBP blanking, `pipe_ctx` pointers, and `dc->optimized_required`.

Programming APIs include `dcn10_update_plane_addr`, `dcn10_update_mpcc`, `dcn10_program_gamut_remap`, `dcn10_program_output_csc`, `dcn10_set_input_transfer_func`, `dcn10_set_output_transfer_func`, `dcn10_set_hdr_multiplier`, and the internal `dcn10_update_dchubp_dpp`. They translate `dc_plane_state` and `dc_stream_state` into HUBP/DPP/MPC/OPP register programming.

Timing and synchronization APIs include `dcn10_get_vupdate_offset_from_vsync`, `dcn10_calc_vupdate_position`, `dcn10_setup_vupdate_interrupt`, `dcn10_wait_for_pipe_update_if_needed`, `dcn10_set_wait_for_update_needed_for_pipe`, `dcn10_enable_timing_synchronization`, `dcn10_enable_vblanks_synchronization`, and `dcn10_enable_per_frame_crtc_position_reset`.

Power and boot helpers include `dcn10_enable_power_gating_plane`, `dcn10_dpp_pg_control`, `dcn10_hubp_pg_control`, `dcn10_disable_vga`, `dcn10_bios_golden_init`, `apply_DEGVIDCN10_253_wa`, `undo_DEGVIDCN10_253_wa`, and `dcn10_verify_allow_pstate_change_high`.

Diagnostics include `dcn10_log_hw_state`, `dcn10_get_hw_state`, `dcn10_clear_status_bits`, `dcn10_did_underflow_occur`, and many static log helpers that read HUBBUB, HUBP, DPP, MPC, OTG, DSC, stream encoder, link encoder, HPO, and clock state.

The implementation operates mainly on `struct dc`, `struct dc_state`, `struct pipe_ctx`, `struct dc_stream_state`, `struct dc_plane_state`, `struct dce_hwseq`, `struct resource_pool`, `struct hubp`, `struct dpp`, `struct mpc`, `struct timing_generator`, `struct output_pixel_processor`, and clock/link/BIOS service structs reached through function tables.

## Control Flow

Initialization starts in `dcn10_init_hw`. It initializes clocks, aligns current bandwidth context with live clock manager values on resume, initializes DCCG, disables VGA when not in accelerated mode, runs BIOS golden init unless DMUB optimized init already did it, derives reference clocks from BIOS firmware info, initializes link encoders and active link status, blanks DP displays, enables plane power gating, optionally resets all pipes, initializes audio/panel/ABM/DMCU, powers AFMT memory, enables DCN clock gating, and notifies watermark ranges.

`dcn10_init_pipes` performs the destructive pipe cleanup path. It blanks enabled timing generators, resets DET allocation, resets MPC instances, builds temporary current-state pipe resource bindings, disconnects MPCCs, disables planes, initializes ODM if available, resets timing generators, and optionally powers down DSCs that are not tied to an already-running DSC-enabled OPTC. Seamless boot paths skip pipes that are intentionally preserved.

Mode-set backend programming uses `dcn10_enable_stream_timing` to enable OPTC clock, program pixel clock, update HDMI TMDS symclk state, program timing/global-sync parameters, set blank color, blank if needed, and enable the CRTC. `dcn10_reset_hw_ctx_wrap` walks old pipes in reverse and calls `dcn10_reset_back_end_for_pipe` when a stream disappears or requires reprogramming.

Frontend programming uses `dcn10_program_pipe`. For top pipes, it programs global sync and VTG params, sets vupdate interrupt, and blanks/unblanks based on pipe-tree visibility. Full updates enable plane resources. `dcn10_update_dchubp_dpp` then programs DPP clock DTO, HUBP VTG and RQ/DLG/TTU, DPP input CSC/bias/scaler, MPCC blending, viewport, cursor, gamut/output CSC, surface config, surface address, and HUBP blanking. Transfer functions are programmed afterward.

Plane disable is split into double-buffered disconnect and final power down. `dcn10_plane_atomic_disconnect` removes the MPCC from the OPP MPC tree and marks disconnect pending unless the pipe is a SubVP phantom. `dcn10_plane_atomic_disable` waits for MPCC disconnect, disables HUBP/DPP/OPP clocks, marks the HUBP power gated, calls power down, and clears the pipe context resource pointers. `dcn10_post_unlock_program_front_end` handles disabled pipes after the unlock point and re-optimizes bandwidth if any plane was disabled.

Bandwidth sequencing is two-phase. `dcn10_prepare_bandwidth` verifies p-state allow-high under sanity checks, sets required clocks before programming, programs DCHUBBUB watermarks and compbuf changes, and may apply stereo frame-packing workarounds. `dcn10_optimize_bandwidth` applies optimized watermarks/clock values after front-end updates and clears or applies workaround state.

Timing synchronization can use reset triggers (`dcn10_enable_timing_synchronization`), vblank alignment with DP DTO override (`dcn10_enable_vblanks_synchronization`), or per-frame CRTC position reset. The code temporarily expands DPG dimensions to avoid visible artifacts while triggers align OTGs, then restores dimensions.

## State And Persistence Behavior

The file mutates live hardware state through register helper macros and block function tables. Persistent software state is stored in `dc->current_state`, pending `dc_state` contexts, `pipe_ctx` fields, `stream` status flags, `plane_state->status`, `dc->clk_mgr->clks`, `dc->optimized_required`, `hubp->power_gated`, `hubp->opp_id`, `hubp->mpcc_id`, `opp->mpc_tree_params`, `opp->mpcc_disconnect_pending`, and hardware sequencer workaround state under `hws->wa_state`.

Surface flip state is mirrored into `plane_state->status.requested_address` and, for immediate flips, `current_address`. Stereo side-by-side/top-and-bottom split programming temporarily patches the left address and restores it after the HUBP programming call.

`dcn10_wait_for_pipe_update_if_needed` and `dcn10_set_wait_for_update_needed_for_pipe` persist short-lived wait metadata in `pipe_ctx->next_vupdate`, `pipe_ctx->wait_frame_count`, and `pipe_ctx->wait_is_required` so consecutive updates do not program before prior double-buffered changes latch.

Power state is tracked both in hardware power-gating registers and software flags. `apply_DEGVIDCN10_253_wa` can deliberately ungate HUBP0 and mark `DEGVIDCN10_253_applied` so stutter can work when all pipes are power-gated; `undo_DEGVIDCN10_253_wa` reverses that state before enabling a plane.

The file does not persist to disk. Its persistence scope is hardware registers, firmware/BIOS service state, in-memory DC resource state, and debug/log output.

## Dependencies And Integration Points

This file depends on the AMD Display Core resource model and hardware block abstraction: DCE/DCN hwseq, DPP, HUBP, HUBBUB, MPC, OPP, timing generator, DCCG, clock manager, DMCU, ABM, link service, BIOS command tables, DMUB hardware lock manager, DMUB PSR/outbox support, and VM helpers. It also uses Linux delay primitives `udelay`/`fsleep`, register helper macros, and DC logging/trace macros.

It integrates upward through `dcn10_hwseq.h` declarations and the function-table wiring in `dcn10_init.c`. Higher-level DC commit paths call these hooks through `dc->hwss` and `dc->hwseq->funcs` rather than directly depending on DCN10 symbols. DCN20 reuses or overrides many of these behaviors, and `dcn10_init.c` already points `program_front_end_for_ctx` at the DCN20 implementation.

Link integration includes DP/HDMI/TMDS symclk tracking, stream encoder and link encoder state reads, DP display blanking, DP DTO/pixel-clock alignment, eDP backlight and power control hooks inherited from DCE110, and DPCD/link service helpers.

Color integration includes `cm_helper_translate_curve_to_hw_format`, `cm_helper_translate_curve_to_degamma_hw_format`, color-space black-color conversion, DPP gamut/CSC/gamma functions, MPC background color for visual confirmation, and DC caps reporting.

## Risks And Edge Cases

Ordering is the largest risk. MPCC disconnect must complete before clocks and power gates are disabled, double-buffered updates must latch before subsequent immediate updates, and bandwidth clocks/watermarks must be raised before demanding programming and lowered only after safe completion.

Several routines assume instance identity between pipe index, HUBP, DPP, and MPCC. Comments call out that MPCC selection currently uses `hubp->inst` and that resume/BIOS state can leave MPCC0 non-idle. Hardware variants with irregular front-end mappings could break these assumptions.

Timing math is sensitive to integer division, low refresh rates, YCbCr420 pixel packing, ODM segment count, and vupdate wrap-around. Incorrect timing can cause missed vupdates, cursor update stalls, blanking artifacts, or non-synchronizable pixel clocks.

Power-gating code has ASIC-specific register domains and wait timeouts. Missing registers are guarded in some places, but unexpected instance ids hit `BREAK_TO_DEBUGGER`. The DCN10 DEGVIDCN workarounds deliberately keep or toggle hardware blocks in unusual states and can affect stutter/p-state behavior.

`dcn10_hw_wa_force_recovery` appears suspicious: the comments describe toggling HUBP disable and blank enable back to zero, but the visible code calls `hubp_disable_control(hubp, true)` and `set_hubp_blank_en(hubp, true)` in both phases. That may be intentional for this tree's code snapshot, but it is a test/review point because it reads like a potential workaround implementation typo.

Color and MPO behavior has explicit DCN1 limitations: output color management occurs before MPC blending, requiring a rear MPO brightness-bias workaround for RGB color spaces. Regressions here can produce visible brightness or alpha artifacts.

## Test Signals

Useful validation signals are successful boot/resume with and without seamless eDP boot, multi-monitor enable/disable, DPMS transitions, hotplug/unplug, plane add/remove, MPO with per-pixel/global alpha, immediate and vsync flips, cursor movement during viewport changes, eDP backlight power sequencing, dynamic audio allocation, and TMDS/DP stream enable paths.

Hardware logs from `dcn10_log_hw_state`, underflow checks from `dcn10_did_underflow_occur`, `TRACE_DC_PIPE_STATE`, MPCC disconnect pending flags, OTG update-pending behavior, DPG blank state, p-state allow-high verification, and DC sync logs are important observability points.

Stress tests should cover bandwidth downclock/upclock transitions, p-state/stutter enablement, SubVP phantom skip paths, DSC power-gating skip logic, stereo SBS/TB address patching, vblank synchronization across displays, low refresh rate modes, YCbCr420, and high-frequency surface-only updates where `fsleep` may be skipped to avoid high-IRQL stalls.
