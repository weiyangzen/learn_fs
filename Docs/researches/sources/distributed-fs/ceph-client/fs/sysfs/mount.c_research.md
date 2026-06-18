# sources/distributed-fs/ceph-client/fs/sysfs/mount.c

## Purpose
This file initializes, mounts, and tears down the sysfs filesystem using kernfs, including namespace-aware mount context setup.

## Important APIs, Types, and Functions
It defines `sysfs_root`, exported internal `sysfs_root_kn`, filesystem type `sysfs_fs_type`, and init function `sysfs_init()`. Context operations are `sysfs_init_fs_context()`, `sysfs_get_tree()`, and `sysfs_fs_context_free()`. `sysfs_kill_sb()` wraps kernfs superblock cleanup and namespace release.

## Control Flow and State
`sysfs_init()` creates a kernfs root with extra open permission checks, records its root node, and registers the `sysfs` filesystem. Mount context setup rejects non-kernel mounts when current network namespace policy forbids mounting, allocates `kernfs_fs_context`, grabs the current net namespace tag, sets `fc->global = true`, and if a namespace exists, switches `fc->user_ns` to the namespace owner's user namespace. `sysfs_get_tree()` delegates to `kernfs_get_tree()` and marks newly created superblocks user-namespace visible.

## Persistence, Dependencies, and Integration
Sysfs mount state is virtual kernfs state rooted at `sysfs_root`. It depends on kobject namespace operations, network namespace tags, fs_context, kernfs, and VFS filesystem registration. `FS_USERNS_MOUNT` allows user namespace mounts subject to sysfs namespace checks.

## Risks and Test Signals
Risk centers on namespace lifetime, user namespace selection, mount permission policy, and correct release of namespace tags on both context free and superblock kill. Tests should cover sysfs mount from initial and non-initial network/user namespaces, failed context allocation paths, kernfs root registration failures, and unmount namespace reference cleanup.
