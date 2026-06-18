<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/compat_audit.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/compat_audit.c

Purpose: Provides 32-bit SPARC syscall audit classes and syscall classification for compat tasks on SPARC64.

Important APIs and control flow: forces `__32bit_syscall_numbers__` before including syscall numbers, builds exported class arrays from generic audit include fragments, and classifies 32-bit `open`, `openat`, `socketcall`, `execve`, and `openat2` specially while returning `AUDITSC_COMPAT` for all others.

State, dependencies, and risks: state is audit class data used by the native audit initializer. Dependencies include 32-bit syscall-number generation, `linux/audit_arch.h`, generic audit fragments, and declarations in `kernel.h`. Risks are syscall-number mismatch if the 32-bit define is omitted, stale special-case coverage, and class arrays not matching native registrations. Test signals are 32-bit compat audit rules and syscall classification for open/socket/exec paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/compat_audit.c -->
