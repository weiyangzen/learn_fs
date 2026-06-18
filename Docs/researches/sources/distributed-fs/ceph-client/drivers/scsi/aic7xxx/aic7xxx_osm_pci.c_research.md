# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_osm_pci.c

Purpose: Linux PCI attachment glue for `aic7xxx` adapters. It binds PCI IDs to the kernel PCI driver model, allocates and configures `ahc_softc` instances, maps register resources, hooks interrupts, handles power management, and forwards PCI config access for the portable PCI logic.

Important APIs and functions: `ahc_linux_pci_id_table`, `aic7xxx_pci_driver`, `ahc_linux_pci_init()`, `ahc_linux_pci_exit()`, `ahc_linux_pci_dev_probe()`, `ahc_linux_pci_dev_remove()`, suspend/resume callbacks, `ahc_pci_read_config()`, `ahc_pci_write_config()`, `ahc_pci_map_registers()`, and `ahc_pci_map_int()`.

Control flow: PCI core matches IDs, probe calls `ahc_find_pci_device()`, allocates a named `ahc_softc`, enables the device, sets bus mastering, chooses 39-bit DMA when supported or falls back to 32-bit DMA, assigns device pointers, calls `ahc_pci_config()`, inherits BIOS/channel flags for secondary multifunction devices, stores drvdata, and registers the SCSI host. Removal unregisters the SCSI host, disables interrupts under lock, and frees the adapter. Register mapping prefers MMIO BAR1, validates it with `ahc_pci_test_register_access()`, and falls back to PIO BAR0. IRQ mapping requests a shared interrupt and stores the assigned IRQ.

State and persistence: runtime state is held in PCI drvdata, `ahc->dev_softc`, `ahc->dev`, bus-space tag/handle, `platform_data->mem_busaddr`, and `platform_data->irq`. No persistence is written. PM resume restores through `ahc_pci_resume()` and core resume.

Dependencies and integration: uses Linux PCI driver, DMA mask, resource, ioremap, IRQ, and PM APIs. It depends on ID constants from `aic7xxx_pci.h`, common hardware configuration in `aic7xxx_pci.c`, and SCSI host registration from `aic7xxx_osm.c`.

Risks: probe error paths must free allocations after `ahc_alloc()`/`pci_enable_device()`; incorrect DMA mask selection can break high-memory transfers; MMIO validation must detect broken mappings before enabling memory access; multifunction inheritance assumes function 0 is already bound. The IO-region helper is gated by `aic7xxx_allow_memio`, despite being the PIO fallback, so option semantics deserve attention.

Test signals: PCI ID table coverage, probe/remove cycles, MMIO and forced- PIO mapping, shared IRQ delivery, DMA mask behavior on >32-bit systems, suspend/resume, multifunction adapters, and failure injection around resource requests and `scsi_add_host()`.
