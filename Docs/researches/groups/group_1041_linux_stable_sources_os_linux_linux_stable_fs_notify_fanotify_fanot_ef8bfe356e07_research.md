# Group Research: group_1041_linux_stable_sources_os_linux_linux_stable_fs_notify_fanotify_fanot_ef8bfe356e07

Scope: `Docs/research_subset_a.md`; all listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/fanotify/fanotify.h -->
# File Research: sources/os/linux/linux-stable/fs/notify/fanotify/fanotify.h

## Summary
Internal fanotify header defining event layouts, file-handle storage, name/fid record packing, permission-event state, mark metadata, and helper accessors used by fanotify event production and userspace copying.

## Main Types
- `struct fanotify_fh`: compact file-handle header with inline or external buffer support.
- `struct fanotify_info`: variable-length layout for old/new directory fids, child fid, and names.
- `struct fanotify_event` plus concrete event types: fid, name, path, permission path, overflow, fs-error, and mount events.
- `struct fanotify_perm_event`: permission/pre-content event state, fd, response, optional range, and audit-rule response info.
- `struct fanotify_mark`: fsnotify mark extension carrying cached fsid.

## Important Details
`fanotify_info` has strict append order: dir fh, second dir fh, file fh, first name, second name. Event type bits share storage with a merge hash. Error events always report an object fh even when invalid. Permission events are not hash-merged. Mark user flags translate internal fsnotify mark flags back to fanotify ABI flags.

