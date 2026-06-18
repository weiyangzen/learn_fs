# sources/distributed-fs/ceph-client/arch/m68k/virt/ints.c

## Purpose

supports the m68k virtual platform used by emulators, including bootinfo parsing, Goldfish timer,
platform devices, interrupts, and reboot hooks

## Important APIs, Types, and Functions

Source read size: 154 lines, 3698 bytes. Includes: `linux/delay.h`, `linux/interrupt.h`,
`linux/irq.h`, `linux/kernel.h`, `linux/sched.h`, `linux/sched/debug.h`, `linux/types.h`,
`linux/ioport.h`, `asm/hwtest.h`, `asm/irq.h`, `asm/irq_regs.h`, `asm/processor.h`; plus 1 more.
Defined functions: `gfpic_read`, `gfpic_write`, `virt_irq_enable`, `virt_irq_disable`,
`virt_irq_startup`, `virt_nmi_handler`, `goldfish_pic_irq`, `virt_init_IRQ`. Declared functions:
`ioread32be`, `iowrite32be`, `m68k_setup_irq_controller`, `DEFINE_RES_MEM_NAMED`, `pr_err`,
`irq_set_chained_handler`. Key macros/defines: `GFPIC_REG_IRQ_PENDING`, `GFPIC_REG_IRQ_DISABLE_ALL`,
`GFPIC_REG_IRQ_DISABLE`, `GFPIC_REG_IRQ_ENABLE`, `GF_PIC(irq)`, `GF_IRQ(irq)`.

## Control Flow and Behavior

control flow starts from the machine config entry, which fills machdep callbacks, configures
IRQ/timer/console/reset hooks, parses bootinfo where needed, and registers platform devices

## State and Persistence

persistent state includes global machdep function pointers, board control register values, parsed
bootinfo data, timer/IRQ state, and platform-device registration records

## Dependencies and Integration Points

integrates with arch/m68k setup, bootinfo records, generic IRQ/time/reboot/platform-device
frameworks, and board-specific hardware headers

## Risks and Test Signals

incorrect callbacks or register programming can prevent console, timer, disk, or reset operation;
board defconfig builds, boot logs, timer ticks, interrupts, and reboot tests are signals
