<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/arbiter/src/arbiter-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/arbiter/src/arbiter-mem-types.h

## Purpose
Memory-accounting type definitions for the arbiter translator.

## APIs, Types, and Functions
Defines `gf_arbiter_mem_types_t`, starting at `gf_common_mt_end + 1`, with `gf_arbiter_mt_inode_ctx_t` for `arbiter_inode_ctx_t` allocations and `gf_arbiter_mt_end` as the accounting upper bound.

## Control Flow, State, and Persistence
No runtime flow. The enum is consumed by `xlator_mem_acct_init()` and `GF_CALLOC()` in `arbiter.c` to classify per-inode context allocations.

## Dependencies and Integration
Includes `glusterfs/mem-types.h` and is listed as a non-installed header in the arbiter build.

## Risks and Test Signals
Risks are enum collisions if the common memory type contract changes or if new allocations are added without new accounting IDs. Test signals are successful `mem_acct_init()` and memory-accounting reports that classify arbiter inode contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/arbiter/src/arbiter-mem-types.h -->
