# sources/distributed-fs/glusterfs/xlators/features/shard/src/shard-mem-types.h

## Purpose
This header defines memory-accounting categories for the shard translator.

## Important APIs and state
`enum gf_shard_mem_types_` starts at `gf_common_mt_end + 1` and defines categories for private translator state, inode list nodes, inode context, int64 allocations, uint64 allocations, and the terminal `gf_shard_mt_end`.

## Dependencies and integration
It includes `glusterfs/mem-types.h` and is intended for `xlator_mem_acct_init()` plus `GF_CALLOC`/`GF_MALLOC` calls in shard implementation code.

## Risks and test signals
The enum should remain append-only before `gf_shard_mt_end` to preserve accounting consistency. Tests should include shard initialization with memory accounting and allocation-failure paths for each allocation class.
