# sources/distributed-fs/ceph-client/fs/notify/fdinfo.c

## Purpose

`fdinfo.c` emits procfs fdinfo diagnostics for inotify and fanotify file descriptors. It walks a group's fsnotify marks and formats watch descriptors, masks, ignored masks, mark flags, object identifiers, and optional exportfs file handles for `/proc/<pid>/fdinfo/<fd>`.

## Important APIs, Types, and Functions

Public functions are `inotify_show_fdinfo()` and `fanotify_show_fdinfo()` when the respective configs are enabled. Internal helpers are `show_fdinfo()`, `show_mark_fhandle()`, `inotify_fdinfo()`, and `fanotify_fdinfo()`. The output covers inode marks, vfsmount marks, superblock marks, and mount-namespace marks, using `inotify_mark_user_mask()` and `fanotify_mark_user_flags()` to convert internal flags back to user-visible bits.

## Control Flow

`show_fdinfo()` takes the group's mark mutex, iterates `group->marks_list`, invokes the backend-specific formatter, and stops if the seq file overflows. `show_mark_fhandle()` tries to take the superblock shared unmount lock, encodes a file handle with `exportfs_encode_fid()`, and appends hex bytes if encoding succeeds. Inotify only reports inode marks with wd/ino/sdev/mask. Fanotify first emits group init/event flags, then reports each mark according to connector type.

## State and Persistence Behavior

The file does not own state. It observes live fsnotify group marks under `group->mark_mutex`, grabs inode references with `igrab()` while formatting inode objects, and drops them with `iput()`. File-handle bytes are generated on demand and are not cached. Seq output is diagnostic and reflects a snapshot that may change immediately after the mutex is released.

## Dependencies and Integration Points

It depends on procfs, seq files, exportfs, fsnotify connectors, inotify/fanotify private headers, mount internals, and inode/superblock lifetime helpers. It is reached through the `.show_fdinfo` file operation in fanotify and inotify anon inode descriptors.

## Risks and Edge Cases

The code must avoid racing object teardown while presenting diagnostics. Inode connector objects may no longer have an inode reference, so `igrab()` failure is handled by skipping output. Exportfs handle encoding may fail, be unsupported, or be unsafe during unmount, so the handle field is optional. Seq overflow stops iteration without corrupting locking.

## Test Signals

Useful tests open inotify/fanotify fds, add inode/mount/sb/mntns marks, and compare `/proc/self/fdinfo` fields. Exportfs-capable and non-exportfs filesystems should both be covered. Regression checks should include mark removal during fdinfo reads and fanotify groups with ignored masks, evictable marks, and mount namespace marks.
