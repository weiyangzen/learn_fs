# sources/distributed-fs/ceph-client/fs/adfs/file.c

## Purpose
`file.c` supplies the VFS operation tables for regular files in the Acorn Disc Filing System driver. It is intentionally thin: the real block mapping and metadata translation live in `inode.c`, while this file exposes generic Linux file helpers through ADFS-specific operation tables.

## Important APIs, types, and functions
The exported tables are `adfs_file_operations` and `adfs_file_inode_operations`. Regular-file operations use `generic_file_llseek`, `generic_file_read_iter`, `generic_file_write_iter`, `generic_file_mmap_prepare`, `simple_fsync`, and `filemap_splice_read`. The inode table wires `.setattr` to `adfs_setattr`.

## Control flow
`adfs_iget()` assigns these tables to regular files. VFS read, write, mmap, splice, seek, fsync, and setattr requests then dispatch through generic helpers, which rely on the inode mapping operations in `inode.c` for folio I/O and block translation.

## State and persistence
This file owns no state. Persistent effects are indirect: writes and attribute updates flow into ADFS inode/private fields and directory-entry writeback.

## Dependencies and integration points
It depends on `adfs.h`, VFS file operation contracts, address-space operations installed elsewhere, and `adfs_setattr()`.

## Risks and test signals
Risks are mismatches between generic write paths and ADFS's limited allocation/truncation support. Test signals include regular file read/write smoke tests, mmap read tests, splice reads, fsync on read-only and writable builds, and setattr coverage for mode, time, and size changes.
