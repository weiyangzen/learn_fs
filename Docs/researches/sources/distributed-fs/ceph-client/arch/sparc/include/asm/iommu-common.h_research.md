# sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu-common.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu-common.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu-common.h` declares the common SPARC64 IOMMU allocation table used by PCI and ATU DMA mapping implementations. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 53 lines, 1445 bytes. Primary surface: `struct iommu_map_table`, `IOMMU_ERROR_CODE`, `IOMMU_POOL_HASHBITS`, and `iommu_tbl_pool_init()`. Symbol scan highlights: `_LINUX_IOMMU_COMMON_H`, `IOMMU_POOL_HASHBITS`, `IOMMU_NR_POOLS`, `IOMMU_ERROR_CODE`, `struct iommu_pool`, `struct iommu_map_table`, `IOMMU_HAS_LARGE_POOL`, `IOMMU_NO_SPAN_BOUND`, `IOMMU_NEED_FLUSH`, `iommu_tbl_pool_init`, `iommu_tbl_range_alloc`, `iommu_tbl_range_free`.

### Control Flow
IOMMU setup initializes pools over a DVMA range; DMA map/unmap code allocates table spans using the lock-protected map and per-pool hints. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
`struct iommu_map_table` persists allocation bitmaps, pool metadata, page shifts, DMA offset, and large-pool hints for a controller. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/spinlock_types.h>`, `<linux/device.h>`, `<asm/page.h>`. Integration dependencies: `linux/kernel.h`, `linux/bitmap.h`, `linux/spinlock.h`, `linux/mmzone.h`, and PCI/ATU IOMMU users.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong table sizing, page shift, or pool locking can lead to DVMA address reuse or leaks under concurrent DMA.

### Test Signals
PCI DMA mapping stress, IOMMU pool allocation/free tests, lockdep, and NUMA-node initialization coverage. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
