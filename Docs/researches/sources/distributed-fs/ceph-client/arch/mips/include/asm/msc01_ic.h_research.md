# sources/distributed-fs/ceph-client/arch/mips/include/asm/msc01_ic.h

Purpose: MIPS System Controller interrupt-controller register definitions and board mapping interface.

Important APIs/types/functions: Defines offsets and absolute addresses for reset, enable/disable masks, raw/masked input status, level/RAM shadow configuration, output status, global enable, vector base/current vector, EOI, config, timer reload/current/config, setup lines, and 64-bit mask/status registers. Field macros cover reset, priority level, spurious flag, shadow RAM read/write fields, global enable, timer enable/interrupt/edge, and setup priority/edge. `msc_irqmap_t` maps board IRQ line, type, and level. `MSC01_IRQ_LEVEL`/`MSC01_IRQ_EDGE` classify trigger type. Externs `init_msc_irqs()` and `ll_msc_irq()` initialize and handle low-level dispatch.

Control flow, state, and persistence: Initialization code programs masks, priorities, and trigger modes from board maps. Interrupt handling reads active vector/status and writes EOI. State persists in interrupt-controller registers.

Dependencies and integration: Requires `MSC01_IC_REG_BASE` from board headers such as Malta. Integrated with MIPS IRQ core, MSC01/SOC-it board setup, and timer interrupt delivery.

Risks and test signals: Priority/trigger configuration and vector base errors can lose or storm interrupts. Test timer, PCI, software, edge/level IRQs, EOI behavior, and board-specific IRQ map coverage.
