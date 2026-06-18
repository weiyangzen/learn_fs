# sources/distributed-fs/ceph-client/arch/sparc/include/asm/kprobes.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/kprobes.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/kprobes.h` defines SPARC kprobe architecture support: breakpoint instruction, per-probe arch state, and single-step/emulation hooks. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 55 lines, 1312 bytes. Primary surface: `BREAKPOINT_INSTRUCTION`, `MAX_INSN_SIZE`, `struct arch_specific_insn`, `struct prev_kprobe`, `flush_insn_slot`, `kretprobe_blacklist_size`, and `arch_remove_kprobe()`. Symbol scan highlights: `_SPARC64_KPROBES_H`, `BREAKPOINT_INSTRUCTION`, `BREAKPOINT_INSTRUCTION_2`, `MAX_INSN_SIZE`, `kretprobe_blacklist_size`, `arch_remove_kprobe`, `flush_insn_slot`, `__kretprobe_trampoline`, `struct arch_specific_insn`, `struct prev_kprobe`, `struct kprobe`, `struct kprobe_ctlblk`, `kprobe_fault_handler`, `kprobe_trap`, `struct pt_regs`.

### Control Flow
kprobes copies and patches SPARC instructions into slots, installs breakpoint opcodes, handles trap callbacks, and may emulate or single-step original instructions. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
per-probe instruction copies and per-CPU previous-kprobe state persist while probes are armed. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm-generic/kprobes.h>`, `<linux/types.h>`, `<linux/percpu.h>`. Integration dependencies: `asm-generic/kprobes.h`, `asm/ptrace.h`, `asm/cacheflush.h`, text patching, and trap notifiers.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
SPARC delay slots, branch encodings, and cache flushing make probe placement risky; bad cleanup leaves patched text or stale instruction slots.

### Test Signals
kernel kprobes selftests, function-entry/return probe tests, branch-delay-slot rejection, and icache-flush validation. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
