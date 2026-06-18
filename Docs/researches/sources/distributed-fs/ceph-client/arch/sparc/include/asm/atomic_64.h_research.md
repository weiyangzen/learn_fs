<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/atomic_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/atomic_64.h

## Purpose
This header implements SPARC64 atomic operations using native compare-and-swap and arithmetic primitives.

## Important APIs, Types, and Functions
It provides `arch_atomic_*` and `arch_atomic64_*` operations, including add/sub/fetch/return/cmpxchg-style helpers with SPARC64 memory-ordering semantics.

## Control Flow
Most operations are inline loops around native atomic instructions and barriers, retrying until the memory update succeeds.

## State and Persistence Behavior
Only the target atomic variables are changed; no persistent global state is held by the header.

## Dependencies and Integration Points
It integrates with generic Linux atomic APIs, queued locks, refcounts, percpu counters, and scheduler synchronization on SPARC64.

## Risks
CAS loop correctness and barrier placement are critical. A wrong constraint or missing memory clobber can create rare SMP data races.

## Test Signals
Run atomic64 selftests, locktorture, refcount tests, KCSAN-style race detection where possible, and SMP stress on SPARC64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/atomic_64.h -->
