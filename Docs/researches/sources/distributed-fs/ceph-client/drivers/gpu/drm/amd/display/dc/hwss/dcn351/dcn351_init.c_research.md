# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/dcn351_init.c

## Purpose
`dcn351_init.c` constructs the DCN351 hw sequencer callback tables. It mostly reuses DCN35 behavior, but binds DCN351-specific block gate/ungate and power up/down sequencing.

## Important APIs, types, and functions
The file defines `dcn351_funcs`, `dcn351_private_funcs`, and `dcn351_hw_sequencer_construct`. Public table differences from DCN35 include `dcn351_calc_blocks_to_gate`, `dcn351_calc_blocks_to_ungate`, `dcn351_hw_block_power_up`, `dcn351_hw_block_power_down`, and `dcn32_disable_link_output`. It reuses DCN35 init, boot power-down, bandwidth prepare/optimize, idle optimization, Z10 restore, DRR/static-screen/long-vblank, root-clock control, and HPO setup. Private functions reuse DCN35 pipe init, plane disable/enable, root-clock controls, ODM, and DP pixel policy plus DCN32 color and pixel-divider helpers.

## Control flow
`dcn351_hw_sequencer_construct` assigns the static public and private tables into `dc->hwss` and `dc->hwseq->funcs`. Common DC code then dispatches through these entries for all display sequencing.

## State and persistence behavior
The file persists function-pointer state on the `dc` object. It does not directly program hardware; it decides which implementation will be used later.

## Dependencies and integration points
It includes DCE/DCN helper headers from DCE110 and DCN10/20/21/30/301/31/32/35 plus the local DCN351 header. It integrates DCN351 as a derivative generation while avoiding duplication of most DCN35 logic.

## Risks and edge cases
The deliberate use of `dcn32_disable_link_output` instead of `dcn35_disable_link_output` is a behavioral difference worth testing, especially for TMDS/SYMCLK cases. DCN35 cursor offload callbacks are not present in the DCN351 public table even though many other DCN35 hooks are reused. The private table omits DCN35's `resync_fifo_dccg_dio` binding, so callers must tolerate that or use inherited alternatives.

## Test signals
Build/link validation, DCN351 probe/init, bandwidth gating transitions, link disable on DP/eDP/TMDS, plane enable/disable, ODM/DSC, idle PSR/Replay, and hardware release should confirm the table is coherent for this derivative ASIC.
