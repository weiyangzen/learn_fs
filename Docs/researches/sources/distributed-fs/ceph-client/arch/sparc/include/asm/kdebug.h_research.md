# sources/distributed-fs/ceph-client/arch/sparc/include/asm/kdebug.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/kdebug.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/kdebug.h` selects SPARC32 or SPARC64 kernel-debug notifier definitions. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 9 lines, 219 bytes. Primary surface: include-time dispatch to `kdebug_64.h` or `kdebug_32.h`. Symbol scan highlights: `___ASM_SPARC_KDEBUG_H`.

### Control Flow
architecture selection exposes the right die-notifier enum and prototypes. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no state in wrapper. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/kdebug_64.h>`, `<asm/kdebug_32.h>`. Integration dependencies: architecture-specific debug headers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong selection breaks exception/debug notifier users.

### Test Signals
build coverage with kprobes, kgdb, and die notifier users. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
