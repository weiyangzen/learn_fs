# sources/distributed-fs/ceph-client/kernel/irq/handle.c

## Purpose
`handle.c` runs registered IRQ actions once a flow handler has decided an interrupt is serviceable. It handles bad IRQs, no-op actions, threaded handler wakeups, optional long-duration warnings, interrupt randomness/spurious accounting, and architecture root IRQ dispatch for `GENERIC_IRQ_MULTI_HANDLER`.

## Important APIs, types, and functions
Public functions include `handle_bad_irq()`, `no_action()`, `__irq_wake_thread()`, `__handle_irq_event_percpu()`, `handle_irq_event_percpu()`, `handle_irq_event()`, `set_handle_irq()`, and `generic_handle_arch_irq()`. Key state includes `handle_arch_irq`, static key `irqhandler_duration_check_enabled`, and `irqhandler_duration_threshold_ns`.

## Control flow
`handle_irq_event()` clears pending state, marks the irq in-progress, drops the descriptor lock, calls `handle_irq_event_percpu()`, then reacquires the lock and clears in-progress. The per-action loop traces entry/exit, optionally measures handler duration, calls each primary handler, warns if it re-enables interrupts, and wakes the IRQ thread when the result is `IRQ_WAKE_THREAD`. Thread wakeup sets `IRQTF_RUNTHREAD`, updates `threads_oneshot`, increments `threads_active`, and wakes the kthread. Root arch handling wraps the architecture handler in `irq_enter()`, irq-reg save/restore, and `irq_exit()`.

## State and persistence
The file mutates descriptor in-progress and pending bits, action thread flags, oneshot masks, and active thread counters. Duration warning configuration is boot-time state from `irqhandler.duration_warn_us=`. No state is persisted beyond runtime.

## Dependencies and integration points
It integrates with flow handlers in `chip.c`, threaded IRQ management in `manage.c`, spurious detection in `spurious.c`, tracepoints, lockdep hardirq-thread annotations, randomness, per-CPU stats, scheduler kthreads, and architecture entry code.

## Risks and test signals
Risks include lost threaded wakeups, incorrect oneshot mask serialization, handlers enabling IRQs, long-duration static key overhead, lock state mismatches around action execution, and root handler registration races. Test signals include shared IRQ return aggregation, `IRQ_WAKE_THREAD` with and without `thread_fn`, oneshot threaded interrupts, duration warning boot parameter, handler tracepoints, spurious accounting, and architecture multi-handler registration.
