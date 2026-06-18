# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/irqflags.h

## Purpose

implements interrupt flag save/restore, enable, disable, and MSR bit manipulation

## Important APIs, Types, and Functions

Source read size: 119 lines, 2529 bytes. Includes: `linux/types.h`, `asm/registers.h`. Defined
functions: `Copyright`, `arch_local_irq_disable`, `arch_local_irq_enable`, `arch_local_irq_save`,
`arch_local_save_flags`, `arch_local_irq_restore`, `arch_irqs_disabled_flags`, `arch_irqs_disabled`.
Declared functions: `volatile`, `arch_irqs_disabled_flags`. Key macros/defines:
`_ASM_MICROBLAZE_IRQFLAGS_H`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
