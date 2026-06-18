<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/swait.c -->
# sources/distributed-fs/ceph-client/kernel/sched/swait.c

## Purpose
`swait.c` implements simple wait queues, a lighter wait primitive used by kernel code that needs exclusive waiters and small, predictable wakeup behavior. It backs APIs declared in `<linux/swait.h>`.

## Important APIs, Types, And Functions
The exported functions are `__init_swait_queue_head`, `swake_up_locked`, `swake_up_one`, `swake_up_all`, `prepare_to_swait_exclusive`, `prepare_to_swait_event`, and `finish_swait`. Internal helpers include `swake_up_all_locked`, `__prepare_to_swait`, and `__finish_swait`.

## Control Flow
Initialization sets up the raw spinlock lockdep class and waiter list. `__prepare_to_swait` records `current` in the waiter and appends it if not already linked. `prepare_to_swait_exclusive` and `prepare_to_swait_event` take the queue lock, enqueue the waiter, and set task state; the event variant removes the waiter and returns `-ERESTARTSYS` if the target state is interruptible and a signal is pending.

Wakeup is FIFO over `q->task_list`. `swake_up_locked` wakes the first waiter with `try_to_wake_up(..., TASK_NORMAL, wake_flags)` and removes it. `swake_up_one` wraps that under IRQ-safe locking. `swake_up_all_locked` repeatedly wakes while the caller already holds the lock; `swake_up_all` splices the list to a temporary list and drops/reacquires the lock between wakeups to bound lock hold time, so it is not for IRQ-disabled regions. Finish paths set the current task running and remove the waiter if still linked.

## State And Persistence
State is only the in-memory `swait_queue_head` raw spinlock and linked list of `swait_queue` entries, each pointing at a task. There is no persistence beyond the lifetime of the wait queue and wait entries.

## Dependencies And Integration Points
The implementation depends on `sched.h`, task states, `try_to_wake_up`, `wake_up_state`, raw spinlocks, lockdep, linked lists, signal-state checks, and exported symbol infrastructure. It integrates with completions and other kernel primitives that choose simple wait queues over full wait queues.

## Risks And Edge Cases
Wait entries must be initialized and finished correctly; stale list linkage can corrupt the queue or cause missed wakeups. `swake_up_locked` assumes the caller holds the queue lock. `swake_up_all` deliberately cannot be used with IRQs disabled because it may release the lock between wakeups. The wake return value is ignored because an already-running waiter should still observe its condition, but callers must use condition loops correctly.

## Test Signals
Useful signals are completion tests, signal-interrupted waits, lockdep on raw-spin use, IRQ-context users of `swake_up_all_locked`, and stress that repeatedly enqueues, wakes one, wakes all, times out, and finishes waiters without list corruption or missed wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/sched/swait.c -->
