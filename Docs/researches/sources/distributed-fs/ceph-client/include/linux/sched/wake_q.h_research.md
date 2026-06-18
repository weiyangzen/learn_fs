# sources/distributed-fs/ceph-client/include/linux/sched/wake_q.h

Purpose: declares wake queues, a mechanism for batching task wakeups until after releasing contended locks.

Important APIs and types: `struct wake_q_head`, `WAKE_Q_TAIL`, `WAKE_Q_HEAD_INITIALIZER`, `DEFINE_WAKE_Q`, `wake_q_init()`, `wake_q_empty()`, `wake_q_add()`, `wake_q_add_safe()`, `wake_up_q()`, and raw spin unlock-and-wake helpers are central.

Control flow: lock or synchronization code marks tasks internally woken, appends them to a wake queue while holding references, releases the protecting lock, and then calls `wake_up_q()` to perform scheduler wakeups. Unlock helpers combine raw spin unlock with wakeup under preemption guard.

State and persistence: queue state is a transient singly-linked list using each task’s embedded `wake_q_node`; tasks cannot be abandoned in a wake queue and must be woken soon.

Dependencies and integration points: depends on `sched.h`, task refs, raw spinlocks, and preemption guards. It integrates futexes, mutex/rtmutex-like paths, and other synchronization primitives with scheduler wakeups.

Risks and test signals: risks include adding a task to two wake queues, failing to call `wake_up_q()`, spurious wakeups without condition loops, and waking before the task is ready. Test futex/mutex contention, PI paths, lock handoff races, wake queue reuse, and PREEMPT_RT spin unlock behavior.
