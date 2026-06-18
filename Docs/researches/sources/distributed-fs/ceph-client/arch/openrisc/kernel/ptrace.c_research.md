<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/ptrace.c

## Purpose
Implements OpenRISC ptrace regsets, register-offset lookup, stack access helpers, and syscall trace/audit hooks.

## Important APIs, Types, And Functions
`genregs_get/set()` expose GPRs, PC, and SR while ignoring writes to SR. Optional `fpregs_get/set()` exposes `fpcsr`. `task_user_regset_view()`, `regs_query_register_offset()`, `regs_get_kernel_stack_nth()`, `ptrace_disable()`, `arch_ptrace()`, `do_syscall_trace_enter()`, and `do_syscall_trace_leave()` complete the interface.

## Control Flow
Ptrace requests route through generic `ptrace_request()` after architecture detach cleanup. Syscall entry may ask ptrace to skip a syscall, then records audit arguments; syscall exit reports audit and ptrace single-step/syscall-exit events.

## State And Persistence
Reads and writes task `pt_regs` and thread FPU state. Clears syscall trace/single-step flags on detach.

## Dependencies And Integration Points
Depends on UAPI regset layout, audit, ptrace core, `entry.S` syscall tracing branches, and task stack layout.

## Risks
Regset size uses 32-bit word assumptions. Letting userspace change SR would be dangerous, so writes are ignored. Syscall skip returns `-1` as a bogus syscall number and relies on entry code bounds handling.

## Test Signals
GDB attach/detach, `PTRACE_GETREGSET`/`SETREGSET`, syscall trace skip tests, audit records, and stack dump helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/ptrace.c -->
