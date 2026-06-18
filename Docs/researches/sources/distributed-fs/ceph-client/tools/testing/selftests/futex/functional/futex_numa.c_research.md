<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_numa.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_numa.c

## Purpose
This stress test exercises futex2 NUMA-aware wait/wake behavior with a custom 64-bit lock word that stores both lock bits and a NUMA node hint.

## Important APIs, Types, And Functions
Important types are `struct futex_numa_32` and `struct thread_args`. Functions include `futex_numa_32_lock()`, `futex_numa_32_unlock()`, `threadfn()`, `contendfn()`, and `main()`. It uses `futex2_wait()` and `futex2_wake()` with `FUTEX2_SIZE_U32`, `FUTEX2_PRIVATE`, optional `FUTEX2_NUMA`, and optional node value.

## Control Flow
Command-line options set worker count, contender count, sleep duration, nanosleep time, and NUMA mode. Worker threads take the custom lock, update paired counters with an invariant check, observe the node field, and unlock. Contender threads intentionally call futex2 wait with a wrong value to create hash-bucket contention.

## State And Persistence
All state is in process memory: global `done`, `lock`, `val1`, and `val2`, plus per-thread counters. The futex node field is kernel-written state in the shared lock word.

## Dependencies And Integration Points
It depends on futex2 wait/wake syscalls, pthreads, atomic builtins, and kernel NUMA futex support.

## Risks
Assertions abort the process on invariant or wake assumptions. The fixed arrays allow at most 512 workers/contenders but input is not bounded against that size. Futex2 syscall availability varies by kernel.

## Test Signals
Expected output includes observed node changes and final total/contender counts without assertion failures or deadlocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_numa.c -->
