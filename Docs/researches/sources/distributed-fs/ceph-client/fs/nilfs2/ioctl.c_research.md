# sources/distributed-fs/ceph-client/fs/nilfs2/ioctl.c

## Purpose
`ioctl.c` implements NILFS user-kernel control operations: checkpoint and snapshot management, metadata queries for tools and cleanerd, cleaner segment movement, sync, resize, FITRIM, allocation range control, filesystem label get/set, and file attribute get/set.

## Important APIs and functions
- `nilfs_ioctl_wrap_copy()` is the common paged userspace copy wrapper for vector-style metadata get/set operations using `struct nilfs_argv`.
- File attributes: `nilfs_fileattr_get()` and `nilfs_fileattr_set()`.
- Checkpoint operations: `nilfs_ioctl_change_cpmode()`, `nilfs_ioctl_delete_checkpoint()`, `nilfs_ioctl_do_get_cpinfo()`, and `nilfs_ioctl_get_cpstat()`.
- Segment/DAT metadata queries: `nilfs_ioctl_do_get_suinfo()`, `nilfs_ioctl_get_sustat()`, `nilfs_ioctl_do_get_vinfo()`, `nilfs_ioctl_do_get_bdescs()`, and `nilfs_ioctl_get_bdescs()`.
- Cleaner preparation: `nilfs_ioctl_move_inode_block()`, `nilfs_ioctl_move_blocks()`, `nilfs_ioctl_delete_checkpoints()`, `nilfs_ioctl_free_vblocknrs()`, `nilfs_ioctl_mark_blocks_dirty()`, `nilfs_ioctl_prepare_clean_segments()`, and `nilfs_ioctl_clean_segments()`.
- Maintenance commands: `nilfs_ioctl_sync()`, `nilfs_ioctl_resize()`, `nilfs_ioctl_trim_fs()`, `nilfs_ioctl_set_alloc_range()`, `nilfs_ioctl_set_suinfo()`, `nilfs_ioctl_get_fslabel()`, `nilfs_ioctl_set_fslabel()`.
- Dispatchers: `nilfs_ioctl()` and `nilfs_compat_ioctl()`.

## Control flow
Most metadata query ioctls copy a `nilfs_argv`, validate item size/count, use `nilfs_ioctl_wrap_copy()` to process at most one page of entries at a time, and copy the updated count back to userspace. Query callbacks hold `ns_segctor_sem` around cpfile, sufile, DAT, or bmap reads.

Mutating checkpoint and sufile ioctls require `CAP_SYS_ADMIN`, obtain write access with `mnt_want_write_file()`, run the metadata operation in a NILFS transaction, and commit or abort based on the result. Snapshot mode changes additionally use `ns_snapshot_mount_mutex`.

Clean-segments is the highest-complexity path. It copies five user vectors, bounds vector sizes by segment count and blocks per segment, serializes GC with `THE_NILFS_GC_RUNNING`, reads source blocks into GC inode caches, optionally marks the superblock discontinued, and calls `nilfs_clean_segments()`. Preparation deletes checkpoints, frees DAT virtual block numbers, and marks live metadata blocks dirty in safe stages. Cleanup removes all GC inodes and clears the running flag.

Sync constructs a segment, flushes the device, and optionally returns the last checkpoint number. Resize and label changes perform capability/write checks and call lower-level helpers. FITRIM verifies discard support, adjusts minlen to device granularity, and delegates to sufile trimming under segment-constructor read lock.

## State and persistence behavior
Ioctls are the bridge between user tools (`lscp`, `rmcp`, `chcp`, `mkcp`, `lssu`, `nilfs_cleanerd`, resize utilities) and persistent cpfile, sufile, DAT, bmap, superblock, and segment state. Mutations dirty metadata and rely on NILFS transactions and segment construction for persistence. The cleaner path creates temporary GC dirty buffers that are later written as moved blocks.

## Dependencies and integration points
The file depends on `cpfile.c`, `sufile` APIs, `dat.c`, bmap lookup/marking, `gcinode.c`, segment construction/cleaning, mount write accounting, capability checks, and Linux compat ioctl handling. It is referenced by regular file and directory operation tables.

## Risks and invariants
Userspace sizes and counts must be tightly validated to avoid overflow and excessive allocation. Cleaner vectors must not exceed `nsegs * blocks_per_segment`. GC must remain serialized and clean up all temporary buffers on failure. Mutating operations must drop mount write references on all paths. `nilfs_ioctl_wrap_copy()` must make forward progress even when callbacks do not update position. Label writes must update both superblock copies when present.

## Test signals
Test every ioctl with valid and invalid sizes/counts, faulting user pointers, permission failures, read-only mount behavior, checkpoint/snapshot lifecycle, cleaner conflict and failure unwinding, DAT/bdesc queries, FITRIM unsupported devices, resize bounds, alloc range edge cases, fslabel length validation, and compat ioctl dispatch.
