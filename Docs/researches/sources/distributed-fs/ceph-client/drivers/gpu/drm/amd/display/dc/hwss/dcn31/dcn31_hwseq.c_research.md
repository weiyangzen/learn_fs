# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn31/dcn31_hwseq.c

## Purpose
Implements DCN 3.1-specific initialization, memory low-power setup, DSC/HUBP power gating, DP 128b/132b infoframe routing, Z10 save/restore through DMUB, system aperture setup, backend reset, HPO control, static-screen triggers, and enhanced backlight control.

## Important APIs, Types, and Functions
Exports `dcn31_init_hw`, `dcn31_dsc_pg_control`, `dcn31_enable_power_gating_plane`, `dcn31_update_info_frame`, `dcn31_z10_save_init`, `dcn31_z10_restore`, `dcn31_hubp_pg_control`, `dcn31_init_sys_ctx`, `dcn31_reset_hw_ctx_wrap`, `dcn31_setup_hpo_hw_control`, `dcn31_set_static_screen_control`, and `dcn31_set_backlight_level`. Internal helpers include `enable_memory_low_power`, `dcn31_reset_back_end_for_pipe`, and a DMUB backlight command helper.

## Control Flow
Initialization starts clocks, runs golden init/VGA disable when not accelerated, initializes DCCG, applies memory low-power policies for DMCU/OPTC/VGA/MPC/VPG, derives reference clocks, initializes only physical endpoint link encoders, blanks DP displays, enables plane PG, optionally blanks eDP when ODM fast-boot would be unsafe, initializes pipes and self-refresh, initializes audio/panels/ABM/DIO/HPO, enables clock gating, initializes watermarks, notifies WM ranges, sets hard max memclk, releases forced pstate, optionally initializes CRB, and queries DMUB caps. Infoframe updates choose HDMI, HPO DP stream encoder for 128b/132b signals, or legacy stream encoder. Reset walks old pipes from high to low, skips top/ODM secondary pipes, resets backend when streams disappear or require reprogramming, disables DSC/CRTC/OPTC clock, handles TMDS symclk refs, DPMS/audio/resource release, and enters transient link-encoder mode when needed.

## State and Persistence Behavior
Mutates memory power registers, link active/FEC state, hubbub self-refresh/pstate/CRB state, panel/ABM state, HPO top control, DMUB idle-restore state, HUBP/DSC PG registers, GART page-table base programming, pipe stream/resource pointers, audio acquisition, link PHY symclk counters/state, `wa_state.skip_blank_stream`, and `dc->caps.dmub_caps`.

## Dependencies and Integration Points
Depends on DCCG, CLK manager, HUBBUB, TG, HUBP, OPP, MPC, MCIF, ABM, DMUB, link service/HWSS, link encoder config, VPG, I2C, DIO, DMCU, and DCE/DCN10/DCN21 helpers. Integrated by `dcn31_init.c` and inherited by DCN314 for init/reset/Z10/HPO behavior.

## Risks and Test Signals
Risk areas include ODM/eDP fast boot handling, HPO DP metadata routing, Z10 restore-needed optimization, backend reset ordering, smartmux/SPRS DSC disable conditions, dynamic audio release, GART MC-address conversion, PG domain mapping, and HPO register gating under debug flags. Test with DP2/HPO links, eDP seamless/ODM boot, Z10 idle restore, DSC, TMDS symclk, dynamic audio, backlight control including AUX mode, suspend/resume, and link encoder assignment transitions.
