<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swait.h -->
# sources/distributed-fs/ceph-client/include/linux/swait.h

## Purpose

`swait.h` defines simple wait queues, a restricted waitqueue variant designed for deterministic lock and IRQ behavior, especially under realtime constraints. It intentionally removes many regular waitqueue features to keep wakeups bounded and simple.

## Important APIs, types, and functions

`struct swait_queue_head` contains a raw spinlock and waiter list. `struct swait_queue` stores the task and list node. Initializer macros create queue heads and waiters, including lockdep-aware on-stack initialization. Core APIs include `swait_active()`, `swq_has_sleeper()`, `swake_up_one()`, `swake_up_all()`, `swake_up_locked()`, `prepare_to_swait_exclusive()`, `prepare_to_swait_event()`, `__finish_swait()`, and `finish_swait()`. Wait macros provide uninterruptible, interruptible, idle, and timeout-exclusive waits.

## Control flow

Waiters initialize a local `swait_queue`, call `prepare_to_swait_event()` in a loop, check the condition, schedule if unmet, and finish with `finish_swait()`. Wakers call one/all wake helpers. All sleepers are exclusive and wakeups target `TASK_NORMAL` semantics, avoiding mixed-state scans and custom callbacks.

## State and persistence behavior

Queue state is the protected task list plus each waiter's current task pointer. `swait_active()` is lockless and only safe with the documented locking or memory-barrier pairing. Timeout macros return remaining jiffies or interrupt status.

## Dependencies and integration points

It depends on lists, raw spinlocks, regular wait macros, current task access, and scheduler state constants. It integrates with RT-sensitive kernel subsystems that need bounded wakeup behavior.

## Risks and test signals

Risks include missed wakeups when using `swait_active()` without barriers, misuse where nonexclusive or custom wake behavior is required, calling `swake_up_all()` from IRQ-disabled contexts contrary to design, and condition expressions with side effects. Tests should cover one/all wakeups, interruptible return paths, timeout return values, idle waits not contributing to load, lockdep initialization, and memory-order patterns around lockless active checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swait.h -->
