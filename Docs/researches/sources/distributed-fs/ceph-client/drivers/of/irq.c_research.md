# sources/distributed-fs/ceph-client/drivers/of/irq.c

## Purpose
`irq.c` resolves devicetree interrupt descriptions into Linux IRQ mappings. It parses `interrupts`, `interrupts-extended`, `interrupt-parent`, and `interrupt-map`, initializes interrupt controllers in parent-first order, and resolves MSI parent/domain mappings.

## Important APIs, types, and functions
Exports include `irq_of_parse_and_map()`, `of_irq_find_parent()`, `of_imap_parser_init()`, `of_imap_parser_one()`, `of_irq_parse_raw()`, `of_irq_parse_one()`, `of_irq_to_resource()`, `of_irq_get()`, `of_irq_get_byname()`, `of_irq_count()`, `of_irq_to_resource_table()`, `of_irq_init()`, `of_msi_xlate()`, `of_msi_get_domain()`, and `of_msi_configure()`. `struct of_intc_desc` stages interrupt-controller initialization. `of_irq_imap_abusers` lists legacy controllers whose `interrupt-map` must be ignored by core parsing.

## Control flow and state
`of_irq_parse_one()` copies the device `reg` address into a bounded buffer, prefers `interrupts-extended`, otherwise finds the interrupt parent and reads `interrupts` cells, then calls `of_irq_parse_raw()`. Raw parsing verifies `#interrupt-cells`, builds a match array from address and interrupt specifier cells, walks interrupt-map translations, and stops at an interrupt-controller unless a valid map overrides it. Successful parse returns a referenced controller node.

`of_irq_get()` converts parsed phandle args into an IRQ domain mapping, returning `-EPROBE_DEFER` if the domain is not registered yet. `of_irq_init()` scans matched interrupt controllers, computes their parents, then initializes roots before children. MSI helpers walk up device parents and use `msi-map`, `msi-map-mask`, or simple `msi-parent` to select a target node and ID.

## Dependencies and integration
The file integrates with irqdomain, resource creation, OF phandle parsing, `of_map_id()`, platform IRQ controller drivers, MSI domains, and architecture workarounds such as OldWorld Mac parsing and `OF_IMAP_NO_PHANDLE`.

## Risks and test signals
Risks include malformed `interrupt-map` lengths, parent phandle leaks, unavailable domains, old firmware workarounds, address-cell mismatch, self-referential maps, and unsupported multiple MSI parents. Test signals include boot interrupt-controller order, deferred-probe behavior, resource tables, MSI device domains, and interrupt-map parser users.
