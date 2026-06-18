# sources/distributed-fs/ceph-client/kernel/irq/irqdomain.c

## Purpose
`irqdomain.c` is the generic IRQ-domain core. It maps hardware interrupt numbers and firmware interrupt specifiers to Linux virtual IRQ descriptors, publishes and removes interrupt domains, manages reverse maps, and implements the allocation/free/activation path for hierarchical interrupt controllers.

## Important APIs, types, and functions
Global state is `irq_domain_list`, `irq_domain_mutex`, and `irq_default_domain`. `struct irqchip_fwid` backs synthetic fwnodes created by `__irq_domain_alloc_fwnode()` and destroyed by `irq_domain_free_fwnode()`. Creation and lifecycle entry points include `irq_domain_instantiate()`, `irq_domain_create_simple()`, `irq_domain_create_legacy()`, `irq_domain_remove()`, and `irq_domain_update_bus_token()`. Mapping APIs include `irq_find_matching_fwspec()`, `irq_create_mapping_affinity()`, `irq_create_fwspec_mapping()`, `irq_create_of_mapping()`, `irq_dispose_mapping()`, and `__irq_resolve_mapping()`. Hierarchy-specific APIs include `__irq_domain_alloc_irqs()`, `irq_domain_free_irqs()`, `irq_domain_alloc_irqs_parent()`, `irq_domain_free_irqs_parent()`, `irq_domain_push_irq()`, `irq_domain_pop_irq()`, `irq_domain_activate_irq()`, and `irq_domain_deactivate_irq()`.

## Control flow
Domain instantiation allocates the `struct irq_domain`, derives a debugfs-safe name from fwnode or bus token data, initializes revmap storage, attaches generic chips and parent/root hierarchy metadata when configured, publishes the domain on the global list, and optionally pre-associates legacy fixed virqs. Firmware mapping first resolves a domain from fwspec/fwnode and bus token, translates the specifier to hwirq/type through `.translate` or `.xlate`, reuses an existing mapping when type-compatible, otherwise allocates descriptors and either associates a flat domain mapping or invokes hierarchical allocation. Free paths remove mappings, clear handlers/chips, synchronize interrupt execution, call domain `.free`/`.unmap`, free hierarchy `irq_data`, and release descriptors.

## State and persistence
All state is in-memory kernel state: domain list membership, fwnode references, `domain->mapcount`, linear and radix-tree reverse maps, default-domain pointer, domain flags, hierarchy `irq_data` chains, and debugfs dentries. Nothing persists across boot, but mappings remain authoritative while descriptors and domains live.

## Dependencies and integration points
This file integrates firmware descriptions from OF, ACPI, software nodes, synthetic irqchip fwnodes, irq descriptors, generic chips, MSI helper hooks, hierarchical irqchips, RCU-protected lookup, debugfs, radix trees, and module-exported genirq APIs. Device-tree xlate helpers and fwspec translate helpers provide common binding formats for interrupt-controller drivers.

## Risks and test signals
Important risks are domain name collisions, leaked fwnode references, revmap corruption during hierarchy push/pop, type mismatches on reused mappings, races between lookup and removal, missing synchronize before descriptor reuse, invalid hierarchy trimming markers, MSI wired-domain special cases, and debugfs lifetime bugs. Test signals include simple and legacy domain creation, OF/fwspec mapping reuse, type mismatch rejection, radix revmap entries beyond linear size, hierarchical parent allocation rollback, push/pop before request_irq, activate failure rollback, domain removal with nonempty revmaps, and debugfs output for parent chains.
