# sources/distributed-fs/ceph-client/arch/csky/include/asm/irq_work.h

## Purpose

declares irq_work availability for C-SKY

## Important APIs, Types, and Functions

Source read size: 11 lines, 208 bytes. Functions: `arch_irq_work_has_interrupt`. Key macros/defines:
`__ASM_CSKY_IRQ_WORK_H`.

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
