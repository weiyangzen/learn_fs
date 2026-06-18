<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/syscall.h

Purpose: provides generic syscall inspection and mutation helpers for Xtensa. Important APIs are `syscall_get_arch`, `sys_call_table`, `syscall_get_nr`, `syscall_set_nr`, `syscall_rollback`, `syscall_get_error`, `syscall_get_return_value`, `syscall_set_return_value`, `syscall_get_arguments`, `syscall_set_arguments`, and Xtensa syscall prototypes `xtensa_rt_sigreturn`, `xtensa_shmat`, and `xtensa_fadvise64_64`.

Control flow maps syscall number and arguments to fields in `pt_regs`; Xtensa uses return register `areg[2]` and argument registers `{6,3,4,5,8,9}`. State is the syscall number and register frame saved by `entry.S`. Dependencies include `linux/err.h`, `asm/ptrace.h`, audit arch definitions, and syscall table generation. Integration points are tracing, audit, seccomp, ptrace, syscall dispatch in `entry.S`, and signal return. Risks are wrong argument register mapping, failure to distinguish error from valid high unsigned returns through `IS_ERR_VALUE`, and syscall table count drift. Test signals include strace/seccomp/audit selftests, syscall fuzzing, fadvise/shmat ABI tests, and ptrace syscall modification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/syscall.h -->
