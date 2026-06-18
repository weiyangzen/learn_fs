# sources/distributed-fs/ceph-client/arch/arm/kernel/ptrace.c

Purpose: implements ARM ptrace user ABI, register regsets, software breakpoint trap hooks, hardware breakpoint ptrace access, VFP/iWMMXt register transfer, and syscall tracing entry/exit.

Important APIs/types/functions: register helpers `regs_query_register_offset/name`, `regs_within_kernel_stack`, `regs_get_kernel_stack_nth`; ptrace hooks `arch_ptrace`, `ptrace_disable`, `ptrace_break`; regset view `task_user_regset_view`; syscall hooks `syscall_trace_enter/exit`. HW breakpoint helpers convert virtual ptrace HBP register numbers to perf events.

Control flow: init registers ARM/Thumb undef hooks for breakpoint instructions. `arch_ptrace` dispatches classic requests and regset copies, validates user register updates with `valid_user_regs`, creates/modifies user HW breakpoints via perf, and handles thread-area/syscall controls. Syscall entry reports ptrace first, then seccomp, tracepoints, and audit; exit audits, tracepoints, and ptrace reports.

State and persistence: per-task `thread.debug.hbp[]`, fp/VFP/iWMMXt state, `abi_syscall`, and saved `pt_regs` are mutated. Breakpoint hooks persist globally.

Dependencies and integration: perf hw_breakpoint, undef hooks, regset core, audit, seccomp, tracepoints, VFP/iWMMXt, signal delivery, and syscall ABI.

Risks: ptrace exposes a stable ABI, so register layout and HBP numbering must not drift; invalid CPSR/user regs must be rejected; hardware breakpoint lifecycle must not leak across fork/exec. Test signals include `strace`, `gdb`, PTRACE regset tests, HW watchpoint tests, seccomp+ptrace ordering, and syscall tracepoints.
