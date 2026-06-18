# sources/distributed-fs/ceph-client/fs/xfs/xfs_export.h

## Purpose
`xfs_export.h` documents and declares the XFS NFS filehandle ABI, especially the 64-bit inode extension.

## Important APIs, types, and functions
It defines packed `struct xfs_fid64` with inode, generation, parent inode, and parent generation fields, plus `XFS_FILEID_TYPE_64FLAG` to tag 64-bit inode handles. It declares `xfs_nfs_get_inode`.

## Control flow
The header has no executable flow. `xfs_export.c` uses the layout and flag while encoding/decoding filehandles; handle ioctl code also uses the 64-bit fileid type to decode XFS handles through exportfs.

## State and persistence
The packed layout is wire-visible persistent ABI. The comment explains operational constraints for NFS exports of filesystems that may contain 64-bit inode numbers.

## Dependencies and integration points
It depends on VFS `struct inode`/`struct super_block` concepts and is included by XFS export and handle code.

## Risks and test signals
Risks are ABI incompatibility if the flag or struct layout changes and NFS deployments that export subdirectories on 64-bit inode filesystems without a suitable `fsid`. Test signals include compile-time layout use, NFS handle round trips, and compatibility with old clients.
