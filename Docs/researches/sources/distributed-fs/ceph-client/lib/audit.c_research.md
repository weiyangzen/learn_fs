<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/audit.c -->
# sources/distributed-fs/ceph-client/lib/audit.c

## Purpose
Provides generic audit syscall classification and syscall-class registration for architectures that use `CONFIG_AUDIT_GENERIC`.

## APIs, Types, and Functions
Exports `audit_classify_arch(int arch)` and `audit_classify_syscall(int abi, unsigned syscall)`. Internal arrays define directory-write, read, write, attribute-change, and signal syscall classes by including architecture-generic audit lists. `audit_classes_init()` registers native and optional compat class arrays.

## Control Flow, State, and Persistence
`audit_classify_arch()` returns whether the audit architecture is compat. `audit_classify_syscall()` routes compat ABIs to `audit_classify_compat_syscall()` and otherwise special-cases open, openat, socketcall, execve/execveat, and openat2 before returning `AUDITSC_NATIVE`. The initcall registers class arrays with the audit subsystem. Registered classes persist for the lifetime of the kernel.

## Dependencies and Integration
Depends on `linux/audit.h`, `asm/unistd.h`, asm-generic audit class include files, optional `CONFIG_AUDIT_COMPAT_GENERIC`, and audit registration APIs. Built through `lib/Makefile` under `CONFIG_AUDIT_GENERIC`.

## Risks and Test Signals
Risks include syscall-number availability differences across architectures, compat classification drift, missing new syscall special cases, and class arrays not matching arch syscall tables. Test signals include audit rule tests for open/openat/openat2/execve/socketcall, compat 32-bit syscall auditing, class-based audit filters, and build tests on architectures with and without each `__NR_*` define.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/audit.c -->
