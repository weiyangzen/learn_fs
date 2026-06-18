# sources/distributed-fs/ceph-client/arch/csky/include/asm/tcm.h

## Purpose

declares tightly-coupled-memory section and allocator helpers

## Important APIs, Types, and Functions

Source read size: 24 lines, 665 bytes. Includes: `linux/compiler.h`. Key macros/defines:
`__ASM_CSKY_TCM_H`, `__tcmdata`, `__tcmconst`, `__tcmfunc`, `__tcmlocalfunc`.

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
