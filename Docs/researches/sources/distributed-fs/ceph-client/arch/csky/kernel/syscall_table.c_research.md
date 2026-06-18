# sources/distributed-fs/ceph-client/arch/csky/kernel/syscall_table.c

Purpose: C-SKY syscall dispatch table generated from syscall metadata.

Important APIs/types/functions: macros: `__SYSCALL(nr,`, `__SYSCALL_WITH_COMPAT(nr,`, `sys_fadvise64_64`, `sys_sync_file_range`

Control flow: Runtime flow is small and callback-oriented, with the generic architecture or subsystem code invoking this file where needed.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/syscalls.h`, `asm/syscalls.h`, `asm/syscall_table_32.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.
