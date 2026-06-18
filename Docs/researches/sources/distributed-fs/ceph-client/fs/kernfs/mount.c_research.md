# sources/distributed-fs/ceph-client/fs/kernfs/mount.c

## Purpose

`sources/distributed-fs/ceph-client/fs/kernfs/mount.c` implements kernfs superblock setup, mount lookup, export handles, namespace matching, superblock teardown, and early kernfs cache/lock initialization. The source was read as a complete 472-line file.

## Important APIs, Types, and Functions

Important exports are `kernfs_root_from_sb`, `kernfs_node_dentry`, `kernfs_super_ns`, `kernfs_get_tree`, `kernfs_free_fs_context`, `kernfs_kill_sb`, and `kernfs_init`. Internal components include `kernfs_sops`, `kernfs_export_ops`, `kernfs_fill_super`, `kernfs_test_super`, `kernfs_set_super`, `kernfs_encode_fh`, `kernfs_fh_to_dentry`, and `kernfs_fh_to_parent`.

## Control Flow

`kernfs_get_tree` allocates `kernfs_super_info`, sets the root/ns pair, and calls `sget_fc` so mounts sharing the same root and namespace reuse a superblock. If a new superblock is created, `kernfs_fill_super` installs kernfs super operations, xattr handlers, optional export ops, UUID, root inode, root dentry, and default dentry operations, then links the superblock into `root->supers`. `kernfs_kill_sb` removes that list entry before killing the anonymous superblock and freeing `kernfs_super_info`. Export decoding maps file handles back to kernfs IDs and then to inodes/dentries.

## State and Persistence Behavior

The persistent state is in `kernfs_root`: slab caches are global after `kernfs_init`, while each live superblock contributes one `kernfs_super_info` list node under `kernfs_supers_rwsem`. File handles persist only as encoded kernfs node IDs plus generation-compatible support for generic 32-bit handles.

## Dependencies and Integration Points

The file integrates kernfs with fs_context, anonymous superblocks, exportfs, statfs, fsnotify path display, xattr handlers from `inode.c`, dentry operations from `dir.c`, and node lookup by ID from kernfs core code. `file.c` notification uses `root->supers` to issue fsnotify events across mounts.

## Risks and Edge Cases

Superblock matching must include namespace tags or different namespace views can alias. `kernfs_node_dentry` requires `KERNFS_ROOT_INVARIANT_PARENT` because it walks ancestors outside continuous locking. Export handle decoding can return `-ESTALE` for removed nodes. Freeze support is explicitly disabled to avoid sysfs power-management deadlocks.

## Test Signals

Useful tests include repeated mount/remount/unmount with shared roots and namespaces, exportfs file-handle encode/decode tests, cgroup/sysfs dentry reconstruction for deep nodes, lockdep for super list rwsem use, UUID/statfs checks, and unmount races with notification work.
