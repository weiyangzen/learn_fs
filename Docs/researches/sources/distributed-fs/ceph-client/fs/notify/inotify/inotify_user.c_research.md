# sources/distributed-fs/ceph-client/fs/notify/inotify/inotify_user.c

## Purpose

`inotify_user.c` implements the userspace inotify syscall and file descriptor ABI. It creates inotify groups, exposes poll/read/ioctl/release operations, resolves watched paths, allocates and updates inode marks, manages watch descriptors in an IDR, enforces per-user instance/watch limits, and initializes inotify sysctls and slab caches.

## Important APIs, Types, and Functions

Syscalls are `inotify_init1`, `inotify_init`, `inotify_add_watch`, and `inotify_rm_watch`. File operations include `inotify_poll()`, `inotify_read()`, `inotify_ioctl()`, and `inotify_release()`. Event read helpers are `get_one_event()`, `round_event_name_len()`, and `copy_event_to_user()`. Watch management helpers include `inotify_find_inode()`, `inotify_add_to_idr()`, `inotify_idr_find()`, `inotify_remove_from_idr()`, `inotify_update_existing_watch()`, `inotify_new_watch()`, and `inotify_update_watch()`. Setup uses `inotify_new_group()`, `do_inotify_init()`, and `inotify_user_setup()`.

## Control Flow

`inotify_init*()` validates fd flags, allocates a group with overflow event, initializes the IDR and ucounts, and returns an anon inode fd. `inotify_add_watch()` validates mask bits and fd type, resolves the path with requested follow/onlydir behavior, checks read permission and LSM notification permission, then updates an existing mark or creates a new one. New watches allocate an inotify mark, reserve a cyclic wd in the IDR, increment watch ucount, and attach an inode mark. `read()` loops over queued events, blocks unless nonblocking or interrupted, copies records with padded names, and destroys events after copy. `rm_watch()` finds the wd, destroys the mark, and drops the lookup reference.

## State and Persistence Behavior

An inotify fd owns an fsnotify group, overflow event, memcg reference, ucounts, and an IDR mapping watch descriptors to inode marks. Marks store masks/flags and a wd. Queued events persist until read, flush, or group destruction. Sysctls control max user instances, max user watches, and max queued events; defaults are set during init based on memory and constants. `INOTIFY_IOC_SETNEXTWD` can set the IDR cursor for checkpoint/restore builds.

## Dependencies and Integration Points

It depends on anon inodes, fd helpers, path lookup, VFS permissions, LSM `security_path_notify()`, fsnotify mark APIs, IDR, ucounts, memcg, sysctl, poll/wait queues, user copy, and fdinfo. It integrates with `inotify_fsnotify.c` through the shared group ops and mark/event types.

## Risks and Edge Cases

Watch descriptor lifetime and refcounting are the delicate parts: the IDR holds a mark reference, lookups take another, and removal must invalidate `wd` before delivery can use it. Updating a watch must handle replace versus `IN_MASK_ADD`, `IN_MASK_CREATE`, recalc masks when bits are dropped or newly needed, and reject incompatible flag combinations. Read must return partial success if at least one event copied, except for `EFAULT`. Name padding must match the inotify ABI.

## Test Signals

Signals include syscall flag validation, adding/removing/updating watches, `IN_MASK_ADD` and `IN_MASK_CREATE`, `IN_DONT_FOLLOW`, `IN_ONLYDIR`, read buffer too small, blocking/nonblocking reads, `FIONREAD`, checkpoint restore wd cursor, sysctl limits, per-user watch exhaustion, and fd close cleanup. Race tests should remove watches during event delivery and path teardown.
