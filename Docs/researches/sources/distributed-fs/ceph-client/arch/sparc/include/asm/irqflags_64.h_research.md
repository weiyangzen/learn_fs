# sources/distributed-fs/ceph-client/arch/sparc/include/asm/irqflags_64.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/irqflags_64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/irqflags_64.h` implements SPARC64 local interrupt flag primitives using `%pstate` IE and PIL manipulation, with trace and raw variants. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 98 lines, 1954 bytes. Primary surface: `arch_local_irq_*`, `arch_irqs_disabled*`, `arch_safe_halt`, `raw_all_irq_*`, `raw_local_irq_*`, and low-level `__raw_local_irq_*` helpers. Symbol scan highlights: `_ASM_IRQFLAGS_H`, `arch_local_save_flags`, `__volatile__`, `arch_local_irq_restore`, `arch_local_irq_disable`, `arch_local_irq_enable`, `arch_irqs_disabled_flags`, `arch_irqs_disabled`, `arch_local_irq_save`.

### Control Flow
inline assembly reads/writes `%pstate` or `%pil`; generic IRQ tracing wraps the raw helpers when tracing is enabled. Safe halt enables interrupts before entering the idle trap path. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
state is held in CPU `%pstate` and `%pil` registers and reflected in tracing/accounting. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/pil.h>`. Integration dependencies: `linux/irqflags.h`, `asm/pstate.h`, `asm/pil.h`, SPARC64 trap code, and lockdep/irq tracing.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
PIL/IE ordering errors can unmask interrupts too early or leave CPUs non-preemptible; tracing wrappers must not recurse through raw paths.

### Test Signals
lockdep IRQ tracing, preemption/softirq stress, CPU idle tests, and low-level assembly inspection. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
