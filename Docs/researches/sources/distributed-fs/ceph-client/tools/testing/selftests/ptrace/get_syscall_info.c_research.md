# sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/get_syscall_info.c

Purpose: validates `PTRACE_GET_SYSCALL_INFO` semantics at signal stops, syscall-entry stops, and syscall-exit stops.

Important APIs and functions: raw `ptrace`, `PTRACE_TRACEME`, `PTRACE_SETOPTIONS(PTRACE_O_TRACESYSGOOD)`, `PTRACE_GET_SYSCALL_INFO`, `PTRACE_SYSCALL`, and `struct ptrace_syscall_info`. `kill_tracee()` and `LOG_KILL_TRACEE` keep failures from leaking children.

Control flow: child stops, then performs `chdir("")`, `gettid`, and `exit_group` with sentinel arguments. Parent iterates wait stops, verifies NONE info at SIGSTOP, verifies entry syscall numbers/args, verifies exit error/value for chdir and gettid, and resumes with `PTRACE_SYSCALL`.

State and persistence: only tracee process state and ptrace stop index.

Dependencies and integration: depends on architecture-independent syscalls plus architecture-specific `arch`, instruction pointer, and stack pointer reporting.

Risks and test signals: exact stop ordering is assumed. Failure points to ptrace syscall info size, op, arguments, return values, or trace option behavior regressions.
