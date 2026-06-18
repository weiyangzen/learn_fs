# sources/distributed-fs/ceph-client/kernel/irq/migration.c

## Purpose
`migration.c` handles pending IRQ affinity moves, especially when interrupts must be migrated while masked or during CPU hotplug. It completes, clears, or defers move-pending state around irqchip affinity callbacks.

## Important APIs, types, and functions
The file exports `irq_fixup_move_pending()`, `irq_force_complete_move()`, `irq_move_masked_irq()`, `__irq_move_irq()`, and `irq_can_move_in_process_context()`. It operates on `struct irq_desc`, `struct irq_data`, descriptor `pending_mask`, and irqdata move-pending flags.

## Control flow
CPU hotplug cleanup checks whether a pending mask still intersects online CPUs and clears move-pending when it no longer has a valid target or when forced. Masked move handling clears move-pending, rejects per-CPU or empty masks, requires `irq_set_affinity`, and calls `irq_do_set_affinity()` while the line is masked; `-EBUSY` re-establishes pending state for a later interrupt. `__irq_move_irq()` masks the interrupt when needed, delegates to `irq_move_masked_irq()`, and restores mask state.

## State and persistence
State is descriptor-local and transient: `IRQD_SETAFFINITY_PENDING`, `desc->pending_mask`, and irqchip/vector migration state. There is no persistence outside live descriptor state.

## Dependencies and integration points
It depends on genirq affinity helpers in `manage.c`, irqchip callbacks, descriptor locking rules, CPU online masks, and hierarchical top-level irqdata resolution. Flow handlers call these helpers when safe to move an IRQ.

## Risks and test signals
Risks include losing pending affinity when the last target CPU goes offline, reprogramming an unmasked edge interrupt, move storms when vector cleanup returns `-EBUSY`, and invalid calls for per-CPU interrupts. Test signals include CPU down with pending moves, edge-triggered IO-APIC-like interrupts, vector allocator busy responses, process-context-capable chips, and forced completion callbacks in parent irqdata chains.
