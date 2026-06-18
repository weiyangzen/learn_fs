# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sp-pci.c

## Purpose

`sp-pci.c` is the PCI frontend for AMD Secure Processor/CCP devices. It matches AMD PCI IDs, maps BARs, allocates MSI-X/MSI interrupts, selects a PSP master device, provides PSP firmware/security sysfs attributes, and supplies generation-specific vdata.

## Important APIs, Types, And Functions

Public entry points are `sp_pci_init()` and `sp_pci_exit()`. Probe/remove/shutdown/PM handlers are `sp_pci_probe()`, `sp_pci_remove()`, `sp_pci_shutdown()`, `sp_pci_suspend()`, `sp_pci_resume()`, and `sp_pci_restore()`. IRQ helpers are `sp_get_msix_irqs()`, `sp_get_msi_irq()`, and `sp_free_irqs()`. Master selection uses `psp_set_master()`, `psp_get_master()`, and `psp_clear_master()`. Static vdata tables define SEV, TEE, platform-access, PSP, and SP device register layouts by PCI ID.

## Control Flow

Probe allocates `sp_device` and PCI-private state, enables the PCI device with managed resources, maps memory BARs, chooses MSI-X or MSI, sets bus mastering and DMA mask, installs PSP master callbacks, stores driver data, and calls `sp_init()`. Remove destroys subdevices and frees interrupts. Shutdown destroys subdevices without a separate IRQ-free path. PM delegates into common SP suspend/resume/restore. Sysfs attribute visibility reads PSP registers and hides all-ones inaccessible values.

## State And Persistence Behavior

`sp_dev_master` tracks the lexicographically earliest PCI PSP device by domain/bus/slot/function. Per-device `struct sp_pci` stores MSI-X vectors. Static vdata tables are immutable hardware descriptors.

## Dependencies And Integration Points

It integrates with PCI core, DMA mask setup, MSI/MSI-X APIs, common SP core, CCP hardware vdata from `ccp-dev.h`, PSP security HSTI attributes, SEV/TEE/platform-access register layouts, and module PCI device tables.

## Risks And Test Signals

Risks include wrong vdata for a PCI ID, master selection changes on hotplug/remove, sysfs reads from inaccessible PSP registers, IRQ fallback behavior, and shutdown/remove cleanup asymmetry. Test all listed PCI IDs where possible, MSI-X one-vector and two-vector paths, MSI fallback, firmware sysfs visibility, multi-socket master selection, suspend/restore, and device removal.
