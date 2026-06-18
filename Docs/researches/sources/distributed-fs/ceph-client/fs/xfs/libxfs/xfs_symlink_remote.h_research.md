# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_symlink_remote.h

Purpose: Declares the remote symlink helper API for XFS inode, bmap, and symlink creation/removal code.

Important APIs, types, and functions: Declares block calculation, header set/check, local-to-remote conversion callback, shortform verification, remote read, symlink target write, and remote truncation functions.

Control flow: Creation paths call the sizing and write helpers; fork conversion code uses `xfs_symlink_local_to_remote`; lookup/readlink uses `xfs_symlink_remote_read`; unlink/inactivation uses `xfs_symlink_remote_truncate`; inode verifiers use `xfs_symlink_shortform_verify`.

State and persistence: The header carries no state, but prototypes define the boundary for persistent remote symlink buffer headers and inline fork validation.

Dependencies and integration points: Integrates with inode fork management, bmap allocation, transactions, buffer cache, and symlink VFS operations.

Risks and test signals: Risks are prototype drift against callers and inconsistent use of owner/path length arguments. Test builds across kernel and userspace libxfs and exercise symlink create/read/remove paths for inline and remote targets.
