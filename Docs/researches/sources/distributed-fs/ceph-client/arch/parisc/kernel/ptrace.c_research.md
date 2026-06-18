<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/ptrace.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/ptrace.c

### Purpose
`ptrace.c` implements PA-RISC debugger control, syscall tracing, native/compat regsets, and register name/stack access helpers.

### Important APIs, Types, And Functions
It provides `ptrace_disable()`, single-step and block-step controls, `arch_ptrace()`, `compat_arch_ptrace()`, `do_syscall_trace_enter()`, `do_syscall_trace_exit()`, regset get/set helpers, `task_user_regset_view()`, `regs_query_register_offset()`, `regs_query_register_name()`, `regs_within_kernel_stack()`, and `regs_get_kernel_stack_nth()`.

### Control Flow
Single stepping manipulates PSW recovery/taken-branch bits and handles nullified instructions by advancing the queue and forcing `SIGTRAP`. Ptrace PEEK/POKE validates offsets and restricts writable registers/PSW bits. Compat ptrace translates 32-bit offsets into 64-bit `pt_regs` slots. Syscall entry performs ptrace, seccomp, tracepoint, and audit processing before returning the possibly modified syscall number; exit reports audit, tracepoints, and ptrace exit events.

### State, Persistence, And Dependencies
State is per-task thread flags and saved `pt_regs`. Regsets depend on ELF note constants, compat layout, `membuf`, audit/seccomp, tracepoints, and PA-RISC PSW semantics.

### Integration Points
Used by `ptrace(2)`, GDB, core dumps, syscall entry assembly, kprobes/perf register lookup, and stacktrace APIs.

### Risks
Only selected registers are writable; mismatches with GDB expectations can break debugging. Compat offset translation is layout-sensitive. Ptrace can alter syscall numbers and return registers, so assembly and C paths must agree on saved register locations.

### Test Signals
Run native and compat GDB single-step/block-step, ptrace register read/write, core dump regset checks, seccomp syscall skipping, syscall tracepoints, and kernel stack nth-entry helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/ptrace.c -->
