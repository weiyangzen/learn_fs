# sources/distributed-fs/ceph-client/fs/sysfs/dir.c

## Purpose
This file implements core sysfs directory operations for kobjects: create, remove, rename, move, and mount-point directories.

## Important APIs, Types, and Functions
It defines global `sysfs_symlink_target_lock`, duplicate-name diagnostics via `sysfs_warn_dup()`, and public helpers `sysfs_create_dir_ns()`, `sysfs_remove_dir()`, `sysfs_rename_dir_ns()`, `sysfs_move_dir_ns()`, `sysfs_create_mount_point()`, and `sysfs_remove_mount_point()`. The backing implementation is kernfs directory creation/removal.

## Control Flow and State
Directory creation selects the parent from `kobj->parent->sd` or `sysfs_root_kn`, obtains ownership via `kobject_get_ownership()`, then calls `kernfs_create_dir_ns()` with the kobject as private data. On success, `kobj->sd` becomes the kernfs node. Removal first clears `kobj->sd` under `sysfs_symlink_target_lock` to prevent symlink operations from dereferencing a freed target, then removes the kernfs directory.

Rename and move are thin wrappers over `kernfs_rename_ns()`, with namespace support. Mount points are special always-empty kernfs directories under a parent kobject, useful for exposing filesystem mount anchors such as tracefs.

## Persistence, Dependencies, and Integration
Sysfs directories are virtual state derived from live kobjects. Dependencies include kernfs, kobject ownership, namespace tags, and symlink code that observes `kobj->sd`. Integration is with driver core and any subsystem publishing kobjects.

## Risks and Test Signals
Important races involve symlinks to kobjects being removed concurrently, duplicate names, missing parent `sd`, and namespace moves. Test signals include kobject add/remove stress, lockdep for `sysfs_symlink_target_lock`, duplicate filename warning paths, namespace-tagged directory lookups, and module unload tests that remove sysfs directories while links exist.
