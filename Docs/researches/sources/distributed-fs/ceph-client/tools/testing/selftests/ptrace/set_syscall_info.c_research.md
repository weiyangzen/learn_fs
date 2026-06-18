# sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/set_syscall_info.c

Purpose: validates `PTRACE_SET_SYSCALL_INFO` by modifying syscall numbers, arguments, and exit results at ptrace syscall stops, then checking both kernel-reported state and tracee-observed behavior.

Important APIs and functions: uses `PTRACE_GET_SYSCALL_INFO`, `PTRACE_SET_SYSCALL_INFO`, `PTRACE_SYSCALL`, `PTRACE_O_TRACESYSGOOD`, `struct ptrace_syscall_info`, and architecture-aware `kernel_ulong_t`. Helpers `check_psi_entry()` and `check_psi_exit()` assert pre/post state.

Control flow: child performs a table of syscalls with expected original entries and expected mutated entries/exits. Parent traces each entry and exit stop, verifies original info, mutates fields, verifies changed info, resumes, and finally requires tracee exit 0 after observing changed syscall behavior.

State and persistence: ptrace-modified syscall state exists only during each stop. Pipes provide valid splice fds for one mutation case.

Dependencies and integration: relies on recent ptrace ABI and architecture details, including s390 syscall number masking and MIPS N32 argument width.

Risks and test signals: exact stop count and mutation semantics are strict. Failures identify broken settable syscall ABI, return-value rewriting, argument rewriting, or info reporting after mutation.
