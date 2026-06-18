# sources/distributed-fs/ceph-client/fs/xfs/xfs_pnfs.h

Purpose: Declares XFS pNFS block layout hooks when exportfs block operations are enabled and provides a no-op layout break helper otherwise.

Important APIs, types, and functions: Under `CONFIG_EXPORTFS_BLOCK_OPS`, declares `xfs_fs_get_uuid`, `xfs_fs_map_blocks`, `xfs_fs_commit_blocks`, and `xfs_break_leased_layouts`. Without that config, `xfs_break_leased_layouts` is an inline no-op returning success.

Control flow: Build-time configuration selects whether XFS exposes pNFS block layout operations or compiles callers against a stub for layout recall.

State and persistence behavior: The header itself has no state. Enabled implementations may allocate blocks, update inode metadata, and force log durability.

Dependencies and integration points: Ties XFS inode operations to NFS/exportfs block layout support and `struct iomap`. The no-op stub lets non-pNFS builds avoid conditional logic at call sites that merely need to break layouts.

Risks: Callers relying on actual layout recall must only do so in configurations where exportfs block ops are enabled. Prototype changes must stay in sync with NFS/exportfs expected hooks.

Test signals: Build with `CONFIG_EXPORTFS_BLOCK_OPS=y` and disabled; verify callers compile in both modes and pNFS export tests only expect block layout behavior in the enabled mode.
