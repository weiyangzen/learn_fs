<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cmpxchg_32.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cmpxchg_32.h

## Purpose
This header supplies SPARC32 compare/exchange and exchange helpers, including emulated behavior for CPUs without native CAS.

## Important APIs, Types, and Functions
It provides `arch_xchg`, `arch_cmpxchg`, and size-specific helpers used by atomics and locks. `CONFIG_EMULATED_CMPXCHG` reflects the architectural limitation that SPARC32 emulation is not completely atomic.

## Control Flow
Callers invoke inline helpers; the implementation performs supported atomic exchange sequences or emulated compare/update paths.

## State and Persistence Behavior
Only caller-provided memory is updated. No header-owned state exists.

## Dependencies and Integration Points
It integrates with atomic operations, futexes, locks, and generic cmpxchg APIs on SPARC32.

## Risks
Code assuming fully atomic CAS can be unsafe on SPARC32. Size handling and alignment constraints must match generic expectations.

## Test Signals
Run cmpxchg/atomic selftests, futex stress, locktorture, and review code paths gated by `EMULATED_CMPXCHG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cmpxchg_32.h -->
