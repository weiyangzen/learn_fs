# sources/distributed-fs/ceph-client/fs/jfs/jfs_mount.c

## Purpose
`jfs_mount.c` implements JFS aggregate/fileset mount setup, read-write mount completion, superblock validation, synchronous superblock state updates, primary/secondary superblock reads, and the mount log record. It turns the on-disk aggregate into the in-memory special inodes and maps needed for normal filesystem operation.

## Important APIs, types, and functions
Public functions are `jfs_mount()`, `jfs_mount_rw()`, `updateSuper()`, and `readSuper()`. Private helpers are `chkSuper()` and `logMOUNT()`. Important integrations are `diReadSpecial()`, `diMount()`, `diUnmount()`, `diFreeSpecial()`, `dbMount()`, `dbUnmount()`, `lmLogOpen()`, `lmLogClose()`, and `lmLog()`.

## Control flow
`jfs_mount()` first calls `chkSuper()` to read and validate the aggregate superblock. It then reads and mounts the aggregate inode allocation map (`AGGREGATE_I`), the block allocation map (`BMAP_I`), optionally the secondary aggregate inode allocation map unless `JFS_BAD_SAIT` is set, and finally the fileset inode allocation map (`FILESYSTEM_I`). On each failure it unwinds already-mounted maps and special inodes in reverse order.

`jfs_mount_rw()` handles completing a read-write mount or remounting from read-only. On remount it revalidates a clean superblock, truncates cached inode/block map pages because fsck may have updated them, remounts the inode and block maps, opens the log with `lmLogOpen()`, marks the superblock mounted/dirty through `updateSuper(sb, FM_MOUNT)`, and writes a `LOG_MOUNT` record via `logMOUNT()`.

## State and persistence behavior
`chkSuper()` validates `JFS_MAGIC`, superblock version, 4 KiB block size, clean state for read-write mounts, secondary AIM/AIT descriptors, block-size logarithms, padding, and state range. It populates `jfs_sb_info` fields including mount flags, state, block-size shifts, UUID, inline/external log descriptors, fsck workspace, and secondary AIT descriptor. `updateSuper()` writes `s_state` synchronously, records external log device and serial on `FM_MOUNT`, and marks DASD usage stale on `FM_CLEAN` for OS/2 compatibility. With `JFS_NOINTEGRITY`, it maps requested states through `sbi->p_state` so no-integrity mounts do not advertise normal clean journaling semantics incorrectly.

## Dependencies and integration points
The file depends on Linux superblock/buffer-head/block-device APIs and JFS incore, filesystem, superblock, dmap, imap, metapage, and debug headers. It is invoked by the VFS JFS mount path and prepares state consumed by inode lookup, allocation maps, transaction manager, log manager, and unmount. The `LOG_MOUNT` record is aggregate-level so replay can stop processing older records for this filesystem.

## Risks
Mount correctness depends on exact cleanup ordering; leaking or double-freeing special inodes would corrupt later mount/unmount. Dirty superblocks are rejected for read-write mounts, so recovery must have completed before `jfs_mount_rw()`. The secondary AIM/AIT validation mutates `j_sb->s_flag` in memory before `brelse()` but does not by itself persist that fix. Remount assumes `chkSuper()` and `FM_CLEAN` are enough before truncating and remounting map pages. `updateSuper()` performs synchronous buffer writes but does not check `sync_dirty_buffer()` failure directly.

## Test signals
Tests should cover clean read-only and read-write mounts, dirty read-write rejection, remount read-only to read-write after fsck changes, primary superblock fallback to secondary, bad magic/version/block-size/padding/state failures, invalid secondary AIM/AIT descriptors, inline and external log setup, no-integrity mount state transitions, and mount/unwind failures injected at each special inode or map mount step.
