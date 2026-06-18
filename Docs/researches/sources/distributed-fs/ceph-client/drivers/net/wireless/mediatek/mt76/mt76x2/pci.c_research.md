<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci.c

Purpose: PCIe bus driver entry point for MT7612/MT7602/MT7662. It matches PCI IDs, enables the device, maps BARs, configures DMA/IRQ, allocates mt76 device state, registers mt76x2 common device, handles remove, and implements PCI suspend/resume.

Important APIs/types/functions: `mt76x2e_probe()`, `mt76x2e_remove()`, suspend/resume callbacks, `mt76x2e_device_table`, `mt76pci_driver`, and PCI-specific `mt76_driver_ops`.

Control flow: probe enables PCI, maps BAR0, sets bus master and 32-bit DMA mask, allocates `mt76x02_dev`, initializes MMIO, powers WLAN off, reads ASIC revision, masks IRQs, requests shared IRQ using `mt76x02_irq_handler()`, registers the device, applies ASPM fixups, and disables ASPM. Suspend disables NAPI/tasklets/worker and saves PCI power state; resume restores power/state, re-enables processing, schedules NAPI, and resumes hardware.

State and persistence: PCI drvdata, mapped MMIO, IRQ registration, DMA mask, mt76 device state, PCI power state, and ASPM-related registers.

Dependencies/integration: Linux PCI PM APIs, mt76 MMIO, shared mt76x02 IRQ/DMA/TXRX, mt76x2 registration/resume/cleanup.

Risks: probe error cleanup before drvdata/registration, suspend tasklet kill vs later resume, IRQ sharing, DMA mask limits, and ASPM magic register writes. Test signals include PCI probe/remove, module unload, suspend/resume, IRQ traffic, ASPM platforms, and unsupported DMA mask failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci.c -->
