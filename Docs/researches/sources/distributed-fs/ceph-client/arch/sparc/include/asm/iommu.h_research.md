# sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/iommu.h` selects the 32-bit or 64-bit SPARC IOMMU header for the current build. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 9 lines, 215 bytes. Primary surface: include-time dispatch to `iommu_64.h` or `iommu_32.h`. Symbol scan highlights: `___ASM_SPARC_IOMMU_H`.

### Control Flow
preprocessor tests choose the proper register and data-structure model. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no state; selected headers define state structures. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/iommu_64.h>`, `<asm/iommu_32.h>`. Integration dependencies: `__sparc__`, `__arch64__`, and the architecture-specific IOMMU headers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong dispatch would compile an incompatible DMA/IOMMU model.

### Test Signals
SPARC32 and SPARC64 defconfig builds. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
