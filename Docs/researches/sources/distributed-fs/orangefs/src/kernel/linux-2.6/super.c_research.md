<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/super.c -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/super.c

## Purpose
Implements OrangeFS/PVFS2 Linux superblock operations, mount/remount/unmount handling, inode allocation/destruction hooks, statfs forwarding, export file-handle support, mount option parsing, and optional filesystem key caching. It is the main bridge between Linux VFS superblock lifecycle callbacks and the user-space `pvfs2-client-core` service-operation channel.

## Important APIs, Types, and Functions
Key exported or externally referenced entry points include `pvfs2_s_ops`, `pvfs2_read_inode`, `pvfs2_remount`, `pvfs2_fill_sb`, version-dependent `pvfs2_get_sb`/`pvfs2_mount`, `pvfs2_kill_sb`, and optional `fsid_key_table_initialize`/`fsid_key_table_finalize`. Internal helpers include `parse_mount_options`, `pvfs2_alloc_inode`, `pvfs2_destroy_inode`, `pvfs2_statfs`, `pvfs2_statfs_lite`, `pvfs2_dirty_inode`, `pvfs2_flush_sb`, and optional export helpers `pvfs2_fh_to_dentry`/`pvfs2_encode_fh`. The file depends heavily on `pvfs2_sb_info_t`, `pvfs2_mount_sb_info_t`, `pvfs2_kernel_op_t`, `PVFS_object_kref`, Linux `struct super_block`, `struct inode`, `struct dentry`, and conditional kernel-version macros.

## Control Flow
Mounting starts by sending `PVFS2_VFS_OP_FS_MOUNT` through `service_operation`, validating returned `fs_id` and root handle, then passing temporary mount metadata to `pvfs2_fill_sb`. `pvfs2_fill_sb` allocates `s_fs_info`, parses options, configures flags and xattr handlers, initializes VFS superblock fields, constructs the root inode via `pvfs2_get_custom_core_inode`, creates the root dentry, and installs export operations. Remount from VFS only reparses options and updates flags; `pvfs2_remount` additionally reissues a priority mount upcall so a restarted client core can rebuild mount state. `pvfs2_statfs` allocates a statfs operation, sends it to userspace, and copies returned capacity counters into `kstatfs`, truncating for older 32-bit `statfs` layouts when necessary. Unmount calls `pvfs2_flush_sb`, `pvfs2_unmount_sb`, removes the superblock from the global list, prunes dcache, runs generic cleanup, checks inode allocation counters, and frees private superblock data.

## State and Persistence
Persistent in-kernel state includes `pvfs2_superblocks`, private `PVFS2_SB(sb)` fields such as `root_khandle`, `fs_id`, `id`, `devname`, saved mount `data`, `mnt_options`, `mount_pending`, and inode allocation counters. Optional fs-key support maintains a module-lifetime `qhash_table` keyed by `PVFS_fs_id`; entries are created lazily via `PVFS2_VFS_OP_FSKEY` and released at module finalize. The file does not persist data to disk; it mirrors remote filesystem state and client-core mount identity inside kernel memory.

## Dependencies and Integration Points
This file integrates VFS super operations, OrangeFS inode helpers, dentry operations, xattr handler registration, bufmap size queries, export/NFS callbacks, global superblock list helpers, and the request queue service path in `waitqueue.c`. It also depends on client-core semantics for mount, remount, statfs, unmount, and fs-key upcalls.

## Risks
Mount option parsing uses a static options array and fixed-length copies; overflow checks exist but concurrent mounts share the static parser buffer. Error paths after partial `s_fs_info` allocation can leak private data in some branches. Fs-key cache access is not visibly protected by a lock in this file. File-handle encoding has compatibility branches and a suspicious connectable dentry variant that sets `len = 6` after writing parent data through `fh[9]`, so NFS export behavior needs focused coverage. Unmount manually calls both `kill_litter_super` and `dput(sb->s_root)` in some configurations, which is sensitive to kernel API expectations.

## Test Signals
Exercise successful and failed mounts with valid and invalid config servers, mount options `intr`, `acl`, `noatime`, `nodiratime`, and unsupported options. Test client-core restart remount, statfs with large counters on 32-bit-compatible paths, unmount after dirty atime updates, repeated mount/unmount leak counters, fs-key cache hit/miss behavior, and NFS file-handle encode/decode round trips when export operations are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/super.c -->
