# sources/distributed-fs/ceph-client/fs/fat/misc.c

## Purpose
`misc.c` provides common FAT utility behavior: filesystem error handling, printk wrappers, FAT32 FSINFO cluster counter flushing, appending allocated cluster chains to inodes, FAT timestamp conversion/truncation, inode timestamp update policy, and synchronous buffer-head write helpers.

## Important APIs, Types, and Functions
- `__fat_fs_error()` implements the `errors=` mount policy: continue, panic, or remount read-only.
- `_fat_msg()` is the underlying FAT message printer used by indexed `fat_msg()` macros.
- `fat_clusters_flush()` writes `free_clusters` and `prev_free` to FAT32 FSINFO.
- `fat_chain_add()` appends a newly allocated cluster chain to an inode and updates `i_start`, `i_logstart`, and `i_blocks`.
- `fat_time_fat2unix()` and `fat_time_unix2fat()` convert between FAT date/time fields and `timespec64`.
- `fat_truncate_atime()`, `fat_truncate_time()`, and `fat_update_time()` enforce FAT timestamp granularity.
- `fat_sync_bhs()` writes and waits for an array of buffer heads.

## Control Flow
Error reporting prints conditionally based on ratelimit/report flags, then either panics or flips `SB_RDONLY` for remount-read-only policy. `fat_clusters_flush()` reads the FSINFO sector, validates signatures, updates counters if known, and marks the buffer dirty.

`fat_chain_add()` locates the current EOF cluster if the inode already has a chain, writes the previous EOF entry to point at the new chain, or initializes an empty inode start cluster. It verifies `i_blocks` matches the computed append position, invalidates the cluster cache on mismatch, and then increments block count.

## State and Persistence
This file mutates superblock read-only state on serious errors, FAT32 FSINFO sectors, inode chain starts, `i_blocks`, inode timestamps, and dirty flags. It does not allocate clusters itself; it connects already allocated chains to inodes and relies on `fatent.c` for FAT entry writes.

## Dependencies and Integration Points
It depends on `fat.h`, VFS inode dirtying, buffer-head IO, ratelimit state, timezone globals, and metadata sync helpers. It is used by mount/unmount, file creation, directory growth, write paths, setattr, fsync, and KUnit tests.

## Risks and Test Signals
Time conversion is fragile because FAT stores local time, has a 1980-2107 date range, two-second mtime resolution, 24-hour atime resolution, and VFAT centiseconds. `fat_chain_add()` must avoid exposing a cluster chain without corresponding inode metadata under synchronous directory semantics. `fat_test.c` directly covers timestamp conversion/truncation; integration tests should verify `errors=`, FSINFO updates, directory creation with sync options, and timestamp persistence.
