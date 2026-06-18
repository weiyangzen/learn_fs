# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn30/dcn30_hwseq.c

## Purpose
Implements DCN 3.0 hardware sequencing for color programming/logging, writeback, MMHUBBUB warmup, hardware init, HDMI/DP metadata, MALL idle optimization, bandwidth preparation, hardware release, display test pattern, pending-update waits, and underflow debug snapshots.

## Important APIs, Types, and Functions
Exports `dcn30_log_color_state`, `dcn30_set_blend_lut`, `dcn30_set_input_transfer_func`, `dcn30_program_gamut_remap`, `dcn30_set_output_transfer_func`, `dcn30_update_writeback`, `dcn30_mmhubbub_warmup`, `dcn30_enable_writeback`, `dcn30_disable_writeback`, `dcn30_program_all_writeback_pipes_in_tree`, `dcn30_init_hw`, `dcn30_set_avmute`, `dcn30_update_info_frame`, `dcn30_program_dmdata_engine`, `dcn30_apply_idle_power_optimizations`, `dcn30_does_plane_fit_in_mall`, `dcn30_hardware_release`, `dcn30_set_disp_pattern_generator`, `dcn30_prepare_bandwidth`, `dcn30_wait_for_all_pending_updates`, and `dcn30_get_underflow_debug_data`. The internal `dcn30_set_mpc_shaper_3dlut` manages MPC RMU/3DLUT resources, and `dcn30_set_writeback` configures DWB mux and MCIF arbitration.

## Control Flow
Color input flow sets pre-degamma, translates distributed-point curves, programs DPP gamcor/blend/shaper/3DLUT where supported, and maps stream gamut remap through MPC on top pipes. Output color flow first tries MPC shaper/3DLUT programming and falls back to output gamma. Writeback flow derives MPCC instances for source planes, warms MCIF/VM buffers, configures DWB mux/MCIF buffer/arbitration, and enables, updates, or disables DWB/MCIF blocks. Hardware init initializes clocks/DCCG, golden init/VGA disable in non-accelerated mode, memory low-power defaults, reference clocks, link encoders/FEC state, DP blanking, plane PG, pipe init or powerdown depending on seamless boot, audio, panel/backlight/ABM, DIO memory, clock gating, watermarks, memclk bounds, pstate control, CRB, and DMUB capabilities. MALL idle optimization checks no-memory-request and single-plane eligibility, computes hysteresis timer values, optionally copies cursor through DMUB, sends MALL allow/disallow commands, and rejects unsupported formats, VM planes, PSR, multi-display, or oversized surfaces.

## State and Persistence Behavior
Mutates DPP/MPC color RAM state, RMU ownership, writeback and MCIF state, link active/FEC state, panel stored backlight, ABM state, hubbub self-refresh/pstate/CRB state, clock-manager hard limits, `dc->caps.dmub_caps`, cursor attributes if copied to MALL, and hardware register state for memory/clock gating. It reads `dc->current_state`, `context->bw_ctx`, stream writeback lists, and debug flags heavily.

## Dependencies and Integration Points
Depends on DPP, MPC, DCCG, HUBBUB, HUBP, OPP, TG, DWB, MCIF_WB, ABM, panel control, link service, DMUB service, clock manager, DIO, and DC state helpers. Integrated by `dcn30_init.c` and reused by DCN301, DCN302, DCN303, DCN31, and DCN314 tables.

## Risks and Test Signals
High-risk areas are MALL eligibility/timer math, DMUB command sequencing, RMU acquisition mismatches, writeback MPCC lookup, VM warmup rejecting p_vmid zero, seamless boot powerdown decisions, and clock/pstate handoffs. Test with color LUT/gamut, 3DLUT, writeback enable/update/disable, HDMI AV mute, DP/HDMI infoframes, dynamic metadata, MALL idle entry/exit, cursor cache, headless boot, seamless eDP boot, FEC links, underflow debug capture, and bandwidth transitions including firmware-based MCLK switching.
