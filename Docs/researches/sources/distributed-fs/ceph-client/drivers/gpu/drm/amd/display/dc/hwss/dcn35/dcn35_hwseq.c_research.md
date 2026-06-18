# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn35/dcn35_hwseq.c

## Purpose
`dcn35_hwseq.c` implements DCN 3.5 hardware sequencing on top of inherited DCN32/DCN31 behavior. Its main additions are DCN35 initialization, root-clock gating, block power-gate decisions and sequences, DCN35-specific idle optimization constraints, plane disable/enable handling, ODM/DSC programming differences, DRR/static-screen controls, cursor offload coordination with DMUB, and a TMDS/SYMCLK-aware link disable path.

## Important APIs, types, and functions
- Initialization and boot: `dcn35_init_hw`, `dcn35_power_down_on_boot`, `dcn35_z10_restore`, and `dcn35_init_pipes`.
- Power/clock management: `dcn35_calc_blocks_to_gate`, `dcn35_calc_blocks_to_ungate`, `dcn35_hw_block_power_down`, `dcn35_hw_block_power_up`, `dcn35_root_clock_control`, `dcn35_dpp_root_clock_control`, `dcn35_dpstream_root_clock_control`, `dcn35_physymclk_root_clock_control`, `dcn35_set_dmu_fgcg`, and `dcn35_setup_hpo_hw_control`.
- Plane and pipe operations: `dcn35_enable_plane`, `dcn35_plane_atomic_disable`, `dcn35_disable_plane`, `dcn35_update_odm`.
- Timing/panel features: `dcn35_set_drr`, `dcn35_set_static_screen_control`, `dcn35_set_long_vblank`, and `dcn35_is_dp_dig_pixel_rate_div_policy`.
- Cursor offload: `dcn35_abort_cursor_offload_update`, `dcn35_begin_cursor_offload_update`, `dcn35_commit_cursor_offload_update`, `dcn35_update_cursor_offload_pipe`, `dcn35_notify_cursor_offload_drr_update`, and `dcn35_program_cursor_offload_now`.

## Control flow
`dcn35_init_hw` initializes clocks, BIOS/DMUB golden state, DCCG, reference clocks, physical link encoders, DP/eDP blanking, Hubbub, pipe reset, self-refresh, audio/panel/ABM, DIO memory power, HPO hardware control, clock gating, watermarks, p-state controls, request limits, DMUB capabilities, and PG status. During bandwidth preparation, `dcn35_prepare_bandwidth` computes blocks to ungate, enables root clocks, powers up hardware blocks, then delegates to `dcn20_prepare_bandwidth`. During optimization, `dcn35_optimize_bandwidth` delegates to DCN20 optimization, computes unused blocks to gate, powers them down, and then disables root clocks. Plane disable waits for MPCC disconnect, clears GSL, gates HUBP/DPP clocks, resets blocks, clears pipe resources, and handles phantom OTG disable.

## State and persistence behavior
The file mutates `pg_block_update` masks, hardware PG domains through `pg_cntl`, DCCG root clock state, HUBP/DPP `power_gated` and cursor-offload flags, pipe resource pointers, stream/link active state, DMUB capability fields, ABM/panel state, DIO memory power, HPO control, static screen controls, DRR registers, and DMUB cursor offload shared memory write indices. Power-gating state is persistent across bandwidth optimizations and must be restored by prepare-bandwidth or hardware-release paths.

## Dependencies and integration points
Dependencies include DCE/DCN hwseq helpers, DCCG, Hubbub, HUBP, DPP, OPP, MPC, DSC, timing generator, link services, link encoder config, VPG, I2C, DMUB outbox/shared state, DMCU, panel control, ABM, and `pg_cntl`. `dcn35_init.c` installs these functions into public/private vtables and reuses many DCN32 functions for color and pixel-divider behavior.

## Risks and edge cases
Power sequencing is the highest-risk area. `calc_blocks_to_gate` and `calc_blocks_to_ungate` must match actual resource ownership, especially sequential ONO, DSC-to-HUBP/DPP coupling, phantom pipes, fused pipe counts, HPO, OPTC domain 24, and eDP presence. Cursor offload uses volatile DMUB shared memory and relies on correct write-index ordering. Idle optimization is limited to one active embedded panel using PSR or Replay on link index 0. `should_avoid_empty_tu` blocks DP tunneling pixel-rate division when average pixels per TU are too low. Link disable intentionally preserves SYMCLK for TMDS when OTG still references it.

## Test signals
Test with DCN35 cold boot, accelerated boot, headless boot, seamless eDP, ODM with DSC, fused-pipe variants, idle PSR/Replay entry, IPS/Z10 restore, DP tunneling rates, HPO DP, plane add/remove, phantom pipe disable, cursor offload updates during full pipe programming, hardware release, and repeated bandwidth prepare/optimize cycles while monitoring PG debug logs and underflow counters.
