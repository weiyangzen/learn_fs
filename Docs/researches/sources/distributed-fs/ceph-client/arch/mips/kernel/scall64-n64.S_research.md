# sources/distributed-fs/ceph-client/arch/mips/kernel/scall64-n64.S

## Purpose
Implements native n64 syscall entry for 64-bit MIPS kernels.

## Important APIs, Types, and Functions
- `handle_sys64` is the n64 syscall entry.
- `sys_call_table` is exported from `asm/syscall_table_n64.h`.

## Control Flow
When no 32-bit compatibility entry has already performed common setup, `handle_sys64` saves pt_regs, enables interrupts, and advances EPC. It saves `a3`, records `TI_SYSCALL`, optionally calls `syscall_trace_enter()`, validates the syscall number against the n64 range, loads the target from `sys_call_table`, calls it, converts errno returns into MIPS error flag format, stores result and restart syscall number, and exits through `syscall_exit_partial`. Invalid calls return `ENOSYS`.

## State and Persistence
Mutates pt_regs and thread-info syscall state. No persistence.

## Dependencies and Integration Points
Depends on stackframe macros, n64 syscall numbering/table generation, syscall trace hooks from `ptrace.c`, and compatibility entry routing from o32/n32 files.

## Risks
Initial save/EPC advancement is conditional on compat config and must not duplicate setup. Error conversion must preserve restart data in `PT_R0`. Null table entries are treated as illegal syscalls.

## Test Signals
n64 syscall ABI, invalid syscall, ptrace/seccomp/audit tracing, restartable syscall, and mixed compat routing tests should pass.
