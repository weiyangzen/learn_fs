# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/dcn351_hwseq.h

## Purpose
`dcn351_hwseq.h` declares the DCN351-specific power-gating override functions.

## Important APIs, types, and functions
The header exports `dcn351_calc_blocks_to_gate`, `dcn351_calc_blocks_to_ungate`, `dcn351_hw_block_power_up`, and `dcn351_hw_block_power_down`, all using `struct dc`, `struct dc_state`, and `struct pg_block_update`.

## Control flow
There is no runtime control flow in the header. The declarations are bound in `dcn351_init.c`.

## State and persistence behavior
No state is owned here. The declared functions mutate power-gate masks and hardware PG domains in the implementation.

## Dependencies and integration points
It includes `hw_sequencer_private.h` for the relevant structures and callback context. It is consumed by `dcn351_init.c`.

## Risks and edge cases
Signature changes must stay synchronized with `dcn351_hwseq.c` and the hwseq callback table. Since these functions override only power sequencing, incorrect binding would make DCN351 fall back to incompatible DCN35 behavior.

## Test signals
Build/link coverage plus runtime power-gating tests on DCN351 validate this header.
