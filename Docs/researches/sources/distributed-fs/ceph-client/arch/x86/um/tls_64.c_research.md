<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/tls_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/tls_64.c

## Purpose
`tls_64.c` implements the minimal 64-bit UML TLS hooks.

## Important APIs, types, and functions
`clear_flushed_tls()` is empty and `arch_set_tls()` stores CLONE_SETTLS value into the saved FS_BASE register slot.

## Control flow
Context switches need no explicit TLS descriptor load because FS/GS base travels in the ptrace register set.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/tls_64.c -->
