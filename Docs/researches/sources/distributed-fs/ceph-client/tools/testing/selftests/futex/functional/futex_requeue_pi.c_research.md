<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue_pi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue_pi.c

## Purpose
This test exercises priority-inheritance requeue operations used to implement PI-aware condition variables and mutexes.

## Important APIs, Types, And Functions
Important globals are `waiters_blocked`, `waiters_woken`, `f1`, `f2`, and `wake_complete`. Helpers include `create_rt_thread()`, `waiterfn()`, `broadcast_wakerfn()`, `signal_wakerfn()`, and `third_party_blocker()`. The fixture variants cover timeout lengths, broadcast vs signal, waker-held PI lock, and third-party owner.

## Control Flow
For each variant, ten RT waiter threads call `futex_wait_requeue_pi()` on `f1` targeting PI futex `f2`. A waker either signals one at a time or broadcasts through `futex_cmp_requeue_pi()`, optionally while holding `f2`. A third-party blocker variant owns `f2` until wake completion. Waiters unlock `f2` after return or after taking it on timeout.

## State And Persistence
All state is process-local futex words, atomic counters, RT pthread attributes, and optional timeout structs. It temporarily consumes realtime scheduling capability.

## Dependencies And Integration Points
It depends on PI futex operations, realtime scheduling (`SCHED_FIFO`), pthreads, kselftest fixture variants, and the `atomic.h` helpers.

## Risks
Creating RT threads may require privileges and can fail under scheduling restrictions. The code relies on sleeps and iteration bounds to avoid races; a failure can leave waiters hung if kernel PI requeue behavior regresses.

## Test Signals
Good signals are all variant combinations completing, `task_count` reaching expected waiter counts, no unexpected `futex_wait_requeue_pi()` errors except allowed timeouts, and no stuck PI lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_requeue_pi.c -->
