# sources/distributed-fs/ceph-client/kernel/irq/spurious.c

## Purpose
`spurious.c` detects and mitigates bad, unhandled, or misrouted interrupts. It reports bogus handler returns, counts repeated unhandled interrupts, disables lines that appear stuck, and optionally polls shared handlers to recover misrouted IRQs.

## Important APIs, types, and functions
The primary entry point is `note_interrupt()`, called after IRQ handlers return. Recovery helpers include `try_one_irq()`, `misrouted_irq()`, and `poll_spurious_irqs()`. Diagnostics use `bad_action_ret()`, `__report_bad_irq()`, and `report_bad_irq()`. Boot/module controls are `noirqdebug_setup()`, `irqfixup_setup()`, `irqpoll_setup()`, `noirqdebug`, and `irqfixup`.

## Control flow
Handler returns are validated first. Threaded IRQ wakeups defer spurious accounting until the next hard interrupt so thread completion can be observed. `IRQ_NONE` updates recent unhandled counters with a decay window. When fixup/polling is enabled, the code polls other shared IRQ handlers looking for a misrouted interrupt and compensates the unhandled count if one handled it. After 100,000 samples, if more than 99,900 were unhandled, it reports handlers, marks the IRQ spurious-disabled, increments depth, disables the line, and starts a timer to periodically poll disabled shared lines.

## State and persistence
State lives in descriptor counters and bits: `irq_count`, `irqs_unhandled`, `last_unhandled`, `threads_handled`, `threads_handled_last`, `IRQS_POLL_INPROGRESS`, `IRQS_PENDING`, and `IRQS_SPURIOUS_DISABLED`. Global runtime state includes `irqfixup`, `noirqdebug`, `irq_poll_cpu`, `irq_poll_active`, and the poll timer.

## Dependencies and integration points
It depends on timer/jiffies, module parameters and boot options, genirq flow handling, shared IRQ actions, descriptor locking, `handle_irq_event()`, and settings helpers for per-CPU/nested/polled/no-debug behavior. It is part of the post-handler accounting path for normal interrupts.

## Risks and test signals
Risks include false disabling of a rarely handled shared line, high overhead from `irqpoll`, PREEMPT_RT incompatibility for fixup options, races with action removal during diagnostics, deferred threaded accounting mistakes, and polling handlers that are not safe when the device did not interrupt. Test signals include bogus return values, repeated `IRQ_NONE`, shared threaded handlers, `irqfixup` and `irqpoll` boot options, spurious-disabled polling recovery, handler removal during reporting, and `noirqdebug` disabling lockup detection.
