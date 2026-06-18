# sources/distributed-fs/ceph-client/fs/nilfs2/gcinode.c

## Purpose
`gcinode.c` provides dummy inodes and page caches used by NILFS garbage collection to read valid old data and node blocks before moving them into a new log segment.

## Important APIs and functions
- `nilfs_gccache_submit_read_data()` registers a data block in a GC inode page cache and submits a read from a physical block or from a DAT-translated virtual block.
- `nilfs_gccache_submit_read_node()` registers a B-tree node block in the associated btnode cache using virtual or physical addressing.
- `nilfs_gccache_wait_and_mark_dirty()` waits for the read, validates uptodate state and B-tree node integrity, then marks the buffer dirty for movement.
- `nilfs_init_gcinode()` initializes a GC inode with buffer-cache aops, GC bmap ops, and attached btnode cache.
- `nilfs_remove_all_gcinodes()` truncates data and node caches and drops all GC inodes from the filesystem GC list.

## Control flow
Cleaner ioctl code groups `nilfs_vdesc` records by inode/checkpoint and obtains GC inodes through `nilfs_iget_for_gc()`. Data block reads use `blkoff` as the pagecache key while `b_blocknr` is set to physical block for I/O and then to virtual block when appropriate. Node reads delegate to `nilfs_btnode_submit_block()`. After all reads are submitted, buffers are waited and marked dirty; dirty GC buffers are then picked up by segment cleaning.

## State and persistence behavior
GC inodes are temporary in-memory holders. Their dirty buffers represent old blocks selected for copying into a new segment, not user-visible inode data. After the cleaning operation, `nilfs_remove_all_gcinodes()` clears all cached folios and node buffers.

## Dependencies and integration points
The file uses DAT translation, btnode submission and corruption checking, B-tree GC bmap initialization, metadata cleanup, and the `ns_gc_inodes` list in `struct the_nilfs`. It is driven by `ioctl.c` clean-segments handling and segment cleaner code outside this work item.

## Risks and invariants
GC inode dirty-list membership is used as a lifecycle marker, and cleaner operation is serialized by `THE_NILFS_GC_RUNNING`. Buffers must not already be on an association list when added to the move list. Node buffers must pass B-tree consistency checks before being dirtied. Physical block zero or invalid DAT translations surface as cleaner failures.

## Test signals
Test cleaner reads for data and node blocks, virtual and physical descriptors, invalid vblock translations, duplicate/conflicting buffers, B-tree node corruption, cleanup after failure, and concurrent GC exclusion.
