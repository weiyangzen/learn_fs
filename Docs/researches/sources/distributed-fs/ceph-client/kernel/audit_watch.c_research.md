# sources/distributed-fs/ceph-client/kernel/audit_watch.c

## Purpose
`audit_watch.c` implements non-recursive path watches for audit rules. It tracks a watched child path through an fsnotify mark on the parent directory, updates inode/device rule matching data when the child is created, moved, or deleted, and removes associated rules when the watched parent disappears.

## Important APIs, types, and functions
`struct audit_watch` stores refcount, device, path, inode, parent pointer, parent watch-list node, and rule-list anchor. `struct audit_parent` stores all watches attached to a parent inode and the embedded fsnotify mark. Public helpers include `audit_to_watch()`, `audit_add_watch()`, `audit_remove_watch_rule()`, `audit_watch_path()`, `audit_watch_compare()`, `audit_get_watch()`, `audit_put_watch()`, plus executable helpers `audit_dupe_exe()` and `audit_exe_compare()`.

Important internals include `audit_init_parent()`, `audit_init_watch()`, `audit_find_parent()`, `audit_add_to_parent()`, `audit_get_nd()`, `audit_update_watch()`, `audit_remove_parent_watches()`, and `audit_watch_handle_event()`.

## Control flow
Rule parsing calls `audit_to_watch()`, which validates absolute non-directory paths, allowed filter lists, equality operation, and mutual exclusivity with inode/tree/watch fields. Rule insertion calls `audit_add_watch()` while holding `audit_filter_mutex`; it takes a temporary watch reference, drops the mutex to resolve the parent path, reacquires the mutex, finds or creates a parent fsnotify mark, attaches the rule to an existing same-path watch or adds a new watch, and chooses the inode hash bucket for the rule list.

Fsnotify events on the parent call `audit_watch_handle_event()`. Create/move-to events update matching watches with the new inode/dev. Delete/move-from invalidates inode/dev and first runs inode filtering for the current context so pending events are not missed. Delete-self/unmount/move-self removes all watches and rules for that parent. Updating a watch duplicates affected rules, swaps RCU list entries, moves the rule to the new inode hash bucket, removes stale exe marks, and RCU-frees old entries.

## State and persistence behavior
Watch state is in-memory and rule-backed. The watched path string remains the stable user rule identity, while inode/dev fields are dynamic matching accelerators. Parent marks live until fsnotify reports `FS_IGNORED` or all watches are removed. Rules are persisted only in kernel memory until userspace deletes or reloads them.

## Dependencies and integration points
The file depends on fsnotify backend APIs, path lookup, audit filter mutex/list structures, inode hash buckets from `audit.c`, RCU rule freeing from `auditfilter.c`, path comparison helpers, and fsnotify mark helpers from `audit_fsnotify.c` for executable filters.

## Risks and invariants
The rule update path must copy-and-replace entries instead of mutating RCU-visible structures in place. Watch and parent refcounts must balance across shared same-path watches. The function deliberately drops `audit_filter_mutex` around path lookup to avoid blocking under the global filter lock; callers expect it locked again on return. Name comparison errors can update the wrong watch. Removing parent watches must also remove exe marks associated with those rules.

## Test signals
Add/delete audit watch rules, create/delete/rename the watched file, replace it with a new inode, delete/unmount/move the parent, add multiple rules for the same path, and delete rules while events occur. Verify inode hash matching after replacement and RCU safety with lockdep/KASAN/KCSAN.
