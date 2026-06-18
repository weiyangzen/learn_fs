# sources/distributed-fs/ceph-client/arch/csky/include/asm/switch_to.h

## Purpose

declares context-switch entry points and switch_to wrapper

## Important APIs, Types, and Functions

Source read size: 35 lines, 923 bytes. Includes: `linux/thread_info.h`, `abi/fpu.h`. Functions:
`__switch_to_fpu`. Key macros/defines: `__ASM_CSKY_SWITCH_TO_H`, `switch_to(prev, next, last)`.
Local structs: `task_struct`.

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
