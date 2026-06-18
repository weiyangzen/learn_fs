<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/irqflags.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/irqflags.h

## Purpose
`irqflags.h` implements m68k local interrupt flag primitives used by spinlocks, preemption, and generic IRQ code.

## Important APIs, Types, and Functions
It defines `arch_local_save_flags()`, `arch_local_irq_disable()`, `arch_local_irq_enable()`, `arch_local_irq_save()`, `arch_local_irq_restore()`, `arch_irqs_disabled_flags()`, and `arch_irqs_disabled()`. The implementations manipulate the status register interrupt priority level.

## Control Flow, State, and Persistence
The functions directly read or write the CPU status register. ColdFire uses `move`/`ori.l`/`andi.l`; classic m68k uses word operations. MMU builds special-case Q40 or non-hardirq contexts when enabling interrupts.

## Dependencies and Integration Points
It depends on `thread_info.h`, `entry.h`, `preempt.h`, and machine macros such as `MACH_IS_ATARI` and `MACH_IS_Q40`. Generic lock and IRQ code call these primitives throughout the kernel.

## Risks
Incorrect masks can enable interrupts in hardirq context or fail to restore IPL. Atari treats HSYNC at IPL 2 specially, so generic disabled-state checks differ from other systems.

## Test Signals
Signals include lockdep/preemption correctness, nested save/restore behavior, Atari HSYNC handling, Q40 interrupt-enable behavior, and compile/run coverage for ColdFire and classic m68k.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/irqflags.h -->
