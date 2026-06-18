# sources/distributed-fs/ceph-client/arch/m68k/sun3/sun3ints.c

## Purpose

initializes and dispatches Sun-3 interrupt sources through m68k interrupt entry and generic IRQ
handling

## Important APIs, Types, and Functions

Source read size: 100 lines, 2142 bytes. Includes: `linux/types.h`, `linux/kernel.h`,
`linux/sched.h`, `linux/kernel_stat.h`, `linux/interrupt.h`, `asm/intersil.h`, `asm/oplib.h`,
`asm/sun3ints.h`, `asm/irq_regs.h`, `linux/seq_file.h`, `sun3.h`. Defined functions:
`sun3_disable_interrupts`, `sun3_enable_interrupts`, `sun3_enable_irq`, `sun3_disable_irq`,
`sun3_int7`, `sun3_int5`, `sun3_vec255`, `sun3_init_IRQ`. Declared functions: `sun3_leds`,
`local_irq_save`, `m68k_setup_user_interrupt`.

## Control Flow and Behavior

control flow is driven by platform initialization, machdep callbacks, interrupt entry, or driver
DMA/clock requests depending on the file

## State and Persistence

persistent state is hardware register state, installed callbacks, cached IDPROM/RTC data, or
MMU/DVMA mappings as appropriate

## Dependencies and Integration Points

integrates with asm/machdep.h, Sun-3 PROM/oplib, sun3.h prototypes, m68k traps, generic
IRQ/timekeeping, and device drivers

## Risks and Test Signals

hardware register ordering and firmware assumptions are the main risks; Sun-3 defconfig boot, PROM
diagnostics, clock, IRQ, and device I/O tests are signals
