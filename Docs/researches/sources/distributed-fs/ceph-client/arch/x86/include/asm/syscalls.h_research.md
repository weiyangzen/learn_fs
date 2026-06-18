<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/syscalls.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/syscalls.h

Purpose: declares x86-specific syscall entry points not covered solely by generic syscall declarations. Important declarations include architecture syscalls such as `sys_ioperm`, `sys_iopl`, and related compat/native variants depending on config.

Control flow: syscall tables reference these symbols; wrappers or entry dispatch call them with decoded arguments. State changes are syscall-specific, commonly task I/O permission bitmap or IOPL emulation state. Dependencies include syscall table generation, processor I/O permission support, and compat ABI.

Risks include missing declarations causing table/build failures and ABI mismatch for x86-specific syscalls. Test signals include ioperm/iopl tests, syscall table link checks, compat syscall invocation, and seccomp/audit naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/syscalls.h -->
