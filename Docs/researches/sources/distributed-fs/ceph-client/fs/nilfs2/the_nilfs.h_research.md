# sources/distributed-fs/ceph-client/fs/nilfs2/the_nilfs.h

## Purpose
This header defines the shared NILFS2 filesystem state object `struct the_nilfs`, the mounted checkpoint/snapshot root object `struct nilfs_root`, state flags, mount option helpers, public lifecycle/function prototypes, and small inline helpers for superblock update policy, segment arithmetic, and block-device flushing.

## Important APIs, Types, And Functions
`enum THE_NILFS_*` flags describe initialization, discontinued log chain, GC activity, dirty superblock, and purge state. `struct the_nilfs` holds the backing block device, superblock buffers, log cursor, latest-segment state, metadata inodes, checkpoint rb-tree, dirty/GC inode lists, mount options, block geometry, CRC seed, and sysfs kobjects. `struct nilfs_root` tracks one mounted checkpoint with refcount, rb-node, ifile, counters, and sysfs snapshot kobject. Inlines include `nilfs_sb_need_update()`, `nilfs_sb_will_flip()`, segment range conversion helpers, `nilfs_shift_to_next_segment()`, `nilfs_last_cno()`, `nilfs_segment_is_active()`, and `nilfs_flush_device()`.

## Control Flow
This header mainly defines data and inline decision logic. Flag macros generate setters, clearers, and testers. Segment helpers are called during allocation, recovery, and segment construction. `nilfs_flush_device()` gates `blkdev_issue_flush()` on the BARRIER mount option and `ns_flushed_device`, sets the flushed flag with an ordering barrier, and normalizes non-EIO errors to success.

## State, Persistence, And Dependencies
Most fields either cache persistent on-disk data or track volatile mount/session state. `ns_sem` protects shared superblock state, `ns_segctor_sem` protects log-write cursor fields, `ns_last_segment_lock` protects latest committed segment fields, and `ns_cptree_lock` protects mounted checkpoint roots. The header depends on Linux block-device, fs, rbtree, buffer-head, refcount, and backing-device definitions.

## Integration Points
Almost every NILFS2 subsystem uses this header: mount/recovery, segment constructor, cleaner, metadata files, sysfs, inode handling, and checkpoint management. `sb->s_fs_info` points at `struct the_nilfs`, making it the cross-subsystem state anchor.

## Risks
The structure mixes persistent metadata, mutable runtime cursor state, and sysfs lifetime state, so lock discipline is critical. Helpers such as `nilfs_segment_is_active()` read cursor fields without locking and are safe only in contexts that already serialize segment state. `nilfs_flush_device()` intentionally suppresses non-EIO flush errors, which matches existing semantics but can hide device behavior from callers.

## Test Signals
Compile tests across NILFS2 are essential because this header affects many users. Runtime signals include KCSAN lock checking during segment construction and sysfs reads, checkpoint mount/unmount refcount tests, flush behavior with and without BARRIER, and boundary tests for segment-zero arithmetic and maximum segment counts.
