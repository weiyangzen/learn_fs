# sources/distributed-fs/ceph-client/fs/minix/file.c

## Purpose

`sources/distributed-fs/ceph-client/fs/minix/file.c` defines regular-file operations and inode operations for Minix files. It wires generic VFS read/write/mmap/splice behavior to Minix fsync and handles attribute changes, including truncation. The source was read as a complete 61-line file for this report.

## Important APIs, Types, and Functions

Important functions and objects are `minix_fsync`, `minix_file_operations`, local `minix_setattr`, and `minix_file_inode_operations`. File operations use `generic_file_llseek`, `generic_file_read_iter`, `generic_file_write_iter`, `generic_file_mmap_prepare`, `filemap_splice_read`, and Minix-specific `minix_fsync`. Inode operations expose `.setattr` and `minix_getattr`.

## Control Flow

`minix_fsync` delegates to `mmb_fsync` with the Minix inode metadata buffer-head list. Regular file reads/writes and mmap setup use generic VFS helpers. `minix_setattr` validates requested attributes with `setattr_prepare`, checks and applies size changes through `inode_newsize_ok`, `truncate_setsize`, and `minix_truncate`, then copies attributes and marks the inode dirty.

## State and Persistence Behavior

Persistent state includes file data blocks, inode size, inode metadata, and Minix metadata buffer heads. `fsync` flushes file data and metadata buffers. Attribute changes update in-memory inode state and mark it dirty for writeback; truncation updates block mappings through Minix truncate code.

## Dependencies and Integration Points

It depends on `minix.h`, buffer-head metadata tracking, generic VFS file operations, attribute helpers, and Minix inode/truncate/getattr support. It is linked into the Minix module by the Makefile and referenced by inode setup code.

## Risks and Edge Cases

Truncation must validate new size before changing `i_size`, then free blocks consistently through `minix_truncate`. The code uses `nop_mnt_idmap`, so idmapped mount semantics are not applied here. Fsync correctness depends on `i_metadata_bhs` tracking all metadata buffers that need flushing.

## Test Signals

Test reads, writes, mmap setup, splice reads, fsync after data and metadata updates, truncate grow/shrink, setattr permission failures, timestamp/size changes, crash/fsck after fsync, and Minix regular-file operations on v1/v2/v3 images.
