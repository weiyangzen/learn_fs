# sources/distributed-fs/ceph-client/fs/sysfs/symlink.c

## Purpose
This file implements sysfs symlink creation, deletion, and rename operations between kobjects or from a kernfs directory to a kobject.

## Important APIs, Types, and Functions
Public helpers include `sysfs_create_link_sd()`, `sysfs_create_link()`, `sysfs_create_link_nowarn()`, `sysfs_delete_link()`, `sysfs_remove_link()`, and `sysfs_rename_link_ns()`. The internal `sysfs_do_create_link_sd()` handles target lookup and duplicate warning behavior.

## Control Flow and State
Creation validates name and parent, then acquires `sysfs_symlink_target_lock` while reading `target_kobj->sd`. If the target has a kernfs node, it takes a kernfs reference, drops the lock, and creates a kernfs link. This is paired with `sysfs_remove_dir()` clearing `kobj->sd` under the same lock. Deletion either removes by plain name or, for `sysfs_delete_link()`, derives the target namespace from the target `sd` when the parent is namespace-enabled. Rename finds the existing link in the target namespace, verifies it is a link and still points to the expected target kobject, then calls `kernfs_rename_ns()`.

## Persistence, Dependencies, and Integration
Symlinks are virtual kernfs nodes. The code depends on kobject directory lifetime, kernfs link semantics, namespace tags, and the directory code's synchronization contract.

## Risks and Test Signals
Risks include target removal races, stale namespace selection, renaming a link that no longer points to the expected kobject, and duplicate link names. Useful tests include concurrent kobject unregister/link create, namespace-tagged delete/rename, duplicate-name warning coverage, and module unload paths that remove links and target directories in varied orders.
