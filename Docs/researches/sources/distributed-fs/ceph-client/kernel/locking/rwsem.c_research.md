# sources/distributed-fs/ceph-client/kernel/locking/rwsem.c

## Purpose
Implements Linux read/write semaphores. In non-PREEMPT_RT builds it uses a packed atomic count, owner hints, wait list, handoff, and optimistic spinning. In PREEMPT_RT builds it substitutes the common rtmutex-backed `rwbase_rt.c` implementation. The common bottom half exports the public rwsem API and lockdep annotations.

## Important APIs, Types, and Functions
- Public exports include `down_read()`, `down_read_interruptible()`, `down_read_killable()`, `down_read_trylock()`, `down_write()`, `down_write_killable()`, `down_write_trylock()`, `up_read()`, `up_write()`, `downgrade_write()`, and debug nested/non-owner variants.
- Non-RT count bits include writer locked, waiters, handoff, readfail, and shifted reader count.
- Non-RT slow paths include `rwsem_down_read_slowpath()`, `rwsem_down_write_slowpath()`, `rwsem_mark_wake()`, `rwsem_try_write_lock()`, `rwsem_wake()`, and `rwsem_downgrade_wake()`.
- Optimistic spinning uses `rwsem_optimistic_spin()`, `rwsem_spin_on_owner()`, and OSQ.

## Control Flow
Readers add `RWSEM_READER_BIAS` with acquire semantics; if no failure bits are set, they mark reader-owned and enter. Otherwise they may steal when no writer/handoff exists or enqueue as read waiters. Writers cmpxchg from unlocked to writer-locked; on failure they may spin on the current owner, then enqueue as write waiters. `rwsem_mark_wake()` grants batches of front-of-queue readers in two passes or wakes a front writer. Handoff is set by long-waiting or RT/DL writers to prevent indefinite stealing. Unlock readers subtract bias and wake when only waiters remain; unlock writers clears owner, releases writer bit, and wakes waiters. PREEMPT_RT maps these operations to `rwbase_rt` while keeping the same public API.

## State and Persistence
Non-RT state is in `count`, `owner`, `wait_lock`, `first_waiter`, optional `osq`, and stack `rwsem_waiter` entries. RT state is `rwbase` with rtmutex and reader counter. State is in-memory only.

## Dependencies and Integration Points
Depends on scheduler state, wake queues, lockdep, hung-task blocker, lock events, trace events, OSQ, rtmutex/rwbase in RT builds, and exported rwsem APIs consumed across kernel subsystems.

## Risks
Packed count transitions are complex: handoff, waiters, reader grant batching, and downgrade must update flags and reader counts atomically. Owner is partly a debugging/spinning hint and may be stale for readers. Optimistic reader-owned spinning uses a time heuristic and nonspinnable flag. PREEMPT_RT semantics differ in fairness and PI behavior.

## Test Signals
rwsem lock torture, mmap-sem-like reader-heavy stress, RT/DL waiter scenarios, signalable reader/write waits, downgrade tests, non-owner debug APIs, hung-task blocker reports, lock event counters for sleep/wake/handoff/spinning, and PREEMPT_RT build coverage.
