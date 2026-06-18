# sources/distributed-fs/ceph-client/arch/csky/include/asm/ftrace.h

## Purpose

defines ftrace call-site and graph tracing architecture hooks

## Important APIs, Types, and Functions

Source read size: 32 lines, 631 bytes. Functions: `ftrace_call_adjust`. Key macros/defines:
`__ASM_CSKY_FTRACE_H`, `MCOUNT_INSN_SIZE`, `HAVE_FUNCTION_GRAPH_FP_TEST`,
`ARCH_SUPPORTS_FTRACE_OPS`, `MCOUNT_ADDR`. Local structs: `dyn_arch_ftrace`.

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
