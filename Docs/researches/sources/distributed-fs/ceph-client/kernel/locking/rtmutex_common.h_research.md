# sources/distributed-fs/ceph-client/kernel/locking/rtmutex_common.h

## Purpose
Private rt_mutex shared header defining waiter data structures, wake queue wrapper, futex proxy prototypes, waiter-tree helpers, initialization helpers, and debug stubs used by rtmutex implementation units.

## Important APIs, Types, and Functions
- `struct rt_waiter_node` stores rbtree entry, priority, and deadline sort keys.
- `struct rt_mutex_waiter` contains lock wait-tree node, owner PI-tree node, task, lock pointer, wake state, and optional ww context.
- `struct rt_wake_q_head` wraps regular wake queues and a PREEMPT_RT special rtlock task.
- Helpers include `rt_mutex_has_waiters()`, `rt_mutex_waiter_is_top_waiter()`, `rt_mutex_top_waiter()`, `task_has_pi_waiters()`, `task_top_pi_waiter()`, `__rt_mutex_base_init()`, `rt_mutex_init_waiter()`, and `rt_mutex_init_rtlock_waiter()`.

## Control Flow
The inline helpers provide the low-level checks used throughout `rtmutex.c`: cached-leftmost rbtree lookup chooses the top waiter, task PI trees choose the top donor, initialization clears rbtree nodes and owner state, and debug helpers poison waiters in debug builds.

## State and Persistence
Defines in-memory waiter/tree layouts only. Waiters are typically stack-allocated and are valid only while the task is blocked or a futex proxy operation owns their lifetime.

## Dependencies and Integration Points
Depends on `linux/rtmutex.h`, task wake queues, debug locks, rbtrees through included kernel headers, and scheduler task fields. Also provides prototypes consumed by futex PI and RCU code paths.

## Risks
`rt_mutex_waiter_is_top_waiter()` is a speculative pointer comparison and assumes callers respect locking/lifetime rules. `task_top_pi_waiter()` assumes a nonempty tree. Waiter initialization and cleanup poisoning help detect use-after-free in debug builds, but production builds rely on exact stack lifetime discipline.

## Test Signals
Compile with and without `CONFIG_RT_MUTEXES` and `CONFIG_DEBUG_RT_MUTEXES`; run PI lock tests that enqueue/dequeue waiters, verify debug poisoning catches stale waiter use, and lockdep checks for wait_lock/pi_lock ordering.
