# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/ioctl.c

## Purpose

Implements NILFS2 ioctl and file-attribute user ABI, including checkpoint management, segment usage queries, cleaner/GC control, filesystem sync, resize, trim, allocation range control, and volume label get/set.

## Main Responsibilities

- Provides `nilfs_ioctl()` dispatch for NILFS-specific ioctls and standard filesystem ioctls such as `FS_IOC_GETVERSION`, `FITRIM`, `FS_IOC_GETFSLABEL`, and `FS_IOC_SETFSLABEL`.
- Implements `nilfs_ioctl_wrap_copy()` as a paged copy wrapper for vector-style metadata operations using `struct nilfs_argv`.
- Gets and sets user-visible inode flags through `nilfs_fileattr_get()` and `nilfs_fileattr_set()`.
- Changes checkpoint modes and deletes checkpoints under `CAP_SYS_ADMIN` and mount write access.
- Returns checkpoint, segment usage, virtual block, and block descriptor information to userspace.
- Drives the NILFS cleaner operation through `NILFS_IOCTL_CLEAN_SEGMENTS`.
- Moves live blocks into GC inode caches, deletes obsolete checkpoints, frees virtual block numbers, marks copied blocks dirty, and invokes segment cleaning.
- Provides sync ioctl that constructs a checkpoint segment, flushes the block device, and optionally returns the checkpoint number.
- Implements resize, FITRIM, allocation range restriction, and superblock label update.

## Important Functions

- `nilfs_ioctl_wrap_copy()` validates vector size/counts, prevents index overflow, chunks work through a page-sized kernel buffer, and copies results back.
- `nilfs_ioctl_get_info()` is the shared wrapper for cpinfo, suinfo, and vinfo queries.
- `nilfs_ioctl_move_inode_block()` submits GC-cache reads for data or node blocks and tracks buffers on an association list.
- `nilfs_ioctl_move_blocks()` groups `nilfs_vdesc` entries by inode/checkpoint, creates GC inodes, reads target blocks, and marks them dirty after read completion.
- `nilfs_ioctl_prepare_clean_segments()` performs the destructive metadata preparation sequence used by segment cleaning.
- `nilfs_ioctl_clean_segments()` copies five userspace vectors, validates element sizes and counts, serializes GC with `THE_NILFS_GC_RUNNING`, moves blocks, runs cleaning, and frees GC inodes.
- `nilfs_ioctl_set_suinfo()` applies segment usage updates inside a NILFS transaction.
- `nilfs_ioctl_set_fslabel()` validates label length, updates both superblocks when present, and commits them.

## Dependencies and Interactions

- Depends on `cpfile`, `sufile`, `dat`, and `bmap` metadata APIs.
- Uses `nilfs_iget_for_gc()` and GC cache functions declared in `nilfs.h`.
- Uses `nilfs_clean_segments()`, `nilfs_construct_segment()`, and log-writer state from segment code.
- Serializes metadata readers with `ns_segctor_sem` and snapshot mode changes with `ns_snapshot_mount_mutex`.
- Uses `mnt_want_write_file()` / `mnt_drop_write_file()` for write ioctls.
- `CONFIG_COMPAT` path maps 32-bit `FS_IOC32_GETVERSION` and forwards supported ioctl commands through `compat_ptr()`.

## Notable Behaviors and Edge Cases

- Most metadata-mutating ioctls require `CAP_SYS_ADMIN`; read-only query ioctls generally do not.
- `nilfs_ioctl_wrap_copy()` rejects item sizes larger than `PAGE_SIZE` and rejects index/count overflow.
- Cleaner inputs are bounded by `nsegs * ns_blocks_per_segment` and integer multiplication overflow checks.
- GC is single-run serialized with `THE_NILFS_GC_RUNNING`; concurrent cleaner calls return `-EBUSY`.
- Block descriptor dirty marking skips dead blocks by comparing current bmap lookup with original block numbers.
- FITRIM returns `-EOPNOTSUPP` when the block device has no discard capability.
- `FS_IOC_SETFSLABEL` copies exactly `NILFS_MAX_VOLUME_NAME + 1`, rejects non-terminated overlong labels, and commits both superblock copies.
