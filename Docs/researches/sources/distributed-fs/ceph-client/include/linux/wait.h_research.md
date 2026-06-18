# sources/distributed-fs/ceph-client/include/linux/wait.h

## Purpose
`wait.h` defines Linux wait queue types and the macro API used to sleep until conditions become true, wake tasks, integrate with poll, handle timeouts/signals/freezer states, and wait while temporarily releasing locks. It is one of the core synchronization contracts in the kernel.

## Important APIs, Types, and Functions
Core types are `struct wait_queue_entry`, `wait_queue_func_t`, and `struct wait_queue_head`. Flags include `WQ_FLAG_EXCLUSIVE`, `WQ_FLAG_WOKEN`, `WQ_FLAG_CUSTOM`, `WQ_FLAG_DONE`, and `WQ_FLAG_PRIORITY`. Initialization APIs include static and dynamic waitqueue initializers, `init_waitqueue_head()`, `init_waitqueue_entry()`, and `init_waitqueue_func_entry()`. Queue operations include add/remove helpers, exclusive/priority variants, and lockless tests `waitqueue_active()`, `wq_has_single_sleeper()`, and `wq_has_sleeper()`. Wake APIs include `__wake_up*()` functions and macros for normal, interruptible, sync, poll, locked, and pollfree wakeups. Wait macros include `wait_event*()`, `io_wait_event()`, freezable variants, interruptible/killable/idle variants, timeout and hrtimer variants, exclusive variants, command variants, and locked variants such as `wait_event_lock_irq*()`. Low-level APIs include `prepare_to_wait*()`, `finish_wait()`, `wait_woken()`, wake functions, `DEFINE_WAIT`, and `task_call_func()`.

## Control Flow
The canonical wait flow initializes a wait entry, calls `prepare_to_wait_event()` to add it and set task state, tests the caller condition, schedules or performs caller-specified commands, then calls `finish_wait()` when the condition becomes true or the wait exits. Wake paths call `__wake_up()` variants, which iterate wait entries and invoke each entry's wake function, respecting exclusive limits and poll keys. Locked wait macros drop and reacquire caller locks around `schedule()`.

## State and Persistence
Wait queue state is in-memory list state protected by `wait_queue_head.lock`. Wait entries are usually stack objects with task pointers and callbacks. There is no persistence after waiting completes. Memory-ordering rules are part of the state contract: lockless `waitqueue_active()` requires barriers paired with waiter state setting, and condition changes must happen before wakeups.

## Dependencies and Integration Points
The header depends on lists, spinlocks, current task access, scheduler task states, timers, hrtimers, freezer state, poll masks, lockdep, and signal handling. It integrates with virtually all blocking kernel subsystems: filesystems, networking, device drivers, mm, poll/epoll, completions, bit waits, and workqueues.

## Risks
Lost wakeups are the central risk if condition stores and wakeups are not ordered correctly. Conditions must be side-effect safe because macros evaluate them multiple times. Stack wait entries must not outlive the call. Locked wait variants require the exact lock state documented by the macro. Pollfree wakeups require RCU-delayed waitqueue freeing. Exclusive waiters can starve if wake counts are wrong.

## Test Signals
Signals include lockdep coverage of waitqueue locks, stress tests for lost wakeups, signal and timeout return values, hrtimer timeout behavior, freezer interactions, poll/epoll teardown with `wake_up_pollfree()`, exclusive waiter fairness, and locked wait variants under contention.
