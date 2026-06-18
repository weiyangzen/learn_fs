<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/barrier.h

## Purpose
Defines Xtensa memory barrier primitives and connects them to generic barrier APIs.

## Important APIs, Types, And Functions
Defines `__mb()` as `memw`, `__rmb()` as compiler `barrier()`, `__wmb()` as `__mb()`, SMP barrier aliases, and atomic barrier hooks for S32C1I cores.

## Control Flow
No runtime control beyond inline assembly barriers. On SMP, generic macros use these definitions for inter-CPU ordering.

## State And Persistence
No state. It enforces ordering of memory operations.

## Dependencies And Integration Points
Depends on Xtensa `memw` semantics, core feature macros, and `asm-generic/barrier.h`.

## Risks And Edge Cases
Using compiler-only read barriers assumes Xtensa read ordering is sufficient. Atomic barrier hooks for S32C1I are compiler barriers, so cache/AtomCtl behavior must make atomic ordering correct.

## Test Signals
Run LKMM litmus-style tests where possible, SMP stress tests, lock/atomic tests, and driver DMA ordering tests on real Xtensa SMP hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/barrier.h -->
