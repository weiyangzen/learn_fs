# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-main.c

Purpose: is the PCI driver entry point for ddbridge. It registers the PCI driver, maps BAR0, sets DMA masks, initializes interrupts/MSI, identifies board metadata, and delegates device setup to `ddbridge-core.c`.

Important APIs/types/functions: `ddb_probe()`, `ddb_remove()`, `ddb_irq_init()`, `ddb_irq_exit()`, `ddb_msi_exit()`, `module_init_ddbridge()`, and `module_exit_ddbridge()`. The PCI ID table matches many Digital Devices device IDs using `DDB_DEVICE_ANY()`. The `msi` module parameter controls MSI/MSI-X use when configured.

Control flow: module init calls `ddb_init_ddbridge()` then `pci_register_driver()`. Probe enables the PCI device, sets bus mastering and DMA mask, allocates `struct ddb`, fills link IDs, calls `get_ddb_info()`, maps registers, reads HW/regmap IDs, disables DMA bases, requests IRQs, and calls `ddb_init()`. Remove unwinds sysfs/DVB/I2C/IRQ/MSI/DMA/MMIO/PCI state.

State and persistence: per-device state is allocated with `vzalloc()` and stored via `pci_set_drvdata()`. `dev->msi` records allocated vectors. No durable state is stored.

Dependencies/integration: integrates PCI core, DMA API, interrupt APIs, board metadata from `ddbridge-hw.c`, core lifecycle, I2C release, MMIO helpers, and register constants.

Risks and test signals: error unwinds must match initialization order; `dma_set_mask()` failure after `pci_enable_device()` is a sensitive path; MSI split interrupt handling depends on hardware mask programming. Test with module load/unload, legacy IRQ and MSI modes, unsupported boards, BAR read failure, and active-stream device removal.
