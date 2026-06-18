# sources/distributed-fs/ceph-client/drivers/iommu/sprd-iommu.c

## Purpose
This file implements the Unisoc/SPRD IOMMU driver. It provides a simple one-device IOMMU model with a flat page table over a 256 MiB aperture, hardware programming for EX and VAU IP versions, TLB update hooks, and platform-driver registration.

## Important APIs, Types, And Functions
`struct sprd_iommu_device` stores the attached domain, hardware version, fault-protection page, MMIO base, device, IOMMU core object, and optional gate clock. `struct sprd_iommu_domain` stores a page-table lock, embedded generic domain, coherent page-table VA/PA, and attached SPRD device. Register helpers are `sprd_iommu_write()`, `sprd_iommu_read()`, `sprd_iommu_update_bits()`, and `sprd_iommu_get_version()`.

Domain/hardware helpers include `sprd_iommu_pgt_size()`, `sprd_iommu_first_vpn()`, `sprd_iommu_vpn_range()`, `sprd_iommu_first_ppn()`, `sprd_iommu_default_ppn()`, `sprd_iommu_hw_en()`, and `sprd_iommu_cleanup()`. Generic IOMMU ops are `sprd_iommu_domain_alloc_paging()`, `sprd_iommu_attach_device()`, `sprd_iommu_map()`, `sprd_iommu_unmap()`, `sprd_iommu_sync_map()`, `sprd_iommu_sync()`, `sprd_iommu_iova_to_phys()`, `sprd_iommu_probe_device()`, and `sprd_iommu_of_xlate()`.

## Control Flow
Probe maps the register resource, allocates a coherent 4 KiB protection page used as the default fault target, registers the IOMMU core device, enables the optional gate clock, reads the hardware version, and stores it. OF xlate resolves the IOMMU platform device and stores its driver data in the client device.

Domain allocation creates a 4 KiB-page-only domain with a forced 0..256 MiB aperture. The first attach lazily allocates a coherent page table sized for the aperture, stores the device pointer, disables hardware, programs first PPN, first VPN, VPN range, default PPN, then re-enables hardware. Map writes sequential PPNs into the flat table under a spinlock. Unmap zeros entries. Sync writes the EX or VAU update register with all ones to clear the hardware TLB buffer. Cleanup frees the coherent table and disables hardware.

## State And Persistence
Persistent state consists of a coherent flat PPN table per attached domain, a coherent protection page per hardware device, the hardware version, and optional clock state. The hardware stores first VPN/range, first PPN, default PPN, enable/gate bits, and update registers.

## Dependencies And Integration Points
The driver integrates with OF platform matching `sprd,iommu-v1`, Linux IOMMU core, coherent DMA allocation, optional clocks, and generic single-device IOMMU groups.

## Risks
The hardware model supports one client per SPRD IOMMU; attaching a different domain reprograms the single hardware table. There is no identity or blocking domain implementation in this file. The flat table has no valid/protection bits in software, so remap detection is absent and zero means unmapped/default behavior. Map ignores `pgsize` directly and assumes generic core supplies 4 KiB pages. Fault handling is not present, relying on default PPN behavior.

## Test Signals
Probe with EX and VAU versions, optional clock present/absent, attach/map/unmap/sync for 4 KiB pages, aperture-boundary rejection, iova-to-phys lookup, domain cleanup on free, and behavior of the protection page on invalid translations.
