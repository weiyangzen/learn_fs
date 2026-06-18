# sources/distributed-fs/ceph-client/arch/sparc/include/asm/kdebug_32.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/kdebug_32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/kdebug_32.h` declares SPARC32 die-notifier events and notifier-chain operations for traps, oopses, and debug exceptions. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 75 lines, 2043 bytes. Primary surface: `enum die_val`, `DIE_*` values, `notify_die`, `register_die_notifier`, and `unregister_die_notifier`. Symbol scan highlights: `_SPARC_KDEBUG_H`, `DEBUG_BP_TRAP`, `int`, `struct kernel_debug`, `sp_enter_debugger`, `__volatile__`, `SP_ENTER_DEBUGGER`, `enum die_val`, `KDEBUG_ENTRY_OFF`, `KDEBUG_DUNNO_OFF`, `KDEBUG_DUNNO2_OFF`, `KDEBUG_TEACH_OFF`.

### Control Flow
trap/oops/debug code calls `notify_die`; registered notifiers such as kprobes, kgdb, or tracing inspect `pt_regs` and can influence handling. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
notifier-chain state is maintained in architecture debug implementation files. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/openprom.h>`, `<asm/vaddrs.h>`. Integration dependencies: `linux/notifier.h`, `asm/ptrace.h`, trap/oops handling, kprobes, and kgdb.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
incorrect event numbers or notifier return handling can hide fatal traps or break probe recovery.

### Test Signals
kprobe hit/fault tests, kgdb trap tests, oops notifier coverage, and SPARC32 exception tests. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
