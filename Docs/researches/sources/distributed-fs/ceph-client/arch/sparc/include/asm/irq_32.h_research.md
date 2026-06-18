# sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq_32.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq_32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/irq_32.h` declares SPARC32 IRQ constants and helpers for building Linux virtual IRQs from PROM/SBus interrupt descriptions. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 24 lines, 498 bytes. Primary surface: `NR_IRQS`, `irq_canonicalize`, `NO_IRQ`, `__irq_ino`, `sparc_floppy_irq`, and `sparc_build_irq()`. Symbol scan highlights: `_SPARC_IRQ_H`, `NR_IRQS`, `irq_canonicalize`, `sun4d_init_sbi_irq`, `NO_IRQ`.

### Control Flow
platform discovery converts real firmware/device interrupt data into kernel IRQ numbers used by drivers and interrupt handlers. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
external `sparc_floppy_irq` tracks the floppy controller IRQ; the IRQ subsystem owns the rest. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/interrupt.h>`. Integration dependencies: `linux/interrupt.h`, `linux/linkage.h`, `linux/threads.h`, PROM/SBus probing, and irq core.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
bad IRQ construction routes devices to wrong handlers or exceeds `NR_IRQS`.

### Test Signals
SPARC32 boot/probe logs, SBus device interrupt tests, and generic IRQ debugfs/proc inspection. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
