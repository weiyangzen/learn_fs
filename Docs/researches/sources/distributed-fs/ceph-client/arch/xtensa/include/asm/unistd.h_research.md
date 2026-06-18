<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/unistd.h

Purpose: selects syscall compatibility wants and includes the Xtensa UAPI syscall numbers. Important definitions include `__ARCH_WANT_SYS_CLONE`, `__ARCH_WANT_NEW_STAT`, `__ARCH_WANT_STAT64`, `__ARCH_WANT_SYS_UTIME32`, `__ARCH_WANT_SYS_GETPGRP`, and `NR_syscalls`.

Control flow is compile-time syscall table generation and generic syscall availability selection. State is the generated syscall ABI exposed through `sys_call_table` and UAPI headers. Dependencies include `uapi/asm/unistd.h` and generated `unistd_32.h`. Integration points are syscall table generation, `entry.S` dispatch, libc ABI, seccomp syscall count, and trace/audit. Risks are stale `NR_syscalls`, unintended legacy syscall exposure, and mismatch with generated headers. Test signals include syscall table build, strace syscall numbers, seccomp bounds checks, and legacy stat/utime/clone syscall tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/unistd.h -->
