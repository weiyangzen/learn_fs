<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue_pi_signal_restart.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue_pi_signal_restart.c

## Purpose
This test verifies signal handling around `futex_wait_requeue_pi()` before and after requeue.

## Important APIs, Types, And Functions
Important helpers are `create_rt_thread()`, `handle_signal()`, `waiterfn()`, and `TEST(futex_requeue_pi_signal_restart)`. It uses `futex_wait_requeue_pi()`, `futex_cmp_requeue_pi()`, `futex_lock_pi()`, `futex_unlock_pi()`, `pthread_kill()`, and atomic flag `requeued`.

## Control Flow
The parent installs a SIGUSR1 handler, starts an RT waiter on `f1`, locks PI futex `f2`, repeatedly signals the waiter before requeue until `futex_cmp_requeue_pi()` succeeds, marks requeued, then signals after requeue. The waiter should restart before requeue and return with `EWOULDBLOCK` after requeue.

## State And Persistence
State is process-local futexes, signal handler state, one RT thread, and the atomic `requeued` flag.

## Dependencies And Integration Points
It depends on PI futex restart behavior, POSIX signals, realtime scheduling, pthreads, and `atomic.h`.

## Risks
Timing is deliberately racy before requeue; the parent loops until the signal and waiter blocking order allows requeue. RT thread creation may fail without privileges.

## Test Signals
Expected behavior is no failure from pre-requeue signals, successful requeue, waiter observing post-requeue `EWOULDBLOCK`, and successful final `FUTEX_UNLOCK_PI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue_pi_signal_restart.c -->
