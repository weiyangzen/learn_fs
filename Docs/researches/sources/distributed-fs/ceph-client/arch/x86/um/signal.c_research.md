<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/signal.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/signal.c

## Purpose
`signal.c` builds and restores x86 UML user signal frames for old i386, RT i386, and x86-64 signal ABIs.

## Important APIs, types, and functions
Important functions are `copy_sc_from_user()`, `copy_sc_to_user()`, `setup_signal_stack_sc()`, `setup_signal_stack_si()`, `sigreturn`, and `rt_sigreturn`.

## Control flow
Delivery copies GPR/fault/FP state to user sigcontext/ucontext frames, writes restorer signatures, aligns stacks per ABI, sets handler arguments/registers, and return syscalls restore signal masks and register state.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/signal.c -->
