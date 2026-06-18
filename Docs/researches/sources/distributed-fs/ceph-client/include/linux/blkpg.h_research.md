# sources/distributed-fs/ceph-client/include/linux/blkpg.h

## Purpose
`blkpg.h` exposes block partition table and disk geometry ioctl definitions to kernel code, while adding compatibility structure support for 32-bit userspace on 64-bit kernels.

## Important APIs, Types, And Functions
The header includes `linux/compat.h` and `uapi/linux/blkpg.h`. Under `CONFIG_COMPAT`, it defines `struct blkpg_compat_ioctl_arg` with compat-sized `op`, `flags`, `datalen`, and user pointer `data` fields. The UAPI include supplies the normal `blkpg_ioctl_arg` and operation/data structures.

## Control Flow And State
There are no functions or mutable state. The only behavior is compile-time: compat builds get a layout matching 32-bit userspace pointer and integer sizes; non-compat builds only use the UAPI definitions.

## Dependencies And Integration Points
This header integrates with block ioctl handling in disk/partition management paths, especially add/delete partition operations. It depends on the compat layer to translate userspace pointers safely.

## Risks And Test Signals
Risks include ABI layout drift between native and compat structs, missing compat handling for partition ioctls, and unsafe use of compat user pointers. Test signals include native and 32-bit compat ioctl tests for partition add/delete, structure size checks, and invalid pointer/datalen handling.
