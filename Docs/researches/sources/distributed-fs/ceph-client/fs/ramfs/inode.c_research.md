# sources/distributed-fs/ceph-client/fs/ramfs/inode.c

Purpose: Implements ramfs filesystem registration, mount-context parsing, superblock setup, inode creation, directory operations, tmpfile support, and teardown.

Important APIs, types, and functions: Defines `struct ramfs_mount_opts`, `struct ramfs_fs_info`, `ramfs_get_inode()`, `ramfs_mknod()`, `ramfs_mkdir()`, `ramfs_create()`, `ramfs_symlink()`, `ramfs_tmpfile()`, `ramfs_dir_inode_operations`, `ramfs_show_options()`, `ramfs_ops`, `ramfs_fs_parameters`, `ramfs_parse_param()`, `ramfs_fill_super()`, `ramfs_get_tree()`, `ramfs_free_fc()`, `ramfs_init_fs_context()`, `ramfs_kill_sb()`, and `ramfs_fs_type`.

Control flow: Mount setup allocates `ramfs_fs_info`, defaults mode to 0755, parses `mode=` while ignoring unknown historical options, and calls `get_tree_nodev()`. Superblock fill sets ramfs magic, page-sized blocks, simple super operations, non-caching dentries, and creates a root directory inode. Inode creation assigns ownership, `ram_aops`, high-user GFP, unevictable mapping, timestamps, and type-specific operation tables. Directory operations use simple VFS helpers after security initialization.

State and persistence: All file data and metadata live in memory only. Superblock private info stores mount mode. Inode address spaces are unevictable and have no backing device. `kill_anon_super()` drops the anonymous in-memory superblock.

Dependencies and integration points: Uses VFS fs-context API, simple directory helpers, page symlink helpers, LSM inode initialization, generic ramfs file ops from the selected file implementation, and `FS_USERNS_MOUNT`.

Risks and test signals: Risks include unlimited memory consumption, mount option compatibility, security xattr initialization failures, link-count mistakes, tmpfile completion errors, and user namespace mount behavior. Test mount with and without `mode=`, create/link/unlink/rename/mkdir/rmdir/symlink/tmpfile flows, memory pressure, and teardown cleanup.
