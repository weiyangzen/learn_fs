# sources/distributed-fs/ceph-client/arch/csky/include/asm/perf_event.h

## Purpose

declares perf architecture support limits

## Important APIs, Types, and Functions

Source read size: 14 lines, 359 bytes. Includes: `abi/regdef.h`. Key macros/defines:
`__ASM_CSKY_PERF_EVENT_H`, `perf_arch_fetch_caller_regs(regs, __ip)`.

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
