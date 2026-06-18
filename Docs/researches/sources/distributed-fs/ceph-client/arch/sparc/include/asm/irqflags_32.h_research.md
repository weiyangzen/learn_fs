# sources/distributed-fs/ceph-client/arch/sparc/include/asm/irqflags_32.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/irqflags_32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/irqflags_32.h` implements SPARC32 local interrupt enable/disable/save/restore helpers using `%psr` PIL bits and trap-enable state. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 48 lines, 1060 bytes. Primary surface: `arch_local_irq_save`, `arch_local_irq_restore`, `arch_local_irq_enable`, `arch_local_irq_disable`, `arch_local_save_flags`, `arch_irqs_disabled_flags`, `arch_irqs_disabled`, and `arch_safe_halt`. Symbol scan highlights: `_ASM_IRQFLAGS_H`, `arch_local_irq_restore`, `arch_local_irq_save`, `arch_local_irq_enable`, `arch_local_save_flags`, `volatile`, `arch_local_irq_disable`, `arch_irqs_disabled_flags`, `arch_irqs_disabled`.

### Control Flow
inline assembly reads `%psr`, manipulates `PSR_PIL`, writes the new value, and executes nops for pipeline synchronization; save/restore paths preserve caller interrupt state. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
state is the CPU processor status register interrupt level. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/types.h>`, `<asm/psr.h>`. Integration dependencies: `asm/psr.h`, privileged SPARC32 assembly, lock/interrupt core, and idle loop code.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
incorrect PSR synchronization or PIL masking can corrupt critical-section interrupt state.

### Test Signals
lockdep IRQ state checking, interrupt storm tests, idle/halt behavior, and disassembly review. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
