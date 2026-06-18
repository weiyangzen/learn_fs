# sources/distributed-fs/ceph-client/fs/adfs/super.c

## Purpose
`super.c` implements ADFS filesystem registration, mount context parsing, disc-record probing, superblock setup, inode-cache lifecycle, statfs, remount option handling, and teardown.

## Important APIs, types, and functions
Key functions are `adfs_init_fs_context()`, `adfs_parse_param()`, `adfs_get_tree()`, `adfs_fill_super()`, `adfs_probe()`, `adfs_validate_bblk()`, `adfs_validate_dr0()`, `adfs_put_super()`, `adfs_statfs()`, and `adfs_reconfigure()`. Module entry/exit are `init_adfs_fs()` and `exit_adfs_fs()`. `adfs_sops` defines superblock operations.

## Control flow
Mount allocates `adfs_sb_info`, parses `uid`, `gid`, `ownmask`, `othmask`, and `ftsuffix`, then probes either the boot-block disc record or single-zone disc record. After `adfs_read_map()` succeeds, it selects F or F+ directory operations, constructs a synthetic root `object_info`, creates the root inode, and installs default dentry operations. Reconfigure syncs and structure-copies parsed options into the live superblock info.

## State and persistence
Superblock state includes ownership/mask options, directory layout operations, name length, map metadata, and UID/GID policy. Persistent media state is read from the disc record and map; teardown releases map buffers and RCU-frees the superblock info.

## Dependencies and integration points
It depends on block-device mounting, `fs_context`, buffer_head probing, ADFS map and directory backends, slab inode caches, and VFS statfs/show_options contracts.

## Risks and test signals
Risks include invalid disc-record acceptance, block-size retry errors, option-copying pointer/state bugs on remount, root object synthesis mismatches, and cleanup leaks after partial mount failure. Test signals include boot-block and DR0 images, 256/512/1024-byte sectors, F and F+ roots, mount option display, remount option changes, silent mount failures, and module load/unload.
