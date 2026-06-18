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
