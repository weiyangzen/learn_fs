# sources/distributed-fs/ceph-client/kernel/irq/resend.c

## Purpose
`resend.c` retries pending edge interrupts that may have arrived while disabled or masked. It prefers hardware retrigger support and falls back to a software tasklet resend when configured.

## Important APIs, types, and functions
Important functions are `check_irq_resend()`, optional `irq_inject_interrupt()`, `clear_irq_resend()`, and `irq_resend_init()`. Software resend uses `irq_resend_list`, `irq_resend_lock`, `resend_tasklet`, `resend_irqs()`, and `irq_sw_resend()`. Hardware retry uses `try_retrigger()` and irqchip `irq_retrigger` or hierarchy retrigger callbacks.

## Control flow
`check_irq_resend()` runs with interrupts disabled and `desc->lock` held. It rejects level-triggered IRQs, avoids duplicate replay, clears pending state, attempts hardware retrigger, falls back to software enqueue, and marks `IRQS_REPLAY` on success. Software resend queues the descriptor on an hlist and later invokes `desc->handle_irq()` from the tasklet. Generic injection first tries `irq_set_irqchip_state(...PENDING...)`, then uses resend for activated non-NMI interrupts.

## State and persistence
Runtime state is `IRQS_PENDING`, `IRQS_REPLAY`, each descriptor `resend_node`, and the global software resend list. There is no persistent storage.

## Dependencies and integration points
It depends on irq descriptor internals, irqchip retrigger/state callbacks, tasklets, nested-thread parent IRQ routing, hierarchy helpers, and optional `CONFIG_GENERIC_IRQ_INJECTION` testing support.

## Risks and test signals
Risks include resending level IRQs incorrectly, invoking handlers from unsuitable context, nested threaded IRQs without valid parent IRQs, replay bit not clearing in flow handlers, list races during descriptor teardown, and injection perturbing affinity changes. Test signals include disabled edge IRQ pending replay, chips with and without hardware retrigger, nested threaded interrupts, software resend disabled builds, clear during free, and debug injection success/failure paths.
