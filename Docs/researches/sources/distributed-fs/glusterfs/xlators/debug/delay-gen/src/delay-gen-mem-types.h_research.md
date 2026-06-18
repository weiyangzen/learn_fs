# sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/delay-gen-mem-types.h

## Purpose
This header declares memory accounting IDs for the delay-gen debug translator.

## Important APIs, Types, And Functions
It defines enum `gf_delay_gen_mem_types_` with `gf_delay_gen_mt_dg_t` for the private `dg_t` allocation and `gf_delay_gen_mt_end` for registration.

## Control Flow
No executable control flow exists. `delay-gen.c` passes `gf_delay_gen_mt_end` to `xlator_mem_acct_init()` and uses `gf_delay_gen_mt_dg_t` when allocating private state.

## State And Persistence Behavior
It affects memory accounting labels only and persists no data.

## Dependencies And Integration Points
It includes `<glusterfs/mem-types.h>` and follows translator-local memory type numbering from `gf_common_mt_end + 1`.

## Risks
Adding allocations without corresponding types reduces diagnostic quality. Reordering is low risk for this small debug translator but still should be avoided.

## Test Signals
Translator initialization and memory-accounting dumps should show the delay-gen private allocation under this type.
