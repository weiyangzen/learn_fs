# Research: subset-b-001441

Grouped research report for the DCN10/DCN20 AMD Display Core hardware sequencer files in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn10/dcn10_hwseq.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn10/dcn10_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn10/dcn10_hwseq.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn10/dcn10_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn10/dcn10_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn10/dcn10_init.c

## Purpose

`dcn10_init.c` wires the DCN10 hardware sequencer into the Display Core object model. It builds two static function tables: the public `hw_sequencer_funcs` installed as `dc->hwss`, and the private `hwseq_private_funcs` installed as `dc->hwseq->funcs`.

This file is the generation-specific dispatch layer for DCN10. It does little direct hardware work itself; its importance is deciding which implementation functions are used for mode-set, plane updates, power, color, timing, link, audio, logging, and diagnostics.

## Important APIs, Types, And Functions

`dcn10_hw_sequencer_construct(struct dc *dc)` is the only exported function defined here. It copies `dcn10_funcs` into `dc->hwss` and `dcn10_private_funcs` into `dc->hwseq->funcs`.

`dcn10_funcs` maps high-level hooks such as `init_hw`, `power_down_on_boot`, `apply_ctx_to_hw`, `program_front_end_for_ctx`, `post_unlock_program_front_end`, `update_plane_addr`, `program_output_csc`, `pipe_control_lock`, `interdependent_update_lock`, `prepare_bandwidth`, `optimize_bandwidth`, timing sync, stream/audio/link control, logging, cursor, clock, underflow, DCC, and visual confirm to DCN10/DCE/DCN20 routines.

`dcn10_private_funcs` maps lower-level sequencing hooks such as `init_pipes`, `plane_atomic_disconnect`, `program_pipe`, `update_mpcc`, transfer functions, power-down, blanking, reset, stream timing, vupdate interrupt, underflow, VGA disable, BIOS golden init, plane atomic power, plane power gating, DPP/HUBP power gating, HDR multiplier, and p-state verification.

## Control Flow

The construction path is simple: resource construction code calls `dcn10_hw_sequencer_construct`, after which all later DC code invokes operations indirectly through function tables. There are no branches in the constructor itself.

The table composition is meaningful. DCN10 uses `dce110_apply_ctx_to_hw`, `dce110_enable_accelerated_mode`, stream/audio/link/backlight helpers from DCE110, and `dcn20_program_front_end_for_ctx` for front-end programming. This means DCN10 dispatch is a hybrid rather than a file-local implementation set.

## State And Persistence Behavior

The file mutates only the `struct dc` function-table fields. After construction, those function pointers persist for the lifetime of the `dc` instance and determine all hardware sequencing behavior for that device. There is no dynamic allocation, file I/O, register programming, or persistent data in this file.

Several slots are explicitly set to `NULL`, such as `apply_ctx_for_surface`, private stream gating hooks, `init_blank`, and DSC power-gating control. Callers must guard optional hooks before invocation or use generation-specific fallbacks.

## Dependencies And Integration Points

The file includes `hw_sequencer_private.h`, `dce110/dce110_hwseq.h`, `dcn10/dcn10_hwseq.h`, and `dcn20/dcn20_hwseq.h`. The `dcn20` dependency is notable because DCN10's public `program_front_end_for_ctx` hook points to `dcn20_program_front_end_for_ctx`, implying a shared or backported front-end sequencing path.

It integrates with all higher-level Display Core commit code through `dc->hwss` and private hwseq dispatch. A mismapped function pointer changes runtime behavior globally for the generation.

## Risks And Edge Cases

The largest risk is table mismatch: a hook may point to a routine with subtly different assumptions than the DCN10 resource set. For example, a DCN20 front-end routine includes ODM/SubVP/update-flag concepts that must remain compatible with the DCN10 configuration it is used for in this tree.

Optional `NULL` hooks require careful checks throughout the call sites. Adding a new caller that assumes a hook is present can break DCN10.

Because many hooks are inherited from DCE110, changes in older shared helpers can affect DCN10 even if DCN10 implementation files are untouched.

## Test Signals

Build tests catch signature mismatches. Runtime smoke tests should confirm that construction occurs before any mode-set path and that every important hook invoked by DCN10 commit flows is non-NULL or intentionally guarded. Mode-set, plane update, link output, audio, cursor, color, bandwidth, and suspend/resume tests validate that the chosen cross-generation function mix is coherent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn10/dcn10_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn10/dcn10_init.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn10/dcn10_init.h

## Purpose

