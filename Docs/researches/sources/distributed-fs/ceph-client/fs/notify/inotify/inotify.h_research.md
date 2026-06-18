# sources/distributed-fs/ceph-client/fs/notify/inotify/inotify.h

## Purpose

`inotify.h` is the private inotify backend header. It defines the queued inotify event object, inode mark extension carrying the watch descriptor, user-mask conversion helpers, backend operation declarations, and ucounts helpers for instance/watch limits.

## Important APIs, Types, and Functions

Important types are `struct inotify_event_info` and `struct inotify_inode_mark`. `INOTIFY_E()` casts generic fsnotify events to inotify events. `INOTIFY_USER_MASK` identifies event bits exposed to userspace. `inotify_mark_user_mask()` maps internal fsnotify mask/flags back to userspace `IN_*` bits. External declarations include `inotify_ignored_and_remove_idr()`, `inotify_handle_inode_event()`, `inotify_fsnotify_ops`, and `inotify_inode_mark_cachep`. Ucount helpers are `dec_inotify_instances()`, `inc_inotify_watches()`, and `dec_inotify_watches()`.

## Control Flow

This header has no standalone control flow. Its helpers are called while creating fdinfo output, allocating events, removing marks, and enforcing per-user limits.

## State and Persistence Behavior

`struct inotify_event_info` instances live on a group's notification queue until read or flushed. `struct inotify_inode_mark` instances live while a watch descriptor is present in the group IDR and a mark is attached to an inode. The `wd` can become `-1` during teardown to prevent delivery with invalid descriptors.

## Dependencies and Integration Points

It depends on generic fsnotify backend structures, public inotify UAPI constants, slab cache declarations, and ucounts. It is shared by `inotify_fsnotify.c`, `inotify_user.c`, and `fdinfo.c`.

## Risks and Edge Cases

The user-mask helper must expose only stable userspace bits and synthesize flags like `IN_EXCL_UNLINK` and `IN_ONESHOT` from fsnotify mark flags. Internal-only bits such as `FS_EVENT_ON_CHILD` must not leak to userspace. Watch descriptor invalidation must be visible to event delivery.

## Test Signals

Signals include fdinfo mask output, one-shot watch behavior, exclusive unlink behavior, ignored event emission, and build coverage with inotify enabled.
