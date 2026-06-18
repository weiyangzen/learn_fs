# sources/distributed-fs/ceph-client/arch/sh/kernel/irq_32.c

Purpose: provides 32-bit SH compact IRQ flag save/restore helpers.

Important APIs and control flow: `arch_local_irq_restore()` writes the interrupt mask bits in SR. If passed `ARCH_IRQ_DISABLED`, it sets the IMASK bits with `or #0xf0`; otherwise it clears the disabled mask and, on CPUs with banked SR RB support, merges the saved `r6_bank` value before loading SR. `arch_local_save_flags()` reads SR and returns only the IMASK bits. Both helpers are marked `notrace` and exported for low-level users.

State, dependencies, and risks: state is the processor SR interrupt mask and optional banked register context. Dependencies include `ARCH_IRQ_DISABLED`, `CONFIG_CPU_HAS_SR_RB`, inline assembly constraints, and Linux irqflags semantics. Risks are severe because incorrect SR restoration can leave interrupts permanently masked or restore the wrong bank bit. Test signals are irqflags tracing-free builds, nested local_irq_save/restore behavior, interrupt enable/disable stress, and CPU variants with/without SR.RB banking.
