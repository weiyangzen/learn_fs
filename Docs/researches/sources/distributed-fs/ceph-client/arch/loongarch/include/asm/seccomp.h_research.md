<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/seccomp.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/seccomp.h

Purpose: maps LoongArch syscall architecture identifiers into the generic seccomp/audit ABI.
Important APIs and types: defines `SECCOMP_ARCH_NATIVE` and compatibility constants for 32-bit/64-bit LoongArch when enabled.
Control flow: seccomp and audit code use these constants while evaluating filters against syscall events. There is no local runtime logic.
State and persistence: no state; constants become part of userspace filter ABI expectations.
Dependencies and integration: depends on `linux/audit.h` architecture tags and `asm/unistd.h` syscall-number selection.
Risks and test signals: wrong audit arch values cause filters to match the wrong ABI or reject valid syscalls. Signals include seccomp selftests, audit syscall tests, and compat syscall tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/seccomp.h -->
