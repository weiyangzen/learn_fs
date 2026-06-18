# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/exceptions.h

## Purpose

declares exception handlers and hardware exception enable/disable helpers

## Important APIs, Types, and Functions

Source read size: 69 lines, 1930 bytes. Declared functions: `Copyright`. Key macros/defines:
`_ASM_MICROBLAZE_EXCEPTIONS_H`, `HWEX_MSR_BIT`, `__enable_hw_exceptions()`,
`__disable_hw_exceptions()`.

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
