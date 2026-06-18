# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/maltaint.h

Purpose: Interrupt number assignments for Malta boards across CPU, MSC01C, and MSC01E interrupt configurations.

Important APIs/types/functions: `MALTA_INT_BASE` starts at zero. CPU interrupt aliases include software interrupts, mailbox pins, I8259A, GIC chained interrupt, SMI, and core high/low lines. `MSC01C_INT_BASE` and `MSC01E_INT_BASE` are `96`, with constants for timer, PCI, software, mailbox, performance counter, and CPU counter interrupts.

Control flow, state, and persistence: No functions or state. These constants drive interrupt mapping tables and chained interrupt setup.

Dependencies and integration: Consumed by Malta IRQ setup, legacy i8259 routing, GIC integration, and MSC01 interrupt-controller code.

Risks and test signals: Off-by-one or base mismatches route interrupts to wrong Linux IRQs. Test by booting Malta variants, verifying timer tick, PCI interrupts, SMI, software IRQs, and GIC chained delivery.
