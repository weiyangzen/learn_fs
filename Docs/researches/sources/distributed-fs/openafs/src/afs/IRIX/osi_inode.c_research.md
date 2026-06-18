# sources/distributed-fs/openafs/src/afs/IRIX/osi_inode.c

## sources/distributed-fs/openafs/src/afs/IRIX/osi_inode.c

Purpose: implements IRIX inode syscalls for OpenAFS server/salvager operation, focusing on XFS-backed Vice inode creation, opening, link-count adjustment, and listing metadata.

Important APIs/types/functions: `afsidestroy`, `xfs_getinode`, `xfs_igetinode`, `xfs_icreatename64`, `afs_syscall_icreatename64`, `afs_syscall_iopen`, `iopen`, `iopen64`, `xfs_iincdec64`, `iincdec64`, `afs_syscall_iinc64`, `afs_syscall_idec64`, and `afs_syscall_ilistinode64`. Legacy EFS `getinode`, `igetinode`, `icreate`, and `afs_syscall_icreate` return `ENOSYS`; `iinc`/`idec` return `ENOTSUP`.

Control flow: XFS lookup resolves a VFS by device, calls `xfs_iget`, unlocks the inode, validates vnode attributes, and returns an XFS inode/vnode. `xfs_icreatename64` copies a base path, builds/locates a per-volume AFS inode directory, creates it with root attributes if needed, creates a hidden file with a base64 name/tag, stores AFS parameters in root XFS attributes, sets mode/uid/gid markers, returns the inode number, and cleans up partial files/directories on failure. Link-count changes verify magic and volume id via uid/gid/mode, update encoded link bits, or remove the hidden file and possibly its empty volume directory when count reaches zero. Listing reads XFS attributes and vnode stats into `i_list_inode_t`.

State/persistence: persists Vice inode metadata in XFS extended attributes and namespace files, with uid clipped to RW volume id and gid set to `XFS_VICEMAGIC`; link count is encoded in mode bits.

Dependencies/integration: depends on IRIX XFS internals, `afs/xfsattrs.h`, VOP attribute wrappers, volume create mutex, OpenAFS syscall registration, base64 naming, and root-only privilege checks.

Risks/test signals: high risk around cleanup after partial creates, directory create/remove races, 64-bit inode composition, XFS attribute version mismatches, link-count overflow above 7, and legacy unsupported syscall callers. Test fileserver inode create/open/inc/dec/list, volume special directories, concurrent vos create/zap, invalid attribute versions, and 32/64-bit syscall entry points.
