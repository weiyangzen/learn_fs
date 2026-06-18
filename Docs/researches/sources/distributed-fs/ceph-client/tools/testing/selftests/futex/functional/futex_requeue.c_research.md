<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue.c

## Purpose
This test verifies non-PI `FUTEX_CMP_REQUEUE` behavior for moving waiters from one futex to another.

## Important APIs, Types, And Functions
It defines `waiterfn()`, `TEST(requeue_single)`, and `TEST(requeue_multiple)`, using `futex_wait()`, `futex_cmp_requeue()`, and `futex_wake()`.

## Control Flow
Waiter threads block on `f1` with a short timeout. The single test requeues one waiter from `f1` to `f2` and wakes it. The multiple test creates ten waiters, wakes three and requeues seven, then wakes exactly seven from `f2`.

## State And Persistence
State is local futex words and pthread waiters. No persistent system state is modified.

## Dependencies And Integration Points
It depends on pthreads, the local `futextest.h` wrappers, and kselftest harness.

## Risks
The test uses `usleep(WAKE_WAIT_US)` rather than a deterministic barrier, so very slow systems can race waiter blocking. Waiter threads are not explicitly joined, relying on test process exit after wake checks.

## Test Signals
Expected syscall return counts are `1` then `1` in the single case and `10` then `7` in the multiple case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue.c -->
