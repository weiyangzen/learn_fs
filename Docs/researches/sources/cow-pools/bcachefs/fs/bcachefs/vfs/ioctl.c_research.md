# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/ioctl.c

Implements bcachefs file ioctl handling for attribute reinheritance, label/version/shutdown ioctls, subvolume create/destroy/list/path queries, snapshot-tree queries, reflink option propagation, raw direct reads, and unpoisoning poisoned extents.

Key entry points:
- `bch2_fs_file_ioctl()` dispatches all file-level bcachefs and generic filesystem ioctls, falling back to `bch2_fs_ioctl()` for global bcachefs commands.
- `bch2_compat_fs_ioctl()` maps selected 32-bit compat commands to native handling.
- `bch2_ioc_reinherit_attrs()` reapplies inherited inode attributes from a directory to a named child and performs project quota transfer if needed.
- `bch2_ioc_getlabel()`, `bch2_ioc_setlabel()`, `bch2_ioc_getversion()`, and `bch2_ioc_goingdown()` implement generic filesystem label/version/shutdown controls.
- `bch2_ioctl_subvolume_create*()` and `bch2_ioctl_subvolume_destroy*()` create snapshots/subvolumes and remove subvolumes through VFS path lookup and bcachefs create/unlink transactions.
- `bch2_ioctl_subvolume_list()` and `bch2_ioctl_subvolume_to_path()` expose subvolume child listings and subvolume-root paths.
- `bch2_ioctl_snapshot_tree()` reports snapshot tree metadata and per-snapshot accounting.
- `bch2_ioc_set_reflink_p_may_update_opts()` and `bch2_ioc_propagate_reflink_p_opts()` update reflink option propagation metadata.
- `bch2_ioc_pread_raw()` performs privileged owner raw direct reads with optional poison-check suppression and returns structured error messages.
- `bch2_ioc_unpoison()` clears poisoned extent flags in regular extents and reflink targets.

Core mechanics:
- Subvolume creation validates flags, optionally resolves a source path for snapshots, syncs inodes before snapshot creation, performs VFS path creation and permission/security checks, and calls `__bch2_create()` under `snapshots.create_lock`.
- Subvolume destruction uses the VFS locked path-removal API, adjusts lock ordering around `mnt_want_write()`, revalidates the victim dentry, checks permissions, and calls `__bch2_unlink(..., deleting_snapshot=true)`.
- Subvolume listing iterates `BTREE_ID_subvolume_children`, checks that the caller can traverse from child root to parent via full VFS permission checks, converts inums to relative paths, and emits packed user records.
- Snapshot-tree query resolves tree id from argument or current file subvolume, requires `CAP_SYS_ADMIN` for arbitrary tree ids, flushes the btree write buffer, iterates snapshots in the tree, reads per-snapshot accounting, and copies bounded node records to userspace.
- Reflink option propagation walks extent keys, updates `KEY_TYPE_reflink_p` flags, then propagates options to underlying `reflink_v` records spanning front/back padding.
- Raw pread requires `O_DIRECT` and file ownership/capability, imports a userspace buffer, calls the direct I/O read path with a `bch_read_err_report`, and copies error count/message state back to userspace.
- Unpoisoning rebuilds extent keys with the poisoned flag cleared and commits updates across regular and reflink-backed ranges.

Important invariants:
- Label setting and shutdown require `CAP_SYS_ADMIN`; arbitrary snapshot-tree lookup and reflink feature enablement do too.
- Subvolume create/destroy reject cross-filesystem paths with `-EXDEV`.
- v2 subvolume ioctls copy structured error messages back through `bch2_copy_ioctl_err_msg()`.
- User buffer writes use explicit `copy_to_user_errcode()`, `put_user()`, padding zero-fill, and range-size checks.
- Permission-sensitive traversal deliberately unlocks the btree transaction before calling `inode_permission()` because ACL lookup may start its own transaction.

Filesystem relevance:
- This file is the user-control surface for bcachefs-specific VFS features: subvolumes, snapshots, reflink metadata maintenance, poison recovery, raw reads, labels, and controlled emergency shutdown.

Notable risks:
- Subvolume listing combines btree traversal with VFS permission checks and transaction relocking, making restart/error handling subtle.
- Some comments and strings contain typos such as "invalid flasg", but behavior is unaffected.
- Raw reads and unpoison operations intentionally expose low-level repair/diagnostic functionality and are guarded by ownership/capability checks.
