# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/the_nilfs.h

## Summary
Defines the central NILFS shared state object, checkpoint-root object, NILFS state flags, mount-option helpers, segment geometry helpers, and public `the_nilfs` interfaces.

## Main Contents
- `enum` flags for initialization, discontinued log chain, GC running, dirty superblock, and purging.
- `struct the_nilfs`, the per-device shared NILFS supervisor object.
- Generated inline flag helpers such as `set_nilfs_init()` and `nilfs_sb_dirty()`.
- Mount option bit helpers.
- `struct nilfs_root` for mounted checkpoint/snapshot roots.
- Superblock update constants and helpers.
- Segment geometry helpers and flush helper.

## Important Details
`struct the_nilfs` contains:
- VFS and block-device references.
- Primary and secondary superblock buffers/pointers.
- Superblock write time/count/state/update frequency.
- Current segment constructor cursor: segment sequence, current/next full segment, partial segment offset, next checkpoint, last write times, dirty block count.
- Latest super-root cursor and GC protection sequence.
- Log writer pointer and segment-constructor semaphore.
- Metadata inode pointers for DAT, cpfile, and sufile.
- Checkpoint root rb-tree and dirty inode/GC lists.
- Mount options, reserved uid/gid, checkpoint interval, watermark, disk geometry, inode size, CRC seed, and sysfs kobjects.

`nilfs_flush_device()` issues a block-device flush only when barriers are enabled and volatile data is not already marked flushed. It uses a write memory barrier around `ns_flushed_device`.

## Risks
Several fields have different locking rules: some are immutable after initialization, some are under `ns_sem`, some under `ns_segctor_sem`, and latest segment fields under `ns_last_segment_lock`. Callers need to follow those ownership boundaries to avoid stale sysfs output, incorrect segment allocation, or superblock cursor corruption.