`dcn10_init.h` is a small construction header for the DCN10 hardware sequencer. It exposes the constructor needed by resource or device initialization code without pulling in the full DCN10 hardware sequencing declaration surface.

## Important APIs, Types, And Functions

The header forward declares `struct dc` and declares `void dcn10_hw_sequencer_construct(struct dc *dc);`.

## Control Flow

There is no implemented control flow. The header supports the initialization control flow where a caller builds or owns a `struct dc`, calls the constructor, and then uses the installed hw sequencing function tables.

## State And Persistence Behavior

The header itself stores no state. The declared constructor mutates `dc->hwss` and `dc->hwseq->funcs` in `dcn10_init.c`; that function-table state persists for the lifetime of the `dc` object.

## Dependencies And Integration Points

It intentionally depends only on a forward declaration of `struct dc`, keeping include coupling low. It is the narrow integration point for code that only needs to construct DCN10 sequencing and does not need the full list of individual DCN10 hwseq functions from `dcn10_hwseq.h`.

## Risks And Edge Cases

The guard macro name `__DC_DCN10_INIT_H__` prevents multiple inclusion. The main risk is constructor availability: if the implementation or symbol export changes, generation initialization code fails at compile/link time.

## Test Signals

Compiler and linker coverage verify the declaration matches the definition. Runtime display initialization tests verify that the constructor is called and that `dc->hwss`/`dc->hwseq->funcs` are populated before use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn10/dcn10_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn20/dcn20_hwseq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn20/dcn20_hwseq.c

## Purpose

`dcn20_hwseq.c` implements DCN 2.0 hardware sequencing extensions and overrides for AMD Display Core. It builds on DCN10 concepts but adds DCN20-specific support for GSL-based immediate-flip synchronization, ODM combine, DSC power gating, DPP/HUBP/DSC domains up to six instances, DPG blanking through OPP, writeback, DMData, virtual/system address context setup, DCCG stream clock programming, DP 128b/132b/HPO handling, SubVP/phantom pipe handling, MALL/SubVP state interactions, and richer color LUT programming.

The file supplies public and private hooks declared in `dcn20_hwseq.h` and is also partially reused by the DCN10 constructor for front-end programming in this code snapshot.

## Important APIs, Types, And Functions

Front-end programming is centered on `dcn20_program_front_end_for_ctx`, static `dcn20_program_pipe`, `dcn20_detect_pipe_changes`, `dcn20_update_dchubp_dpp`, `dcn20_post_unlock_program_front_end`, and `dcn20_post_unlock_reset_opp`. These compute granular update flags, disconnect old MPCCs, program only changed blocks, defer phantom-pipe programming when needed, and complete post-unlock cleanup.

Stream timing and output control include `dcn20_enable_stream_timing`, `dcn20_enable_stream`, `dcn20_unblank_stream`, `dcn20_reset_back_end_for_pipe`, `dcn20_reset_hw_ctx_wrap`, `dcn20_setup_vupdate_interrupt`, and `dcn20_blank_pixel_data`.

Plane lifecycle APIs include `dcn20_enable_plane`, `dcn20_plane_atomic_disable`, `dcn20_disable_plane`, `dcn20_disable_pixel_data`, `dcn20_update_plane_addr`, and `dcn20_update_mpcc`.

Power-gating and initialization APIs include `dcn20_enable_power_gating_plane`, `dcn20_dpp_pg_control`, `dcn20_hubp_pg_control`, `dcn20_dsc_pg_control`, `dcn20_dccg_init`, `dcn20_disable_vga`, `dcn20_init_blank`, `dcn20_wait_for_blank_complete`, and `dcn20_fpga_init_hw`.

Color APIs include `dcn20_log_color_state`, `dcn20_program_output_csc`, `dcn20_set_output_transfer_func`, `dcn20_set_input_transfer_func`, `dcn20_set_blend_lut`, and `dcn20_set_shaper_3dlut`. Compared with DCN10, output gamma moves to MPC and input programming adds blend LUT, shaper LUT, and 3D LUT support.

Bandwidth and memory APIs include `dcn20_prepare_bandwidth`, `dcn20_optimize_bandwidth`, `dcn20_update_bandwidth`, `dcn20_init_vm_ctx`, `dcn20_init_sys_ctx`, and SubVP surface-address save calls inside `dcn20_update_dchubp_dpp`.

