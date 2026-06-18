# sources/distributed-fs/ceph-client/arch/csky/include/asm/bitops.h

## Purpose

provides architecture bit operations and delegates generic helpers where appropriate

## Important APIs, Types, and Functions

Source read size: 79 lines, 1406 bytes. Includes: `linux/compiler.h`, `asm/barrier.h`, `asm-
generic/bitops/ffz.h`, `asm-generic/bitops/fls64.h`, `asm-generic/bitops/sched.h`, `asm-
generic/bitops/hweight.h`, `asm-generic/bitops/lock.h`, `asm-generic/bitops/atomic.h`, `asm-
generic/bitops/non-atomic.h`, `asm-generic/bitops/le.h`; plus 1 more. Functions: `ffs`, `__ffs`,
`fls`, `__fls`. Key macros/defines: `__ASM_CSKY_BITOPS_H`.

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
