<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/ptrace_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/ptrace_64.c

## Purpose
`ptrace_64.c` implements 64-bit UML register get/set, USER-area access, and `PTRACE_ARCH_PRCTL`.

## Important APIs, types, and functions
`putreg()`, `poke_user()`, `getreg()`, `peek_user()`, and `subarch_ptrace()`.

## Control flow
The code validates canonical FS/GS bases and ring-3 segment selectors, maps user offsets to host register indices, handles debug registers, and routes FP/arch_prctl requests.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/ptrace_64.c -->
