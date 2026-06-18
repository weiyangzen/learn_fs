# sources/distributed-fs/ceph-client/kernel/locking/rtmutex.c

## Purpose
Core real-time mutex implementation with priority inheritance, used by rt_mutex APIs, PI futexes, and PREEMPT_RT substitutions for mutexes and spin/rwlocks. It manages owner encoding, priority-ordered wait queues, owner PI trees, chain walking, deadlock detection, wakeup handoff, and slow lock/unlock paths.

## Important APIs, Types, and Functions
- Owner helpers: `rt_mutex_set_owner()`, `rt_mutex_clear_owner()`, `mark_rt_mutex_waiters()`, `fixup_rt_mutex_waiters()`, and cmpxchg acquire/release helpers.
- Ordering helpers: `rt_waiter_node_less()`, `rt_mutex_enqueue()`, `rt_mutex_dequeue()`, `rt_mutex_enqueue_pi()`, and `rt_mutex_dequeue_pi()`.
- PI propagation: `rt_mutex_adjust_prio()`, `task_blocks_on_rt_mutex()`, `remove_waiter()`, and `rt_mutex_adjust_prio_chain()`.
- Acquisition and release: `try_to_take_rt_mutex()`, `rt_mutex_slowtrylock()`, `__rt_mutex_trylock()`, `__rt_mutex_slowlock()`, `rt_mutex_slowlock()`, `__rt_mutex_lock()`, `rt_mutex_slowunlock()`, and `__rt_mutex_unlock()`.
- RT lock support: `rtlock_slowlock_locked()` and `rtlock_slowlock()` under `RT_MUTEX_BUILD_SPINLOCKS`.

## Control Flow
Fast acquisition cmpxchg's owner from NULL to current when no waiters bit is present. Slow acquisition takes `wait_lock`, marks the waiters bit to force serialization, tries again, then enqueues a stack waiter in the lock waiters rbtree and links the top waiter into the owner's `pi_waiters` rbtree. If the owner is blocked, `rt_mutex_adjust_prio_chain()` walks at most `max_lock_depth` links, requeueing waiters as priorities/deadlines change and detecting cycles when configured. A blocked task loops trying to take the lock, checking signals/timeouts/ww kills, optionally spinning on an on-CPU owner, and scheduling. Unlock either fast cmpxchg-releases owner or slow-path deboosts current, sets owner to waiter-transitional state, queues the top waiter, and wakes after dropping `wait_lock`.

## State and Persistence
`rt_mutex_base` holds `owner` with a low waiters bit, raw `wait_lock`, and cached rbtree of waiters. Each task has `pi_lock`, `pi_waiters`, and `pi_blocked_on`. Waiter objects are stack-allocated for normal waits or supplied by futex proxy paths. No disk persistence.

## Dependencies and Integration Points
Depends on scheduler priority/deadline APIs, `rt_mutex_setprio()`, wake queues, task state helpers, lock events, lockdep/debug hooks, optional ww_mutex code, and trace lock events. Included directly by `rtmutex_api.c`, `rwsem.c` RT code, and `spinlock_rt.c` with build macros selecting exported subsets.

## Risks
Priority-inheritance chain walking is high risk: reverse lock ordering requires trylock/retry, task lifetime relies on references, and stale chain observations must be revalidated. Waiters bit transitions are deliberately transient and must be fixed before leaving slow paths. Deadlock handling differs for ww_mutex cycles, debug builds, futex full chain walks, and RT locks. Wakeup ordering includes a deliberate preempt-disable region to avoid inversion between deboost and wake.

## Test Signals
RT mutex torture, PI futex tests, scheduler priority/deadline changes while blocked, `max_lock_depth` sysctl, ww_mutex deadlock tests, PREEMPT_RT spinlock substitution stress, lockdep, KCSAN, and lock event counters for slow acquire/sleep/deadlock/wake paths.
