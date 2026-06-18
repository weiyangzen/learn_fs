# sources/distributed-fs/ceph-client/include/linux/irq.h

## Purpose
`irq.h` is the central generic IRQ subsystem contract for architecture and interrupt-controller code. It defines IRQ trigger/status bits, per-IRQ data objects, `irq_chip` callbacks, generic IRQ chip helpers, descriptor allocation, flow handlers, affinity, hierarchy propagation, IPI helpers, and top-level IRQ handler registration.

## Important APIs, types, and functions
Core types include `struct irq_common_data`, `struct irq_data`, `struct irq_chip`, `struct irq_chip_regs`, `struct irq_chip_type`, `struct irq_chip_generic`, domain generic-chip info, and `struct irq_matrix`. Important APIs cover `irqd_*` accessors, built-in handlers, parent-chip helpers, `irq_set_chip_and_handler*`, status modifiers, chip/data getters, descriptor allocation/freeing, generic chip callbacks/setup, register read/write wrappers, IRQ matrix alloc/free, IPI send helpers, and `set_handle_irq`.

## Control flow
IRQ domains allocate descriptors and attach `irq_data` to chips. Flow handlers call chip callbacks for ack/mask/eoi/unmask and actions. Affinity and wake state propagate through `irq_chip` methods and, for stacked domains, parent helper functions. Generic chip setup maps register offsets and bit masks into reusable handlers.

## State and persistence
State is runtime interrupt metadata: trigger type, disabled/masked/in-progress flags, affinity masks, MSI descriptors, chip/private data, generic chip mask caches, wake state, and IRQ matrix allocations.

## Dependencies and integration points
It depends on arch IRQ headers, `irqdesc.h`, cpumasks, topology, I/O accessors, MSI, irqdomain hierarchy, SMP migration, power management, kexec, and proc/debugfs display.

## Risks and test signals
Risks include direct mutation of accessor-protected state, broken chip callback ordering, affinity migration races, stale generic-chip mask caches, hierarchy parent failures, and invalid descriptor lifetime. Tests should cover all trigger types, chained/stacked chips, managed affinity CPU hotplug, suspend/wake, MSI compose/write, IPI domains, generic-chip register access, and spurious interrupt accounting.
