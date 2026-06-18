<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/bugs_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/bugs_64.c

## Purpose
`bugs_64.c` is the 64-bit UML placeholder for architecture bug checks.

## Important APIs, types, and functions
`arch_check_bugs()` and `arch_examine_signal()` are empty implementations.

## Control flow
Boot and signal paths call these hooks, but 64-bit UML has no CMOV-style compatibility check here.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/bugs_64.c -->
