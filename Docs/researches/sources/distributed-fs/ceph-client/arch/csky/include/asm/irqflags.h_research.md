# sources/distributed-fs/ceph-client/arch/csky/include/asm/irqflags.h

## Purpose

implements local interrupt enable/disable/save/restore primitives

## Important APIs, Types, and Functions

Source read size: 49 lines, 1132 bytes. Includes: `abi/reg_ops.h`, `asm-generic/irqflags.h`.
Functions: `arch_local_irq_save`, `arch_local_irq_enable`, `arch_local_irq_disable`,
`arch_local_save_flags`, `arch_local_irq_restore`, `arch_irqs_disabled_flags`. Key macros/defines:
`__ASM_CSKY_IRQFLAGS_H`, `arch_local_irq_save`, `arch_local_irq_enable`, `arch_local_irq_disable`,
`arch_local_save_flags`, `arch_local_irq_restore`, `arch_irqs_disabled_flags`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
