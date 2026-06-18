# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/delay.h

## Purpose

defines busy-wait delay loops and calibration hooks

## Important APIs, Types, and Functions

Source read size: 85 lines, 2138 bytes. Includes: `linux/param.h`. Defined functions: `Copyright`,
`__udelay`. Declared functions: `volatile`, `__bad_udelay`, `__udelay`. Key macros/defines:
`_ASM_MICROBLAZE_DELAY_H`, `__MAX_UDELAY`, `__MAX_NDELAY`, `udelay(n)`, `ndelay(n)`, `muldiv(a, b,
c)`. External symbols referenced/declared: `loops_per_jiffy`, `__bad_udelay`, `__bad_ndelay`.

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
