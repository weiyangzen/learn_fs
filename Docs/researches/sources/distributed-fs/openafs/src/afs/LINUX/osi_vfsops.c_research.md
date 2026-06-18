## sources/distributed-fs/openafs/src/afs/LINUX/osi_vfsops.c

Purpose: Linux filesystem-type and superblock operations for mounting, rooting, statfs, inode allocation, and unmounting the OpenAFS filesystem.

Important APIs and state: defines `afs_fs_type`, `afs_sops`, global `afs_globalVp`, `afs_globalVFS`, `afs_cacheMnt`, `afs_was_mounted`, and `afs_backing_dev_info`. Main functions include `afs_fill_super`, `afs_root`, mount/get-tree wrappers, `afs_alloc_inode`, `afs_destroy_inode`, `afs_evict_inode`/`afs_clear_inode`, `afs_put_super`, `afs_statfs`, `afs_init_inodecache`, and `afs_destroy_inodecache`.

Control flow: mount enters through modern `fs_context` `get_tree_nodev`, `mount_nodev`, or older `get_sb_nodev` depending on kernel features. `afs_fill_super` takes the AFS global lock, rejects remount after prior mount via `afs_was_mounted`, pins the module, populates superblock flags and operations, configures dentry operations, initializes backing-device info/read-ahead settings, optional export ops, max file size, and calls `afs_root`. `afs_root` creates a request, checks initialization, fetches `afs_rootFid`, fills the root inode, and creates `s_root`. On failure, setup is unwound and vcaches are flushed. Unmount uses `afs_put_super` to clear globals, call `afs_shutdown(AFS_WARM)`, release the cache mount, verify allocations, destroy backing-device info, clear `s_dev`, and release the module.

Dependencies and integration: depends on Linux superblock, mount, BDI, slab/inode-cache, and dentry APIs. It integrates with `osi_vnodeops.c` through `afs_dentry_operations` and `afs_fill_inode`, and with NFS export support via `afs_export_ops` when enabled.

State and persistence: mount state is global and intentionally single-instance. The filesystem fakes statfs capacity with `AFS_VFS_FAKEFREE`; actual cache/server state lives elsewhere.

Risks: single-remount prevention requires module reload after mount/unmount. Failure cleanup must match partially initialized BDI and module refs. Inode eviction panics if a vcache is still on VLRU/hash queues, which is correct as an invariant check but can crash if lifecycle accounting is wrong.

Test signals: mount/unmount, failed root acquisition, repeated mount without reload, backing-device setup on old/new kernels, inode cache create/destroy, statfs values, NFS export builds, and leak checks after unmount.
