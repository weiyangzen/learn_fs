# sources/distributed-fs/ceph-client/arch/csky/kernel/syscall.c

Purpose: syscall number, argument, return-value, and skip helpers for tracing/seccomp/audit.

Important APIs/types/functions: functions: `SYSCALL_DEFINE1`, `SYSCALL_DEFINE6`, `SYSCALL_DEFINE4`; types: `thread_info`, `pt_regs`; syscalls: `set_thread_area`, `mmap2`, `csky_fadvise64_64`

Control flow: Runtime flow is organized around `SYSCALL_DEFINE1`, `SYSCALL_DEFINE6`, `SYSCALL_DEFINE4`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is stored in task_struct, thread_info, pt_regs, signal frames, and saved thread context rather than durable storage.

Dependencies and integration: Depends on `linux/syscalls.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Register layout and restart semantics are ABI-sensitive and must stay compatible with libc, debuggers, audit, seccomp, and core dumps.

Test signals: C-SKY cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.
