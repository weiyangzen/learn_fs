<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/unistd.h

## Purpose
Exports the generated OpenRISC 32-bit syscall numbers to userspace.

## Important APIs, Types, And Functions
Includes `asm/unistd_32.h`.

## Control Flow
No control flow. Generated syscall constants are consumed by libc, assembly stubs, seccomp filters, and kernel syscall table generation.

## State And Persistence
No runtime state; syscall numbers are stable ABI.

## Dependencies And Integration Points
Generated through UAPI Kbuild. Kernel side includes this via `asm/unistd.h` and builds `sys_call_table`.

## Risks
Generation or include failure breaks all userspace syscall constants. Renumbering is not ABI-compatible.

## Test Signals
Headers install, libc build, syscall table size checks, and userspace syscall smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/unistd.h -->
