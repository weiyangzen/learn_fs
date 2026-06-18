# sources/distributed-fs/ceph-client/kernel/sched/completion.c

## Purpose
`completion.c` implements the kernel completion primitive: a synchronization point where one or more waiters block until another context signals completion. Unlike semaphores, completions document event synchronization rather than mutual exclusion and support single or all-waiter wakeups.

## Important APIs, Types, And Functions
The key object is `struct completion`, with `done` and an `swait_queue_head`. Exported APIs include `complete()`, `complete_on_current_cpu()`, `complete_all()`, `wait_for_completion()`, `wait_for_completion_timeout()`, `wait_for_completion_io()`, `wait_for_completion_io_timeout()`, `wait_for_completion_interruptible()`, `wait_for_completion_interruptible_timeout()`, `wait_for_completion_killable()`, `wait_for_completion_state()`, `wait_for_completion_killable_timeout()`, `try_wait_for_completion()`, and `completion_done()`. Internal helpers include `complete_with_flags()`, `do_wait_for_common()`, `__wait_for_common()`, `wait_for_common()`, and `wait_for_common_io()`.

## Control Flow
`complete()` and `complete_on_current_cpu()` lock the swait queue, increment `done` unless saturated at `UINT_MAX`, and wake one waiter with optional wake flags. `complete_all()` sets `done` to `UINT_MAX` and wakes all waiters; callers must reinitialize before reuse. Wait paths call `might_sleep()`, annotate acquire/release, lock the wait queue, enqueue an swait entry if `done` is zero, set the requested task state, drop the lock while scheduling, reacquire, and repeat until signaled, interrupted, or timed out. On success, single completions decrement `done` unless saturated.

## State And Persistence
Completion state is entirely in memory and owned by the embedding subsystem. `done` is a counter for single completions or saturated `UINT_MAX` after `complete_all()`. Waiters are transient swait queue entries. No state persists outside the object lifetime.

## Dependencies And Integration Points
The implementation depends on scheduler task states, `schedule_timeout()`, `io_schedule_timeout()`, raw spinlocks with IRQ save/restore, swait queues, lockdep, and completion memory-order annotations. Completions are used throughout the kernel for task startup/shutdown, async work, device operations, RPC-like waits, and module teardown.

## Risks
Misuse risks include calling blocking waits from atomic context, reinitializing too soon after `complete_all()`, freeing a completion while `complete()` still references it, ignoring interruptible return codes, or expecting `completion_done()` to indicate absence of waiters after `complete_all()`. Implementation risks are memory ordering, lost wakeups, timeout semantics, and PREEMPT_RT locking constraints.

## Test Signals
Signals include unit or subsystem tests covering single waiter, multiple waiter, timeout, interruptible/killable waits, IO waits, `try_wait_for_completion()`, `completion_done()`, and `complete_all()` reinitialization discipline. Lockdep should catch atomic-context waits or invalid RT contexts.
