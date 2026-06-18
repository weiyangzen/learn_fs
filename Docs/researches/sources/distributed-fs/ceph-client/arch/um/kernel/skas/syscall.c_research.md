# sources/distributed-fs/ceph-client/arch/um/kernel/skas/syscall.c

## Purpose
Dispatches syscalls trapped from UML userspace into the kernel syscall table while integrating ptrace, audit, seccomp, and time-travel scheduling behavior.

## Important APIs, Types, and Functions
`handle_syscall()` copies the syscall number from UML pt_regs, initializes `-ENOSYS`, calls `syscall_trace_enter()`, runs `secure_computing()`, invokes `sys_call_table[syscall]` with up to six arguments, stores the return value, and calls `syscall_trace_leave()`.

## Control Flow, State, and Persistence
The function mutates only the current pt_regs and time-travel accounting. In infinite/external time travel, `sched_yield` and error-returning syscalls advance `tt_extra_sched_jiffies` or sleep briefly to avoid pathological busy loops that would starve simulated time.

## Dependencies and Integration Points
Called from the SKAS userspace loop on SIGSYS or ptrace syscall stops. Depends on syscall trace hooks, Linux seccomp, UML syscall/register macros, delay helpers, and the architecture syscall table.

## Risks and Test Signals
Risks include wrong syscall number/argument extraction, seccomp ordering mismatches, and time-travel livelocks. Test normal syscalls, invalid syscall numbers, ptrace syscall tracing, seccomp denial, ASAN spinlocks, and time-travel external simulations.
