# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_fire.c

## Purpose
Sun4u FIRE PCIe host controller driver. It initializes PBM registers, IOMMU translation, PCIe link/control state, MSI event queues, and the platform driver for `pciex108e,80f0`.

## Important APIs, Types, and Functions
`fire_probe()` allocates `pci_pbm_info` and `iommu`. `pci_fire_pbm_init()` fills PBM fields, parses resources, initializes hardware/IOMMU/MSI, scans the bus, and links into `pci_pbm_root`. `pci_fire_pbm_iommu_init()` programs FIRE IOMMU control, TSB base, flush registers, and write-complete register. MSI support implements `struct pci_msiq_entry` and `pci_fire_msiq_ops` including dequeue, setup, teardown, allocation, and IRQ construction. `pci_fire_hw_init()` programs parity, fatal reset, core interrupt, TLU, LPU, DMC, and PEC registers.

## Control Flow
At `subsys_initcall`, the platform driver registers. Probe sets register bases from OF `reg`, discovers ranges and PBM properties, initializes hardware, IOMMU, MSI, then scans PCI and registers the PBM. MSI interrupts are drained by common MSI code using FIRE queue ops.

## State and Persistence
Long-lived state sits in PBM/IOMMU objects, the IOMMU table, and a 512 KiB MSI queue allocation. Hardware state includes IOMMU, event queue, MSI map/clear/address, and PCIe control registers. No persistent storage.

## Dependencies and Integration Points
Uses UPA register accessors, OF/platform/PCI/MSI/IRQ APIs, `iommu_table_init()`, `build_irq()`, `sparc64_pbm_msi_init()`, and shared PCI helpers.

## Risks and Test Signals
MSI queue allocation requires contiguous memory; queue routing uses fixed assumptions; error interrupt handling is left as a placeholder. Test via FIRE boot logs, resource ranges, MSI queue logs, PCIe enumeration, MSI delivery, and DMA across the configured aperture.
