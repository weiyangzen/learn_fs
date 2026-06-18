<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/dir.c -->
# sources/distributed-fs/ceph-client/fs/kernfs/dir.c

## Purpose
`kernfs/dir.c` implements kernfs directory and tree management: node naming/path construction, reference and active-reference lifetime, sibling rbtree indexing, root and directory creation, lookup/readdir VFS operations, activation/hiding/removal, self-removal, namespace-aware find/walk, and rename/move.

## Important APIs, types, and functions
Major exported functions include `kernfs_name`, `kernfs_path_from_node`, `pr_cont_kernfs_name`, `pr_cont_kernfs_path`, `kernfs_get_parent`, `kernfs_get_active`, `kernfs_put_active`, `kernfs_get`, `kernfs_put`, `kernfs_node_from_dentry`, `kernfs_new_node`, `kernfs_find_and_get_node_by_id`, `kernfs_add_one`, `kernfs_find_and_get_ns`, `kernfs_walk_and_get_ns`, `kernfs_create_root`, `kernfs_destroy_root`, `kernfs_root_to_node`, `kernfs_create_dir_ns`, `kernfs_create_empty_dir`, `kernfs_activate`, `kernfs_show`, `kernfs_remove`, `kernfs_break_active_protection`, `kernfs_unbreak_active_protection`, `kernfs_remove_self`, `kernfs_remove_by_name_ns`, and `kernfs_rename_ns`. VFS tables are `kernfs_dops`, `kernfs_dir_iops`, and `kernfs_dir_fops`.

## Control flow
Names and paths are resolved under RCU and, when parent pointers are mutable, `kernfs_rename_lock`. Sibling lookup uses a per-directory red-black tree ordered by a 31-bit hash, namespace id, and name. New nodes allocate an RCU-freed name, a slab node, a cyclic idr id with generation high bits, optional iattrs/security xattrs, and a parent reference; `kernfs_add_one` validates namespace requirements and active parent directory state, links the node, updates parent revision/timestamps, and activates it unless the root requested deactivated creation.

Active references gate kernfs file and syscall operations. `kernfs_get_active` fails once a node is deactivated; removal marks a subtree removing, biases active counts negative, drains active users and open files, clears VFS inode link counts for mounted supers, unlinks siblings, and drops base references in postorder. `kernfs_remove_self` breaks the caller's own active protection to avoid self-deadlock, arbitrates concurrent self-removers with `KERNFS_SUICIDAL/SUICIDED`, and waits for the winning operation to drain. Rename validates active source/target, invariant-parent roots, and duplicate destination, unlinks from the old rbtree, updates parent/name/ns under the rename lock when needed, recomputes hash, and relinks.

VFS lookup searches by namespace and instantiates positive or negative dentries with revision tracking. Dentry revalidation drops stale negatives when parent revisions changed and invalidates positives whose node was deactivated, moved, renamed, or namespace-mismatched. Readdir emits dots, then iterates active children in hash order, retaining the current node in `file->private_data` for seek continuity.

## State and persistence behavior
Kernfs state is in-memory only. Persistent-looking identifiers are runtime inode ids from `root->ino_idr` plus generation bits. Important mutable state includes parent RCU pointers, names, namespace tags, rb nodes, active and base refcounts, flags (`KERNFS_ACTIVATED`, `HIDDEN`, `REMOVING`, `EMPTY_DIR`, `SUICIDAL`, `SUICIDED`), directory child trees, subdir counts, revision counters for dentry invalidation, mounted-super lists, and optional inode attributes/xattrs. RCU frees names/nodes after final `kernfs_put`.

## Dependencies and integration points
This file depends on VFS inode/dentry/file operation hooks, RCU, idr, red-black trees, rwsems/spinlocks, namespace ids, LSM kernfs security initialization, kernfs internal inode/file/symlink helpers, fsnotify-facing inode nlink clearing, and caller-provided `kernfs_syscall_ops` for mkdir/rmdir/rename. It is core infrastructure for sysfs-like and cgroup-like filesystems.

## Risks and test signals
Risks include active-reference leaks or underflows, removal racing lookup/readdir/rename, namespace hash collisions and ordering errors, stale negative dentries after directory changes, self-removal waiting bugs, RCU name lifetime mistakes, invariant-parent violations, and deadlocks involving `kernfs_rwsem`, `kernfs_supers_rwsem`, `kernfs_iattr_rwsem`, rename lock, and open-file draining. Tests should exercise concurrent create/remove/lookup/readdir, namespace-filtered directories, rename across parents and no-op renames, hidden/show activation, deactivated-root batch creation, self-deleting files with concurrent writers, id lookup with generation mismatch, dentry revalidation after move/remove, and fault injection for idr/slab/security allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/dir.c -->
