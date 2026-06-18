<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/sys_call_table_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/sys_call_table_64.c

## Purpose
`sys_call_table_64.c` builds the x86-64 UML syscall dispatch table.

## Important APIs, types, and functions
It maps unsupported `iopl`/`ioperm` to `sys_ni_syscall`, includes `asm/syscalls_64.h`, and exports `sys_call_table` plus `syscall_table_size`.

## Control flow
Preprocessor expansion declares syscall prototypes and then fills the cacheline-aligned table.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/sys_call_table_64.c -->
