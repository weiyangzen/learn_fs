# sources/distributed-fs/ceph-client/drivers/acpi/irq.c

Purpose: `irq.c` is the ACPI GSI-to-Linux-IRQ mapping layer. It tracks the active ACPI IRQ model, maps and unmaps GSIs through irqdomains, parses IRQ resources from `_CRS`, exposes IRQ resource lookup to drivers, and creates child IRQ hierarchies for GIC systems.

Important APIs, types, and functions: exported APIs include `acpi_gsi_to_irq()`, `acpi_register_gsi()`, `acpi_unregister_gsi()`, `acpi_irq_get()`, `acpi_get_gsi_dispatcher()`, and `acpi_irq_create_hierarchy()`. Init-time setters are `acpi_set_irq_model()` and `acpi_set_gsi_to_irq_fallback()`. Internal parsing revolves around `struct acpi_irq_parse_one_ctx`, `acpi_irq_parse_one_cb()`, and `acpi_irq_parse_one()`.

Control flow: architecture setup calls `acpi_set_irq_model()` with a dispatcher returning the fwnode for a GSI. GSI registration builds an `irq_fwspec` with hardware GSI and trigger/polarity type, then creates an irqdomain mapping. `_CRS` lookup walks IRQ and Extended IRQ resources, skips producer Extended IRQs, counts through interrupt arrays by index, resolves resource-source fwnodes, fills Linux resource flags, and creates a mapping for the selected interrupt. Affinity lookup reuses the same parse path and asks irq core for fwspec affinity metadata.

State and persistence: global state is `acpi_irq_model`, the GSI-domain dispatcher, and an optional arch fallback from GSI to IRQ. IRQ mappings persist in the irqdomain core until unregistered or disposed.

Dependencies and integration: depends on ACPI resource descriptors, fwnode handles, irqdomain APIs, architecture interrupt-controller setup, and device resource consumers such as platform and GED drivers.

Risks: callers rely on dispatcher initialization before mapping; otherwise registration fails. Extended IRQ resource-source lookup can fail if firmware names are wrong. `acpi_unregister_gsi()` refuses to dispose GIC SGIs below 16 but other incorrect unmaps can still disrupt shared mappings. Missing irqdomains return `-EPROBE_DEFER` from `acpi_irq_get()`, so drivers need retry-safe probe paths.

Test signals: verify GSI mapping for IRQ and Extended IRQ resources, resource-source fwnode lookup, index handling across multi-interrupt resources, trigger/polarity/share/wake flags, fallback GSI mapping, GIC hierarchy creation, affinity extraction, and unregister behavior.
