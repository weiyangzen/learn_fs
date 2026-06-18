<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/seccomp.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/seccomp.h

Purpose: wires Xtensa into generic seccomp by declaring the native audit architecture, syscall count, and human-readable name. Important definitions are `SECCOMP_ARCH_NATIVE`, `SECCOMP_ARCH_NATIVE_NR`, and `SECCOMP_ARCH_NATIVE_NAME`, plus inclusion of `asm-generic/seccomp.h`.

Control flow is generic: seccomp and audit code compare syscall metadata against these constants when filtering. State is not stored here; runtime state lives in task seccomp filters and audit records. Dependencies include `AUDIT_ARCH_XTENSA` and `NR_syscalls`. Integration points are `ptrace.c` syscall entry, `secure_computing()`, audit, BPF seccomp filters, and libc sandboxing. Risks are audit architecture mismatch or syscall-count drift leading to bad filter behavior. Test signals include seccomp filter selftests, audit syscall records, invalid syscall filtering, and syscall table count consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/seccomp.h -->
