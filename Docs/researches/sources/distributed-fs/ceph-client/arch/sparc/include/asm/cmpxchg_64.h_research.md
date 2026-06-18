<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cmpxchg_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cmpxchg_64.h

## Purpose
This header implements SPARC64 native exchange and compare/exchange operations.

## Important APIs, Types, and Functions
It provides size-specific `xchg`/`cmpxchg` helpers, including 64-bit CAS-backed loops and memory-ordering wrappers used by generic atomics.

## Control Flow
Inline assembly attempts the atomic operation and returns the observed or exchanged value, retrying when needed for compound operations.

## State and Persistence Behavior
Only the target memory location changes.

## Dependencies and Integration Points
It underpins atomic APIs, queued locks, refcounts, futexes, and lock-free kernel code on SPARC64.

## Risks
Inline assembly constraints, alignment, and memory barriers are correctness-critical on SMP.

## Test Signals
Run atomic/cmpxchg selftests, qspinlock stress, futex tests, and SMP contention workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cmpxchg_64.h -->
