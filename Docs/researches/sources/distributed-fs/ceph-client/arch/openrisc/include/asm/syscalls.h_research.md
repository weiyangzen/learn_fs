<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/syscalls.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/syscalls.h

## Purpose
Declares OpenRISC syscall wrappers that differ from generic syscall prototypes.

## Important APIs, Types, And Functions
Declares `sys_or1k_atomic()`, includes generic syscall declarations, and declares assembly wrappers `__sys_clone()`, `__sys_clone3()`, and `__sys_fork()`.

## Control Flow
`sys_call_table.c` aliases generic syscall names to these wrappers. `entry.S` wrappers save extra callee-saved registers before calling the common clone/fork implementations.

## State And Persistence
No state in the header. The wrappers preserve user register state across fork-like paths.

## Dependencies And Integration Points
Depends on OpenRISC syscall ABI, generic syscall prototypes, `clone_args`, and user pointer annotations.

## Risks
Wrapper signature drift causes stack/register corruption at syscall boundaries. `sys_or1k_atomic()` is legacy and must preserve ABI even if internally minimal.

## Test Signals
Fork/clone/clone3 syscall tests, module build checks, and atomic syscall compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/syscalls.h -->
