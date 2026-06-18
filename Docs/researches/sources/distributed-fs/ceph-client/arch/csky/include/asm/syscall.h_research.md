# sources/distributed-fs/ceph-client/arch/csky/include/asm/syscall.h

## Purpose

defines syscall argument, number, rollback, and return-value accessors

## Important APIs, Types, and Functions

Source read size: 81 lines, 1697 bytes. Includes: `linux/sched.h`, `linux/err.h`, `abi/regdef.h`,
`uapi/linux/audit.h`. Functions: `syscall_get_nr`, `syscall_set_nr`, `syscall_rollback`,
`syscall_get_error`, `syscall_get_return_value`, `syscall_set_return_value`,
`syscall_get_arguments`, `syscall_set_arguments`, `syscall_get_arch`. Key macros/defines:
`__ASM_SYSCALL_H`.

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
