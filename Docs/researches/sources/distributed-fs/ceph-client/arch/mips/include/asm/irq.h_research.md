# sources/distributed-fs/ceph-client/arch/mips/include/asm/irq.h


### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/irq.h` MIPS interrupt, IRQ-controller, IRQ-stack, IRQ-register, CPU idle, or local IRQ flag support. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 83 lines / 2257 bytes. macros/constants: `_ASM_IRQ_H`, `IRQ_STACK_SIZE`, `IRQ_STACK_START`, `irq_canonicalize`, `CP0_LEGACY_COMPARE_IRQ`, `CP0_LEGACY_PERFCNT_IRQ`, `arch_trigger_cpumask_backtrace`; types/functions/declarations: `extern void *irq_stack[NR_CPUS];`, `static inline bool on_irq_stack(int cpu, unsigned long sp)`, `static inline int irq_canonicalize(int irq)`, `extern void do_IRQ(unsigned int irq);`, `struct irq_domain;`, `extern void do_domain_IRQ(struct irq_domain *domain, unsigned int irq);`, `extern void arch_init_irq(void);`, `extern void spurious_interrupt(void);`, `extern int cp0_compare_irq;`, `extern int cp0_compare_irq_shift;`, `extern int cp0_perfcount_irq;`, `extern int cp0_fdc_irq;`, `extern int get_c0_fdc_int(void);`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/linkage.h>`, `<linux/smp.h>`, `<asm/mipsmtregs.h>`, `<irq.h>`.

### Integration Points
Used by interrupt entry/exit, irqdomains, PIC/CPU irqchips, timers, scheduler idle, tracing, and diagnostics. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Missing hazards, wrong stack bounds, bad IRQ numbering, or failed acknowledgements can create lost interrupts or storms. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
