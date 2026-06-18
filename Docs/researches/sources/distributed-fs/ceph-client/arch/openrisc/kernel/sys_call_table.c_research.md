<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/sys_call_table.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/sys_call_table.c

## Purpose
Defines the OpenRISC syscall dispatch table.

## Important APIs, Types, And Functions
Defines `__SYSCALL` macros, aliases `sys_mmap2`, `sys_clone`, `sys_clone3`, and `sys_fork`, and creates `void *sys_call_table[__NR_syscalls]` from generated `asm/syscall_table_32.h`.

## Control Flow
`entry.S` indexes this table after validating the syscall number and jumps to the selected function.

## State And Persistence
Static table persists for kernel lifetime.

## Dependencies And Integration Points
Depends on generated syscall headers, OpenRISC wrappers in `entry.S`, and generic syscall declarations.

## Risks
Wrong aliases break fork/clone register preservation. Table type is `void *`, so function prototype checking is limited.

## Test Signals
Syscall number coverage, fork/clone/mmap tests, unknown syscall returning `-ENOSYS`, and generated table size matching `__NR_syscalls`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/sys_call_table.c -->
