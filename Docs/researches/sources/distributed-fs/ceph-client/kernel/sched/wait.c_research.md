# sources/distributed-fs/ceph-client/kernel/sched/wait.c

## Purpose

`kernel/sched/wait.c` implements the generic wait-queue primitives used across the kernel to put tasks to sleep until a condition changes and to wake them with well-defined ordering. It owns wait-queue initialization, queue insertion and removal, common wake-up scanning, helper preparation/finish APIs used by wait-event macros, interruptible wait helpers, and the `wait_woken()` protocol for waiters that need explicit wake-state tracking.

## Important APIs, Types, and Functions

The file works primarily on `struct wait_queue_head` and `struct wait_queue_entry`. Public entry points include `__init_waitqueue_head()`, `add_wait_queue()`, `add_wait_queue_exclusive()`, `add_wait_queue_priority()`, `add_wait_queue_priority_exclusive()`, `remove_wait_queue()`, `__wake_up()`, `__wake_up_locked()`, `__wake_up_locked_key()`, `__wake_up_sync_key()`, `__wake_up_locked_sync_key()`, `__wake_up_sync()`, `__wake_up_pollfree()`, `prepare_to_wait()`, `prepare_to_wait_exclusive()`, `init_wait_entry()`, `prepare_to_wait_event()`, `do_wait_intr()`, `do_wait_intr_irq()`, `finish_wait()`, `autoremove_wake_function()`, `wait_woken()`, and `woken_wake_function()`.

Internally, `__wake_up_common()` is the central queue scanner. It invokes each entry's wake callback, stops if a callback returns a negative value, and consumes exclusive wakeups until the requested `nr_exclusive` reaches zero. `__wake_up_common_lock()` wraps this with `wq_head->lock` and IRQ save/restore. Waiter ordering is controlled by `WQ_FLAG_EXCLUSIVE`, `WQ_FLAG_PRIORITY`, and `WQ_FLAG_WOKEN`.

## Control Flow

Wait queues are initialized by setting up the spinlock, lockdep class/name, and list head. Non-exclusive waiters are normally inserted at the head, exclusive waiters at the tail, and priority waiters at the head. `add_wait_queue_priority_exclusive()` allows only one priority waiter at the front of a queue and returns `-EBUSY` if a priority waiter already occupies that position.

Wake-up flow starts with a caller such as `__wake_up()` taking the wait-queue lock and running `__wake_up_common()`. The scanner is safe against callback-side deletion by using `list_for_each_entry_safe_from()`. Exclusive entries let "wake one" and "wake N" behavior coexist with non-exclusive broadcast entries. Sync wakeups pass `WF_SYNC`; current-CPU wakeups pass `WF_CURRENT_CPU`; pollfree wakeups pass a poll key containing `EPOLLHUP | POLLFREE` and assert that the queue was drained.

Wait setup follows a consistent pattern: insert the entry while holding the queue lock, then set the current task state before releasing the lock. `prepare_to_wait_event()` additionally handles pending signals and removes a waiter that should abort with `-ERESTARTSYS`, while preserving the rule that an exclusive waiter already selected by a wakeup must not silently lose the event. `finish_wait()` restores `TASK_RUNNING` and removes the entry if still queued, using `list_empty_careful()` before taking the lock.

`wait_woken()` and `woken_wake_function()` implement a paired barrier protocol around `WQ_FLAG_WOKEN`. The waiter sets its task state, schedules only if the flag is not set and the kthread is not stopping/parking, then clears `WQ_FLAG_WOKEN` with `smp_store_mb()`. The waker executes `smp_mb()`, sets `WQ_FLAG_WOKEN`, and delegates to `default_wake_function()`.

## State and Persistence

The persistent state is in caller-owned wait-queue heads and wait entries: queue membership, flags, callback pointers, and the task stored in `wq_entry->private`. The file does not allocate long-lived objects. It mutates `current->state` through `set_current_state()` and `__set_current_state()`, and relies on the queue spinlock plus memory barriers to publish queue membership before condition checks and wake decisions.

## Dependencies and Integration Points

This file is part of scheduler infrastructure via `sched.h`. It depends on list primitives, spinlocks, lockdep, task states, signal state checks, `schedule()`, `schedule_timeout()`, default wake functions, kthread stop/park checks, poll key conversion, and exported wait-queue helpers consumed by drivers, filesystems, networking, mm, and other kernel subsystems.

## Risks and Edge Cases

The main risks are lost wakeups, incorrect exclusive wake consumption, and memory-ordering regressions. The ordering comment in `prepare_to_wait()` is central: waiters must be visible to wakers before subsequent condition checks can move past state publication. `finish_wait()` intentionally uses a careful lockless list-empty test that is safe only because other modifiers take the queue lock. Wake callbacks that delete themselves or return negative values affect scan progress. `__wake_up_pollfree()` is sensitive because poll users must detach before the wait-queue head is destroyed. Interruptible helpers return with the queue lock still held on signal failure, matching their documented calling convention.

## Test Signals

Useful tests include repeated wait-event and wake-up races under SMP stress, exclusive waiter fairness and wake count behavior, priority-exclusive insertion conflict handling, signal interruption of `prepare_to_wait_event()` and `do_wait_intr*()`, pollfree teardown with epoll users, kthread stop/park while in `wait_woken()`, and lockdep coverage for locked versus unlocked wake APIs.
