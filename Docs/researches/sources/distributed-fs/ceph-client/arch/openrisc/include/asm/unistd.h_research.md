<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/unistd.h

## Purpose
Selects syscall families wanted by the OpenRISC kernel side and includes the UAPI syscall number header.

## Important APIs, Types, And Functions
Defines `__ARCH_WANT_STAT64`, `__ARCH_WANT_SYS_FORK`, `__ARCH_WANT_SYS_CLONE`, and `__ARCH_WANT_TIME32_SYSCALLS`, then includes `uapi/asm/unistd.h`.

## Control Flow
No control flow. The defines influence generated syscall tables and generic syscall declarations.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Integrated with syscall table generation, `sys_call_table.c`, `entry.S`, and generic unistd generation.

## Risks
Changing these wants alters userspace ABI availability. Time32 and legacy fork/clone choices must remain compatible with OpenRISC userlands.

## Test Signals
Generated `unistd_32.h` consistency, syscall table build, and userspace ABI tests for legacy syscalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/unistd.h -->
