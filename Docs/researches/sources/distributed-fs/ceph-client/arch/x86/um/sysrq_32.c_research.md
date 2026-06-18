<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/sysrq_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/sysrq_32.c

## Purpose
`sysrq_32.c` prints 32-bit UML register state for diagnostics.

## Important APIs, types, and functions
`show_regs()` prints EIP/ESP/EFLAGS and i386 GPR/segment fields.

## Control flow
Sysrq/oops paths pass saved pt_regs and the function formats register values with taint/CPU context.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/sysrq_32.c -->
