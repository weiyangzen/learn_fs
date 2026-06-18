# sources/distributed-fs/ceph-client/drivers/iommu/s390-iommu.c

## Purpose
This file implements Linux IOMMU operations for IBM s390 zPCI devices. It builds and maintains zPCI DMA translation tables, registers IOAT state with firmware/hypervisor interfaces, handles blocking and identity domains, tracks devices attached to paging domains, and exposes translation refresh and counters.

## Important APIs, Types, And Functions
`struct s390_domain` embeds `struct iommu_domain`, a device list, counters, root DMA table pointer, list lock, RCU head, and root table origin type. Table helpers calculate region/segment/page indexes, set table origins, validate/invalidate entries, set protection bits, and recover child table pointers. Slab caches are created by `dma_alloc_cpu_table_caches()`, with allocation/free helpers for region and page tables.

Table walk/update functions include `dma_walk_rf_table()`, `dma_walk_rs_table()`, `dma_get_seg_table_origin()`, `dma_get_page_table_origin()`, `dma_walk_region_tables()`, `dma_walk_cpu_trans()`, and `dma_update_cpu_trans()`. Domain and device operations include `s390_domain_alloc_paging()`, `s390_domain_free()`, `s390_iommu_attach_device()`, `blocking_domain_attach_device()`, `s390_attach_dev_identity()`, `s390_iommu_probe_device()`, `s390_iommu_get_resv_regions()`, `s390_iommu_map_pages()`, `s390_iommu_unmap_pages()`, `s390_iommu_iova_to_phys()`, and TLB sync functions. Exported zPCI integration points are `zpci_iommu_register_ioat()`, `zpci_get_iommu_ctrs()`, `zpci_init_iommu()`, and `zpci_destroy_iommu()`.

## Control Flow
Subsystem init forces DAC for IOMMU DMA, derives the aperture from high memory and the `s390_iommu_aperture=` parameter, and creates table caches. Device probe accepts only PCI devices, validates zPCI DMA aperture, sets shadow-on-flush for devices needing TLB refresh, initializes the per-device domain lock, and starts every device in the blocking domain.

Paging-domain allocation chooses an RTX/RSX/RFX root type based on requested aperture, zPCI supported table modes, and device DMA bounds, then initializes a 4 KiB-only domain. Attach first moves the device to blocking, registers the new IOAT using the root table origin and zPCI DMA range, updates `zdev->dma_table` and `zdev->s390_domain`, and adds the device to the domain list under RCU. Identity attach also goes through blocking first, then registers a zero IOTA pass-through IOAT.

Map validates 4 KiB page size, aperture bounds, and alignment, then walks/allocates translation tables and installs valid PTEs, marking entries protected when `IOMMU_WRITE` is absent. Unmap invalidates PTEs, adds the range to the gather, and updates counters. TLB sync and flush walk the attached zPCI device list and call `zpci_refresh_trans()` or full refresh, handling hypervisor memory pressure in sync-map by falling back to full refresh.

## State And Persistence
Persistent state lives in multi-level zPCI translation tables allocated from kmem caches, per-domain attached-device RCU lists, counters, and per-device `zdev->s390_domain`/`dma_table`/IOMMU core objects. Domain freeing is RCU-delayed so readers of attached devices and tables can finish. Boot parameters persist in static aperture configuration.

## Dependencies And Integration Points
The driver depends on s390 zPCI architecture definitions and operations from `asm/pci_dma.h`, generic IOMMU APIs, IOMMU DMA helper state, RCU lists, and zPCI firmware/hypervisor calls such as `zpci_register_ioat()`, `zpci_unregister_ioat()`, and `zpci_refresh_trans()`.

## Risks
Attach uses blocking as a fail-safe before registering a new IOAT; failures after blocking leave DMA blocked. Table allocation is concurrent and uses `cmpxchg`, so all table-entry encoding and validity tests must be exact. Refresh operations can fail or require full refresh fallback under hypervisor pressure. Aperture calculations mutate `zdev->end_dma`, so configuration affects reserved regions and domain geometry. Some error propagation from IOAT registration is intentionally suppressed for device error/removal states.

## Test Signals
s390 boot with zPCI devices, strict/deferred flush modes, varying `s390_iommu_aperture`, attach to paging/identity/blocking domains, 4 KiB map/unmap and iova-to-phys, zPCI refresh counters, device removal/error state IOAT registration behavior, and table cleanup under RCU after detach.
