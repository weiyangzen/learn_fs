<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_irq.h -->
# sources/distributed-fs/ceph-client/include/linux/of_irq.h

## Purpose
This header declares OF interrupt parsing, interrupt-map iteration, irqdomain mapping, MSI domain lookup, and platform IRQ initialization interfaces.

## Important APIs, types, and functions
`of_irq_init_cb_t` names early IRQ controller init callbacks. `struct of_imap_parser` and `struct of_imap_item` support parsing `interrupt-map`. Workaround flags support old 32-bit PowerMac mappings. Core APIs include `of_irq_parse_raw()`, `irq_create_of_mapping()`, `of_irq_to_resource()`, `of_irq_init()`, `of_irq_parse_one()`, `of_irq_count()`, `of_irq_get()`, `of_irq_get_byname()`, `of_irq_get_affinity()`, `of_irq_to_resource_table()`, `of_irq_find_parent()`, interrupt-map parser helpers, OF MSI domain lookup/configuration/xlate, and `irq_of_parse_and_map()`.

## Control flow
Drivers parse an indexed or named interrupt specifier from a device node, find the interrupt parent, translate raw cells through interrupt maps/irqdomains, and create Linux IRQ mappings. Early boot calls `of_irq_init()` over OF-declared interrupt controllers. MSI paths locate a matching MSI irqdomain and configure device MSI state. Disabled `CONFIG_OF_IRQ` stubs return zero, `NULL`, or errno, while SPARC keeps `irq_of_parse_and_map()` declared separately.

## State and persistence
Parser structs hold transient cursor and parent-args state; callers must release `item.parent_args.np` on premature iterator exit. Persistent state is irqdomain mappings, irq resources, MSI configuration, and legacy workaround globals on PowerMac.

## Dependencies and integration points
It depends on OF, `linux/irq.h`, irqdomains, resources, cpumasks, device model, MSI domains, and architecture-specific SPARC/PPC behavior.

## Risks and test signals
Risks include leaked parent node references, incorrect interrupt-cell counts, oldworld PowerMac workaround regressions, MSI token mismatch, missing affinity data, and disabled-stub return values hiding absent IRQs. Test interrupt-map parsing, named/indexed IRQ lookup, IRQ resource tables, MSI domains, SPARC/PPC builds, irqdomain mapping failures, and `!CONFIG_OF_IRQ` compile paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_irq.h -->
