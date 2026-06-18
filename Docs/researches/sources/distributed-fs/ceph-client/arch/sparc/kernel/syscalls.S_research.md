# sources/distributed-fs/ceph-client/arch/sparc/kernel/syscalls.S

Purpose: provides sparc64 low-level syscall entry wrappers, fork/clone/exec stubs, signal-return stubs, syscall tracing paths, native/compat dispatch, error return protocol, and fork return.

Important APIs/symbols: defines `sys64_execve`, `sys64_execveat`, compat `sys32_execve*`, `sys32_sigstack`, `sys32_sigreturn`, `sys_rt_sigreturn`, `sys32_rt_sigreturn`, `sys_vfork`, `sys_fork`, `sys_clone`, `__sys_clone3`, `ret_from_fork`, `sparc_exit_group`, `sparc_exit`, `linux_sparc_syscall32`, `linux_sparc_syscall`, trace labels, and `ret_sys_call`.

Control flow: exec/fork/clone stubs flush register windows before jumping/calling C helpers. Signal return calls C restorers and then either returns directly or invokes `syscall_trace_leave()` if flags demand. Syscall dispatch validates `%g1` against `NR_syscalls`, loads function addresses from 32-bit or 64-bit tables, handles tracing/seccomp/audit/tracepoint/NOHZ entry, marshals up to six args from input registers, calls the target, stores return value into `pt_regs`, advances TPC/TNPC, and clears or sets carry bits based on errno unless `TIF_SYS_NOERROR` forces success.

State and persistence: mutates pt_regs, thread flags such as `TI_NEW_CHILD`/`TI_WSAVED`, register-window state, and syscall condition codes. Delegated syscalls perform actual persistent effects.

Dependencies and integration points: depends on `entry.h` offsets, syscall tables, tracing/seccomp hooks, signal restore code, process fork helpers, and SPARC register-window ABI.

Risks: register-window flushing and carry-bit errno convention are ABI-critical. Trace paths can modify registers and must reload args/syscall number. Compat dispatch must zero-extend 32-bit arguments correctly.

Test signals: native and compat syscall smoke tests, ptrace/seccomp/audit tracing, restart/error/success returns, `force_successful_syscall_return()`, fork/vfork/clone/clone3, kernel thread `ret_from_fork`, exec wrappers, and signal return from traced and untraced tasks.
