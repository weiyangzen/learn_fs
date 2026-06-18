# sources/distributed-fs/ceph-client/kernel/locking/rtmutex_api.c

## Purpose
Builds public rt_mutex APIs on top of `rtmutex.c`, exposes PI futex proxy operations, registers the `kernel.max_lock_depth` sysctl, and, under PREEMPT_RT, provides regular mutex APIs backed by rt_mutex internals.

## Important APIs, Types, and Functions
- Public rt_mutex exports: `rt_mutex_base_init()`, `rt_mutex_lock()`, `rt_mutex_lock_interruptible()`, `rt_mutex_lock_killable()`, `rt_mutex_trylock()`, `rt_mutex_unlock()`, and debug nested variants.
- Futex APIs: `rt_mutex_futex_trylock()`, `__rt_mutex_futex_trylock()`, `__rt_mutex_futex_unlock()`, `rt_mutex_futex_unlock()`, `rt_mutex_init_proxy_locked()`, `rt_mutex_proxy_unlock()`, `__rt_mutex_start_proxy_lock()`, `rt_mutex_start_proxy_lock()`, `rt_mutex_wait_proxy_lock()`, and `rt_mutex_cleanup_proxy_lock()`.
- PI maintenance: `rt_mutex_adjust_pi()` and `rt_mutex_postunlock()`.
- PREEMPT_RT mutex exports mirror regular mutex functions with rtmutex backing.

## Control Flow
`__rt_mutex_lock_common()` wraps lockdep acquire, calls `__rt_mutex_lock()`, and releases lockdep on failure. Trylock uses `__rt_mutex_trylock()` and acquires lockdep only on success. Futex proxy start attempts direct ownership for a target task, otherwise enqueues the supplied waiter with full chainwalk deadlock detection; wait then blocks on that waiter, and cleanup races with possible late ownership by trying to take the lock before removing the waiter. PREEMPT_RT mutex wrappers call the same rtmutex core while preserving normal mutex lockdep names and I/O-wait handling.

## State and Persistence
Adds global in-memory `max_lock_depth` exposed through sysctl. All lock state remains inside `rt_mutex`, `rt_mutex_base`, supplied futex waiters, and task PI fields.

## Dependencies and Integration Points
Depends on `rtmutex.c` with `RT_MUTEX_BUILD_MUTEX`, proc sysctl registration, lockdep, futex PI callers, wake queues, and PREEMPT_RT mutex substitution. The proxy APIs integrate with futex pi_state lifetime rules and hash bucket locking.

## Risks
Proxy locking is sensitive to races where the owner releases while a waiter is being enqueued or cleaned up. `rt_mutex_start_proxy_lock()` removes the waiter on failure while `__rt_mutex_start_proxy_lock()` deliberately does not, so caller contracts differ. PREEMPT_RT mutex behavior differs from non-RT mutex in PI and sleeping spinlock interactions.

## Test Signals
PI futex selftests, robust futex timeout/signal cleanup, lockdep class checks for futex proxy locks, `max_lock_depth` sysctl changes, PREEMPT_RT mutex API compatibility tests, and debug task-free checks for nonempty PI trees.
