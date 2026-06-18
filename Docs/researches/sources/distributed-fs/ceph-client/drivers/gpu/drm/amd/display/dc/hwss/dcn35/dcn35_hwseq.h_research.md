# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn35/dcn35_hwseq.h

## Purpose
`dcn35_hwseq.h` declares the DCN35 hw sequencer functions that supplement inherited DCN32 behavior and are bound by `dcn35_init.c`.

## Important APIs, types, and functions
The declarations cover DCN35 init, boot power-down, idle optimization, Z10 restore, pipe init, plane enable/disable, ODM, root-clock controls, power-gate mask calculation, power up/down sequencing, DRR/static-screen/long-vblank controls, DP pixel-rate policy, hardware release, cursor offload, HPO control, and link-output disable.

## Control flow
The header has no runtime control flow. It defines callable contracts for public and private hwseq vtables.

## State and persistence behavior
No state is stored in this header. Its functions operate on persistent DC object state, pipe contexts, PG masks, root clock state, DMUB shared memory, and hardware registers in the implementation.

## Dependencies and integration points
It includes `hw_sequencer_private.h`, which supplies callback table structures and core display types. It is consumed by DCN35 init code and by DCN351, which reuses most DCN35 behavior while replacing a subset of power-gating functions.

## Risks and edge cases
The header contains duplicate declarations for `dcn35_dsc_pg_control` and `dcn35_disable_link_output`. It also declares functions such as `dcn35_dsc_pg_control` and `dcn35_enable_power_gating_plane` that are not implemented in the read `dcn35_hwseq.c`, indicating either stale declarations or definitions outside this subset. Build coverage determines whether those declarations are harmless.

## Test signals
Build/link tests should catch missing declarations or definitions. Runtime tests should focus on vtable-bound paths in `dcn35_init.c` and derivative reuse by DCN351.
