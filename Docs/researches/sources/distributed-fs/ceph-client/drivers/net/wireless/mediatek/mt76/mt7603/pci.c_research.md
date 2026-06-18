# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/pci.c

Purpose: PCI bus glue for MT7603 devices. It binds MediaTek PCI device ID `0x7603`, maps BAR0, sets DMA capability, wires the shared IRQ handler, and hands the allocated device to common MT7603 registration.

Important APIs/functions: defines `mt76pci_device_table`, `mt76pci_probe()`, `mt76pci_remove()`, and exported `struct pci_driver mt7603_pci_driver`. Uses `pcim_enable_device`, `pcim_iomap_regions`, `pci_set_master`, `dma_set_mask`, `mt76_alloc_device`, `mt76_mmio_init`, `devm_request_irq`, `mt7603_register_device`, and `mt7603_unregister_device`.

Control flow: probe enables the PCI function, maps BAR0, enables bus mastering, restricts DMA to 32 bits, allocates an mt76-backed `mt7603_dev`, initializes MMIO, reads chip ID/revision registers, masks interrupts, requests a shared IRQ, then calls common registration. Any failure after allocation frees the mt76 device. Remove fetches driver data from PCI state and unregisters the common device.

State and persistence: initializes only runtime state: MMIO base, ASIC revision in `mdev->rev`, IRQ registration, and mt76/mac80211 registration side effects. Firmware names are declared with `MODULE_FIRMWARE` but loading happens in common MCU code.

Dependencies and integration: depends on Linux PCI/module/DMA APIs and the common declarations in `mt7603.h`. `mt7603_register_device()` is responsible for setting PCI drvdata, mac80211 registration, firmware, DMA, and hardware setup.

Risks: only 32-bit DMA is accepted; systems requiring a different mask will fail probe. Interrupts are masked before request, but ordering with common registration must keep the device quiet until handlers and rings are ready. Error handling frees the mt76 allocation but relies on devm/pcim for IRQ and mapping cleanup.

Test signals: PCI modalias/module autoload for vendor MediaTek device `0x7603`, successful "ASIC revision" log, IRQ request success, firmware request for `mt7603_e1.bin`/`mt7603_e2.bin`, and clean unload/reprobe without leaked IRQs or stale netdevs.
