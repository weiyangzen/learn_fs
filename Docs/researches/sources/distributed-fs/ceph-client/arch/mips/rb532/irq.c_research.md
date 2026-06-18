# sources/distributed-fs/ceph-client/arch/mips/rb532/irq.c

Purpose: interrupt controller support for the RC32434/RB532. It maps grouped interrupt pending/mask registers to Linux IRQs and dispatches CPU interrupt pins.

Important APIs and control flow: `intr_group[]` describes five interrupt groups with valid masks and KSEG1 register bases. `rb532_enable_irq()` and `rb532_disable_irq()` manipulate group masks and CPU IP bits; GPIO mapped interrupts clear GPIO status when disabled. `rb532_set_type()` supports high/low level GPIO IRQs. `arch_init_irq()` installs `rc32434_irq_type` for all RC32434 IRQs. `plat_irq_dispatch()` prioritizes CP0 timer IP7, then finds the highest pending grouped interrupt and calls `do_IRQ()`.

State, persistence, and integration: state lives in hardware interrupt mask registers and CP0 status/cause bits. It depends on GPIO helpers, MIPS IRQ descriptors, and rc32434 IRQ constants. Risks include fragile bit math around `fls()`, no locking around shared mask registers, and limited GPIO trigger type support. Test signals are boot-time IRQ initialization, timer interrupts, Ethernet/CF/GPIO IRQ delivery, and absence of spurious interrupt storms.
