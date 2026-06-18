<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsnotify_backend.h -->
# sources/distributed-fs/ceph-client/include/linux/fsnotify_backend.h

Purpose: Defines the internal backend contract for Linux filesystem notifications. It centralizes event masks, group priorities, event payload typing, mark storage, and public helpers used by VFS hooks and notification backends such as inotify, dnotify, and fanotify.

Important APIs/types/functions: Event masks include `FS_ACCESS`, `FS_MODIFY`, directory entry events, mount namespace events, permission events, `FS_ERROR`, `FS_Q_OVERFLOW`, and reporting flags such as `FS_EVENT_ON_CHILD` and `FS_ISDIR`. Core types are `fsnotify_ops`, `fsnotify_group`, `fsnotify_event`, `fsnotify_mark`, `fsnotify_mark_connector`, `fsnotify_sb_info`, `fsnotify_iter_info`, `fs_error_report`, `file_range`, and `fsnotify_mnt`. The exported surface includes `fsnotify()`, `__fsnotify_parent()`, deletion/free hooks, group lifecycle helpers, event queue helpers, mark add/find/destroy helpers, and `fsnotify_pre_content()`.

Control flow: VFS call sites pass typed event data into `fsnotify()`. The core resolves inode/dentry/path/superblock/mount data using inline accessors, walks matching marks via `fsnotify_iter_info`, applies mark and ignore masks, and dispatches to `fsnotify_ops`. Backend groups queue userspace events through `fsnotify_insert_event()` or implement direct inode handling.

State and persistence behavior: State is in memory: groups hold notification queues, wait queues, fasync state, max queue length, shutdown state, backend-private data, and all marks. Marks are refcounted, protected by group mutexes, mark locks, connector locks, and SRCU-delayed destruction. Superblocks lazily hold watched-object counters by priority.

Dependencies and integration points: Depends on VFS objects, dentries, paths, mount namespaces, refcounts, IDR, mempools, memcg, user namespaces, and nofs allocation scope. Integrates with inode eviction, superblock teardown, mount teardown, dcache parent watched flags, fanotify permission flows, and inotify ID allocation.

Risks: Mask bit overloading (`FS_IN_IGNORED` versus `FS_ERROR`) is backend-specific. Incorrect locking can deadlock reclaim or race mark teardown. Ignore masks have legacy semantics that differ from canonical flag-aware masks. Queue overflow handling depends on a valid group overflow event. Stubbed `!CONFIG_FSNOTIFY` paths silently return success/zero.

Test signals: Exercise inotify/fanotify create, delete, rename, mount, unmount, overflow, child-watch, and permission events; verify dentry parent watched flag updates; run lockdep and KCSAN around mark add/remove; test fanotify pre-content/content permission behavior; build both `CONFIG_FSNOTIFY=y` and disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsnotify_backend.h -->
