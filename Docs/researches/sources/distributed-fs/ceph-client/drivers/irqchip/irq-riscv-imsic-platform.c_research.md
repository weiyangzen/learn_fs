<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-platform.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-platform.c

## Purpose
`irq-riscv-imsic-platform.c` creates the IMSIC MSI parent domain used by platform and PCI MSI consumers after early IMSIC state has been initialized.

## Important APIs, Types, and Functions
Important helpers include `imsic_cpu_page_phys()`, IRQ chip callbacks `imsic_irq_mask()`, `imsic_irq_unmask()`, `imsic_irq_retrigger()`, `imsic_irq_ack()`, MSI composition helpers, SMP affinity move helpers, `imsic_irq_domain_alloc()`, `imsic_irq_domain_free()`, debugfs show, `imsic_init_dev_msi_info()`, `imsic_msi_parent_ops`, `imsic_irqdomain_init()`, and DT/ACPI probe entry points.

## Control Flow
The base IRQ domain allocates one IMSIC vector per Linux IRQ from the global matrix, installs the IMSIC IRQ chip with `handle_edge_irq`, marks it noprobe, and sets affinity to online CPUs. The chip composes MSI messages as a per-CPU IMSIC page address plus vector ID. Affinity changes allocate a new vector, optionally program a temporary vector for non-atomic MSI updates, write the final MSI message, update descriptor chip data and effective affinity, and move pending state between vectors. Platform probe verifies the early fwnode matches and calls `imsic_irqdomain_init()`.

## State and Persistence
The domain stores per-IRQ `struct imsic_vector` chip data. Vector enable/move state is maintained by `irq-riscv-imsic-state.c`. The base domain is singleton `imsic->base_domain` and cannot be created twice.

## Dependencies and Integration Points
It depends on MSI lib parent-domain helpers, IMSIC state exports, PCI/platform MSI bus tokens, irq matrix allocation, SMP affinity infrastructure, generic IRQ debugfs, and ACPI early probe ordering.

## Risks and Edge Cases
Multi-MSI allocation is explicitly unsupported. PCI MSI/MSI-X domains get `IRQCHIP_MOVE_DEFERRED` for non-atomic device message updates. A missing early IMSIC probe or fwnode mismatch fails domain creation. Freeing assumes the chip data vector is valid.

## Test Signals
Test platform and PCI MSI allocation, MSI message address/data composition, retrigger via MMIO write, affinity migration with deferred and immediate moves, debugfs vector display, ACPI early domain creation before PCI scan, and multi-MSI rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-platform.c -->
