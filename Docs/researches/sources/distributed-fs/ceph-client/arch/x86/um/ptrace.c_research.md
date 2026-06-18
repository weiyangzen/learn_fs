<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/ptrace.c

## Purpose
`ptrace.c` implements UML regset views and FP state conversions shared by ptrace, core dumps, and signal code.

## Important APIs, types, and functions
Key functions include i387/fxsr conversion helpers, `genregs_get()`, `genregs_set()`, `generic_fpregs_get/set()`, `task_user_regset_view()`, and `init_regset_xstate_info()`.

## Control flow
Regset operations iterate saved UML register slots, copy FP/XSTATE buffers, and expose i386/x86_64 note types through `user_uml_view`.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/ptrace.c -->
