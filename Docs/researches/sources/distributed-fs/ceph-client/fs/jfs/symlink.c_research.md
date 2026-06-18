<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/symlink.c -->
# sources/distributed-fs/ceph-client/fs/jfs/symlink.c

## Purpose
`symlink.c` defines the inode operation tables used by JFS symbolic links. It separates fast symlinks stored inline in the inode from normal symlinks whose content is page-cache backed through JFS address-space operations.

## Important APIs, types, and functions
The file exports `jfs_fast_symlink_inode_operations` and `jfs_symlink_inode_operations`. Fast symlinks use `.get_link = simple_get_link`; normal symlinks use `.get_link = page_get_link`. Both support `.setattr = jfs_setattr` and `.listxattr = jfs_listxattr`.

## Control flow
There is no function body here. `namei.c` selects the fast operation table when a symlink target fits in `IDATASIZE` and stores the pointer in `inode->i_link`; otherwise it selects the page-backed operation table after allocating an xtree extent and setting JFS address-space operations.

## State and persistence behavior
Fast symlink state persists in the JFS inode inline area. Long symlink state persists as file data mapped by the inode xtree. Both forms share inode metadata, mode, xattrs, and setattr behavior.

## Dependencies and integration points
It depends on Linux symlink helpers, `jfs_setattr`, `jfs_listxattr`, and the construction decisions in `jfs_symlink`. It is a narrow VFS integration point rather than a storage implementation.

## Risks and test signals
Risks are mismatches between chosen operations and where the target was stored, xattr listing on symlink inodes, and setattr behavior on inline versus page-backed symlinks. Tests should create targets just below, at, and above the inline threshold, read links after remount, list xattrs on symlinks, and verify truncation/unlink cleanup of long symlink extents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/symlink.c -->