Auxiliary features include `dcn20_program_triple_buffer`, `dcn20_setup_gsl_group_as_lock`, `dcn20_set_flip_control_gsl`, `dcn20_update_odm`, `dcn20_enable_writeback`, `dcn20_disable_writeback`, `dcn20_dmdata_status_done`, `dcn20_set_dmdata_attributes`, `dcn20_program_dmdata_engine`, `dcn20_disable_stream_gating`, `dcn20_enable_stream_gating`, and `dcn20_set_disp_pattern_generator`.

## Control Flow

`dcn20_enable_stream_timing` programs DCCG pixel-rate dividers, configures ODM combine when multiple OPP heads serve one OTG, enables the OPTC clock, programs pixel clock, handles DP 128b/132b DTBCLK DTO setup, updates TMDS symclk state, applies optional platform workarounds, programs OTG timing, sets MPC output rate control for ODM/two-pixels-per-container/interlace cases, enables OPP pipe clocks and extra-pixel programming, blanks through DPG, enables CRTC, delays a frame, applies DRR/static-screen controls, and finalizes phantom CRTC enable for SubVP phantom pipes.

`dcn20_program_front_end_for_ctx` starts by logging topology changes and disabling triple buffer for full updates when configured. It counts active HUBPs, may force p-state change control during first enable, computes per-pipe update flags with `dcn20_detect_pipe_changes`, turns on phantom OTGs before disabling phantom pipes, blanks top/ODM-master pipes being disabled, disconnects MPCCs for disabled or OPP-changed pipes, pre-updates ODM for blanked OTG masters, then programs all top-to-bottom pipe chains. It separately handles writeback trees and an MPO transition read-start workaround.

`dcn20_detect_pipe_changes` is the diff engine. It compares old and new `pipe_ctx` values and sets flags for disable, enable, ODM topology change, SubVP phantom transitions, plane changes, global sync, DET size, OPP/TG changes, MPCC changes, DPPCLK, scaler, viewport, HUBP interdependent timing, RQ/DLG/TTU, unbounded requests, and test pattern changes. Later programming paths rely on these flags for minimal hardware updates.

`dcn20_program_pipe` uses those flags to blank/unblank OTG masters, program global sync/TG, update ODM, enable plane resources, program DET size, update HUBP/DPP/MPC state, HDR multiplier, input/output transfer functions, OPP formatter, ABM pipe association, and test pattern generation.

`dcn20_update_dchubp_dpp` performs the detailed block programming. It gates DPPCLK when needed, updates DTO on enable, programs HUBP VTG/RQ/DLG/TTU using either `hubp_setup2`/`hubp_setup_interdependent2` or older helpers, sets unbounded requesting, programs DPP setup and cursor matrix, bias/scale, MPCC blending, scaler, viewport, mcache split, cursor, gamut/output CSC, surface config, MALL/SubVP surface address save, plane address, HUBP unblank, and phantom post-enable hooks.

`dcn20_post_unlock_program_front_end` waits for OPP heads that were removed, disables old planes, waits for flip pending to clear on newly enabled non-phantom pipes, waits for ODM slice-count increases to latch before clocks can be reduced, releases p-state force, programs deferred phantom pipes, updates forced p-state/MALL configuration, applies DEDCN21 workaround, and optionally disables self-refresh during MPO transitions.

Bandwidth sequencing calls clock-manager and HUBBUB hooks. `dcn20_prepare_bandwidth` raises/programs clocks, temporarily inflates SubVP p-state watermark values for programming, programs watermarks and possibly decreases compbuf size. `dcn20_optimize_bandwidth` programs optimized watermarks, handles softmax memory clock, increases compbuf size, delegates firmware-based MCLK switching to DMUB when needed, updates clocks, and may program extended blank for z-state support.

## State And Persistence Behavior

The file persists state in `pipe_ctx->update_flags`, `stream_res.gsl_group`, `dc->res_pool->gsl_groups`, `hubp->power_gated`, `hubp->opp_id`, `hubp->mpcc_id`, `opp->mpc_tree_params`, `opp->mpcc_disconnect_pending`, `dc->optimized_required`, `dc->clk_mgr->clks`, `context->bw_ctx`, `link->phy_state`, `stream` adjustment and metadata fields, writeback resource state, and workaround state under `dc->hwseq->wa_state`.

GSL group allocation is stateful. `dcn20_setup_gsl_group_as_lock` finds a free group, stores the group as a one-based value in `pipe_ctx->stream_res.gsl_group`, marks the corresponding `dc->res_pool->gsl_groups` slot in use, and programs TG GSL registers. It frees that state on disable or vsync flip transition.

Surface address state is mirrored into `plane_state->status` like DCN10, with the additional call to `vm_helper_mark_vmid_used` so VMID usage is tracked per HUBP. SubVP main pipes save surface addresses through a DMUB block sequence for MALL/SubVP behavior.

