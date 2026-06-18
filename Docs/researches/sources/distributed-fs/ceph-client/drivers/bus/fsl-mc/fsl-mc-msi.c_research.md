# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-msi.c

Purpose: provides MSI domain glue for `fsl-mc` devices. It creates FSL MC MSI IRQ domains, finds the right firmware-described domain for child objects, allocates/free MSI descriptors, and programs MSI address/data pairs into MC objects through DPRC commands.

Important APIs: `fsl_mc_msi_create_irq_domain()` adjusts MSI domain/chip callbacks and tags the domain as `DOMAIN_BUS_FSL_MC_MSI`; `fsl_mc_find_msi_domain()` maps OF `msi-map` or ACPI IORT domains using the device ICID; `fsl_mc_msi_domain_alloc_irqs()` and `fsl_mc_msi_domain_free_irqs()` wrap generic MSI allocation. Internally, `fsl_mc_domain_calc_hwirq()` combines ICID and MSI index, and `fsl_mc_msi_write_msg()` programs hardware.

Control flow: on domain creation, default ops are filled when requested: `set_desc` computes readable unique hwirqs, and `irq_write_msi_msg` stores the MSI message then calls `dprc_set_irq()` for a DPRC IRQ or `dprc_set_obj_irq()` for child-object IRQs. Allocation initializes device MSI data and allocates the requested range.

State and persistence: no persistent storage; state lives in generic MSI descriptors and the owning bus IRQ resource table. The MC firmware persists the programmed IRQ target until reprogrammed or object reset. Freeing with a zero MSI address is intentionally ignored because the MC does not require explicit unprogramming.

Dependencies and integration: depends on generic MSI domains, irqdomain, OF MSI mapping, ACPI IORT, FSL MC bus ICID/root traversal, and DPRC IRQ command wrappers. It integrates with `fsl_mc_device_add()` via inherited MSI domains and with MC allocator-provided `irq_resources`.

Risks: wrong owner-device association in `irq_resources` programs the wrong MC object; ICID-based hwirq construction must remain unique within the domain; level-capable domains are force-cleared; missing OF `msi-map` falls back to parent domain, which is intentional but platform-sensitive. Test signals are MSI allocation/free, interrupt delivery for DPRC and child objects, OF fallback behavior, ACPI IORT domain lookup, and error paths from `dprc_set_irq()`/`dprc_set_obj_irq()`.
