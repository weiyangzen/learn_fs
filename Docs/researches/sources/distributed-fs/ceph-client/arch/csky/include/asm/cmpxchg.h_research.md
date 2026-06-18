# sources/distributed-fs/ceph-client/arch/csky/include/asm/cmpxchg.h

## Purpose

implements cmpxchg/xchg helpers and atomic exchange contracts

## Important APIs, Types, and Functions

Source read size: 165 lines, 4256 bytes. Includes: `linux/bug.h`, `asm/barrier.h`, `linux/cmpxchg-
emu.h`, `asm-generic/cmpxchg.h`. Key macros/defines: `__ASM_CSKY_CMPXCHG_H`, `__xchg_relaxed(new,
ptr, size)`, `arch_xchg_relaxed(ptr, x)`, `__cmpxchg_relaxed(ptr, old, new, size)`,
`arch_cmpxchg_relaxed(ptr, o, n)`, `__cmpxchg_acquire(ptr, old, new, size)`,
`arch_cmpxchg_acquire(ptr, o, n)`, `__cmpxchg(ptr, old, new, size)`, `arch_cmpxchg(ptr, o, n)`,
`arch_cmpxchg_local(ptr, o, n)`.

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