## Risks
The variable record offsets and inline/external fh handling are ABI-sensitive because `fanotify_user.c` copies these structures into userspace info records. The ordered setters rely on callers building `fanotify_info` in exactly the documented sequence. Permission-event state transitions must match the read/write/release paths in `fanotify_user.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/fanotify/fanotify.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/fanotify/fanotify_user.c -->
# File Research: sources/os/linux/linux-stable/fs/notify/fanotify/fanotify_user.c

## Summary
Implements the userspace fanotify API: `fanotify_init`, `fanotify_mark`, fanotify fd operations, event formatting, permission-event response handling, mark accounting, sysctl limits, and init-time cache setup.

## Main APIs
- Syscalls: `fanotify_init`, `fanotify_mark`, compat/split-arg variants.
- File operations: `fanotify_read()`, `fanotify_write()`, `fanotify_poll()`, `fanotify_ioctl()`, `fanotify_release()`.
- Mark operations: add, remove, flush, fsid/fid validation, mark flag updates, error-event pool initialization.
- Event copy helpers for metadata, FID/DFID/name records, pidfd records, error records, range records, and mount-id records.
- Permission machinery: response validation, access list handling, wait wakeups, and timeout watchdog warnings.

## Behavior
`fanotify_init` validates privilege, class, FID/name/pidfd/mount-reporting combinations, event fd flags, queue limits, audit capability, and creates an anon inode backed by an fsnotify group. `fanotify_mark` resolves the target object, validates mark type and event mask, enforces namespace capabilities and LSM checks, verifies filesystem fid/fsid support when required, and adds/removes/flushes fsnotify marks. Reads dequeue one event at a time, copy ABI metadata and info records, install event fds/pidfds, and move permission events to an access-list until userspace writes a response.

## State and Synchronization
The notification queue and permission access-list are protected by `group->notification_lock`. Group mark changes use fsnotify group locking. User limits are enforced with `ucounts`; event memory is charged to the creator memcg. Permission groups can be linked into a global watchdog list protected by `perm_group_lock`. Error events use a per-group mempool initialized only when `FAN_FS_ERROR` is requested.

## Risks
This file is fanotify’s ABI choke point. Flag validation is intentionally strict: mount namespace events cannot mix with inode fid/fd modes, permission events require the right class, and rename reporting requires names. Permission-event cleanup must always wake waiters and avoid leaving access-list events unanswered. FID mode depends on stable filesystem export operations and fsid rules, especially weak fsids and btrfs subvolume checks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/fanotify/fanotify_user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/fdinfo.c -->
# File Research: sources/os/linux/linux-stable/fs/notify/fdinfo.c

## Summary
Implements `/proc/<pid>/fdinfo` reporting for inotify and fanotify file descriptors when procfs support is enabled.

## Main APIs
- `inotify_show_fdinfo()`.
- `fanotify_show_fdinfo()`.
- Internal shared `show_fdinfo()` mark iterator.

## Behavior
The code locks the fsnotify group, walks `group->marks_list`, and emits per-mark details. Inotify output reports watch descriptor, inode number, superblock device, user-visible mask, and optionally an export file handle. Fanotify output reports group init flags and event flags, then inode, mount, superblock, or mount-namespace mark details with masks and ignore masks.

## Important Details
File handles are emitted only when `CONFIG_EXPORTFS` can encode the inode. Encoding is done under a shared superblock lock. Fanotify mark flags are converted back to user ABI flags through `fanotify_mark_user_flags()`.

## Risks
This is observability code but still depends on mark connector validity while holding the group lock. Output format is user-visible proc ABI, so field names and ordering should be treated carefully.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/fdinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/fdinfo.h -->
# File Research: sources/os/linux/linux-stable/fs/notify/fdinfo.h

## Summary
Small header declaring fdinfo display hooks for inotify and fanotify.

## Contents
Declares `inotify_show_fdinfo()` and `fanotify_show_fdinfo()` under `CONFIG_PROC_FS` and the corresponding feature configs. When procfs is disabled, both names are defined as `NULL`.

## Risks
The header is intentionally minimal. Callers use these symbols in file operations, so the config-dependent `NULL` fallback must remain compatible with file operation initialization.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/fdinfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/fsnotify.c -->
# File Research: sources/os/linux/linux-stable/fs/notify/fsnotify.c

## Summary
Core fsnotify dispatcher and object cleanup implementation. It routes VFS events to interested fsnotify groups across inode, parent, mount, superblock, and mount-namespace marks.

## Main APIs
- Object cleanup: `__fsnotify_inode_delete()`, `__fsnotify_vfsmount_delete()`, `__fsnotify_mntns_delete()`, `fsnotify_sb_delete()`, `fsnotify_sb_free()`.
- Parent/name routing: `fsnotify_set_children_dentry_flags()`, `__fsnotify_parent()`.
- Main dispatcher: `fsnotify()`.
- Permission optimization: `fsnotify_open_perm_and_set_mode()`.
- Mount namespace events: `fsnotify_mnt()`.
- Init: `fsnotify_init()`.

## Behavior
The dispatcher first uses aggregate object masks to avoid SRCU traversal when no mark can match. When marks exist, it builds a multi-head iterator over all relevant mark lists, selects one group at a time by priority, applies ignore masks, and invokes either the group `handle_event` callback or inode-event fallback. Parent/name info is included when a parent watches children or when inode/sb/mount marks require parent/name reporting.

## State and Synchronization
Mark list traversal is protected by `fsnotify_mark_srcu`. Dentry child interest is cached in `DCACHE_FSNOTIFY_PARENT_WATCHED` and cleared lazily. Superblock teardown clears marks, sends unmount notifications, and waits for watched-object counters to drain. Permission-open optimization stores nonotify mode bits in the opened file based on current watcher masks.

## Risks
The mark iterator’s priority and grouping rules are central to fanotify permission ordering and ignore-mask semantics. Parent/name reporting has security-sensitive filtering for special files. Permission events may abort further delivery when a high-priority listener denies access, so ordering and return handling must remain exact.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/fsnotify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/fsnotify.h -->
# File Research: sources/os/linux/linux-stable/fs/notify/fsnotify.h

## Summary
Internal fsnotify header for connector accessors, mark cleanup helpers, SRCU state, group comparison, and connector cache initialization.

## Contents
Defines `fsnotify_connp_t`, typed connector-to-object helpers for inode, mount, superblock, and mount namespace, object-to-superblock helpers, and inline clear-mark helpers for each object type.

## Important Details
The header exposes `fsnotify_mark_srcu`, `fsnotify_compare_groups()`, `fsnotify_unmount_inodes()`, `fsnotify_destroy_marks()`, and `fsnotify_set_children_dentry_flags()`. Superblock marks are reached through optional `fsnotify_sb_info`.

## Risks
These helpers encode the connector object model used by `mark.c` and `fsnotify.c`. Incorrect object type handling can corrupt mark lists or miss cleanup during inode eviction, mount teardown, superblock shutdown, or namespace destruction.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/fsnotify.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/group.c -->
# File Research: sources/os/linux/linux-stable/fs/notify/group.c

## Summary
Implements fsnotify group allocation, teardown, reference counting, queue shutdown, and fasync helper support.

## Main APIs
- `fsnotify_alloc_group()`.
- `fsnotify_destroy_group()`.
- `fsnotify_group_stop_queueing()`.
- `fsnotify_get_group()`, `fsnotify_put_group()`.
- `fsnotify_fasync()`.

## Behavior
A group owns a notification queue, mark list, mark mutex, wait queue, optional overflow event, private backend state, memcg reference, and refcount. Destruction stops queueing, clears all marks, waits for user-wait-pinned marks, waits for deferred mark destruction, flushes notifications, frees the overflow event, and drops the group reference.

## State and Synchronization
`notification_lock` protects queue shutdown and queue state. `mark_mutex` protects `marks_list` and group-private mark state. Refcount finalization calls backend `free_group_priv`, releases memcg, destroys the mutex, and frees the group.

## Risks
Group teardown ordering matters because fanotify permission events can pin marks while waiting for userspace. Queue shutdown must happen before final flush so no new events appear after cleanup starts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/group.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/inotify/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/notify/inotify/Kconfig

## Summary
Kconfig entry for userspace inotify support.

## Contents
Defines `INOTIFY_USER` as a default-enabled bool, selects `FSNOTIFY`, and describes inotify fd-based file and directory event monitoring with poll/select support, one-shot watches, and unmount notifications.

## Risks
Disabling this removes the userspace inotify syscalls and associated support objects while the lower fsnotify infrastructure can still be selected by other clients.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/inotify/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/inotify/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/notify/inotify/Makefile

## Summary
Build rule for inotify userspace support.

## Contents
When `CONFIG_INOTIFY_USER` is enabled, builds `inotify_fsnotify.o` and `inotify_user.o`.

## Risks
The split matches backend event handling in `inotify_fsnotify.c` and syscall/fd/mark management in `inotify_user.c`; both are required for a working userspace inotify implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/inotify/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/inotify/inotify.h -->
# File Research: sources/os/linux/linux-stable/fs/notify/inotify/inotify.h

## Summary
Internal inotify header defining event and mark structures plus shared helpers and backend declarations.

## Main Types
- `struct inotify_event_info`: queued event with mask, watch descriptor, rename cookie, and optional name.
- `struct inotify_inode_mark`: fsnotify mark extension carrying the watch descriptor.

## Important Details
`INOTIFY_USER_MASK` limits user-visible watch/event bits to `IN_ALL_EVENTS`. `inotify_mark_user_mask()` reconstructs user-visible flags such as `IN_EXCL_UNLINK` and `IN_ONESHOT`. The header declares the fsnotify ops table, mark cache, event handler, and IDR cleanup helper.

## Risks
Inotify relies on bit layout compatibility between `IN_*` and `FS_*` constants, checked in `inotify_user.c`. Watch descriptor lifetime depends on keeping the IDR and mark refcounts aligned.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/inotify/inotify.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/inotify/inotify_fsnotify.c -->
# File Research: sources/os/linux/linux-stable/fs/notify/inotify/inotify_fsnotify.c

## Summary
Inotify backend implementation for fsnotify event delivery, event merging, backend cleanup, and mark/event freeing.

## Main APIs
- `inotify_handle_inode_event()`.
- `inotify_fsnotify_ops`.
- Internal queue merge and cleanup callbacks.

## Behavior
On an interested inode event, the backend allocates an `inotify_event_info`, copies the watch descriptor, mask, cookie, and optional name, and queues it to the group. Adjacent duplicate events are merged when mask, watch descriptor, name length, and name match, except `IN_IGNORED`. One-shot marks are destroyed after event delivery.

## State and Synchronization
The watch descriptor is read with `READ_ONCE()` because mark destruction can race with event handling. Allocations are charged to the listener group memcg rather than the event-generating task. Group private cleanup destroys the IDR and decrements the inotify instance ucount.

## Risks
A mark with `wd == -1` must not generate user events. Allocation failure is converted to queue overflow so userspace can detect loss. `IN_MOVE_SELF` and `IN_DELETE_SELF` deliberately suppress `IN_ISDIR` for compatibility.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/inotify/inotify_fsnotify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/inotify/inotify_user.c -->
# File Research: sources/os/linux/linux-stable/fs/notify/inotify/inotify_user.c

## Summary
Implements userspace inotify syscalls, anon inode file operations, watch descriptor IDR management, per-user limits, sysctls, and init-time cache setup.

## Main APIs
- Syscalls: `inotify_init`, `inotify_init1`, `inotify_add_watch`, `inotify_rm_watch`.
- File operations: read, poll, ioctl, release, fasync.
- Watch management: new watch, existing watch update, IDR add/find/remove, ignored-event cleanup.
- Init: `inotify_user_setup()`.

## Behavior
`inotify_init*` creates an fsnotify group with a preallocated overflow event and per-user instance accounting. `inotify_add_watch` validates mask bits, resolves the path, checks read permission and `security_path_notify()`, then creates or updates an inode mark. Reads dequeue events, copy `struct inotify_event` plus padded name bytes to userspace, and destroy each event after copying. `inotify_rm_watch` finds the mark by watch descriptor and destroys it.

## State and Synchronization
The group IDR maps watch descriptors to `inotify_inode_mark` objects and is protected by `idr_lock`. Group mark updates use `fsnotify_group_lock()`. Watch and instance limits use ucounts. Queue reads use `notification_lock` and `notification_waitq`.

## Risks
IDR and mark refcounts are tightly coupled: removing a descriptor drops the IDR-held mark reference and sets `wd = -1`. `IN_MASK_ADD` and `IN_MASK_CREATE` are mutually exclusive. Existing watch replacement must recalculate inode masks when bits are dropped or newly added.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/inotify/inotify_user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/mark.c -->
# File Research: sources/os/linux/linux-stable/fs/notify/mark.c

## Summary
Core fsnotify mark and connector lifetime implementation. It manages mark attachment, detachment, refcounts, connector allocation, object masks, inode pinning, watched-object accounting, SRCU-safe traversal, and deferred destruction.

## Main APIs
- Ref/lifetime: `fsnotify_get_mark()`, `fsnotify_put_mark()`, `fsnotify_free_mark()`, `fsnotify_destroy_mark()`.
- Add/find/clear: `fsnotify_add_mark_locked()`, `fsnotify_add_mark()`, `fsnotify_find_mark()`, `fsnotify_clear_marks_by_group()`, `fsnotify_destroy_marks()`.
- Permission wait support: `fsnotify_prepare_user_wait()`, `fsnotify_finish_user_wait()`.
- Superblock unmount support: `fsnotify_unmount_inodes()`.
- Init: `fsnotify_init_mark()`, `fsnotify_init_connector_caches()`.

## Behavior
Marks are attached to per-object connectors for inodes, mounts, superblocks, or mount namespaces. Connector lists are sorted by group priority and address so dispatch can merge mark lists by group. Recalculation updates aggregate object masks and manages inode references when any attached mark requires the inode to be pinned. Detachment removes the mark from the group list first, then leaves object-list removal to the final put path.

## State and Synchronization
Required lock ordering is `group->mark_mutex`, then `mark->lock`, then `connector->lock`. Object-list traversal is protected by `fsnotify_mark_srcu`. Mark and connector freeing is deferred through workqueues after SRCU grace periods. Superblocks track watched-object counters by priority to support teardown and permission fast paths.

## Risks
This is the most sensitive lifetime file in the fsnotify stack. Races among group destruction, object teardown, permission waits, and lockless event dispatch are handled by mark refs, group user-wait counters, SRCU, and deferred freeing. Any change to detach ordering, connector mask recalculation, or inode reference rules risks use-after-free, leaked inode pins, missed events, or unmount hangs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/mark.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/notification.c -->
# File Research: sources/os/linux/linux-stable/fs/notify/notification.c

## Summary
Implements fsnotify notification queue primitives, overflow handling, queue insertion/removal, event destruction, flushing, and rename cookie generation.

## Main APIs
- `fsnotify_get_cookie()`.
- `fsnotify_insert_event()`.
- `fsnotify_destroy_event()`.
- `fsnotify_peek_first_event()`, `fsnotify_remove_first_event()`, `fsnotify_remove_queued_event()`.
- `fsnotify_flush_notify()`.

## Behavior
Events are queued on a group notification list under `notification_lock`. Backends may supply a merge callback and an insert callback. If the group is shutting down or the queue exceeds `max_events`, the group overflow event is queued once. Successful insertion wakes readers and sends async notification via fasync.

## State and Synchronization
`group->q_len` tracks queue length. Overflow events are per-group and are never freed through normal event destruction. Event destruction checks that the event is not still queued before invoking backend `free_event`.

## Risks
Queue overflow semantics are user-visible. The overflow event must not be double-queued or freed. Permission events may be removed and freed by different CPUs, so the queued-list sanity check uses locking when needed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/notification.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nsfs.c -->
# File Research: sources/os/linux/linux-stable/fs/nsfs.c

## Summary
Implements `nsfs`, the pseudo-filesystem backing namespace file descriptors, `/proc/<pid>/ns/*` paths, namespace ioctls, namespace export file handles, and stashed namespace dentries.

## Main APIs
- Path/open helpers: `nsfs_get_root()`, `ns_get_path_cb()`, `ns_get_path()`, `open_namespace_file()`, `open_namespace()`, `open_related_ns()`.
- Ioctls: namespace owner/parent/type/id queries, pid translation queries, mount namespace info, next/previous mount namespace iteration.
- Identification helpers: `ns_get_name()`, `proc_ns_file()`, `ns_match()`, `is_current_namespace()`.
- Export operations: `nsfs_encode_fh()`, `nsfs_fh_to_dentry()`, export open/permission hooks.
- Init: `nsfs_init()`.

## Behavior
Namespace files are represented by stashed dentries and inodes whose private data is `struct ns_common`. Opening a namespace consumes or transfers namespace references into a path/file. Ioctls expose related namespaces, namespace IDs, owner uid for user namespaces, pid mappings for pid namespaces, and extensible mount namespace metadata. Export file handles encode namespace id, type, and inode number and can resolve back to dentries through the namespace tree with permission checks.

## State and Synchronization
The singleton `nsfs_mnt` hosts all namespace dentries. Inode eviction drops active namespace references and calls namespace-specific put. File-handle lookup uses RCU namespace-tree lookup and then obtains a namespace reference unless inactive. Mount namespace iteration can return a new fd plus optional info struct.

## Risks
Namespace handles are security-sensitive. `nsfs_fh_to_dentry()` restricts access to namespaces outside the caller’s view unless `may_see_all_namespaces()` permits it, and pid namespace handles reject dead current pid namespaces. Extensible ioctl size handling must preserve backward and forward compatibility.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nsfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/Kconfig

## Summary
Kconfig options for the legacy NTFS filesystem driver.

## Contents
Defines `NTFS_FS` as a tristate depending on NLS and iomap support, `NTFS_DEBUG` for extra checks and debug messages, and `NTFS_FS_POSIX_ACL` for Linux-only POSIX ACL support.

## Important Details
The help text identifies this as NTFS support for Windows NT/2000/XP/2003-era filesystems. Debug messages are disabled by default and can be enabled by boot/module option or `/proc/sys/fs/ntfs-debug`.

## Risks
The POSIX ACL option is explicitly Linux-only and ignored by Windows. Debug mode can add significant runtime overhead.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/Makefile

## Summary
Build rules for the NTFS kernel module.

## Contents
Builds `ntfs.o` when `CONFIG_NTFS_FS` is enabled and lists the component objects for address-space operations, attributes, collation, directories, files, indexes, inode/MFT handling, runlists, superblock, Unicode, allocation, logs, reparse points, compression, iomap, quota, object IDs, and block-device I/O.

## Important Details
`CONFIG_NTFS_DEBUG` adds `-DDEBUG` through `ccflags`.

## Risks
The object list defines the module composition; omitting any of these pieces would break major filesystem functionality such as metadata lookup, compression, or iomap I/O.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/aops.c -->
# File Research: sources/os/linux/linux-stable/fs/ntfs/aops.c

## Summary
Implements NTFS address-space operations for page-cache read, readahead, writeback, block mapping, swap activation, and MFT-specific writeback integration.

## Main APIs
- `ntfs_read_folio()`.
- `ntfs_bmap()`.
- `ntfs_readahead()`.
- `ntfs_writepages()`.
- `ntfs_swap_activate()`.
- Address-space operation tables `ntfs_aops` and `ntfs_mft_aops`.

## Behavior
Reads use iomap bio reads with a custom end-io handler that zeros bytes beyond initialized size inside partially initialized folio ranges. Encrypted attributes are rejected because EFS is unsupported; compressed nonresident data is delegated to the NTFS compression reader. Readahead is skipped for resident and compressed files. Writeback uses iomap for nonresident attributes unless the volume is shutting down or the file is encrypted.

## State and Synchronization
`ntfs_bmap()` reads initialized size under `ni->size_lock`, then maps VCN to LCN under `ni->runlist.lock`. It returns zero for holes, sparse/uninitialized ranges, unsupported attribute types, and errors. Iomap operation tables are supplied by NTFS read/writeback code in neighboring files.

## Risks
`bmap()` cannot distinguish block zero from hole/error, which is called out for `$Boot`. Initialized-size handling is important to avoid exposing stale data. Encrypted and compressed paths must stay excluded from generic iomap paths unless full support exists.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ntfs/aops.c -->