Bandwidth functions temporarily mutate SubVP watermark values in `context->bw_ctx` and then restore them where needed so DMCUB receives the original value. Firmware-based MCLK switching updates both `context->bw_ctx.bw.dcn.clk.p_state_change_support` and `dc->clk_mgr->clks.fw_based_mclk_switching`.

No disk persistence is performed. Hardware registers and in-memory DC resource state are the persistence surfaces.

## Dependencies And Integration Points

The file includes DCN20 resource/DSC/OPTC headers, DCE hwseq, DCN10 color/hubbub helpers, DCCG, ABM, DMCU, HUBP, OPP, IPP, MPC, MCIF writeback, VM helper, DMUB hardware lock manager, link encoder config, link hardware sequencing, link service, and private DC state helpers. It uses Linux delays and Display Core register/logging macros.

It integrates upward through `dcn20_hwseq.h` and generation-specific function tables in other init files. It also integrates downward with block-specific function tables, so behavior depends heavily on optional hooks such as `hubp_setup2`, `set_out_rate_control`, `set_dtbclk_dto`, `set_odm_combine`, `dsc_pg_control`, `dmdata_set_attributes`, `phantom_hubp_post_enable`, and many DCCG methods.

Link integration is broader than DCN10: it handles DP HPO/128b132b stream encoder unblanking, DTBCLK DTO and stream clock setup, PHYD32 clock source selection from link encoder transmitter, USB4 DPIA symclk disable corner cases, and standard DP stream encoder ODM combine setup.

## Risks And Edge Cases

The update-flag diff model is powerful but risky: missing a flag means a changed hardware block will not be reprogrammed; setting too many flags can cause unnecessary programming and flicker/underflow. SubVP phantom transitions are especially delicate and are explicitly deferred to avoid MPO transition underflow.

GSL group handling has limited resources and uses ASSERTs for no-free-group cases. Failure to clear `stream_res.gsl_group` or `res_pool->gsl_groups` can leak synchronization groups or leave immediate-flip behavior wrong.

Power-gating domains have ASIC-specific exceptions. DPP5 and HUBP5 are deliberately not power-gated because the hardware feature is disabled and may hard reset if used. Optional DOMAIN8-11 and DOMAIN19-21 register presence is checked inconsistently depending on path.

ODM and DTBCLK programming depend on correct OPP head enumeration, slice widths, pixel-rate dividers, and segment counts. Incorrect ordering around ODM slice-count increases can allow clocks to drop before double-buffered hardware catches up.

DMData programming disables generic HDR static metadata infoframe validity when dynamic metadata is used. Bugs here can break HDR metadata delivery or cause HDMI/DP mode-specific metadata size mistakes.

`dcn20_update_dchubp_dpp` has many nested update conditions mixing pipe, plane, and stream flags. Tests need to cover current-state in-place updates because viewport programming has special handling when `context == dc->current_state`.

## Test Signals

Key runtime signals are clean full modesets, fast plane updates, immediate flip with pipe split, GSL enable/disable transitions, ODM combine/bypass changes, SubVP main/phantom enable and disable, MALL address save, DSC enable/disable/power gate, writeback enable/disable, dynamic metadata, DP HPO/128b132b, USB4 DPIA link behavior, and DPP/HUBP power gating on six-pipe ASICs.

Debug signals include color state logs, MPCC tree state, DPG pending/blank state, hubp flip pending waits, OPTC double-buffer pending waits, p-state force state, compbuf/watermark programming, VMID marking, DCCG DTO/symclk programming, and underflow/DET warnings during MPO or phantom transitions.

Regression tests should include suspend/resume, first pipe enable from zero active HUBPs, active stream disable, eDP backlight unblank, multi-plane alpha composition, PQ and distributed point transfer functions, 3D LUT/shaper/blend LUT, test pattern changes, and bandwidth recalculation via `dcn20_update_bandwidth`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn20/dcn20_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn20/dcn20_hwseq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn20/dcn20_hwseq.h

## Purpose

`dcn20_hwseq.h` declares the DCN20 hardware sequencing interface. It extends the DCN10 sequencing surface with DCN20-specific hooks for advanced color pipelines, ODM, DSC power gating, writeback, DMData, VM/system aperture setup, GSL flip synchronization, DCCG initialization, DPG blanking, and display pattern generation.

The header is the local contract between DCN20 implementation files, generation initialization tables, and cross-generation users such as the DCN10 init table that references `dcn20_program_front_end_for_ctx`.

