# sources/distributed-fs/ceph-client/fs/notify/fsnotify.c

## Purpose

`fsnotify.c` is the central VFS notification dispatcher. It clears marks during object teardown, maintains child dentry flags for parent watches, determines when parent/name context is required, merges mark lists by group priority, applies ignore masks, dispatches events to group operations, handles permission-event short-circuiting, and initializes global fsnotify connector infrastructure.

## Important APIs, Types, and Functions

Exported or externally used functions include `__fsnotify_inode_delete()`, `__fsnotify_vfsmount_delete()`, `__fsnotify_mntns_delete()`, `fsnotify_sb_delete()`, `fsnotify_sb_free()`, `fsnotify_set_children_dentry_flags()`, `__fsnotify_parent()`, `fsnotify()`, `fsnotify_open_perm_and_set_mode()`, and `fsnotify_mnt()`. Important internal helpers include `fsnotify_event_needs_parent()`, `fsnotify_object_watched()`, `fsnotify_handle_inode_event()`, `send_to_group()`, `fsnotify_iter_select_report_types()`, and `fsnotify_iter_next()`.

## Control Flow

VFS hook wrappers call `__fsnotify_parent()` or `fsnotify()`. The parent helper fast-paths when no parent/object masks are interested, otherwise obtains the parent, snapshots the child name if needed, adds `FS_EVENT_ON_CHILD` when appropriate, and calls `fsnotify()`. The dispatcher determines primary and secondary inode roles for dirent, rename, and child events, fast-paths when no connector lists or masks are present, enters `fsnotify_mark_srcu`, seeds iterators from sb, mount, inode, parent/second inode, and mount namespace connectors, and repeatedly selects all marks for the highest-priority current group. `send_to_group()` clears non-surviving ignore masks on modify, combines mark masks and effective ignore masks, and invokes either `group->ops->handle_event` or the inode-event fallback. Permission-event errors stop iteration and return to the VFS.

## State and Persistence Behavior

The file mutates object-level masks only indirectly through mark clearing and relies on mark connector state maintained by `mark.c`. It updates dentry `DCACHE_FSNOTIFY_PARENT_WATCHED` flags eagerly when a directory starts watching children and clears stale positives lazily on later child events. Superblock deletion flushes inodes, clears sb marks, waits for watched-object counters to drop, and warns if priority watchers remain. Open permission setup stores `FMODE_NONOTIFY*` optimization bits on files based on current priority watchers and object masks.

## Dependencies and Integration Points

It depends on VFS dentries/inodes/mounts/superblocks, SRCU-protected fsnotify connectors, `fsnotify_backend.h`, permission event mode bits, and mount namespace data. It integrates with fanotify/inotify/dnotify group ops, mark lifecycle helpers in `mark.c`, group queues in `notification.c`, and filesystem teardown paths.

## Risks and Edge Cases

The complex part is preserving delivery semantics while optimizing fast paths. Parent/name context must not leak special-file access/modify events through parent watches. Rename handling only reports same-parent rename to dnotify's inode-event fallback. Ignore mask handling must combine marks from the same group across object types so one mark's ignore mask suppresses another mark's positive interest. SRCU must be held while walking connector lists unless permission waiting pins marks and temporarily drops SRCU.

## Test Signals

Signals include inotify and fanotify selftests for parent watches, child name reporting, ignored masks, modify clearing, rename cookies, unmount events, superblock/mount marks, mount namespace events, and permission denial. VFS teardown tests should verify no lingering marks or watched-object counters after inode eviction, unmount, and namespace destruction. Performance-sensitive tests should exercise the no-watch fast path.
