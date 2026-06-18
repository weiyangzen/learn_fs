<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/stub_segv.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/stub_segv.c

## Purpose
`stub_segv.c` provides the signal handler used inside UML syscall stubs to capture fault information.

## Important APIs, types, and functions
`stub_segv_handler()` is placed in `.__syscall_stub`.

## Control flow
On SIGSEGV it extracts fault info from host ucontext into stub data and traps back to the UML monitor with `int3`.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/stub_segv.c -->
