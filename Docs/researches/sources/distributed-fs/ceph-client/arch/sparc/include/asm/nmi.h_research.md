# sources/distributed-fs/ceph-client/arch/sparc/include/asm/nmi.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/nmi.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/nmi.h` declares SPARC NMI support hooks for perf and watchdog-style interrupt handling. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 14 lines, 318 bytes. Primary surface: `arch_trigger_cpumask_backtrace`, `nmi_cpu_busy`, and related NMI declarations depending on config. Symbol scan highlights: `__NMI_H`, `nmi_init`, `perfctr_irq`, `nmi_adjust_hz`, `start_nmi_watchdog`, `stop_nmi_watchdog`.

### Control Flow
debug/watchdog/perf code calls architecture NMI hooks to interrupt CPUs or collect backtraces. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
NMI state is owned by perf/watchdog and interrupt code. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: no direct include directives. Integration dependencies: generic NMI/watchdog APIs, perf events, and SPARC interrupt handling.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
bad NMI routing can deadlock diagnostics or fail to capture hung CPUs.

### Test Signals
lockup detector, perf NMI sampling, and CPU backtrace trigger tests. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
