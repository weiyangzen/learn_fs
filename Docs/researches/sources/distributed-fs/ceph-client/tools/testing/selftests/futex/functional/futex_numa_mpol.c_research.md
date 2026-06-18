<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_numa_mpol.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_numa_mpol.c

## Purpose
This kselftest verifies futex2 NUMA node initialization, memory boundary validation, and optional memory-policy-derived node hints.

## Important APIs, Types, And Functions
It defines `thread_lock_fn()`, `create_max_threads()`, `join_max_threads()`, `__test_futex()`, `test_futex()`, and `TEST(futex_numa_mpol)`. It uses `struct futex32_numa`, `futex2_wait()`, `futex2_wake()`, `mmap()`, `mprotect()`, optional `mbind()`, and `numa_set_mempolicy_home_node()`.

## Control Flow
The test maps two pages, protects the second page, launches 64 waiters, and wakes them while checking success or expected errors. It verifies regular NUMA initialization, misaligned address `EINVAL`, out-of-range and read-only/no-access `EFAULT`, restored RW success, and optional MPOL node selection.

## State And Persistence
State is anonymous memory protection and futex/numa fields in the mapped page. Optional memory policy is applied to the mapping only.

## Dependencies And Integration Points
It depends on futex2 NUMA flags, pthread barriers, memory protection faults, kselftest harness, and optional libnuma 2.0.18+.

## Risks
Pointer arithmetic on `void *` relies on GNU C. The MPOL section is skipped without libnuma and may be sensitive to available NUMA nodes and permissions.

## Test Signals
Pass signals include non-`FUTEX_NO_NODE` after regular wake, correct `EINVAL`/`EFAULT` cases, pass for RW retry, and MPOL pass or explicit skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_numa_mpol.c -->
