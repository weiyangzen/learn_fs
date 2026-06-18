# sources/distributed-fs/ceph-client/arch/arm/include/asm/unistd.h

## Purpose
Defines ARM syscall-number selection, ABI compatibility wants, ignored legacy syscalls, and inclusion of generated syscall tables.

## Important APIs, Types, And Functions
Important macros/constants include __ASM_ARM_UNISTD_H, __ARCH_WANT_NEW_STAT, __ARCH_WANT_STAT64, __ARCH_WANT_SYS_GETHOSTNAME, __ARCH_WANT_SYS_PAUSE, __ARCH_WANT_SYS_GETPGRP, __ARCH_WANT_SYS_NICE, __ARCH_WANT_SYS_SIGPENDING. It depends directly on #include <uapi/asm/unistd.h>, #include <asm/unistd-nr.h>.

## Control Flow
Build-time syscall table generation and entry code use the __ARCH_WANT_* and __IGNORE_* definitions to expose ARM-compatible system calls.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <uapi/asm/unistd.h>, #include <asm/unistd-nr.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
