# sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/oplib.h` selects the SPARC32 or SPARC64 OpenBoot PROM library interface. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 9 lines, 215 bytes. Primary surface: include-time dispatch to `oplib_64.h` or `oplib_32.h`. Symbol scan highlights: `___ASM_SPARC_OPLIB_H`.

### Control Flow
platform code includes a single header and receives the proper PROM API for its ABI. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no wrapper state. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/oplib_64.h>`, `<asm/oplib_32.h>`. Integration dependencies: architecture-specific PROM library headers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong dispatch breaks early boot and firmware calls.

### Test Signals
SPARC32/SPARC64 boot and PROM library build coverage. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
