# sources/distributed-fs/ceph-client/arch/csky/include/asm/atomic.h

## Purpose

implements C-SKY atomic_t/atomic64_t operations and memory-order variants

## Important APIs, Types, and Functions

Source read size: 202 lines, 4363 bytes. Includes: `asm-generic/atomic64.h`, `asm/cmpxchg.h`,
`asm/barrier.h`, `asm-generic/atomic.h`. Functions: `arch_atomic_read`, `arch_atomic_set`,
`arch_atomic_fetch_add_unless`, `arch_atomic_inc_unless_negative`,
`arch_atomic_dec_unless_positive`, `arch_atomic_dec_if_positive`. Key macros/defines:
`__ASM_CSKY_ATOMIC_H`, `__atomic_acquire_fence()`, `__atomic_release_fence()`, `ATOMIC_OP(op)`,
`ATOMIC_FETCH_OP(op)`, `ATOMIC_OP_RETURN(op, c_op)`, `ATOMIC_OPS(op, c_op)`,
`arch_atomic_fetch_add_relaxed`, `arch_atomic_fetch_sub_relaxed`, `arch_atomic_add_return_relaxed`,
`arch_atomic_sub_return_relaxed`, `ATOMIC_OPS(op)`, `arch_atomic_fetch_and_relaxed`,
`arch_atomic_fetch_or_relaxed`, `arch_atomic_fetch_xor_relaxed`, `arch_atomic_fetch_add_unless`,
`arch_atomic_inc_unless_negative`, `arch_atomic_dec_unless_positive`; plus 1 more.

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
