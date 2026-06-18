# sources/distributed-fs/ceph-client/include/linux/rcuwait.h

## Purpose

`rcuwait.h` provides a minimal wait primitive for cases that need one waiting task pointer protected by RCU-style access rather than a full wait queue. It is used where wakeup paths need to safely observe a blocked task while external locking serializes waiter setup and teardown.

## Important APIs, Types, and Functions

`__RCUWAIT_INITIALIZER()` and `rcuwait_init()` initialize the embedded `struct rcuwait` task pointer to `NULL`. `rcuwait_active()` uses `rcu_access_pointer()` to test whether a task is registered, explicitly without serialization guarantees. `prepare_to_rcuwait()` stores `current` with `rcu_assign_pointer()`. `finish_rcuwait()` and `rcuwait_wake_up()` are external implementation functions.

The waiting macros are `rcuwait_wait_event()`, `rcuwait_wait_event_timeout()`, and the internal `___rcuwait_wait_event()`. They combine `prepare_to_rcuwait()`, `set_current_state()`, signal checks, `schedule()` or `schedule_timeout()`, and `finish_rcuwait()`.

## Control Flow

A caller holding the appropriate lock calls a wait macro. The macro publishes `current`, sets the task state in a loop, checks the condition, handles pending signals for interruptible states by returning `-EINTR`, schedules, and finally removes the task from the wait object. The wake side calls `rcuwait_wake_up()`, whose barriers pair with the `set_current_state()` barrier documented in the macro.

## State and Persistence Behavior

The only state is the wait object's RCU-protected task pointer and the current task state while waiting. The pointer is transient and must be serialized by caller-owned locking around wait preparation and finish.

## Dependencies and Integration Points

The header depends on RCU pointer helpers, scheduler signal state, and kernel types. It is suitable for low-overhead one-waiter synchronization in core kernel subsystems where a full `wait_queue_head_t` is unnecessary.

## Risks

`rcuwait_active()` is only a hint, so using it as a synchronization guarantee can lose wakeups. Callers must lock around waiter setup/finish and condition updates. The condition expression is reevaluated after task-state publication; side effects in the condition can be surprising. Timeout callers must handle the standard zero/remaining-time conventions.

## Test Signals

Tests should race waiter registration, wakeup, signals, timeout expiry, and condition changes under the caller's lock. Lockdep and scheduler instrumentation should verify no sleeps occur in invalid contexts and that wakeups are not lost under high contention.
