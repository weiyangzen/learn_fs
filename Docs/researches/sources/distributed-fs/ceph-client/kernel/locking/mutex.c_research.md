# sources/distributed-fs/ceph-client/kernel/locking/mutex.c

## Purpose
Implements the generic non-PREEMPT_RT Linux mutex and wound/wait mutex acquisition paths, plus the common `atomic_dec_and_mutex_lock()` helper that remains outside the non-RT block. A mutex is a sleeping exclusive lock with owner tracking, a wait list, optional optimistic spinning, lockdep/debug hooks, hung-task blocker integration, and lock contention tracepoints.

## Important APIs, Types, and Functions
- Public exports include `mutex_lock()`, `mutex_unlock()`, `mutex_trylock()`, `mutex_lock_interruptible()`, `mutex_lock_killable()`, `mutex_lock_io()`, `ww_mutex_lock()`, `ww_mutex_lock_interruptible()`, `ww_mutex_trylock()`, `ww_mutex_unlock()`, and `atomic_dec_and_mutex_lock()`.
- Internal fast paths are `__mutex_trylock_fast()`, `__mutex_unlock_fast()`, `__mutex_trylock_common()`, and `__mutex_trylock_or_handoff()`.
- Wait-list and handoff helpers are `__mutex_add_waiter()`, `__mutex_remove_waiter()`, `__mutex_handoff()`, `__mutex_lock_common()`, and `__mutex_unlock_slowpath()`.
- Optional spin-on-owner support uses `mutex_optimistic_spin()`, `mutex_spin_on_owner()`, `mutex_can_spin_on_owner()`, and the optimistic spin queue from `osq_lock.c`.
- Wound/wait integration comes from `ww_mutex.h` via `__ww_mutex_add_waiter()`, `__ww_mutex_check_waiters()`, `__ww_mutex_check_kill()`, and `ww_mutex_lock_acquired()`.

## Control Flow
The uncontended path tries to atomically set `lock->owner` from `0` to `current` with acquire semantics. On failure, `__mutex_lock_common()` disables preemption, records lockdep contention, tries a full owner/flag aware trylock, then optionally optimistic-spins while the owner is running. If spinning fails, the task is inserted into the circular waiter list protected by `wait_lock`, `current->blocked_on` is set, and the task sleeps in the requested state until it can pick up an explicit handoff or acquire the owner field. Unlock first attempts a release cmpxchg to clear an owner with no flags; the slow path clears or hands off ownership and queues the top waiter for wakeup.

## State and Persistence
State is in memory only. `struct mutex` stores `owner` with low-bit flags for waiters, handoff, and pickup; `first_waiter` anchors a circular list; `wait_lock` serializes slow paths; `osq` serializes optimistic spinners when enabled. Waiter records live on blocked tasks' stacks, and hung-task blocker state is updated while waiting.

## Dependencies and Integration Points
Depends on `linux/mutex.h`, `linux/ww_mutex.h`, scheduler state and wake queues, raw spinlocks, lockdep, trace events, `osq_lock`, and hung-task debugging. It integrates with scheduler blocked-on tracking through `__set_task_blocked_on()` and with exported lock contention tracepoints `contention_begin` and `contention_end`.

## Risks
The correctness-critical areas are owner flag transitions, release/acquire pairing across handoff, wakeup ordering while canceling signalable waits, and preserving wait-list order for ww_mutex deadlock avoidance. Optimistic spinning uses speculative `task_struct` owner reads and relies on preemption-disabled RCU-like lifetime protection. `mutex_unlock()` cannot be used as the final reference drop when another task may free the object immediately after observing unlock.

## Test Signals
Build coverage should include `CONFIG_DEBUG_MUTEXES`, `CONFIG_DEBUG_LOCK_ALLOC`, `CONFIG_MUTEX_SPIN_ON_OWNER`, ww_mutex users, and PREEMPT_RT disabled/enabled configurations. Runtime signals include lockdep splats, hung-task blocker reports, `contention_begin/end` tracepoints, ww_mutex `-EDEADLK` handling, and stress tests that combine signal interruption, handoff, trylock, and unlock/free races.
