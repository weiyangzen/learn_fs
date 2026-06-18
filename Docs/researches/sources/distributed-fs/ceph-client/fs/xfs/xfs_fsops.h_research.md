# sources/distributed-fs/ceph-client/fs/xfs/xfs_fsops.h

## Purpose
`xfs_fsops.h` declares the filesystem-level operation API used by ioctl and mount lifecycle code.

## Important APIs, types, and functions
It declares data/log growfs, reserve-block adjustment, filesystem going-down, AG metadata reserve initialization, and AG metadata reserve teardown functions.

## Control flow
Ioctl code calls growfs, reserve, and going-down functions; mount/remount paths call reservation helpers after geometry changes or during teardown.

## State and persistence
The header owns no state. Declared functions mutate durable superblock geometry and runtime reservation/shutdown state in `xfs_fsops.c`.

## Dependencies and integration points
It depends on `struct xfs_mount`, growfs ioctl structures, and `enum xfs_free_counter`.

## Risks and test signals
Risks are API signature drift with ioctl callers and mount code. Test signals are build coverage and ioctl exercises for growfs/reserve/goingdown.