## Important APIs, Types, And Functions

Color and transfer declarations include `dcn20_log_color_state`, `dcn20_set_blend_lut`, `dcn20_set_shaper_3dlut`, `dcn20_set_input_transfer_func`, `dcn20_set_output_transfer_func`, and `dcn20_program_output_csc`.

Front-end and plane declarations include `dcn20_program_front_end_for_ctx`, `dcn20_post_unlock_program_front_end`, `dcn20_update_plane_addr`, `dcn20_update_mpcc`, `dcn20_disable_plane`, `dcn20_plane_atomic_disable`, `dcn20_enable_plane`, `dcn20_update_dchubp_dpp`, `dcn20_update_odm`, `dcn20_detect_pipe_changes`, and `dcn20_post_unlock_reset_opp`.

Stream/timing declarations include `dcn20_enable_stream`, `dcn20_unblank_stream`, `dcn20_enable_stream_timing`, `dcn20_setup_vupdate_interrupt`, `dcn20_reset_back_end_for_pipe`, `dcn20_reset_hw_ctx_wrap`, `dcn20_init_blank`, `dcn20_wait_for_blank_complete`, and `dcn20_set_disp_pattern_generator`.

Power, bandwidth, and initialization declarations include `dcn20_enable_power_gating_plane`, `dcn20_dpp_pg_control`, `dcn20_hubp_pg_control`, `dcn20_dsc_pg_control`, `dcn20_disable_vga`, `dcn20_prepare_bandwidth`, `dcn20_optimize_bandwidth`, `dcn20_update_bandwidth`, `dcn20_dccg_init`, `dcn20_fpga_init_hw`, `dcn20_init_vm_ctx`, and `dcn20_init_sys_ctx`.

Feature-specific declarations include `dcn20_program_triple_buffer`, `dcn20_enable_writeback`, `dcn20_disable_writeback`, `dcn20_dmdata_status_done`, `dcn20_program_dmdata_engine`, `dcn20_set_dmdata_attributes`, `dcn20_set_flip_control_gsl`, `dcn20_setup_gsl_group_as_lock`, `dcn20_disable_stream_gating`, and `dcn20_enable_stream_gating`.

## Control Flow

The header does not implement control flow, but the declared API set reveals the DCN20 commit sequence: detect pipe changes, pre-disconnect/blank old resources, program updated pipe chains, defer selected post-unlock work, disable old planes, then optimize clocks/watermarks. It also separates stream timing, stream enable, and stream unblank paths.

The presence of `dcn20_update_bandwidth` shows a mid-commit recalculation path that validates bandwidth, prepares bandwidth, and refreshes HUBP timing registers without a full front-end reconstruction.

## State And Persistence Behavior

All functions operate on caller-provided DC state and hardware block objects. Persistent effects are in hardware registers and in-memory structures such as `pipe_ctx`, `dc_state`, resource pools, VM configs, writeback info, and link/stream state. The header itself has no storage.

Several declarations expose optional generation hooks that function tables may install or leave absent depending on ASIC generation. Callers must preserve optional-hook checks.

## Dependencies And Integration Points

The header includes `hw_sequencer_private.h`, which provides the core Display Core hardware sequencing types. Its declarations reference DC pipe, stream, state, writeback, virtual address, physical address, timing, color, and pattern-generator types provided by the broader DC include graph.

It integrates with generation init files that populate `dc->hwss` and `dc->hwseq->funcs`, with DCN10/DCN20 implementation reuse, and with downstream block drivers for HUBP, DPP, MPC, OPP, DCCG, DSC, DWB/MCIF, DMData, and link encoders.

## Risks And Edge Cases

The header exposes many specialized hooks with subtle preconditions, such as valid writeback pipe instances, nonzero VMIDs for virtual context setup, OTG-master-only ODM updates, pipe-split immediate flip GSL setup, and phantom/SubVP pipe semantics. Incorrect call ordering can cause underflow, missed double-buffer latching, or power-gating faults.

Because this header is a cross-file ABI within the driver, signature changes require synchronized edits in implementations and function-table assignments. Adding a new implementation hook without updating generation tables can leave NULL behavior in mode-set paths.

## Test Signals

Compile coverage verifies declaration/definition consistency. Runtime coverage should exercise each category of hook through DCN20 modesets: stream timing/unblank, plane enable/disable, pipe-split immediate flips, ODM changes, DSC gating, writeback, DMData, bandwidth updates, VM context initialization, color LUTs, and display test patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn20/dcn20_hwseq.h -->
