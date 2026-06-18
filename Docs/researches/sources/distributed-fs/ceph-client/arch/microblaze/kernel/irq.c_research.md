# sources/distributed-fs/ceph-client/arch/microblaze/kernel/irq.c

Purpose: bridges low-level MicroBlaze interrupt entry to the generic Linux IRQ subsystem.

Important APIs and state: `do_IRQ(struct pt_regs *regs)` is called from `_interrupt`; `init_IRQ()` initializes irqchips from the device tree.

Control flow: `do_IRQ()` installs IRQ regs, marks hard IRQs off, enters IRQ context, calls `handle_arch_irq(regs)`, exits IRQ context, restores prior regs, and marks hard IRQs on. `init_IRQ()` delegates to `irqchip_init()`.

State and persistence: updates per-CPU IRQ context accounting and current IRQ regs; no persistent architecture data is allocated here.

Dependencies and integration: requires `handle_arch_irq` from irqchip initialization and correct assembly-provided `pt_regs`.

Risks and test signals: missing irqchip or bad OF interrupt tree leaves `handle_arch_irq` unusable. Test timer interrupts, nested IRQ accounting, lockdep hardirq state, and DT irqchip probing.
