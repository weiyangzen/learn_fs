# sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq.h` selects the SPARC32 or SPARC64 IRQ contract. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 9 lines, 207 bytes. Primary surface: include-time dispatch to `irq_64.h` or `irq_32.h`. Symbol scan highlights: `___ASM_SPARC_IRQ_H`.

### Control Flow
architecture preprocessor selection exposes the right IRQ count, builder, and controller hooks. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
no state in this wrapper. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/irq_64.h>`, `<asm/irq_32.h>`. Integration dependencies: `__sparc__`, `__arch64__`, and architecture IRQ headers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong selection breaks interrupt numbering and controller integration.

### Test Signals
SPARC32/SPARC64 build coverage and irqchip probe tests. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
