# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/linkage.h

This header defines Alpha linkage helpers. `cond_syscall(x)` emits a weak symbol alias to `sys_ni_syscall`; `SYSCALL_ALIAS(alias, name)` emits an assembler alias and global symbol.

There is no runtime state in the header, but it directly affects syscall symbol resolution and assembly linkage. Integration is syscall table generation and weak optional syscalls. Risks are assembler syntax drift and aliases not matching generated syscall names. Test signals are syscall table/header generation and no unresolved syscall symbols.
