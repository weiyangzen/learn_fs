# sources/distributed-fs/ceph-client/include/linux/irqdomain.h

## Purpose
`irqdomain.h` defines the hardware-to-Linux IRQ translation framework: firmware specs, domain creation/removal, reverse maps, legacy/linear/tree/nomap/hierarchical domains, mapping allocation, stock translators, IPI reservations, MSI/wired helpers, and generic-chip integration.

## Important APIs, types, and functions
Key types are `struct irq_fwspec`, `struct irq_fwspec_info`, `struct irq_domain_ops`, `struct irq_domain`, and `struct irq_domain_info`. APIs include fwnode allocation/free, `irq_domain_instantiate`, devm/simple/legacy/linear/tree/hierarchy creators, domain finders, mapping create/dispose/resolve helpers, stock xlate/translate functions, `irq_domain_set_info`, hierarchical alloc/free/activate/deactivate/push/pop/parent helpers, IPI reserve/destroy, and MSI wired helpers.

## Control flow
Firmware supplies interrupt specifiers. Domain ops match/select, translate hwirqs/types, map descriptors, allocate/free hierarchical IRQs, and activate/deactivate hardware. Reverse maps use linear arrays or radix trees to resolve hwirq to descriptor/virq during interrupt dispatch.

## State and persistence
Runtime state includes domain list links, fwnode, bus token, flags, mapcount, root mutex, parent, MSI parent ops, host data, generic chips, PM device, hwirq limits, radix reverse map, and appended linear revmap.

## Dependencies and integration points
It depends on OF/fwnode, mutexes, radix trees, irq chips/data/descriptors, generic MSI, generic chips, and device-managed resources. It is the core integration layer for irqchips, GPIO, MSI, IPIs, and firmware descriptions.

## Risks and test signals
Risks include duplicate fwnode/bus-token domains, reverse-map leaks, hierarchy parent allocation rollback, wrong trigger translation, stale fwnodes, and no-map/direct-map misuse. Tests should cover each domain type, DT/ACPI fwspec translation, mapping create/dispose races, hierarchical MSI allocation, IPI domains, generic chip removal, and disabled `CONFIG_IRQ_DOMAIN` stubs.
