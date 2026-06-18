# sources/distributed-fs/ceph-client/arch/mips/cobalt/irq.c

Purpose: provides Cobalt interrupt initialization and CP0 interrupt dispatch.

Important APIs: `arch_init_irq()` initializes MIPS CPU IRQs, GT641xx interrupts, and i8259 interrupts, then requests cascade IRQs with `no_action`. `plat_irq_dispatch()` prioritizes GT641xx on IP2, i8259 on IP6, then CPU IRQs IP3/IP4/IP5/IP7, otherwise spurious.

Control flow and state: dispatch reads CP0 status/cause pending bits and forwards to `gt641xx_irq_dispatch()`, `i8259_irq()`, or `do_IRQ()`. There is no local persistent state beyond registered cascade descriptors.

Dependencies and integration: depends on GT64120/GT641xx and i8259 interrupt support plus Cobalt IRQ constants from `<irq.h>`.

Risks and test signals: cascade IRQ registration must match platform wiring. Boot should show no failed cascade requests; devices behind PCI/ISA should generate interrupts through the expected paths; spurious interrupt counters should remain low.
