<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/barrier/src/barrier-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/barrier/src/barrier-mem-types.h

## Purpose
Memory-accounting type definitions for the barrier translator.

## APIs, Types, and Functions
Defines `gf_barrier_mt_priv_t` for `barrier_priv_t` allocations and `gf_barrier_mt_end` as the memory-accounting bound, starting after common types.

## Control Flow, State, and Persistence
No control flow. Consumed by `mem_acct_init()` and private allocation in `barrier.c`.

## Dependencies and Integration
Includes `glusterfs/mem-types.h` and is a private build header.

## Risks and Test Signals
Risks are missing accounting IDs if more allocation classes are introduced. Test signals are successful memory-accounting initialization and statedump/mem-accounting visibility for barrier private state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/barrier/src/barrier-mem-types.h -->
