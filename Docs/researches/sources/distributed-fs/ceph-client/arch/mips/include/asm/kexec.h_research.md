# sources/distributed-fs/ceph-client/arch/mips/include/asm/kexec.h


### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/kexec.h` MIPS debugging, crash/kexec, KGDB, kprobe, die-notifier, and breakpoint instrumentation contract. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 51 lines / 1495 bytes. macros/constants: `KEXEC_SOURCE_MEMORY_LIMIT`, `KEXEC_DESTINATION_MEMORY_LIMIT`, `KEXEC_CONTROL_MEMORY_LIMIT`, `KEXEC_CONTROL_PAGE_SIZE`, `KEXEC_ARCH`, `MAX_NOTE_BYTES`; types/functions/declarations: `static inline void crash_setup_regs(struct pt_regs *newregs,`, `struct pt_regs *oldregs)`, `struct kimage;`, `extern unsigned long kexec_args[4];`, `extern int (*_machine_kexec_prepare)(struct kimage *);`, `extern void (*_machine_kexec_shutdown)(void);`, `extern void (*_machine_crash_shutdown)(struct pt_regs *regs);`, `extern const unsigned char kexec_smp_wait[];`, `extern unsigned long secondary_kexec_args[4];`, `extern atomic_t kexec_ready_to_reboot;`, `extern void (*_crash_smp_send_stop)(void);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<asm/stacktrace.h>`.

### Integration Points
Used by trap handling, crash kernels, runtime instrumentation, debuggers, and module probing. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Register layout, delay-slot, cache-flush, or SMP rendezvous bugs can make diagnostics unreliable or hang reboot. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
