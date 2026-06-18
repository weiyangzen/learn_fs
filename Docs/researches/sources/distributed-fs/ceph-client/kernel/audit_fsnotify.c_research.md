# sources/distributed-fs/ceph-client/kernel/audit_fsnotify.c

## Purpose
`audit_fsnotify.c` implements fsnotify-backed executable/path mark tracking for audit rules, especially `AUDIT_EXE` style filters. It associates an audit rule with a filesystem mark, tracks the target inode/device as filesystem events occur, and removes rules automatically when the marked object disappears or is unmounted.

## Important APIs, types, and functions
`struct audit_fsnotify_mark` stores the tracked device, inode, insertion path string, embedded `fsnotify_mark`, and owning `audit_krule`. The global `audit_fsnotify_group` is initialized by `audit_fsnotify_init()`. Public helpers are `audit_alloc_mark()`, `audit_remove_mark()`, `audit_remove_mark_rule()`, `audit_mark_path()`, and `audit_mark_compare()`.

`audit_update_mark()` refreshes inode/device values or sets them to unset. `audit_mark_handle_event()` is the fsnotify event callback. `audit_autoremove_mark_rule()` logs and deletes the owning rule when the mark target is invalidated. `audit_fsnotify_free_mark()` releases mark memory through `audit_fsnotify_mark_free()`.

## Control flow
Rule parsing calls `audit_alloc_mark()` with a pathname. The function rejects non-absolute paths and trailing slashes, resolves the parent and child dentry, rejects negative child dentries, allocates the mark, stores the path, records the child inode/dev, and attaches an inode mark to the parent directory with create/move/delete/self event masks. On create/move/delete events, the callback compares the event dentry name with the final path component and updates the stored inode/dev. On delete-self, unmount, or move-self events, it autoremove-deletes the rule through `audit_del_rule()`.

## State and persistence behavior
State is in-memory and tied to fsnotify marks. The persistent user-visible effect is that audit rules with executable/path conditions continue matching the current inode for a path as it is recreated or moved into place, and are removed when the watched container itself disappears.

## Dependencies and integration points
This file depends on fsnotify backend APIs, path lookup (`kern_path_parent`), audit rule deletion/logging, audit filters, LSM/security includes, and path comparison from `auditfilter.c`. `audit_watch.c` calls `audit_dupe_exe()` and `audit_exe_compare()` using these mark helpers.

## Risks and invariants
Path validation and dentry comparison are important: the mark lives on the parent directory but stores child inode/dev. If name comparison is wrong, unrelated events can retarget rules. Autoremove calls into the rule engine from fsnotify context, so locking and GFP choices (`GFP_NOFS` for logging) must avoid filesystem recursion. Mark memory ownership must leave `path` attached exactly once or cleared on attach failure.

## Test signals
Tests should cover `AUDIT_EXE` rules for an executable path, replacement by rename, deletion and recreation, parent directory move/delete/unmount, duplicate exe rule copying, and rule deletion cleanup. Fault injection for allocation and fsnotify mark attach failures is useful.
