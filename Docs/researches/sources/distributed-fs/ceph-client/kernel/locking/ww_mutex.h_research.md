# sources/distributed-fs/ceph-client/kernel/locking/ww_mutex.h

## Purpose
Implements the internal wound/wait mutex policy shared by regular mutex and RT mutex builds. It abstracts waiter traversal and wait-lock handling, orders ww acquisition contexts, decides when a transaction should die or wound another owner, and maintains `ww_mutex.ctx` accounting.

## Important APIs, Types, And Functions
The file defines the `MUTEX`, `MUTEX_WAITER`, and `WAIT_LOCK` aliases for normal versus `WW_RT` builds. Traversal helpers are `__ww_waiter_first`, `__ww_waiter_next`, `__ww_waiter_prev`, `__ww_waiter_last`, and `__ww_waiter_add`. Policy helpers include `ww_mutex_lock_acquired`, `__ww_ctx_less`, `__ww_mutex_die`, `__ww_mutex_wound`, `__ww_mutex_check_waiters`, `ww_mutex_set_context_fastpath`, `__ww_mutex_kill`, `__ww_mutex_check_kill`, `__ww_mutex_add_waiter`, and `__ww_mutex_unlock`.

## Control Flow
On acquisition, `ww_mutex_lock_acquired` records the context and increments its acquired count. Fastpath acquisitions publish `lock->ctx`, use a memory barrier against the waiters flag, then scan waiters if contention appeared. Slowpath waiter insertion sorts context waiters by transaction priority and stamp, kills younger wait-die contexts early, or wounds younger holders for wound-wait. Unlock clears the context and decrements the acquired count.

## State And Persistence
State lives in `struct ww_acquire_ctx` fields such as `stamp`, `acquired`, `wounded`, `contending_lock`, and `is_wait_die`, and in `struct ww_mutex.ctx`. No durable persistence exists. Memory ordering is explicit around context publication and waiter visibility.

## Dependencies And Integration Points
Depends on mutex internals, rtmutex internals under `WW_RT`, lockdep annotations, wake queues, scheduler blocked-on tracking, and optional RT/deadline priority comparisons. It is included by the mutex and rtmutex implementations rather than being a standalone public header.

## Risks And Edge Cases
Correctness depends on sorted waiter iteration, matching barriers between fastpath context publication and slowpath waiter insertion, and not mixing wait-die with wound-wait in one class. RT mode adds task priority and deadline ordering, while non-RT mode cannot use unstable PI priority. Debug checks catch recursive acquisition, class mismatches, and wrong post-`-EDEADLK` recovery.

## Test Signals
Signals come from ww mutex selftests, lockdep warnings, RT and non-RT build coverage, ABBA/cycle deadlock tests, and stress runs that force repeated `-EDEADLK` plus `ww_mutex_lock_slow` recovery.
