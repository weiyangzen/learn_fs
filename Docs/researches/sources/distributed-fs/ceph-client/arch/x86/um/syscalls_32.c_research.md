<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/syscalls_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/syscalls_32.c

## Purpose
`syscalls_32.c` supplies the 32-bit UML `arch_prctl` syscall stub.

## Important APIs, types, and functions
`SYSCALL_DEFINE2(arch_prctl)` always returns `-EINVAL`.

## Control flow
The syscall table can expose the symbol, but i386 UML does not implement x86-64 FS/GS base arch_prctl semantics.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/syscalls_32.c -->
