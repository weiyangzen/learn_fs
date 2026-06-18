# sources/distributed-fs/ceph-client/fs/nilfs2/the_nilfs.c

## Purpose
This file implements lifecycle, mount-time initialization, recovery setup, superblock selection, disk-layout validation, segment accounting helpers, discard handling, and mounted-checkpoint root management for the shared `struct the_nilfs` object.

## Important APIs, Types, And Functions
Externally used functions include `alloc_nilfs()`, `destroy_nilfs()`, `init_nilfs()`, `load_nilfs()`, `nilfs_set_last_segment()`, `nilfs_nrsvsegs()`, `nilfs_set_nsegments()`, `nilfs_discard_segments()`, `nilfs_count_free_blocks()`, `nilfs_near_disk_full()`, `nilfs_lookup_root()`, `nilfs_find_or_create_root()`, `nilfs_put_root()`, `nilfs_fall_back_super_block()`, and `nilfs_swap_super_block()`. Internal helpers validate superblocks with CRC32, load the super root and metadata files, parse block size, store disk layout, choose primary versus secondary superblock, and track recovery metadata.

## Control Flow
`alloc_nilfs()` allocates and initializes locks, lists, rb-tree roots, atomics, and defaults. `init_nilfs()` sets an initial block size, loads and validates superblocks, checks feature compatibility, adjusts the VFS block size if needed, stores layout fields, initializes the log cursor, and marks the object initialized. `load_nilfs()` searches for a super root, optionally rolls back to the spare superblock, loads DAT/CPFILE/SUFILE from the super root, creates sysfs state, and performs roll-forward recovery when the filesystem was not clean. Failure paths drop sysfs and metadata inodes in reverse order.

## State, Persistence, And Dependencies
The file mirrors persistent superblock and super-root contents into `struct the_nilfs`: block geometry, segment count, CRC seed, mount state, last partial segment, checkpoint number, and metadata inode pointers. It depends on NILFS recovery, segment, DAT, CPFILE, SUFILE, and segbuf helpers, Linux buffer-head I/O, block-device size/flush/discard APIs, rbtrees, spinlocks, rwsems, and refcounts.

## Integration Points
Mount code calls `init_nilfs()` and `load_nilfs()` before the filesystem is usable. Segment construction updates last-segment state through `nilfs_set_last_segment()`. Cleaner and allocator paths use reserved-segment and near-full helpers. Snapshot/current-root users use the rb-tree root lookup/create/put functions, which also integrate with sysfs snapshot groups.

## Risks
Superblock choice and fallback are high-risk because invalid CRCs, mismatched block sizes, or a bad secondary-superblock offset can decide whether recovery is possible. `nilfs_find_or_create_root()` inserts the new root into the rb-tree before creating its sysfs group; if sysfs creation fails, the function frees the object without erasing the rb-node, leaving a stale tree pointer. Discard batching assumes contiguous segment ranges are supplied in ascending order for optimal merging. Recovery temporarily clears read-only mount flags when it must write, so failures must always restore `sb->s_flags`.

## Test Signals
Signals include mounting images with valid, stale, corrupt, and missing primary/secondary superblocks; forced block-size changes; malformed layout fields; clean versus unclean mounts with `norecovery`; read-only block devices; injected failures in metadata-file loads and sysfs creation; discard tests with contiguous and discontiguous segment lists; and KASAN tests for checkpoint root creation failure.
