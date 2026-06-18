# sources/distributed-fs/ceph-client/drivers/misc/rp1/rp1_pci.c

Purpose: PCI driver for Raspberry Pi RP1 that maps the endpoint, allocates 61 MSI-X vectors, presents them as an OF IRQ domain for child devices, and populates RP1 subdevices from device tree.

Important APIs and types: `struct rp1_dev` stores PCI device, IRQ domain, backing PCI IRQ data per hardware IRQ, BAR1 mapping, and level-triggered flags. IRQ helpers are `msix_cfg_set/clr()`, `rp1_mask_irq()`, `rp1_unmask_irq()`, `rp1_irq_set_type()`, `rp1_chained_handle_irq()`, `rp1_irq_xlate()`, activate/deactivate hooks, and `rp1_unregister_interrupts()`. PCI lifecycle is `rp1_probe()`/`rp1_remove()`.

Control flow: probe requires an OF node, validates BAR1 length as firmware-initialized, enables PCI with pcim, maps BAR1, sets bus master, allocates exactly `RP1_INT_END` MSI-X vectors, creates a linear IRQ domain, maps each hwirq, sets the RP1 irq chip/handler, installs a chained handler on each PCI MSI-X vector, then calls `of_platform_default_populate()` to instantiate child devices. Chained handling masks through the parent MSI irq data, dispatches the mapped child virq, and acknowledges level-triggered interrupts via RP1 MSI-X config register.

State and persistence: per-device state is devm/pcim-managed except IRQ vectors/domain mappings, which are explicitly removed. Hardware MSI-X config bits persist until cleared/deactivated or device reset.

Dependencies and integration points: depends on OF IRQ domains, PCI MSI-X, Raspberry Pi vendor/device IDs, and child DT nodes for Ethernet/USB/I2C/SPI/UART and other RP1 blocks.

Risks and test signals: exact vector count is required; partial allocation fails. `rp1_irq_xlate()` trusts hwirq values from DT enough to index arrays, so DT validation matters. Cleanup should remove chained handlers/mappings before freeing vectors. Tests should cover missing OF node, short BAR/firmware-not-running case, vector allocation failure, level vs edge IRQ ack behavior, child device probe, and remove/depopulate ordering.
