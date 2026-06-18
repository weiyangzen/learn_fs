## sources/distributed-fs/ceph-client/arch/arm64/kernel/syscall.c

### Purpose
`syscall.c` is the common EL0 SVC dispatcher for native and compat ARM64 syscalls. It handles syscall work flags, tracing, MTE async faults, stack randomization, nospec table indexing, fallback private compat syscalls, and return-value storage.

### Important APIs, Types, And Functions
Key functions are `do_el0_svc`, `do_el0_svc_compat`, `el0_svc_common`, `invoke_syscall`, `do_ni_syscall`, `has_syscall_work`, and `__invoke_syscall`.

### Control Flow
The dispatcher stores the original first argument and syscall number, checks for pending asynchronous MTE faults and returns restart state before executing the syscall, handles ptrace/audit/seccomp-style entry work, calls the selected syscall from the native or compat table with `array_index_nospec`, writes the return value into pt_regs, and conditionally performs exit tracing or single-step work.

### State, Persistence, And Dependencies
State is current thread flags, pt_regs syscall fields, randomized kernel stack offset, trace/audit state, and returned register values. It has no independent persistence.

### Integration Points
It connects exception entry assembly to `sys.c`, `sys32.c`, `sys_compat.c`, generic syscall tracing, seccomp/ptrace/audit, MTE, debug monitors, and rseq debug handling.

### Risks
Skipping or tracing syscall numbers must preserve ABI expectations around `NO_SYSCALL` and `x0`. Missing nospec indexing would expose table speculation risk. MTE async fault ordering intentionally prevents the syscall from executing.

### Test Signals
Run syscall ABI and ptrace/seccomp/audit tests, compat SVC tests, out-of-range syscall tests, MTE async fault tests, single-step syscall tests, and kstack offset hardening coverage.
