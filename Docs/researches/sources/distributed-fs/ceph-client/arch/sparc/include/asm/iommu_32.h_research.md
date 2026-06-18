# sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu_32.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu_32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu_32.h` defines the sun4m SPARC32 SBus IOMMU register block, control/error bits, IOPTE format, and invalidation helpers. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 122 lines, 5865 bytes. Primary surface: `struct iommu_regs`, `IOMMU_CTRL_*`, `IOMMU_AFSR_*`, `IOMMU_SBCFG_*`, `IOMMU_MFSR_*`, `IOPTE_*`, `struct iommu_struct`, `iommu_invalidate()`, and `iommu_invalidate_page()`. Symbol scan highlights: `_SPARC_IOMMU_H`, `struct iommu_regs`, `IOMMU_CTRL_IMPL`, `IOMMU_CTRL_VERS`, `IOMMU_CTRL_RNGE`, `IOMMU_RNGE_16MB`, `IOMMU_RNGE_32MB`, `IOMMU_RNGE_64MB`, `IOMMU_RNGE_128MB`, `IOMMU_RNGE_256MB`, `IOMMU_RNGE_512MB`, `IOMMU_RNGE_1GB`, `IOMMU_RNGE_2GB`, `IOMMU_CTRL_ENAB`, `IOMMU_AFSR_ERR`, `IOMMU_AFSR_LE`, `IOMMU_AFSR_TO`, `IOMMU_AFSR_BE`, `IOMMU_AFSR_SIZE`, `IOMMU_AFSR_S`, `IOMMU_AFSR_RESV`, `IOMMU_AFSR_ME`, `IOMMU_AFSR_RD`, `IOMMU_AFSR_FAV`, and 28 more.

### Control Flow
SBus DMA code programs the IOMMU base/control registers, fills IOPTEs, then flushes the whole IOMMU TLB or a single page via write-only registers. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
`struct iommu_struct` keeps mapped registers, IOPTE table, managed DVMA range, and allocation bitmap. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/page.h>`, `<asm/bitext.h>`. Integration dependencies: `asm/page.h`, `asm/bitext.h`, `sbus_writel`, SBus DMA, and page-table types.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
register layout or bit mismatch causes DMA faults; incomplete invalidation can leave stale translations active.

### Test Signals
sun4m SBus DMA tests, IOMMU fault injection/logging, and map/unmap/invalidate stress. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
