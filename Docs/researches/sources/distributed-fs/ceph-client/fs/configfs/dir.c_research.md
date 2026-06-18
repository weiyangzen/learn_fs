# sources/distributed-fs/ceph-client/fs/configfs/dir.c

Purpose: implements configfs directory operations, config item/group attachment and detachment, mkdir/rmdir, readdir, subsystem registration, group registration, dependency pinning, and most configfs tree lifecycle rules.

Important APIs/functions: `configfs_make_dirent()`, `configfs_create_dir()`, `configfs_create_link()`, `configfs_lookup()`, `populate_attrs()`, `populate_groups()`, `configfs_mkdir()`, `configfs_rmdir()`, directory file operations, `configfs_register_group()`, `configfs_unregister_group()`, `configfs_register_default_group()`, `configfs_register_subsystem()`, `configfs_unregister_subsystem()`, `configfs_depend_item()`, `configfs_depend_item_unlocked()`, and `configfs_undepend_item()` are central. `configfs_dirent_lock` protects dirent linkage, symlink target link counts, and attach/drop state flags.

Control flow: subsystem registration pins configfs, links a root group, allocates a dentry, attaches the group, populates attributes/default groups, then marks dirents ready. User `mkdir()` validates parent readiness and `make_item`/`make_group` callbacks, pins owner modules, links the item under subsystem mutex, attaches the VFS view, and rolls back on any failure. `rmdir()` blocks links/dependents, marks the fragment dead, detaches default children and attributes, notifies clients, unlinks objects, and drops module references. Lookup instantiates attributes lazily from unpinned dirents. Readdir uses a cursor dirent to traverse under the global spinlock.

State and persistence: configfs is RAM-backed. Persistent in-memory state lives in `config_item` hierarchies, `configfs_dirent` trees, fragment death markers, child/default group lists, module references, and dependency counts.

Dependencies/integration: integrates VFS inode locks, dcache operations, module refcounting, configfs public callbacks in `include/linux/configfs.h`, `file.c` attribute creation, `inode.c` inode allocation/drop, `mount.c` pin/release, and `symlink.c` link serialization.

Risks: lock ordering is critical: inode mutex before `configfs_dirent_lock`, plus `configfs_symlink_mutex` around rmdir/link races. Recursive default-group attach/detach can stress lockdep and stack depth. Client callbacks must obey configfs reference rules; calling dependency APIs from callbacks is explicitly unsafe.

Test signals: mkdir/rmdir success and rollback, default group recursion, visible/invisible attributes, lazy attribute lookup, readdir under concurrent mutation, symlink versus rmdir races, dependent item preventing removal, subsystem unregister with non-empty tree, module reference release, and lockdep coverage.
