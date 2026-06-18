<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue_pi_mismatched_ops.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue_pi_mismatched_ops.c

## Purpose
This regression test ensures the kernel rejects `FUTEX_CMP_REQUEUE_PI` when the waiter used plain `FUTEX_WAIT` instead of `FUTEX_WAIT_REQUEUE_PI`.

## Important APIs, Types, And Functions
It defines globals `f1`, `f2`, `child_ret`, helper `blocking_child()`, and `TEST(requeue_pi_mismatched_ops)`. It uses `futex_wait()`, `futex_cmp_requeue_pi()`, and `futex_wake()`.

## Control Flow
A child thread blocks in plain `futex_wait()` on `f1`. The parent sleeps briefly, then calls `futex_cmp_requeue_pi()` from `f1` to `f2`. Correct behavior is `-1/EINVAL`, after which the parent wakes the child using non-PI `FUTEX_WAKE` and joins it.

## State And Persistence
State is two process-local futex words and one child thread.

## Dependencies And Integration Points
It depends on PI futex validation, pthreads, and kselftest harness.

## Risks
If the kernel fails to detect the mismatch, it may incorrectly hand a PI lock to a waiter not prepared for it and hang. The final `else` path appears to print pass text for a failure string, which can weaken result reporting.

## Test Signals
The key signal is `FUTEX_CMP_REQUEUE_PI` returning `EINVAL`, followed by `FUTEX_WAKE` waking exactly one child and a clean join.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue_pi_mismatched_ops.c -->
