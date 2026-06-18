# sources/distributed-fs/ceph-client/arch/parisc/include/asm/syscall.h

Purpose: provides PA-RISC syscall inspection and mutation helpers for tracing, seccomp, audit, and ptrace.

Important APIs/types/functions: defines `NR_syscalls`, `syscall_get_nr`, `syscall_set_nr`, `syscall_get_arguments`, `syscall_set_arguments`, `syscall_get_error`, `syscall_get_return_value`, `syscall_set_return_value`, `syscall_rollback`, and `syscall_get_arch`.

Control flow: tracing/seccomp code reads syscall number and args from `pt_regs`, may rewrite them, and later reads or sets the return value/error according to PA-RISC ABI.

State and persistence: operates on saved syscall register frames. Dependencies and integration: depends on uapi audit constants, compat, errnos, and ptrace helpers.

Risks and test signals: PA-RISC argument registers differ from many architectures; mistakes break tracing and seccomp. Test strace, seccomp user notification/filtering, ptrace syscall emulation, and compat syscalls.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
