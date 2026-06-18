# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hw_irq.h

Purpose: Implements PowerPC local interrupt masking primitives, soft-mask state, lazy interrupt replay checks, PMI handling, and idle IRQ preparation declarations.

Important APIs, types, and functions: Defines `PACA_IRQ_*` pending bits, soft mask states, hard enable/disable helpers, `irq_soft_mask_*()` operations, `arch_local_irq_*()` operations, PMI pending helpers, PMU save/restore macros, `hard_irq_disable()`, `lazy_irq_pending()`, `should_hard_irq_enable()`, `do_hard_irq_enable()`, `arch_irq_disabled_regs()`, idle prep APIs, and `mtmsr_isync_irqsafe()`.

Control flow: Code manipulates soft mask bits in PACA/regs, disables or enables hardware EE/RI bits as required, queues pending events for lazy replay, treats PMI specially where necessary, and prepares idle paths to avoid losing pending interrupts.

State and persistence: Runtime state lives in PACA fields, MSR bits, pt_regs snapshots, and pending interrupt bits. No persistent storage exists.

Dependencies and integration points: Depends on PACA, MSR accessors, tracing, lockdep IRQ state, PMU code, idle code, and low-level exception entry/exit.

Risks: Hardware and software masks can diverge. Enabling hard IRQs in unsafe contexts risks reentrancy. PMI handling is config-sensitive. Lazy pending bits must be replayed in the right order.

Test signals: IRQ enable/disable nesting, soft-mask transitions through exception entry/exit, PMU interrupt save/restore, idle entry with pending IRQs, lockdep IRQ tracing, and SMP stress with doorbell/decrementer/external interrupts.
