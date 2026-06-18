# sources/distributed-fs/ceph-client/arch/mips/include/asm/kprobes.h


### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/kprobes.h` MIPS debugging, crash/kexec, KGDB, kprobe, die-notifier, and breakpoint instrumentation contract. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 76 lines / 1622 bytes. macros/constants: `_ASM_KPROBES_H`, `__ARCH_WANT_KPROBES_INSN_SLOT`, `MAX_INSN_SIZE`, `flush_insn_slot`, `kretprobe_blacklist_size`, `SKIP_DELAYSLOT`; types/functions/declarations: `struct kprobe;`, `struct pt_regs;`, `typedef union mips_instruction kprobe_opcode_t;`, `struct arch_specific_insn {`, `struct prev_kprobe {`, `struct kprobe *kp;`, `struct kprobe_ctlblk {`, `struct prev_kprobe prev_kprobe;`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm-generic/kprobes.h>`, `<linux/ptrace.h>`, `<linux/types.h>`, `<asm/cacheflush.h>`, `<asm/kdebug.h>`, `<asm/inst.h>`.

### Integration Points
Used by trap handling, crash kernels, runtime instrumentation, debuggers, and module probing. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Register layout, delay-slot, cache-flush, or SMP rendezvous bugs can make diagnostics unreliable or hang reboot. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
