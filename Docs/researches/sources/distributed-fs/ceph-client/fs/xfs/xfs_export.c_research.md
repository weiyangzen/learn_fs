# sources/distributed-fs/ceph-client/fs/xfs/xfs_export.c

## Purpose
`xfs_export.c` supplies XFS exportfs operations for NFS and pNFS. It encodes stable file handles, decodes file handles back to dentries or parents, looks up `..`, and forces inode metadata to the log for NFS commit semantics.

## Important APIs, types, and functions
The externally referenced object is `xfs_export_operations`. Helper `xfs_fileid_length` validates supported 32-bit and 64-bit inode filehandle layouts. `xfs_fs_encode_fh` emits either generic `struct fid` or packed `struct xfs_fid64` handles. `xfs_nfs_get_inode` resolves an inode number/generation pair. `xfs_fs_fh_to_dentry`, `xfs_fs_fh_to_parent`, `xfs_fs_get_parent`, and `xfs_fs_nfs_commit_metadata` implement exportfs callbacks.

## Control flow
Encoding chooses parent-bearing fileid types only when a parent inode is supplied, and adds `XFS_FILEID_TYPE_64FLAG` when the filesystem can expose 64-bit inode numbers. Decode checks that the supplied filehandle length is sufficient, extracts inode/generation fields, calls `xfs_nfs_get_inode`, and wraps the result with `d_obtain_alias`. `xfs_nfs_get_inode` uses `XFS_IGET_UNTRUSTED`, translates invalid/stale/corrupt inode references to `-ESTALE`, reloads incomplete unlinked state if necessary, rejects generation mismatches and private inodes, and returns a VFS inode.

## State and persistence
Filehandles persist outside the kernel as inode/generation identities plus optional parent identity. The code itself keeps no private state. `commit_metadata` persists pending inode metadata by forcing the inode log item.

## Dependencies and integration points
It integrates with Linux exportfs, NFS filehandle ABI, XFS inode cache, directory lookup, pNFS block export callbacks under `CONFIG_EXPORTFS_BLOCK_OPS`, and the handle ioctl code that reuses `xfs_nfs_get_inode`.

## Risks and test signals
Risks include stale handles after inode reuse, NFSv2 handle-size limits with 64-bit inodes and subtree checks, generation zero being valid rather than wildcard, unlinked-list reload failures forcing shutdown, and private inode exposure. Test signals include encode/decode with and without parent handles, 32-bit and 64-bit inode filesystems, stale generation lookup, invalid inode numbers, exported subdirectories with `fsid`, pNFS block callbacks, and metadata commit after NFS writes.
