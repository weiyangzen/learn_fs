# sources/distributed-fs/ceph-client/fs/nilfs2/cpfile.c

## Purpose
`cpfile.c` implements the NILFS checkpoint metadata file. It stores checkpoint entries, tracks valid checkpoint counts, maintains the snapshot list, imports ifile roots from checkpoints, finalizes new checkpoints during segment construction, and serves checkpoint/snapshot information to ioctls and mount paths.

## Important APIs and functions
- Address helpers convert checkpoint numbers to metadata file block offsets and entry offsets: `nilfs_cpfile_get_blkoff()`, `nilfs_cpfile_get_offset()`, `nilfs_cpfile_checkpoint_offset()`, and snapshot-list offset helpers.
- Block helpers get the header, get/create checkpoint blocks with initialization, find existing checkpoint blocks in a range, and delete empty checkpoint blocks.
- `nilfs_cpfile_read_checkpoint()` validates a checkpoint, reads its embedded ifile inode, and initializes `struct nilfs_root` counters and ifile pointer.
- `nilfs_cpfile_create_checkpoint()` creates or reuses a checkpoint entry, updates per-block valid counts and header `ch_ncheckpoints`, and dirties metadata.
- `nilfs_cpfile_finalize_checkpoint()` writes final checkpoint contents: root counts, block increment, creation time, minor flag, checkpoint number, ifile inode, and ifile bmap.
- `nilfs_cpfile_delete_checkpoints()` invalidates non-snapshot checkpoints in a range, updates block/header counts, deletes now-empty checkpoint blocks, and returns `-EBUSY` if snapshots were encountered.
- Query and mode APIs include `nilfs_cpfile_get_cpinfo()`, `nilfs_cpfile_delete_checkpoint()`, `nilfs_cpfile_is_snapshot()`, `nilfs_cpfile_change_cpmode()`, and `nilfs_cpfile_get_stat()`.
- `nilfs_cpfile_read()` creates and initializes the cpfile inode at mount/load time.

## Control flow
Checkpoint reads and queries use `mi_sem` read locking; mutations take it for write. Entry blocks are addressed by checkpoint number after accounting for the header's first-entry offset. Creation gets the header and target entry block, clears invalid state on first creation, increments the block-level count except for the header-containing first block, increments the global count, and marks both block and cpfile dirty.

Deletion scans checkpoint blocks over `[start, end)`, skips holes, invalidates plain checkpoints, counts snapshots without deleting them, decrements per-block counts, and removes an entry block when no valid checkpoints remain outside the first block. Header counts are adjusted once after the scan.

Snapshot conversion updates a doubly-linked list sorted by checkpoint number using `ch_snapshot_list` as sentinel. `nilfs_cpfile_set_snapshot()` walks backward from the list tail to locate insertion points, patches previous/current/list entries, sets the snapshot flag, increments `ch_nsnapshots`, and dirties all involved buffers. Clearing a snapshot performs the inverse splice and zeroes the checkpoint's snapshot links.

## State and persistence behavior
Persistent state includes `struct nilfs_cpfile_header` counters and snapshot sentinel, `struct nilfs_checkpoint` entries with validity/minor/snapshot flags, embedded ifile inode data, root object counters, and per-block `cp_checkpoints_count` stored in the first checkpoint-sized region of each block. All changes dirty buffers and the metadata inode so segment construction persists them in the NILFS log.

## Dependencies and integration points
The file uses `mdt.c` for metadata block I/O, `nilfs_read_inode_common()` and `nilfs_write_inode_common()` from inode handling, `nilfs_bmap_write()` for embedded ifile bmap persistence, and ioctl paths for user-visible checkpoint operations. Mount and snapshot roots use `nilfs_cpfile_read_checkpoint()` through `ifile.c`.

## Risks and invariants
Checkpoint number zero is invalid. Current or future checkpoint numbers are rejected by some query paths. Snapshot entries cannot be deleted as plain checkpoints, and mounted snapshots cannot be demoted. Header counts must match entry invalidation and snapshot list updates. Missing header blocks and invalid checkpoint entries are treated as metadata corruption. The snapshot splice code is sensitive to cross-block list entries and buffer reference cleanup.

## Test signals
Useful tests include creating/finalizing checkpoints, deleting ranges with holes and snapshots, converting checkpoints to snapshots and back, querying checkpoint and snapshot lists across block boundaries, reading checkpoint roots, handling corrupted invalid entries, and verifying header counts after partial failures.
