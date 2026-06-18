<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/syscall.h

Purpose: supplies x86 syscall inspection and mutation helpers for generic syscall tracing, seccomp, audit, ptrace, and restart logic. Important APIs include `syscall_get_nr()`, `syscall_rollback()`, `syscall_get_error()`, `syscall_get_return_value()`, `syscall_set_return_value()`, `syscall_get_arguments()`, `syscall_get_arch()`, and syscall-user-dispatch hooks.

Control flow: tracing/seccomp/audit code reads syscall number and argument registers from `pt_regs`; ptrace and restart paths can roll back or replace return values; ABI detection distinguishes x86-64, i386 compat, and x32-style syscall state.

State and persistence: operates on transient syscall `pt_regs` and thread status flags. Dependencies include register ABI, `thread_info` compat status, audit arch constants, seccomp, ptrace, and syscall table conventions. Risks include wrong register mapping, compat ABI confusion, and bad rollback corrupting restarted syscalls. Test signals include strace/ptrace, seccomp, audit, syscall restart, x32/ia32 emulation, and syscall user dispatch tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/syscall.h -->
