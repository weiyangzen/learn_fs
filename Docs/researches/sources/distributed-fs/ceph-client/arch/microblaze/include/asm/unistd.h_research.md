# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/unistd.h

## Purpose

connects MicroBlaze syscall numbering to generic generated syscall headers

## Important APIs, Types, and Functions

Source read size: 38 lines, 1053 bytes. Includes: `uapi/asm/unistd.h`. Key macros/defines:
`_ASM_MICROBLAZE_UNISTD_H`, `__ARCH_WANT_NEW_STAT`, `__ARCH_WANT_STAT64`, `__ARCH_WANT_SYS_ALARM`,
`__ARCH_WANT_SYS_GETHOSTNAME`, `__ARCH_WANT_SYS_PAUSE`, `__ARCH_WANT_SYS_SIGNAL`,
`__ARCH_WANT_SYS_TIME32`, `__ARCH_WANT_SYS_UTIME32`, `__ARCH_WANT_SYS_WAITPID`,
`__ARCH_WANT_SYS_SOCKETCALL`, `__ARCH_WANT_SYS_FADVISE64`, `__ARCH_WANT_SYS_GETPGRP`,
`__ARCH_WANT_SYS_NICE`, `__ARCH_WANT_SYS_OLDUMOUNT`, `__ARCH_WANT_SYS_SIGPENDING`,
`__ARCH_WANT_SYS_SIGPROCMASK`, `__ARCH_WANT_SYS_CLONE`, `__ARCH_WANT_SYS_VFORK`,
`__ARCH_WANT_SYS_FORK`.

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
