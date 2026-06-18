# sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/readdir-ahead-mem-types.h

## Purpose
Defines memory-accounting IDs for the readdir-ahead translator.

## Important APIs, Types, And Functions
`enum gf_rda_mem_types_` names allocations for `rda_local`, fd context, private config, inode context, and the end marker.

## Control Flow
`readdir-ahead.c` calls `xlator_mem_acct_init(this, gf_rda_mt_end)` and uses these IDs for `GF_CALLOC` allocations.

## State And Persistence
No persistent state; the enum labels runtime allocations for diagnostics.

## Dependencies And Integration Points
Includes `glusterfs/mem-types.h` and is included by both `readdir-ahead.h` and `readdir-ahead.c`.

## Risks
Forgetting to add new allocation classes can obscure leak reports. Reordering IDs can confuse long-running diagnostic expectations.

## Test Signals
Memory-accounting init should succeed, and leak/statedump tooling should attribute readdir-ahead locals, fd contexts, private config, and inode contexts correctly.
