<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/inode.c -->
# sources/distributed-fs/ceph-client/fs/erofs/inode.c

## Purpose
`inode.c` reads EROFS on-disk inodes, initializes VFS inode state and operations, supports fast symlinks, exposes stat/fiemap/ioctl behavior, and maps NIDs to stable inode-cache keys.

## Important APIs, types, and functions
Important functions include `erofs_read_inode`, `erofs_fill_symlink`, `erofs_fill_inode`, `erofs_iget`, `erofs_getattr`, `erofs_ioctl`, `erofs_compat_ioctl`, and `erofs_ioctl_get_volume_label`. It exports inode operation tables `erofs_generic_iops`, `erofs_symlink_iops`, and `erofs_fast_symlink_iops`.

## Control flow
`erofs_read_inode` locates inode metadata by NID, handles metabox inodes, reads compact or extended inode layouts across block boundaries, decodes mode, uid/gid, nlink, size, times, xattr size, datalayout, start block, device id, chunk info, compressed block counts, and DAX eligibility. Symlinks with inline data are copied into a cached NUL-terminated link. `erofs_fill_inode` assigns file, directory, symlink, or special operations, enables large folios, chooses address-space operations based on datalayout and I/O mode, and optionally enables inode sharing. `erofs_iget` uses `iget5_locked` keyed by NID.

## State and persistence
Persistent state is on-disk inode metadata. Runtime state includes `struct erofs_inode` fields, page-cache aops, cached symlink strings, inode sharing links, ACL/xattr initialization flags, and VFS inode cache membership.

## Dependencies and integration points
It depends on EROFS metadata reads, xattr/ACL helpers, data and compressed aops selection, inode-sharing support, VFS stat/ioctl/fiemap, and metabox-aware NID conversion.

## Risks and test signals
Risks include malformed inode formats, negative or overflowed sizes, xattr body size mistakes, 48-bit address decoding, compressed inodes when ZIP support is disabled, chunk format validation, fast symlink NUL validation, and DAX on unsupported layouts. Test signals include compact/extended inodes, all file types, inline symlinks, compressed and chunked files, metabox images, ACL/noacl xattrs, STATX attributes, volume-label ioctl, and 32-bit inode-number squashing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/inode.c -->
