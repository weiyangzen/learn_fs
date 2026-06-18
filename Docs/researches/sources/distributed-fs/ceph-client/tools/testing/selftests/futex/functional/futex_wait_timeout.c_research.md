<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_timeout.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_timeout.c

## Purpose
This test validates timeout behavior for multiple futex wait operations, including classic waits, bitset waits, PI lock waits, requeue-PI waits, and futex2 `waitv`.

## Important APIs, Types, And Functions
Important functions are `get_pi_lock()`, `test_timeout()`, `futex_get_abs_timeout()`, and tests `wait_bitset`, `requeue_pi`, `lock_pi`, and `waitv`. It calls `futex_wait()`, `futex_wait_bitset()`, `futex_wait_requeue_pi()`, `futex_lock_pi()`, and `futex_waitv()`.

## Control Flow
The wait-bitset and requeue tests compute relative or absolute timeouts for monotonic and realtime clocks and expect `ETIMEDOUT`. The lock-PI test starts a thread that locks `futex_pi` forever, then verifies the main thread times out trying to lock it and rejects unsupported timeout flags. The waitv test checks monotonic and realtime absolute timeouts.

## State And Persistence
State is local futex words, a global PI futex, one barrier, and a helper thread that blocks indefinitely within the process.

## Dependencies And Integration Points
It depends on futex classic and futex2 syscalls, PI futex support, pthread barriers, and kselftest harness.

## Risks
The helper thread intentionally blocks forever after taking the PI lock; test process teardown must end it. Historical `FUTEX_LOCK_PI` realtime semantics are subtle and encoded in the expected flags.

## Test Signals
Pass signals are nonzero syscall returns with `errno == ETIMEDOUT` for timeout paths and `ENOSYS` for invalid `FUTEX_CLOCK_REALTIME` on `FUTEX_LOCK_PI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_wait_timeout.c -->
