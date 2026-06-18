# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/pci.c

Purpose: PCI bus frontend for MT7615/MT7663/MT7611 devices. It binds PCI IDs, prepares PCI resources, enters common MMIO probe, and implements PCI power-management suspend/resume.

Important APIs and functions: `mt7615_pci_device_table[]` matches MediaTek device IDs `0x7615`, `0x7663`, and `0x7611`. `mt7615_pci_probe()` enables the device, maps BAR0, allocates IRQ vectors, sets DMA mask, disables ASPM, chooses the register map, and calls `mt7615_mmio_probe()`. `mt7615_pci_remove()` unregisters common device state and frees IRQ vectors. PM callbacks `mt7615_pci_suspend()` and `mt7615_pci_resume()` coordinate firmware HIF suspend, NAPI/worker disablement, DMA reset, PDMA sleep protection, PCI D-state transitions, and ownership handoff.

Control flow: Probe is linear resource setup with a single error path freeing IRQ vectors. Suspend wakes the device, optionally tells firmware to suspend HIF, disables software packet processing, resets DMA, waits for PDMA idle, enables MT7663 sleep protection, saves PCI state, changes power state, and gives control to firmware. Resume reverses ownership, restores PCI D0/state, clears MT7663 sleep protection, detects whether PDMA rings need reinitialization, re-enables workers/NAPI, schedules NAPI, and clears HIF suspend.

State and persistence: Tracks PCI power state, wake capability, saved PCI config, mt76 worker/NAPI enabled state, and device PM ownership. No filesystem persistence; firmware blobs are declared through `MODULE_FIRMWARE()`.

Dependencies: Linux PCI APIs, mt76 PCI helpers, `mt7615_mmio_probe()`, `mt7615_dma_reset()`, `mt7615_wait_pdma_busy()`, Connac MCU HIF suspend, and register macros in `regs.h`.

Risks: Suspend/resume ordering is delicate; failing to stop NAPI/workers before DMA reset can race RX/TX rings. Returning early after setting HIF suspend can leave firmware/host state mismatched if later restore paths miss it. PDMA reset detection only logs and does not reinitialize in this file. PCI IRQ cleanup mixes devm IRQ and vector freeing.

Test signals: Device probe/remove, module autoload by PCI ID, runtime and system suspend/resume, traffic after resume, MT7663 sleep-protection polling, and absence of stuck queues or IRQ storms.
