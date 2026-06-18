# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_init.c

Purpose: PCI driver, module lifecycle, libsas transport registration, sysfs attributes, BIOS update interface, resource mapping, and probe/remove orchestration for the AIC94xx driver.

Important APIs/types/functions: `aic94xx_init()` creates global caches, attaches the SAS transport, registers the PCI driver, and creates a driver `version` attribute. `asd_pci_probe()` enables PCI, allocates SCSI host and `asd_ha_struct`, sets DMA mask, maps BARs/IO ports, creates DMA pools, calls `asd_init_hw()`, requests IRQ/MSI, posts ESCBs, creates device attrs, registers the SAS HA, and starts scanning. `asd_pci_remove()` reverses those resources. `asd_store_update_bios()` validates requested firmware and calls flash update/verify helpers.

Control flow: probe is a staged setup with labeled error unwinding. Scan start enables configured PHYs; scan finish waits at least one second then drains libsas work. Remove unregisters libsas, disables interrupts, kills done-list tasklet, removes attrs, frees IRQ/MSI, turns off LEDs, hard-resets chip, frees pending queues/caches, unmaps IO, and disables PCI.

State and persistence: module globals include `use_msi`, transport template, and slab caches. Per-device state includes BAR mappings, SCSI host, sysfs attributes, BIOS status, and firmware image pointer. BIOS update/verify can persistently alter adapter flash via SDS helpers.

Dependencies and integration: integrates Linux PCI, SCSI host, libsas, sas_ata sysfs groups, firmware loader, DMA masks/pools, interrupts, and the hwi/SDS/seq/task/TMF implementation files.

Risks and test signals: BIOS update parsing uses sysfs input and firmware bytes; validation of PCI IDs, length, and checksum is critical. Probe unwinding must remain balanced across many labels. `asd_unregister_sas_ha()` calls both `sas_unregister_ha()` and host removal/put, so ordering matters. Test signals include module load/unload, probe failure injection at every stage, MSI and shared IRQ paths, sysfs attr reads, BIOS verify/update failure codes, and scan/discovery timing.
