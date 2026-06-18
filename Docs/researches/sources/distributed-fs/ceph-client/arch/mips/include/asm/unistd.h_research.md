# sources/distributed-fs/ceph-client/arch/mips/include/asm/unistd.h

## Purpose

`unistd.h` selects MIPS syscall-number ranges and generic syscall feature wants for O32, N32, and N64 ABIs.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Includes: `uapi/asm/unistd.h`, `asm/unistd_nr_n32.h`, `asm/unistd_nr_n64.h`, `asm/unistd_nr_o32.h`. Macros/constants: `_ASM_UNISTD_H`, `__NR_N32_Linux`, `__NR_64_Linux`, `__NR_O32_Linux`, `NR_syscalls`, `__ARCH_WANT_NEW_STAT`, `__ARCH_WANT_OLD_READDIR`, `__ARCH_WANT_SYS_ALARM`, `__ARCH_WANT_SYS_GETHOSTNAME`, `__ARCH_WANT_SYS_IPC`, `__ARCH_WANT_SYS_PAUSE`, `__ARCH_WANT_SYS_UTIME`, `__ARCH_WANT_SYS_UTIME32`, `__ARCH_WANT_SYS_WAITPID`, `__ARCH_WANT_SYS_SOCKETCALL`, `__ARCH_WANT_SYS_GETPGRP`, `__ARCH_WANT_SYS_NICE`, `__ARCH_WANT_SYS_OLD_UNAME`, `__ARCH_WANT_SYS_OLDUMOUNT`, `__ARCH_WANT_SYS_SIGPENDING`, `__ARCH_WANT_SYS_SIGPROCMASK`, `__ARCH_WANT_STAT64`, `__ARCH_WANT_SYS_TIME32`, `__ARCH_WANT_COMPAT_STAT`, `__ARCH_WANT_SYS_FORK`, `__ARCH_WANT_SYS_CLONE`, `__IGNORE_fadvise64_64`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with generated syscall tables and generic syscall wrappers.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 68 lines and 1872 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
