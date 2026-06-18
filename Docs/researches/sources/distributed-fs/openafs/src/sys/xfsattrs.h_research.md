# sources/distributed-fs/openafs/src/sys/xfsattrs.h

## Purpose
`xfsattrs.h` defines SGI XFS extended-attribute structures used to represent OpenAFS vice inodes and directory markers under `AFS_SGI_XFS_IOPS_ENV`.

## Important APIs, types, and functions
Important definitions include `afs_inode_params_t`, `AFS_XFS_ATTR`, `AFS_XFS_ATTR_VERS`, name-version constants, `AFS_INODE_DIR_NAME`, `afs_xfs_attr_t`, `SIZEOF_XFS_ATTR_T`, link/magic helpers, `AFS_XFS_DATTR`, `afs_xfs_dattr_t`, `vice_inode_info_t`, and `i_list_inode_t`.

## Control flow
There is no runtime control flow. Conditional compilation exposes the definitions only for SGI XFS IOPS builds.

## State and persistence behavior
The structures describe persistent XFS inode attributes: volume/vnode/uniquifier/data-version parameters, parent inode, name scheme version, link count encoded in mode bits, clipped volume ids, directory attributes, and list-inode records.

## Dependencies and integration points
It depends on `<sys/attributes.h>` and must match kernel XFS attribute handling, salvager `ViceInodeInfo`, and utilities such as ListViceInodes and XFS inode repair code.

## Risks
Packed size assumptions are critical; comments note XFS attribute size constraints and `SIZEOF_XFS_ATTR_T` intentionally differs from `sizeof`. Any field layout change can make existing vice inodes unreadable. Kernel/user `ino_t` width differences are handled by conditional fields.

## Test signals
Build SGI XFS IOPS paths, create/list/fix vice inodes, verify attribute sizes and offsets, and run salvager/ListViceInodes compatibility checks for both name-version schemes.
