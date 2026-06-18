# sources/distributed-fs/ceph-client/arch/mips/kernel/scall32-o32.S

## Purpose
Implements 32-bit MIPS o32 syscall entry and the o32 indirect `sys_syscall` helper for 32-bit kernels.

## Important APIs, Types, and Functions
- `handle_sys` is the o32 syscall exception entry.
- `sys_syscall` implements the userspace `syscall(__NR_x, ...)` indirection helper.
- `sys_call_table` is exported from `asm/syscall_table_o32.h`.

## Control Flow
`handle_sys` saves partial pt_regs with `SAVE_SOME`, enables interrupts, advances EPC past the syscall instruction, saves `a3` for restart, copies arguments 5-8 from the user stack into pt_regs with exception-table fixups, stores the original syscall number in `TI_SYSCALL`, optionally calls `syscall_trace_enter()`, range-checks the o32 syscall number, loads the table entry, calls it, converts negative errno returns into positive errno plus error flag in `PT_R7`, stores the result in `PT_R2`, and exits through `syscall_exit_partial`. Bad user stack or missing syscall produces `EFAULT`/`ENOSYS`.

## State and Persistence
Mutates the current exception frame, thread-info syscall field, and return registers. No persistent storage.

## Dependencies and Integration Points
Depends on MIPS entry stackframe macros, user access macros, o32 syscall numbering, `syscall_trace_enter/leave` from `ptrace.c`, and generic syscall table generation. Optional MIPS MT FPU-affinity aliases scheduler affinity syscalls.

## Risks
Argument 5-8 stack copying is fragile and intentionally uses a coarse stack pointer sanity check. Indirect syscall handling must avoid recursion and shift arguments correctly. Error convention relies on `-EMAXERRNO` threshold and o32 `a3` error flag.

## Test Signals
o32 syscall ABI tests should validate six/eight-argument syscalls, indirect `syscall()`, invalid syscall numbers, bad user stack faulting, tracing/seccomp skip paths, and errno flag behavior.
