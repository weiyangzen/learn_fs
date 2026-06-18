<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/waitwake.c -->
# sources/distributed-fs/ceph-client/kernel/futex/waitwake.c

Purpose: implements ordinary futex wait and wake operations, wake-op atomic operations, multi-futex wait (`futex_waitv` backend), timeout/restart handling, and the memory-ordering protocol that prevents lost wakeups.

Important APIs/types/functions: main functions are `futex_wake()`, `futex_wake_op()`, `futex_wait_setup()`, `__futex_wait()`, `futex_wait()`, `futex_do_wait()`, `futex_wait_multiple_setup()`, `futex_wait_multiple()`, `futex_unqueue_multiple()`, and `futex_wake_mark()`. Internal helpers include `__futex_wake_mark()`, `futex_atomic_op_inuser()`, `futex_sleep_multiple()`, and `futex_wait_restart()`.

Control flow: wait setup computes the futex key, increments bucket waiter counts, locks the bucket, rereads the user value under the lock, queues only if the value still matches, sets `TASK_INTERRUPTIBLE|TASK_FREEZABLE`, and releases the lock. `__futex_wait()` sleeps, then distinguishes real wakeup from timeout, signal, or spurious wakeup by attempting to unqueue. Wake paths key the address, skip locking when waiter count is zero, scan matching bucket entries, honor bitsets, mark waiters woken, and perform actual wakeups after dropping the bucket lock. `futex_wake_op()` additionally performs an encoded atomic operation on a second futex and conditionally wakes that bucket.

State and persistence behavior: state is transient wait queue state in `futex_q`, bucket waiter counters, task sleep state, restart-block fields for interrupted timed waits, and optional hrtimer sleepers. Multi-wait stores one `futex_q` per user-supplied waiter and returns the index of a woken futex.

Dependencies and integration points: uses key/hash helpers from `core.c`, queue primitives from `futex.h`, scheduler/freezer task states, hrtimers, restart blocks, architecture futex atomic operations, signal handling, and futex2 parsing in `syscalls.c`.

Risks: the waiter-counter barriers are the critical no-lost-wakeup invariant. Reordering the value reread, queue insertion, or wake-side waiter check can block tasks forever. Wake-op must handle page faults without holding bucket locks and retry shared keys when mappings can change. Multi-wait is vulnerable to partial enqueue cleanup bugs and ambiguous wake-index reporting.

Test signals: basic wait/wake and bitset selftests, timeout and restart tests, signal interruption, spurious wake stress, `FUTEX_WAKE_OP` operation/compare matrix, fault injection on both futex addresses, `futex_waitv` multi-wait tests, private vs shared mapping races, freezer interaction during waits, and memory-ordering stress on SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/waitwake.c -->
