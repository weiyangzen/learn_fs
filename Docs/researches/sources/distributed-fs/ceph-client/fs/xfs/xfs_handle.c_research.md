# sources/distributed-fs/ceph-client/fs/xfs/xfs_handle.c

## Purpose
`xfs_handle.c` implements XFS handle ioctls, privileged open/readlink-by-handle, legacy attribute list/multi operations by handle, and parent-pointer enumeration ioctls.

## Important APIs, types, and functions
Public functions include `xfs_find_handle`, `xfs_handle_to_dentry`, `xfs_open_by_handle`, `xfs_readlink_by_handle`, `xfs_ioc_attr_list`, `xfs_attrlist_by_handle`, `xfs_ioc_attrmulti_one`, `xfs_attrmulti_by_handle`, `xfs_ioc_getparents`, and `xfs_ioc_getparents_by_handle`. Helpers initialize filesystem/file handles, decode kernel/user handles to dentries or inodes, format attr list entries, map attr flags, perform attr get/set/remove, and format parent pointer records.

## Control flow
`xfs_find_handle` resolves either an fd or path, verifies an XFS regular file/directory/symlink, initializes an fs or file handle, and copies it to userspace. Handle decode requires a directory file as the authority and validates handle length before using exportfs or `xfs_nfs_get_inode`. `xfs_open_by_handle` requires `CAP_SYS_ADMIN`, restricts target types, applies append/immutable/directory-write checks, opens a new fd, and marks regular-file opens `O_NOATIME`/`FMODE_NOCMTIME`. `xfs_readlink_by_handle` similarly requires privilege and symlink target. Attribute list/multi paths copy legacy request arrays, decode the handle, allocate bounded buffers, filter namespaces, and perform attr get/set/remove with write-mount accounting. Parent enumeration requires parent-pointer feature and privilege, lists `XFS_ATTR_PARENT` records through the attr cursor, formats variable-length records with parent handles and names, expands the final record to fill the buffer, and copies records/request state back.

## State and persistence
Handles persist outside the kernel as fsid plus inode/generation. Attribute set/remove operations persist xattrs and may invalidate ACL cache for root namespace changes. Parent pointer reads are read-only, but corrupt parent attr decode marks the inode sick. Runtime state includes copied request buffers, attr cursors, per-call kernel output buffers, held dentries/inodes, and mount write references.

## Dependencies and integration points
It integrates with XFS export/NFS inode lookup, Linux path/fd/open helpers, xattr and parent-pointer subsystems, ACL cache, health marking, ioctl dispatch, privilege checks, usercopy, and VFS readlink/open semantics.

## Risks and test signals
Risks include exposing handle operations without proper privilege, stale handle generation, non-directory authority files, user buffer overflow/short-buffer handling, attr namespace flag conflicts, immutable/append enforcement, parent pointer corruption loops, and cursor continuation correctness. Test signals include all handle-generating ioctls, open/readlink by stale and valid handles, regular/dir/symlink and rejected special files, attrlist cursor continuation, attrmulti mixed success/error array reporting, root/secure/user namespace filters, parent list small-buffer `-EMSGSIZE`, root-directory parent flag, getparents by handle without exportfs dentry connection, and corruption marking on malformed parent attrs.
