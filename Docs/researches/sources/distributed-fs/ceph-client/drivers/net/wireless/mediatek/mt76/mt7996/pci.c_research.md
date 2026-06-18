# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/pci.c

## Purpose
`pci.c` is the PCI probe/remove layer for MT7996-family devices. It binds primary WLAN PCI functions and secondary HIF functions, coordinates discovery of optional HIF2, enables PCI resources and DMA masks, creates the MMIO/mt76 device, initializes WFSYS/NPU/WED/IRQ plumbing, registers the full WLAN device, and advertises required firmware blobs to the kernel module loader.

## Important APIs, Types, And Functions
Two PCI ID tables split primary devices (`MT7996_DEVICE_ID`, `MT7992_DEVICE_ID`, `MT7990_DEVICE_ID`) from secondary HIF devices (`*_DEVICE_ID_2`). A global `hif_list`, `hif_lock`, and `hif_idx` track probed secondary HIFs. `mt7996_pci_hif2_probe()` allocates and registers an `mt7996_hif` object with BAR0 regs, IRQ, and PCIe bandwidth data. `mt7996_pci_init_hif2()` stamps a recognition ID into the primary device and searches the HIF list via `mt7996_pci_get_hif2()`.

The main entry point is `mt7996_pci_probe()`. Remove paths are split into `mt7996_hif_remove()` for secondary functions and `mt7996_pci_remove()` for primary devices. Driver objects `mt7996_hif_driver` and `mt7996_pci_driver` are registered by `mmio.c`.

## Control Flow
Probe enables the PCI device, maps BAR0, sets bus mastering, installs 36-bit streaming and 32-bit coherent DMA masks, and disables ASPM through mt76. If the probed ID is a secondary HIF, it only records HIF metadata and returns. For primary functions, it calls `mt7996_mmio_probe()`, resets WFSYS, tries to find HIF2, initializes NPU metadata, initializes WED for primary HIF or allocates IRQ vectors, requests the primary IRQ, disables interrupt masks, and enables the PCIe MAC interrupt master switch.

If HIF2 is present, the probe repeats WED/IRQ setup for the secondary PCI device, requests a shared interrupt using the same `mt7996_irq_handler()`, disables HIF2 masks, and enables the secondary PCIe interrupt master switch. Finally it calls `mt7996_register_device()`. Error labels unwind HIF2 IRQ/WED/vector references, primary IRQ/WED/vectors, HIF device references, and mt76 allocation.

## State And Persistence
Runtime state includes the global HIF list, reference counts on secondary HIF devices, `dev->hif2`, `dev->hif2->irq`, PCI IRQ vectors, WED attachment state, NPU MMIO physical base/type, interrupt enable registers, and the mt76 device registered as PCI driver data. No persistent data is written. Module firmware declarations identify firmware names for udev/kernel loading.

## Dependencies And Integration Points
`pci.c` integrates Linux PCI managed APIs, mt76 PCI helpers, DMA mask APIs, WED initialization from `mmio.c`, IRQ handling from `mmio.c`, WFSYS reset and device registration from init/reset code, NPU setup from mt76/NPU paths, and firmware filenames from `mt7996.h`. The secondary HIF handshake depends on `MT_PCIE_RECOG_ID` registers and the separate HIF PCI driver being registered before the primary driver.

## Risks
Dual-HIF discovery is order-sensitive and uses a global incrementing recognition ID plus a shared list. Reference handling must remain correct across probe failures and remove. The use of `pci_get_device()` in the HIF2 existence check can affect device references if not balanced by PCI core expectations. Error unwinding mixes WED detach, IRQ vector freeing, devm IRQ freeing, and HIF references; new failure points need careful placement. Shared IRQs for primary/HIF2 rely on the common handler correctly masking both interrupt domains.

## Test Signals
Probe should succeed for each primary chip ID with and without a secondary HIF device present. Logs and sysfs should show the device registered after firmware load. Dual-HIF systems should request both IRQs and route band-specific traffic without interrupt stalls. Failure tests should cover WED attach failure, IRQ allocation failure, request_irq failure, register-device failure, and removal of primary/secondary functions without leaked references or stale HIF list entries.
