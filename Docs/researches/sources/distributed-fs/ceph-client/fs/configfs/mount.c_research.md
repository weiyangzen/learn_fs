# sources/distributed-fs/ceph-client/fs/configfs/mount.c

Purpose: registers and mounts the configfs RAM filesystem, owns the root group/dirent, the dirent slab cache, and filesystem pinning helpers used by subsystem registration.

Important APIs/functions: `configfs_fill_super()` initializes the superblock, creates the root inode/dentry, initializes `configfs_root_group`, attaches the root dirent, and installs default dentry ops. `configfs_pin_fs()` and `configfs_release_fs()` wrap `simple_pin_fs()` and `simple_release_fs()` for users that need a live root without a user mount. `configfs_init()` creates `configfs_dir_cachep`, creates `/sys/kernel/config` mount point, and registers the filesystem. `configfs_exit()` reverses these steps. `configfs_free_inode()` frees symlink bodies stored in `i_link`.

Control flow: core init registers configfs early. User mount uses `get_tree_single()` to share a singleton filesystem instance. Kernel subsystem registration pins the filesystem and creates top-level groups under the root.

State and persistence: global `configfs_mount`, `configfs_mnt_count`, `configfs_dir_cachep`, `configfs_root_group`, and `configfs_root` persist while configfs is loaded. The filesystem contents are RAM state only.

Dependencies/integration: integrates VFS single-superblock mounting, sysfs mount-point creation under `kernel_kobj`, config item initialization, inode/dir operations, and dentry ops.

Risks: root dirent is static and excluded from normal dirent freeing. Symlink bodies must be freed in inode free. Failure paths must remove the sysfs mount point and destroy the cache. Pin counts must balance or configfs can remain mounted internally.

Test signals: mount/umount, internal pin/release without user mount, module load failure injection at cache/mountpoint/register steps, symlink inode free, and top-level subsystem register/unregister.
