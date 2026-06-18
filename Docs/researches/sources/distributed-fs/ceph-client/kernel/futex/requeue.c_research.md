<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/requeue.c -->
# sources/distributed-fs/ceph-client/kernel/futex/requeue.c

Purpose: implements moving waiters from one futex key to another, including plain `FUTEX_REQUEUE`/`FUTEX_CMP_REQUEUE` and PI-aware condition-variable flows that wait on a non-PI futex and acquire a PI futex before returning.

Important APIs/types/functions: key exports are `futex_requeue()` and `futex_wait_requeue_pi()`. The file defines `futex_q_init`, the requeue-PI state machine (`Q_REQUEUE_PI_*`), and helpers `requeue_futex()`, `futex_requeue_pi_prepare()`, `futex_requeue_pi_complete()`, `futex_requeue_pi_wakeup_sync()`, `requeue_pi_wake_futex()`, `futex_proxy_trylock_atomic()`, and `handle_early_requeue_pi_wakeup()`.

Control flow: `futex_requeue()` keys source and destination futexes, locks both buckets in address order, optionally compares the source value, and either wakes the first `nr_wake` waiters or moves subsequent waiters to the destination bucket. In PI mode it validates distinct keys, restricts wake count to one, preallocates PI state, may acquire the target PI futex for the top waiter, then requeues remaining waiters onto the target rtmutex with proxy locking. `futex_wait_requeue_pi()` waits on the source futex, synchronizes with any concurrent requeue, handles early signal/timeout wakeups, and completes rtmutex acquisition or owner fixup after requeue.

State and persistence behavior: requeue changes only runtime queue state: `futex_q.key`, plist membership, `lock_ptr`, waiter counts, optional `pi_state`, `rt_waiter`, `requeue_pi_key`, `requeue_state`, and temporary hash references. PI requeue state records whether a waiter should be ignored, is in progress, has been requeued, or acquired the lock.

Dependencies and integration points: depends on hash-bucket queue primitives, PI helpers in `pi.c`, wait setup in `waitwake.c`, rtmutex proxy locking, PREEMPT_RT `rcuwait` synchronization, and syscall dispatch in `syscalls.c`. It implements the kernel side required by pthread condition variables using `FUTEX_WAIT_REQUEUE_PI` paired with `FUTEX_CMP_REQUEUE_PI`.

Risks: missed state transitions can strand waiters on the wrong bucket, lose wakeups, or corrupt rtmutex waiter state. PI requeue must reject mismatched source/target keys and incompatible waiter types. Early wakeups racing with requeue are especially risky on PREEMPT_RT because a task cannot block on both a bucket rtmutex and a proxy rtmutex.

Test signals: requeue and cmp-requeue futex selftests, pthread condvar PI tests, signal and timeout races during `FUTEX_WAIT_REQUEUE_PI`, deadlock-detection cases, target-key mismatch tests, PREEMPT_RT stress, fault injection on source/target user words, and wait-count accounting checks under heavy contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/requeue.c -->
