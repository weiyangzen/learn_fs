# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn42/dcn42_init.c

## Purpose
`dcn42_init.c` installs the DCN42 hardware sequencer vtables. It composes DCN42-specific functions with inherited DCN401, DCN35, DCN32, DCN31, DCN30, DCN21, DCN20, DCN10, DCE110, and DCN314 helpers.

## Important APIs and Tables
- `static const struct hw_sequencer_funcs dcn42_funcs` is installed into `dc->hwss`.
- `static const struct hwseq_private_funcs dcn42_private_funcs` is installed into `dc->hwseq->funcs`.
- `dcn42_hw_sequencer_init_functions(struct dc *dc)` performs both assignments.

DCN42 uses its own `init_hw`, `power_down_on_boot`, MPCC update, color histogram, bandwidth prepare/optimize, hardware release, setup stereo, DMUB locks, and driver PG hooks. It reuses many DCN401 implementations for gamut remap, front-end programming, stream enable/unblank, output transfer, link disable, cursor position/offload, DCC propagation wait, FAMS2 update, outstanding updates, pipe change detection, and backend reset. It selects DCN35 implementations for plane enable/disable, DRR, static screen control, idle power optimization, cursor offload management, and root-clock private helpers.

## Control Flow and State Behavior
Like the DCN401 init file, runtime behavior is function-pointer installation. The table contents define which hardware paths are active for the ASIC. Driver PG is exposed through public `hwss` entries (`hw_block_power_up`, `hw_block_power_down`, `root_clock_control`, `calc_blocks_to_gate`, `calc_blocks_to_ungate`) while root-clock primitive helpers are installed in the private table.

## Dependencies and Integration Points
The file integrates DCN42 with the generic DC commit code and with inherited generation implementations. It includes DCN314 specifically for `dcn314_resync_fifo_dccg_dio`, DCN35 for root-clock and power behavior, and DCN401 for most DCN4 base sequencing.

## Risks and Test Signals
The risk profile is vtable composition. A stale inherited function can miss a DCN42 hardware requirement, and a DCN42 override can accidentally bypass sequence variants available in DCN401. Build tests catch type mismatches; runtime tests should verify DCN42 boot, normal modesets, power-down-on-boot, driver PG, root-clock control, PSR/Replay locks, RMCM, stereo, cursor offload, and inherited DCN401 front-end programming.
