# sources/distributed-fs/ceph-client/fs/notify/inotify/inotify_fsnotify.c

## Purpose

`inotify_fsnotify.c` adapts generic fsnotify events into inotify queue records. It allocates inotify event payloads, merges duplicate consecutive events, handles one-shot watch destruction, emits `IN_IGNORED`, removes watch descriptors from the IDR during mark teardown, and supplies the `fsnotify_ops` implementation for inotify groups.

## Important APIs, Types, and Functions

The main backend function is `inotify_handle_inode_event()`. Event coalescing is implemented by `event_compare()` and `inotify_merge()`. Teardown callbacks are `inotify_freeing_mark()`, `inotify_free_group_priv()`, `inotify_free_event()`, and `inotify_free_mark()`. `inotify_fsnotify_ops` binds these callbacks to the generic fsnotify group.

## Control Flow

When fsnotify dispatches an inode event to an inotify mark, `inotify_handle_inode_event()` calculates the optional name length, reads the mark's watch descriptor, skips delivery if the wd is invalid, charges allocation to the monitoring group's memcg, fills an `inotify_event_info`, and queues it with `fsnotify_add_event()`. Consecutive identical non-ignored events may merge. If allocation fails, the group queues an overflow event. For `IN_ONESHOT`, the mark is destroyed after queueing the event. When a mark is freed, `inotify_freeing_mark()` queues `IN_IGNORED` and removes the wd from the IDR.

## State and Persistence Behavior

Queued event state includes mask, wd, rename cookie, name length, and name bytes. Group-private state includes the IDR of watch descriptors and ucount references. Event memory is freed after userspace reads or queue flush. Mark memory is returned to `inotify_inode_mark_cachep` only after generic mark lifetime rules allow final free.

## Dependencies and Integration Points

It depends on generic fsnotify queue APIs, inotify private types, memcg accounting, inode mark flags, IDR cleanup in `inotify_user.c`, and ucounts. It is invoked from the generic fsnotify dispatch fallback through `.handle_inode_event`.

## Risks and Edge Cases

Important edge cases are racing mark detach, invalid wd suppression, memory allocation failure producing overflow rather than silent loss, preserving historical lack of `IN_ISDIR` on `IN_MOVE_SELF`/`IN_DELETE_SELF`, and avoiding merge of ignored events. One-shot destruction must not invalidate an event already queued for userspace.

## Test Signals

Inotify selftests should verify duplicate event coalescing, overflow on small queues or forced allocation failure, one-shot removal, `IN_IGNORED`, rename cookies, name padding, and wd reuse/removal races. Memcg accounting is indirectly exercised by creating watchers from constrained cgroups.
