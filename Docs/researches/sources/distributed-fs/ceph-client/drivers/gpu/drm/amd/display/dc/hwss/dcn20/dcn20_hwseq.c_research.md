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
