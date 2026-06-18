<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/syscall.h

## Purpose
`syscall.h` defines the UML syscall table function type and audit architecture selection.

## Important APIs, types, and functions
Important interfaces are `sys_call_ptr_t`, external `sys_call_table[]`, and `syscall_get_arch()` returning `AUDIT_ARCH_I386` or `AUDIT_ARCH_X86_64`.

## Control flow
Generic syscall code indexes `sys_call_table` and audit code calls `syscall_get_arch()` for records.

## State and persistence behavior
State is the external syscall table generated in `sys_call_table_*.c`.

## Dependencies and integration points
It depends on generic syscall helpers and UAPI audit constants.

## Risks and edge cases
The function pointer signature must match syscall table wrappers; wrong audit arch breaks audit/seccomp classification.

## Test signals
Signals are syscall execution, audit/seccomp tests, and table-size sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/syscall.h -->
