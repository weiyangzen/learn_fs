# sources/distributed-fs/ceph-client/kernel/irq/cpuhotplug.c

## Purpose
`cpuhotplug.c` migrates interrupts away from CPUs going offline and restores managed interrupt affinity when CPUs come online. It protects both ordinary affinity masks and managed MSI-style interrupts across CPU hotplug and isolation scenarios.

## Important APIs, types, and functions
Public functions are `irq_migrate_all_off_this_cpu()` and `irq_affinity_online_cpu()`. Internal helpers are `irq_needs_fixup()`, `migrate_one_irq()`, `hk_should_isolate()`, and `irq_restore_affinity_of_irq()`. It uses `irq_fixup_move_pending()`, `irq_force_complete_move()`, `irq_do_set_affinity()`, managed-shutdown flags, pending masks, `cpu_online_mask`, and housekeeping masks.

## Control flow
During offline migration, every active IRQ is locked and passed to `migrate_one_irq()`. That function skips per-CPU, stopped, or non-affine interrupts, completes pending move cleanup, chooses a pending or current affinity mask, masks chips that cannot move in process context, shuts down managed IRQs with no online target, or reassigns non-managed IRQs to the online CPU mask if necessary. On CPU online, the code scans active IRQs under sparse-lock protection and restarts managed shutdown IRQs whose affinity includes the new CPU, then optionally updates affinity to isolate from non-housekeeping CPUs.

## State and persistence
State changes persist in descriptor and irqdata flags: pending move masks, effective affinity, managed shutdown, disable depth/start state, and optional affinity notification work. No state is external to the IRQ core.

## Dependencies and integration points
The file integrates with the CPU hotplug state machine, generic pending IRQ migration, managed IRQ affinity, housekeeping CPU isolation, irqchip affinity callbacks, and descriptor iteration. It relies on the outgoing CPU already being removed from `cpu_online_mask` when migration runs.

## Risks and test signals
Risks include failing to migrate an IRQ whose effective mask contains only the dying CPU, breaking user affinity unexpectedly, not preserving a pending setaffinity request, managed IRQ depth imbalance, `-ENOSPC` from vector allocation, and isolation behavior moving single-target IRQs unexpectedly. Test signals include CPU offline/online with managed and unmanaged IRQs, pending affinity move during hotplug, chips requiring mask during migration, no online CPU in affinity mask, vector exhaustion fallback, and housekeeping isolation configs.
