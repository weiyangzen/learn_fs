<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/syscalls_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/syscalls_64.c

## Purpose
`syscalls_64.c` implements 64-bit UML `arch_prctl`, context-switch no-op, and mmap offset validation.

## Important APIs, types, and functions
`arch_prctl()`, `SYSCALL_DEFINE2(arch_prctl)`, `arch_switch_to()`, and `SYSCALL_DEFINE6(mmap)`.

## Control flow
FS/GS base options read/write saved register slots; mmap rejects unaligned byte offsets and calls `ksys_mmap_pgoff`.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/syscalls_64.c -->
