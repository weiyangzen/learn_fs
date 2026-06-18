# sources/distributed-fs/ceph-client/arch/m68k/q40/q40ints.c

## Purpose

implements Q40 interrupt controller setup, IRQ masking/unmasking, timer interrupt handling, and
legacy sound tick programming

## Important APIs, Types, and Functions

Source read size: 334 lines, 8121 bytes. Includes: `linux/types.h`, `linux/kernel.h`,
`linux/errno.h`, `linux/interrupt.h`, `linux/irq.h`, `asm/machdep.h`, `asm/ptrace.h`, `asm/traps.h`,
`asm/q40_master.h`, `asm/q40ints.h`, `q40.h`. Defined functions: `q40_irq_startup`,
`q40_irq_shutdown`, `q40_init_IRQ`, `q40_mksound`, `q40_timer_int`, `q40_sched_init`,
`q40_irq_handler`, `q40_irq_enable`, `q40_irq_disable`. Declared functions: `Copyright`, `pr_warn`,
`m68k_irq_startup_irq`, `local_irq_save`, `floppy_hardint`, `do_IRQ`, `disable_irq`, `enable_irq`,
`master_outb`. Key macros/defines: `SVOL`, `IRQ_INPROGRESS`, `DEBUG_Q40INT`. Types visible in this
file: `IRQ_TABLE`.

## Control Flow and Behavior

q40_init_IRQ() installs irq_chip handlers, q40_irq_startup()/shutdown()/enable()/disable()
manipulate hardware masks, q40_timer_int() drives the scheduler tick, q40_sched_init() requests the
timer IRQ, and q40_irq_handler() demultiplexes pending sources

## State and Persistence

persistent state includes disabled/active IRQ mask bits, timer programming, IRQ chip state, and in-
progress IRQ bookkeeping

## Dependencies and Integration Points

integrates with asm/q40_master.h, asm/q40ints.h, generic irq_chip/handle_irq_event, machdep
interrupt entry, and timer/sound hooks from q40/config.c

## Risks and Test Signals

lost mask updates or bad demux ordering produce stuck IRQs or timer stalls; boot IRQ logs,
keyboard/network/disk interrupts, timer tick accounting, and sound tests are signals
