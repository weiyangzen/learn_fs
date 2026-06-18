# sources/distributed-fs/ceph-client/fs/xfs/xfs_symlink.h

## Purpose

`sources/distributed-fs/ceph-client/fs/xfs/xfs_symlink.h` declares the kernel-internal XFS symlink API. It is the small contract used by inode operation code and inactive inode cleanup to create, read, and free symlinks. The source was read as a complete 16-line file for this report.

## Important APIs, Types, and Functions

The header declares `xfs_symlink(struct mnt_idmap *idmap, struct xfs_inode *dp, struct xfs_name *link_name, const char *target_path, umode_t mode, struct xfs_inode **ipp)`, `xfs_readlink(struct xfs_inode *ip, char *link)`, and `xfs_inactive_symlink(struct xfs_inode *ip)`.

## Control Flow

There is no executable flow in the header. Callers use `xfs_symlink` during VFS symlink creation, `xfs_readlink` for readlink/get_link operations, and `xfs_inactive_symlink` during inode inactivation.

## State and Persistence Behavior

The header owns no state. Its declared functions manipulate persistent symlink inode data and directory metadata in `xfs_symlink.c`.

## Dependencies and Integration Points

The declarations rely on XFS inode/name types and Linux idmapped mount types being visible to including translation units. Integration points are VFS inode operations and inode reclaim/inactivation paths.

## Risks and Edge Cases

The API exposes raw XFS inode pointers and caller-provided buffers, so callers must pass locked/lifetime-valid objects according to the implementation contract and enough storage for symlink contents.

## Test Signals

Compile coverage of VFS symlink operation files and inactive inode code is the direct signal; runtime behavior is covered by the `xfs_symlink.c` test signals.
