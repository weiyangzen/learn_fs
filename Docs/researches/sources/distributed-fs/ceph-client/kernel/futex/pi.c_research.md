<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/pi.c -->
# sources/distributed-fs/ceph-client/kernel/futex/pi.c

Purpose: implements priority-inheritance futex locking and unlocking on top of rtmutexes. It maintains `futex_pi_state`, attaches waiters to owners, handles owner death/exit races, transfers ownership during unlock, and repairs user-space futex words when rtmutex ownership and user TIDs diverge.

Important APIs/types/functions: public futex-internal entry points are `refill_pi_state_cache()`, `get_pi_state()`, `put_pi_state()`, `futex_lock_pi_atomic()`, `fixup_pi_owner()`, `futex_lock_pi()`, and `futex_unlock_pi()`. Important internal helpers are `attach_to_pi_state()`, `attach_to_pi_owner()`, `handle_exit_race()`, `wake_futex_pi()`, `__fixup_pi_state_owner()`, and `lock_pi_update_atomic()`.

Control flow: `futex_lock_pi()` preallocates PI state, builds a futex key, locks the hash bucket, and calls `futex_lock_pi_atomic()`. The atomic helper either acquires an uncontended lock by updating the user word, attaches to existing PI state, or sets `FUTEX_WAITERS` and creates PI state for the owner. If blocking is needed, the waiter is queued in the futex bucket, then proxied onto the rtmutex; after wake, `fixup_pi_owner()` reconciles kernel and user-space ownership. `futex_unlock_pi()` validates that current owns the futex word, finds the top PI waiter, and either passes ownership with `wake_futex_pi()` or atomically clears the word.

State and persistence behavior: `futex_pi_state` objects are runtime refcounted and cached per current task through `pi_state_cache`. Each PI state owns an `rt_mutex_base`, an owner pointer, key, and owner-list link. User-space state is the futex word containing TID, `FUTEX_WAITERS`, and `FUTEX_OWNER_DIED`; kernel state must be kept consistent with that word except in documented immutable-user-page failure cases.

Dependencies and integration points: depends on rtmutex proxy locking, futex hash-bucket locking from `core.c`, task lookup by virtual pid, per-task `pi_lock`, futex exit state, robust-list owner death, and fault repair through `fault_in_user_writeable()`. Requeue-PI uses `futex_lock_pi_atomic()` and PI-state references to acquire locks on behalf of waiters.

Risks: this is highly concurrency-sensitive. Risks include deadlock detection regressions, owner TID mismatch, races with exiting owners between robust-list and PI-list cleanup, missing `FUTEX_WAITERS`, stale `pi_state` references, page faults while holding locks, PREEMPT_RT lock handoff issues, and inconsistent user/kernel ownership after lock stealing.

Test signals: PI futex selftests for lock, trylock, unlock, timeout, signal, owner death, robust mutexes, invalid user word manipulation, exiting owner live-lock avoidance, priority boosting/deboosting, page-fault injection during cmpxchg, requeue-PI condition-variable tests, and lockdep/rtmutex debug coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/pi.c -->
