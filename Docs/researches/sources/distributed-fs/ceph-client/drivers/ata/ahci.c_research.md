# sources/distributed-fs/ceph-client/drivers/ata/ahci.c

Purpose: implements the PCI AHCI SATA low-level driver, binding a large PCI ID table to `ata_port_info` profiles, board quirks, power management, interrupt-vector setup, and libata/libahci host activation.

Important APIs/functions: `module_pci_driver(ahci_pci_driver)`, `ahci_init_one`, `ahci_remove_one`, `ahci_shutdown_one`, `ahci_pci_save_initial_config`, `ahci_pci_reset_controller`, `ahci_pci_init_controller`, `ahci_init_irq`, `ahci_configure_dma_masks`, `ahci_update_initial_lpm_policy`, and reset quirks `ahci_vt8251_hardreset`, `ahci_p5wdh_hardreset`, `ahci_avn_hardreset`. `ahci_port_info[]` maps chipset IDs to `AHCI_HFLAG_*` policy and custom port ops.

Control flow: probe rejects unsupported overlap modes, selects BARs, enables/maps PCI resources, allocates `ahci_host_priv`, applies chipset/DMI/remapped-NVMe quirks, saves capabilities, allocates `ata_host`, chooses IRQ mode, annotates ports, marks external ports, computes LPM policy, configures DMA masks, resets/initializes the HBA, prints capabilities, enables bus mastering, and activates the host. Remove/shutdown delegate to libata after sysfs cleanup.

State/persistence: module params (`marvell_enable`, `mobile_lpm_policy`, `mask_port_map`, `mask_port_ext`), PCI config, AHCI registers, saved caps/maps, IRQ vectors, DMA mask, LPM policy, external flags, runtime PM state, and `remapped_nvme` sysfs state.

Dependencies/integration: PCI core, libata, libahci, DMI, PM, DMA mapping, sysfs, Intel AHCI remap registers, `ahci_ops`, `ahci_pmp_retry_srst_ops`, and `ahci_host_activate`.

Risks/test signals: PCI ID/DMI quirk regressions can break old chipsets, suspend, MSI, DMA addressing, LPM, PMP, or hotplug. Test with probe logs, link bring-up, `/proc/interrupts`, sysfs `remapped_nvme`, suspend/resume, LPM/hotplug, and dmesg quirk messages.
