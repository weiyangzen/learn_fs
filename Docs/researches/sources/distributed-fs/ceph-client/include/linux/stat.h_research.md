<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stat.h -->
# sources/distributed-fs/ceph-client/include/linux/stat.h

Purpose: Defines internal kernel file metadata structures and constants used by VFS stat/statx paths.

Important APIs/types/functions: Permission aggregate macros, `UTIME_NOW`, `UTIME_OMIT`, `struct kstat`, `KSTAT_ATTR_FS_IOC_FLAGS`, `KSTAT_ATTR_VFS_FLAGS`, `STATX_CHANGE_COOKIE`, and `STATX_ATTR_CHANGE_MONOTONIC`.

Control flow: No executable flow. Filesystems fill `struct kstat`; VFS/statx code converts it to user-visible stat data according to `result_mask` and requested flags.

State and persistence behavior: `struct kstat` is a transient metadata snapshot containing mode, link count, block size, attributes, inode/device IDs, ownership, size, timestamps, blocks, mount ID, change cookie, subvolume, DIO alignment, and atomic-write limits.

Dependencies: Architecture stat definitions, UAPI stat constants, kernel types, time, and uid/gid wrappers.

Integration points: VFS `getattr`, stat/statx syscalls, NFSd change-cookie handling, and filesystem-specific attribute reporting. Ceph-style distributed filesystems use this structure to return remote inode metadata through VFS.

Risks: Incorrect `result_mask`, timestamp, attribute, or alignment fields can mislead userspace. Internal statx extension bits must not collide with public ABI unexpectedly.

Test signals: stat/statx syscall tests, filesystem getattr tests, DIO alignment reporting tests, change-cookie tests, and permission macro compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stat.h -->
