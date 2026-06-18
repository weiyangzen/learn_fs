# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hardirq.h

Purpose: Defines PowerPC hardirq accounting layout and stack/interrupt entry helpers required by the generic IRQ subsystem.

Important APIs, types, and functions: `irq_cpustat_t` embeds `__softirq_pending` and optional `timer_irqs_event`. `ack_bad_irq()` is declared for unexpected IRQs. `ARCH_WANTS_NMI_IRQSTAT` advertises architecture NMI irqstat needs.

Control flow: Low-level interrupt entry increments/uses per-CPU irq stats, generic hardirq code reads pending softirq state, and unexpected vectors call `ack_bad_irq()`.

State and persistence: Per-CPU irq statistics are volatile runtime state. No persistence beyond kernel memory.

Dependencies and integration points: Depends on generic hardirq definitions and PowerPC low-level interrupt code. It integrates with softirq scheduling and debug/accounting code.

Risks: Layout must match generic expectations. Optional event accounting is config-sensitive, and bad IRQ handling must avoid recursive interrupt failure.

Test signals: Interrupt storm handling, bad IRQ reporting, softirq pending propagation, timer IRQ event accounting under `CONFIG_PPC_WATCHDOG`, and SMP per-CPU stat isolation.
