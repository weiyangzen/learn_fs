<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/super25.c -->
# sources/distributed-fs/lustre-release/lustre/llite/super25.c

## Purpose
`super25.c` is the Linux VFS superblock and module-registration layer for the Lustre client filesystem. It allocates llite inode slabs, exposes `lustre_super_operations`, implements mount/remount through `fs_context`, and initializes or tears down client-wide llite, VVP, xattr, tunable, and cache resources.

## Important APIs, Types, And Functions
Important functions include `ll_alloc_inode()`, `ll_destroy_inode()`, `ll_drop_inode()`, `ll_show_devname()`, `lustre_fill_super()`, `lustre_get_tree()`, `lustre_reconfigure()`, `lustre_init_fs_context()`, `lustre_kill_super()`, `lustre_init()`, and `lustre_exit()`. The exported VFS tables are `lustre_super_operations`, `lustre_fs_context_ops`, and `lustre_fs_type`.

## Control Flow
Module initialization sets up libcfs, slab caches (`lustre_inode_cache`, `ll_file_data`, `ll_pcc_inode`, quota iterator), llite tunables, VVP global state, a cl environment for inode finalization, xattr cache infrastructure, and finally registers the `lustre` filesystem type. Mounting calls `lustre_fill_super()`, initializes Lustre mount state, waits for OBD zombie cleanup, rejects or redirects server mounts, starts the MGC for client mounts, and calls `ll_fill_super()`. Remount synchronizes the filesystem, pushes read-only state to the MDT import, toggles `SB_RDONLY`, and swaps mount options.

## State And Persistence
Persistent runtime state includes slab caches, the registered filesystem type, per-superblock `lustre_sb_info`/`ll_sb_info`, mount data in `fs_context->fs_private`, and client/VVP/xattr global registrations. Inode objects are allocated from `ll_inode_cachep`; final freeing is RCU-delayed to allow VFS readers and llcrypt state to drain.

## Dependencies And Integration Points
This file binds the VFS to lower Lustre layers: `lustre_init_lsi()`, `lustre_start_mgc()`, `ll_fill_super()`, `ll_put_super()`, `ll_delete_inode()`, `ll_statfs()`, `ll_umount_begin()`, `llite_tunables_register()`, `vvp_global_init()`, `ll_xattr_init()`, and server mount handling when built with server support.

## Risks And Edge Cases
Initialization has many staged resources and must unwind in reverse order on failure. Mount disables lockdep around special Lustre mount locking. Remount read-only transitions can fail if the MDT import rejects `KEY_READ_ONLY`. `ll_drop_inode()` depends on inode cache and encryption policy decisions. Exit must call `rcu_barrier()` before destroying the inode cache.

## Test Signals
Test mount/unmount loops, failed mount injection at each init stage, client versus server target mount attempts, remount read-only/read-write, inode allocation pressure, encrypted inode eviction, module unload after active inodes, and `/proc/mounts` device-name rendering for MGS and direct-device mount data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/super25.c -->
