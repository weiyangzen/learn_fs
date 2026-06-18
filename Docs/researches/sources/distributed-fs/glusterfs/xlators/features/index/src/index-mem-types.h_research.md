# sources/distributed-fs/glusterfs/xlators/features/index/src/index-mem-types.h

## Purpose
Defines translator-specific memory accounting IDs for the index translator.

## Important APIs, Types, and Functions
`enum gf_index_mem_types_` reserves IDs for private state, inode ctx, fd ctx, local frame state, and an end sentinel used by `xlator_mem_acct_init()`.

## Control Flow
There is no control flow; `index.c` uses these constants in allocation calls and memory-accounting initialization.

## State and Persistence
No runtime state. Values must remain unique relative to `gf_common_mt_end`.

## Dependencies and Integration Points
Includes `<glusterfs/mem-types.h>` and feeds GlusterFS memory accounting.

## Risks and Edge Cases
Adding new allocated types without extending this enum reduces accounting precision. Reordering values can disturb diagnostics that rely on stable type names.

## Test Signals
Compile and statedump/mem-accounting checks should show index allocations under these categories.
