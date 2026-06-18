<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/namei.c -->
# sources/distributed-fs/ceph-client/fs/erofs/namei.c

## Purpose
`namei.c` implements EROFS directory lookup. It exploits alphabetically sorted directory entries to binary-search both directory blocks and entries within a block.

## Important APIs, types, and functions
Important functions include `erofs_dirnamecmp`, `find_target_dirent`, `erofs_find_target_block`, `erofs_namei`, and VFS lookup wrapper `erofs_lookup`. It exports `erofs_dir_iops`.

## Control flow
Lookup rejects names longer than `EROFS_NAME_LEN`, then `erofs_namei` builds a query string and searches directory blocks. `erofs_find_target_block` binary-searches blocks by comparing the first name in each block, preserving matched prefix lengths to reduce comparisons and retaining the last candidate block. If needed, `find_target_dirent` binary-searches entries inside the candidate block. On success the nid and file type are returned and `erofs_lookup` instantiates the inode through `erofs_iget`; `-ENOENT` creates a negative dentry.

## State and persistence
No persistent state changes. Runtime state is metadata buffer ownership during search and dentry/inode cache results.

## Dependencies and integration points
It depends on sorted EROFS directory format, `erofs_bread`, NID-based inode loading, tracepoints, xattr/ACL-capable directory inode operations, and VFS dentry splicing.

## Risks and test signals
Risks include corrupted `nameoff` values, binary-search assumptions violated by unsorted directories, prefix-cache comparison bugs, candidate buffer lifetime mistakes, and metabox NID handling. Test signals include positive/negative lookup, first/last/middle entries, single-entry blocks, unsorted or corrupt directory blocks, long-name rejection, and lookup in metabox-backed directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/namei.c -->
