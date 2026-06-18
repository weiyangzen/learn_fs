# sources/distributed-fs/ceph-client/arch/mips/include/asm/irqflags.h


### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/irqflags.h` MIPS interrupt, IRQ-controller, IRQ-stack, IRQ-register, CPU idle, or local IRQ flag support. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 185 lines / 4208 bytes. macros/constants: `_ASM_IRQFLAGS_H`; types/functions/declarations: `static inline void arch_local_irq_disable(void)`, `static inline unsigned long arch_local_irq_save(void)`, `static inline void arch_local_irq_restore(unsigned long flags)`, `static inline void arch_local_irq_enable(void)`, `static inline unsigned long arch_local_save_flags(void)`, `static inline int arch_irqs_disabled_flags(unsigned long flags)`, `static inline int arch_irqs_disabled(void)`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/compiler.h>`, `<linux/stringify.h>`, `<asm/compiler.h>`, `<asm/hazards.h>`.

### Integration Points
Used by interrupt entry/exit, irqdomains, PIC/CPU irqchips, timers, scheduler idle, tracing, and diagnostics. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Missing hazards, wrong stack bounds, bad IRQ numbering, or failed acknowledgements can create lost interrupts or storms. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
