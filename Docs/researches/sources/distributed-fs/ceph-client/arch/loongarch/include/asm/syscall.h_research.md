<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/syscall.h

Purpose: provides LoongArch syscall introspection and mutation helpers for tracing, seccomp, audit, and ptrace.
Important APIs and types: implements `syscall_get_nr`, `syscall_rollback`, `syscall_get_error`, `syscall_get_return_value`, `syscall_set_return_value`, `syscall_get_arguments`, and syscall argument storage conventions.
Control flow: syscall entry saves arguments in `pt_regs`; tracing/seccomp code uses these helpers before and after `do_syscall` to inspect, modify, or roll back calls.
State and persistence: operates on transient `pt_regs` state, especially syscall number, argument registers, return register, and original first argument.
Dependencies and integration: aligns with `entry.S`, `ptrace.h`, `unistd.h`, audit/seccomp, ftrace/perf syscall tracing, and signal restart handling.
Risks and test signals: ABI register mistakes break tracing or syscall restarts. Signals include `strace`, ptrace syscall tests, seccomp user notification, audit, and syscall restart tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/syscall.h -->
