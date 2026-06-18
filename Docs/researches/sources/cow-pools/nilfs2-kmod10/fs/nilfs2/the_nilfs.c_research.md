# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/the_nilfs.c

## Summary
Implements lifecycle, loading, recovery orchestration, disk layout validation, superblock selection, segment geometry, discard, free-space accounting, and checkpoint-root management for the shared `struct the_nilfs`.

## Main Responsibilities
- Allocates and initializes `struct the_nilfs`.
- Releases superblock buffers and NILFS state.
- Loads DAT, cpfile, and sufile from the latest super root.
- Searches for the latest valid super root and runs roll-forward recovery when required.
- Selects between primary and secondary superblocks using CRC validity and checkpoint recency.
- Validates on-disk layout fields from the superblock.
- Tracks latest segment cursor and superblock dirty state.
- Provides segment count, reserved segment, block range, free-space, and near-full helpers.
- Maintains the rb-tree of mounted checkpoint roots.

## Key APIs
- `nilfs_set_last_segment()`.
- `alloc_nilfs()`, `destroy_nilfs()`.
- `load_nilfs()`.
- `nilfs_nrsvsegs()`, `nilfs_set_nsegments()`.
- `init_nilfs()`.
- `nilfs_discard_segments()`.
- `nilfs_count_free_blocks()`, `nilfs_near_disk_full()`.
- `nilfs_lookup_root()`, `nilfs_find_or_create_root()`, `nilfs_put_root()`.
- `nilfs_fall_back_super_block()`, `nilfs_swap_super_block()`.

## Important Behavior
`init_nilfs()` reads superblocks at the primary and computed secondary locations, chooses the valid/newest copy, checks feature compatibility, possibly changes VFS blocksize, validates disk layout, stores mount state, and initializes the log cursor.

`load_nilfs()` searches for the latest super root from the stored cursor. If the search fails with `-EINVAL`, it can fall back to the spare superblock, reinitialize cursor state, drop the clean flag, and retry. When the filesystem is not clean, it either skips recovery for read-only `norecovery`, temporarily enables writes for recovery, or rejects recovery if the device is physically read-only or unsupported read-only-compatible features are present.

Recovery loads the super-root metadata files, creates sysfs device state, salvages orphan logs, marks the filesystem clean, and commits the superblock. On failure it unwinds sysfs and metadata inodes.

Superblock validation checks magic, byte size, and CRC while treating the checksum field as zero. Secondary superblock validation rejects positions that would lie inside the segment area.

Checkpoint roots are cached in `ns_cptree` by checkpoint number. Creation initializes refcounts and counters, links the rb-tree node, and creates a sysfs snapshot group.

## State and Synchronization
`ns_last_segment_lock` protects latest super-root cursor fields. `ns_sem` protects mount-state checks and superblock fields. `ns_cptree_lock` protects checkpoint-root lookup, insertion, erasure, and refcount final decrement.

## Risks
Superblock selection and recovery fallback are correctness-critical. The code must keep VFS `sb->s_flags` restored after temporary recovery writes. Checkpoint-root creation has a subtle ordering issue: after rb-tree insertion, sysfs creation failure frees the new root without erasing it from the tree in this file’s current flow.
