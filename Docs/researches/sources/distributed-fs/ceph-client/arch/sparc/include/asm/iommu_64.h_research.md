# sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu_64.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu_64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu_64.h` defines SPARC64 IOMMU, streaming buffer, and ATU data structures and 64-bit IOPTE encoding. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 93 lines, 2489 bytes. Primary surface: `IOPTE_*`, `IOMMU_NUM_CTXS`, `struct iommu_arena`, `struct atu_iotsb`, `struct atu`, `struct iommu`, `struct strbuf`, and `iommu_table_init()`. Symbol scan highlights: `_SPARC64_IOMMU_H`, `IOPTE_VALID`, `IOPTE_64K`, `IOPTE_STBUF`, `IOPTE_INTRA`, `IOPTE_CONTEXT`, `IOPTE_PAGE`, `IOPTE_CACHE`, `IOPTE_WRITE`, `IOMMU_NUM_CTXS`, `struct iommu_arena`, `ATU_64_SPACE_SIZE`, `struct atu_iotsb`, `struct atu_ranges`, `struct atu`, `struct iommu_map_table`, `struct iommu`, `struct strbuf`, `iommu_table_init`.

### Control Flow
PCI controller setup initializes IOMMU map tables and optional ATU IOTSBs; DMA code allocates DVMA addresses, writes 64-bit IOPTEs, manages context bitmaps, and flushes IOMMU/streaming-buffer state. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
`struct iommu` persists page tables, register addresses, context bitmap, locks, dummy pages, and DMA mask; `struct strbuf` persists streaming-buffer registers and flush flag memory. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/iommu-common.h>`. Integration dependencies: `asm/iommu-common.h`, PCI controller code, hypervisor PCI services, spinlocks, DMA mapping, and NUMA allocation.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
context bitmap leaks, bad DMA mask handling, and streaming-buffer flush bugs can corrupt PCI DMA; ATU range assumptions affect large DMA windows.

### Test Signals
SPARC64 PCI DMA stress, IOMMU context exhaustion tests, streaming-buffer flush validation, ATU/IOTSB boot coverage, and sparse checks. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
