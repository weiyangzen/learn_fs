# sources/distributed-fs/ceph-client/fs/nilfs2/file.c

## Purpose
`file.c` defines regular-file VFS operations, fsync behavior, mmap fault handling, and inode operation hooks for NILFS files.

## Important APIs and functions
- `nilfs_sync_file()` is the fsync entry point. It constructs a data-sync segment for datasync or a full segment for fsync when the inode is dirty, then flushes the block device.
- `nilfs_page_mkwrite()` handles writable mmap faults, fills holes in a transaction, marks file data dirty, and waits for writeback for checksum/log consistency.
- `nilfs_file_mmap_prepare()` installs NILFS VM ops and marks file access.
- `nilfs_file_operations` wires generic read/write, ioctl, compat ioctl, mmap, open, fsync, splice, and lease operations.
- `nilfs_file_inode_operations` wires setattr, permission, fiemap, and fileattr get/set.

## Control flow
Fsync checks NILFS inode dirty state rather than blindly constructing a segment. Datasync uses the requested byte range, full fsync constructs a full segment, then `nilfs_flush_device()` forces device flush.

On `page_mkwrite`, the code rejects near-full filesystems with `SIGBUS`, locks the folio, validates mapping/size/uptodate state, short-circuits if all buffers are mapped, otherwise starts a NILFS transaction and invokes `block_page_mkwrite()` with `nilfs_get_block()` to allocate hole blocks. After dirtying the file, it commits and waits for writeback even if the device does not require stable writes, because NILFS log validity depends on checksums over data blocks.

## State and persistence behavior
Regular-file writes become dirty folios and dirty inode/file entries; persistence happens through NILFS segment construction, not ordinary block writeback. Mmap writes reserve blocks and dirty file accounting in transactions so later segment construction can assign disk addresses and record binfo.

## Dependencies and integration points
The file depends on `segment.c` for segment construction and flushing, `inode.c` for `nilfs_get_block()`, `nilfs_set_file_dirty()`, setattr/permission/fiemap, and `ioctl.c` for ioctl handlers. VM operations integrate with Linux filemap faults and page writeback.

## Risks and test signals
Mmap write faults near ENOSPC, folio invalidation races, hole-filling failures, datasync range construction, and device flush failures are important. Tests should include buffered writes, mmap writes to holes and existing blocks, fsync/datasync after dirty and clean states, and read-only remount behavior.
