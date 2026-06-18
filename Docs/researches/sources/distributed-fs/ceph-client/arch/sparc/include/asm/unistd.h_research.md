# sources/distributed-fs/ceph-client/arch/sparc/include/asm/unistd.h

Purpose: SPARC architecture header `unistd.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: macros/constants `_SPARC_UNISTD_H`, `NR_syscalls`, `__NR_time`, `__ARCH_WANT_NEW_STAT`, `__ARCH_WANT_OLD_READDIR`, `__ARCH_WANT_STAT64`, `__ARCH_WANT_SYS_ALARM`, `__ARCH_WANT_SYS_GETHOSTNAME`, `__ARCH_WANT_SYS_PAUSE`, `__ARCH_WANT_SYS_SIGNAL`, `__ARCH_WANT_SYS_TIME32`, `__ARCH_WANT_SYS_UTIME32`, `__ARCH_WANT_SYS_WAITPID`, `__ARCH_WANT_SYS_SOCKETCALL`, `__ARCH_WANT_SYS_FADVISE64`, `__ARCH_WANT_SYS_GETPGRP`, `__ARCH_WANT_SYS_NICE`, `__ARCH_WANT_SYS_OLDUMOUNT`, plus 11 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC_UNISTD_H`, `__32bit_syscall_numbers__`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into syscall/ptrace paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `uapi/asm/unistd.h`. Integration points include syscall/ptrace; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are ABI compatibility breaks. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
