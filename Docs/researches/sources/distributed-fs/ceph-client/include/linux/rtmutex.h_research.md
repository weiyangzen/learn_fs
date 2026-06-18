# sources/distributed-fs/ceph-client/include/linux/rtmutex.h

## Purpose
`rtmutex.h` declares real-time mutexes: blocking mutual exclusion locks with priority-inheritance support.

## Important APIs, types, and functions
Core types are `struct rt_mutex_base` and `struct rt_mutex`. Important macros and APIs include `__RT_MUTEX_BASE_INITIALIZER`, `rt_mutex_base_is_locked()`, `RT_MUTEX_HAS_WAITERS`, `rt_mutex_owner()`, `rt_mutex_base_init()`, `DEFINE_RT_MUTEX()`, `rt_mutex_init()`, `__rt_mutex_init()`, `rt_mutex_lock()`, `rt_mutex_lock_nested()`, `rt_mutex_lock_nest_lock()`, `rt_mutex_lock_interruptible()`, `rt_mutex_lock_killable()`, `rt_mutex_trylock()`, `rt_mutex_unlock()`, and optional `rt_mutex_debug_task_free()`.

## Control flow, state, and persistence
An rtmutex owns a raw spinlock-protected waiter rb-tree and owner pointer. Lock acquisition may block, enqueue waiters by priority, and trigger priority inheritance in the implementation. The low bit of owner can encode waiter presence. Debug-lock builds add lockdep maps and nested-lock variants. State persists in the lock object until initialized again or destroyed with its owner.

## Dependencies and integration points
It depends on compiler annotations, linkage, rbtree types, raw spinlock types, task structs, lockdep, and `CONFIG_RT_MUTEXES`/debug options. It underpins PI locking, futex PI, PREEMPT_RT primitives, and other sleeping locks that need deterministic priority behavior.

## Risks and test signals
Risks include using rtmutexes in atomic context, owner-bit misuse, missing unlock on error paths, lock ordering inversions, priority inheritance chain depth issues, and debug/non-debug API differences. Test signals include rtmutex selftests, lockdep nested-lock coverage, PI futex tests, interruptible/killable acquisition, trylock behavior, task-exit debug cleanup, and PREEMPT_RT scheduling latency tests.
