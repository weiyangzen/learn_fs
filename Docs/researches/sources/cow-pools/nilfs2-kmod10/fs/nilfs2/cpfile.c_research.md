# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/cpfile.c

Implements the NILFS checkpoint metadata file. It creates, finalizes, reads, deletes, enumerates, and changes mode for checkpoints and snapshots.

Key behavior:
- Maps checkpoint numbers to metadata file blocks and offsets, accounting for the checkpoint file header.
- Initializes checkpoint blocks by marking entries invalid.
- Reads a checkpoint into a `nilfs_root`, including restoring the ifile inode and root inode/block counters.
- Creates checkpoint entries idempotently and updates checkpoint counts in the header.
- Finalizes checkpoint contents with root counters, block increment count, creation time, minor flag, cno, and serialized ifile bmap.
- Deletes checkpoint ranges while preserving snapshots and removing empty checkpoint blocks.
- Enumerates plain checkpoints or snapshots into `nilfs_cpinfo` arrays.
- Maintains a doubly linked snapshot list rooted in the cpfile header.
- Changes checkpoint mode between plain checkpoint and snapshot, refusing to clear mounted snapshots.
- Reports checkpoint statistics and initializes the cpfile inode from the on-disk raw inode.

Concurrency: operations take `NILFS_MDT(cpfile)->mi_sem` in read or write mode. Buffer heads are kmap’d at precise entry/list offsets and marked dirty after mutation.

Risk/notes: snapshot list manipulation spans multiple checkpoint blocks and the header, so partial failure handling is important. Deleting a range returns `-EBUSY` if snapshots are encountered. Invalid or missing checkpoint blocks are treated as metadata corruption in critical paths.
