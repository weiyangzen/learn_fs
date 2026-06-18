<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/param.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/param.h

## Purpose
Defines OpenRISC userspace execution page size and imports generic parameter constants.

## Important APIs, Types, And Functions
Sets `EXEC_PAGESIZE` to `8192` and includes `asm-generic/param.h`.

## Control Flow
No control flow.

## State And Persistence
No runtime state. The value is part of userspace-visible ABI expectations.

## Dependencies And Integration Points
Used by libc, proc tooling, and generic kernel UAPI parameters.

## Risks
Changing `EXEC_PAGESIZE` may break binary loaders and userspace assumptions about OpenRISC page granularity.

## Test Signals
Headers-install checks and userspace page-size/auxiliary-vector behavior on OpenRISC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/param.h -->
