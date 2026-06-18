<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/file.c -->
# sources/distributed-fs/ceph-client/fs/efs/file.c

## Purpose
`file.c` defines regular-file operations for the read-only EFS filesystem.

## Important APIs, types, and functions
The file provides `generic_ro_fops` use through inode setup rather than a custom table here, and historically isolates regular file behavior. In this tree it is small because the actual address-space operations live in `inode.c`.

## Control flow
Regular-file reads flow through VFS generic read operations and the EFS address-space operations assigned by `efs_iget`, specifically `block_read_full_folio` with `efs_get_block`. There is no write path because EFS is forced read-only.

## State and persistence
No state is changed. Runtime file state is ordinary VFS read position/cache state; persistent disk contents are never modified.

## Dependencies and integration points
It integrates with `inode.c`, where regular inodes get `generic_ro_fops` and EFS mapping operations.

## Risks and test signals
Risks are mostly integration drift: if VFS regular-file behavior changes, the minimal EFS file layer relies on generic read-only semantics. Test signals include normal reads, mmap/readpage behavior, attempts to open for write, and splice/read paths through generic helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/file.c -->
