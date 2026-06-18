# sources/distributed-fs/ceph-client/fs/xfs/xfs_verify_media.h

## Purpose
`xfs_verify_media.h` is the small declaration header for the XFS media verification ioctl implementation.

## Important APIs, types, and functions
It forward-declares `struct xfs_verify_media` and declares `xfs_ioc_verify_media(struct file *file, struct xfs_verify_media __user *arg)`.

## Control flow
The header is included by ioctl dispatch code that needs to hand a userspace `xfs_verify_media` request to the implementation in `xfs_verify_media.c`.

## State and persistence
The header has no state and performs no persistence. It preserves the userspace pointer annotation for sparse checking.

## Dependencies and integration points
It integrates the ioctl layer with the media verification implementation while avoiding broader include dependencies.

## Risks and test signals
Risks are limited to declaration drift with the implementation or UAPI structure. Test signals come from successful build coverage and ioctl tests that compile through this declaration.
