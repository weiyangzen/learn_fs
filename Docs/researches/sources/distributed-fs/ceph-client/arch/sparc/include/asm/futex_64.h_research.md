<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/futex_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/futex_64.h

## Purpose
This header implements SPARC64 futex atomic operations on user memory.

## Important APIs, Types, and Functions
It provides `arch_futex_atomic_op_inuser()` and `futex_atomic_cmpxchg_inatomic()` style helpers using SPARC64 inline assembly, exception tables, and user-access checks.

## Control Flow
Futex syscalls request an operation; the helper performs the atomic user-memory update or compare/exchange, captures old values, and returns success or fault/error codes.

## State and Persistence Behavior
State changes are in userspace futex words and kernel futex wait queues managed elsewhere.

## Dependencies and Integration Points
It integrates with generic futex code, SPARC64 user access, exception tables, atomics, and memory barriers.

## Risks
User-memory atomic sequences must be fault-safe and atomic. Exception-table mistakes can oops the kernel on bad user addresses.

## Test Signals
Run futex selftests, robust futex tests, invalid-address fault tests, and high-contention pthread workloads on SPARC64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/futex_64.h -->
