# sources/distributed-fs/ceph-client/fs/ufs/file.c

## Purpose
`file.c` provides the regular-file `file_operations` table for UFS, delegating actual I/O and mapping behavior to generic VFS helpers and UFS address-space operations.

## Important APIs, types, and functions
The only exported object is `ufs_file_operations`. It wires `generic_file_llseek`, `generic_file_read_iter`, `generic_file_write_iter`, `generic_file_mmap_prepare`, `generic_file_open`, `simple_fsync`, `filemap_splice_read`, `iter_file_splice_write`, and `generic_setlease`.

## Control flow
There is no custom file-level control flow. VFS calls on regular files flow through generic helpers; block mapping, write_begin/write_end, truncation, and persistence semantics are handled by `inode.c` through `ufs_aops` and inode operations.

## State and persistence
The file stores no state. Reads and writes mutate pagecache and on-disk blocks through generic helpers and UFS address-space callbacks.

## Dependencies and integration points
It depends on the VFS generic file API and is selected by `ufs_set_inode_ops` for regular files. Correct behavior depends on `ufs_aops`, `ufs_setattr`, and superblock mount flags.

## Risks and test signals
Risks are mostly integration risks: generic write paths may reach experimental UFS allocation code when write support is enabled, and `simple_fsync` relies on lower layers marking buffers/inodes correctly. Test signals include buffered read/write, mmap prepare, splice read/write, fsync, file leases, and behavior on read-only mounts.
