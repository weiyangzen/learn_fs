# sources/distributed-fs/ceph-client/arch/csky/include/asm/traps.h

## Purpose

declares trap initialization and exception C handlers

## Important APIs, Types, and Functions

Source read size: 60 lines, 1447 bytes. Includes: `linux/linkage.h`. Key macros/defines:
`__ASM_CSKY_TRAPS_H`, `VEC_RESET`, `VEC_ALIGN`, `VEC_ACCESS`, `VEC_ZERODIV`, `VEC_ILLEGAL`,
`VEC_PRIV`, `VEC_TRACE`, `VEC_BREAKPOINT`, `VEC_UNRECOVER`, `VEC_SOFTRESET`, `VEC_AUTOVEC`,
`VEC_FAUTOVEC`, `VEC_HWACCEL`, `VEC_TLBMISS`, `VEC_TLBMODIFIED`, `VEC_TRAP0`, `VEC_TRAP1`; plus 7
more.

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
