# sources/distributed-fs/ceph-client/fs/jfs/jfs_superblock.h

## Purpose
`jfs_superblock.h` defines the on-disk JFS aggregate superblock layout and declares mount, unmount, superblock I/O, error, and extendfs entry points. It is the shared contract for interpreting block-size geometry, aggregate size, state, flags, log location, fsck workspace, labels, and UUIDs.

## Important APIs, types, and functions
Key constants are `JFS_MAGIC`, `JFS_VERSION`, and `LV_NAME_SIZE`. The central type is `struct jfs_superblock`, containing geometry fields (`s_size`, `s_bsize`, shifts, physical block size), allocation group size, flags/state/compression, secondary AIM/AIT extents, log device/serial/inline log extent, fsck workspace, timestamp, fsck service log fields, extendfs fields, volume UUID/label, and external log UUID. The header declares `readSuper()`, `updateSuper()`, `jfs_error()`, `jfs_mount()`, `jfs_mount_rw()`, `jfs_umount()`, `jfs_umount_rw()`, `jfs_extendfs()`, and the global JFS I/O/sync thread task pointers.

## Control flow
The header is consumed by mount code to read and validate the superblock, by unmount/remount paths to update state, by log manager code to access log descriptors, and by other filesystem code to report errors through `jfs_error()`. It does not execute control flow directly.

## State and persistence behavior
`struct jfs_superblock` is persistent disk data and all numeric fields are little-endian. `s_state` controls clean, mounted, dirty, and recovery-sensitive states. `s_flag` carries aggregate attributes such as inline log, group commit, no-integrity-adjacent behavior, DASD flags, and bad secondary AIT state from `jfs_filsys.h`. `s_logpxd`, `s_logdev`, and `s_loguuid` determine whether the journal is inline or external. Extendfs fields preserve in-progress grow state.

## Dependencies and integration points
The header depends on UUID support and on JFS extent/time types (`pxd_t`, `timestruc_t`). It is included by mount, unmount, metapage, log manager, transaction manager, and other JFS modules that need filesystem state or exported lifecycle functions. Userspace tools must agree with this layout, as noted by the compatibility comments.

## Risks
Changing field order or sizes breaks on-disk compatibility. The `s_fpack` and `LV_NAME_SIZE` OS/2 compatibility constraints are easy to overlook. Callers must always convert little-endian values before arithmetic. Log and fsck extents are trusted during mount after validation; corrupt descriptors can misdirect metadata I/O if checks are incomplete.

## Test signals
Signals include mounting filesystems with inline and external logs, validating UUID/label handling, dirty-state transitions across mount/unmount/remount, extendfs interruption/recovery, DASD flag updates on clean unmount, and compatibility with fsck/jfsutils expectations for the superblock layout.
