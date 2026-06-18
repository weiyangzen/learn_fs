# Group Research: group_799_linux_sources_os_linux_linux_fs_notify_fanotify_fanotify_h_sources_o_63bbccbe82da

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/fanotify/fanotify.h -->
# File Research: sources/os/linux/linux/fs/notify/fanotify/fanotify.h

## Role

This header defines fanotify's private event, file-handle, name, permission, mount-event, and mark structures plus compact inline helpers used by fanotify implementation files.

It sits above the generic fsnotify backend and translates between generic `struct fsnotify_event` / `struct fsnotify_mark` objects and fanotify-specific payloads.

## File Handle And Name Payloads

`struct fanotify_fh` is a fixed-size file-handle header with type, length, flags, and alignment padding. Small handles are stored inline; larger handles use `FANOTIFY_FH_FLAG_EXT_BUF` and an aligned external buffer pointer.

`struct fanotify_info` stores variable-length directory file handle, optional second directory file handle, optional child/object file handle, and one or two names in one packed buffer. The macros compute ordered offsets for:

- old directory handle
- new directory handle for rename
- object/file handle
- first name
- second name for rename

The setter/copy helpers intentionally enforce write order so offsets remain valid.

## Event Types

`enum fanotify_event_type` distinguishes fixed FID events, variable FID/name events, path events, permission path events, overflow events, filesystem error events, and mount events.

`struct fanotify_event` embeds the generic `fsnotify_event`, a merge-hash list node, event mask, compact type/hash bitfields, and the reporting pid.

Concrete event wrappers include:

- `fanotify_fid_event` for fsid plus inline object file handle.
- `fanotify_name_event` for fsid plus variable `fanotify_info`.
- `fanotify_error_event` for filesystem error code/count plus fsid and object handle.
- `fanotify_path_event` for path-based notification.
- `fanotify_mnt_event` for mount namespace attach/detach reporting.
- `fanotify_perm_event` for permission/pre-content events awaiting userspace response.

## Permission Events

Permission events track a path, optional file range, userspace response, state machine, watchdog count, reported fd, receiver pid, and optional audit-rule response info.

The state values are `INIT`, `REPORTED`, `ANSWERED`, and `CANCELED`.

## Mark Helpers

`struct fanotify_mark` wraps a generic fsnotify mark and caches fsid data. Helpers translate internal mark flags back to fanotify user flags, compare fsids, and extract custom errno values from permission responses.

## Design Notes

The header keeps payload layout logic close to the structures. Most helpers are small, inline, and type-discriminating, which keeps the larger fanotify read/write/mark code from open-coding buffer offsets and container conversions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/fanotify/fanotify.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/fanotify/fanotify_user.c -->
# File Research: sources/os/linux/linux/fs/notify/fanotify/fanotify_user.c

## Role

This file implements the userspace fanotify interface: `fanotify_init`, `fanotify_mark`, file operations for fanotify descriptors, event formatting for reads, permission-response writes, mark validation, per-user limits, sysctls, and initialization of fanotify caches.

It depends on generic fsnotify queue/mark mechanics and on fanotify event creation/ops provided elsewhere.

## Limits And Sysctls

The file defines defaults for queued events, user groups, user marks, legacy per-group mark limits, and the permission watchdog. With sysctl enabled it registers:

- `fs/fanotify/max_user_groups`
- `fs/fanotify/max_user_marks`
- `fs/fanotify/max_queued_events`
- `fs/fanotify/watchdog_timeout`

Mark limits are estimated from 1% of addressable memory using inode-mark cost.

## Permission Watchdog

Permission groups with pending access decisions may be linked into `perm_group_list`. The delayed watchdog scans `access_list` entries and rate-limits warnings when a receiving pid has not responded for more than the configured timeout.

Group removal unlinks a group so teardown cannot race with watchdog scans.

## Event Read Path

The read path dequeues one event if its computed variable length fits in the user buffer. Event length accounts for metadata plus optional records:

- FID/DFID/DFID_NAME file-handle records
- old/new rename records
- pidfd record
- filesystem error record
- access range record
- mount id record

For path events, privileged listeners may receive a newly opened fd created with `dentry_open_nonotify()`. `FAN_REPORT_FD_ERROR` controls whether fd creation failures are reported as errors or cause legacy-compatible event dropping.

Permission events are not destroyed after copying. They move to `access_list`, carry the generated fd, and wait for a userspace response.

## Permission Response Write Path

`fanotify_write()` accepts `struct fanotify_response` plus optional audit-rule info. It validates response bits, allow/deny semantics, custom errno support for pre-content groups, audit permissions, and response-info layout.

When a matching fd is found in `access_list`, the event is removed, marked answered, and waiters on `access_waitq` are woken.

## File Operations

The fanotify descriptor supports fdinfo display, poll, read, write, release, ioctl, and no-op seek. `FIONREAD` reports queued metadata length only.

Release stops queueing, removes watchdog tracking, auto-allows outstanding permission events, destroys non-permission events, wakes access waiters, and destroys the fsnotify group.

## `fanotify_init`

The syscall validates privilege, class, FID mode, mount-report mode, pidfd/TID exclusion, event fd open flags, audit permissions, and queue-limit flags. It allocates an fsnotify group, sets group priority from fanotify class, stores user namespace and memcg, creates merge hash and overflow event, initializes wait/list heads, and returns an anonymous inode fd.

Unprivileged groups are restricted to limited reporting modes and cannot receive open fds or real pids for other tasks.

## `fanotify_mark`

The mark path validates command, mark type, mask bits, ignore-mask API combinations, group capabilities, permission-event class restrictions, mount-event restrictions, filesystem-error restrictions, evictable mark scope, and FID requirements.

It resolves the target path or fd, checks read permission and LSM `security_path_notify`, validates fsid and exportfs file-handle support for FID groups, checks namespace/filesystem capabilities for mount/sb/mntns marks, and applies special handling for directory flags, non-directory parent-FID reporting, and ignore masks on writable inodes.

Marks are added, removed, or flushed through generic fsnotify mark APIs with fanotify-specific accounting and fsid consistency checks.

## Design Notes

This file is the fanotify policy boundary. The generic fsnotify layer handles queueing and mark lifetime, while this file enforces syscall ABI rules, privilege model, record layout, and userspace-visible compatibility behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/fanotify/fanotify_user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/fdinfo.c -->
# File Research: sources/os/linux/linux/fs/notify/fdinfo.c

## Role

This file implements `/proc/<pid>/fdinfo` output for inotify and fanotify descriptors when procfs is enabled.

It walks a group's marks under `fsnotify_group_lock()` and prints per-mark state in a userspace-debuggable format.

## Shared Logic

`show_fdinfo()` gets the fsnotify group from `file->private_data`, locks the group, iterates `group->marks_list`, invokes a subsystem-specific printer, and stops if the seq buffer overflows.

When exportfs is enabled, `show_mark_fhandle()` tries to encode an inode file handle under a shared superblock lock and prints handle bytes, type, and hex payload.

## Inotify Output

For inode marks, `inotify_fdinfo()` prints:

- watch descriptor
- inode number
- superblock device
- userspace mask
- ignored mask placeholder
- optional encoded file handle

It grabs the inode with `igrab()` and releases it with `iput()`.

## Fanotify Output

`fanotify_show_fdinfo()` first prints fanotify init flags and event open flags. Per-mark output varies by connector type:

- inode: inode number, device, mark flags, mask, ignore mask, optional handle
- vfsmount: mount id, mark flags, mask, ignore mask
- superblock: device, mark flags, mask, ignore mask
- mount namespace: namespace inode number, mark flags, mask, ignore mask

## Design Notes

The file is intentionally diagnostic. It avoids creating references unless needed and tolerates objects disappearing by using connector type checks and reference helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/fdinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/fdinfo.h -->
# File Research: sources/os/linux/linux/fs/notify/fdinfo.h

## Role

This small header declares fsnotify fdinfo hooks for inotify and fanotify.

When `CONFIG_PROC_FS` is enabled, it exposes `inotify_show_fdinfo()` and/or `fanotify_show_fdinfo()` according to subsystem config. Without procfs, both names are defined as `NULL`.

## Design Notes

The header lets file-operation tables assign `.show_fdinfo` unconditionally inside subsystem code while compiling away procfs support cleanly.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/fdinfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/fsnotify.c -->
# File Research: sources/os/linux/linux/fs/notify/fsnotify.c

## Role

This file contains the central fsnotify dispatcher and object-deletion hooks. VFS notification helpers eventually call `fsnotify()`, which selects interested marks across inode, parent, mount, superblock, and mount namespace objects and calls the registered backend operations.

## Object Cleanup

The file clears marks for deleted inodes, vfsmounts, mount namespaces, and superblocks. Superblock deletion also unmounts watched inodes, clears sb marks, waits for watched-object counters to drain, and warns if priority watchers remain.

## Parent/Child Handling

`fsnotify_set_children_dentry_flags()` marks children of watched directories with `DCACHE_FSNOTIFY_PARENT_WATCHED`.

`__fsnotify_parent()` is the parent-aware entry path. It fast-exits when no object is watched, decides whether parent/name information is required, takes a name snapshot when needed, and calls `fsnotify()` with both parent and child context.

It also lazily clears stale child dentry flags when a parent no longer watches children.

## Event Dispatch

`fsnotify()` builds an iterator over possible mark lists:

- superblock marks
- vfsmount marks
- inode marks
- parent or second-inode marks
- mount-namespace marks

It first checks aggregate masks to avoid SRCU overhead when no mark can care. When marks exist, it enters SRCU, walks each list, and merges them by group priority/address.

For each selected group, `send_to_group()` combines mark masks and effective ignore masks. It clears ignore masks on modify when appropriate and calls either the backend `handle_event()` or the default inode-event adapter.

## Default Inode Adapter

The default adapter supports backends that only implement `handle_inode_event()`. It handles parent marks before child marks, strips `FS_EVENT_ON_CHILD` for child delivery, suppresses names except for directory-entry events, and applies unlink-exclusion behavior.

## Permission Open Optimization

With fanotify access permissions enabled, `fsnotify_open_perm_and_set_mode()` performs open-time checks for priority watchers and sets file mode bits so later permission/pre-content hooks can skip work when no relevant watcher existed at open time.

## Mount Namespace Events

`fsnotify_mnt()` wraps mount namespace attach/detach events in `struct fsnotify_mnt` and sends them only when the namespace has marks.

## Initialization

`fsnotify_init()` verifies event-bit count, initializes SRCU for mark traversal, and initializes connector caches.

## Design Notes

The core design optimizes the no-watch case aggressively, then uses priority-ordered mark list merging to deliver each group one coherent view of its inode/mount/sb marks and ignore masks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/fsnotify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/fsnotify.h -->
# File Research: sources/os/linux/linux/fs/notify/fsnotify.h

## Role

This private header defines fsnotify connector accessors and internal declarations shared by fsnotify implementation files.

## Connectors

`fsnotify_connp_t` is an RCU pointer to a `struct fsnotify_mark_connector`, embedded in watchable objects.

The header provides typed accessors for connector objects:

- inode
- mount
- superblock
- mount namespace

It also maps object type to superblock and retrieves the superblock mark pointer.

## Internal APIs

The header declares:

- notification queue flushing
- global SRCU object for mark traversal
- group priority comparison
- unmount inode cleanup
- connector-based mark destruction
- object-specific mark clearing helpers
- child dentry flag updates
- connector cache initialization

## Design Notes

This file isolates the internal connector abstraction from public fsnotify headers. Callers can clear marks by object type without knowing connector list internals.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/fsnotify.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/group.c -->
# File Research: sources/os/linux/linux/fs/notify/group.c

## Role

This file implements generic fsnotify group allocation, reference counting, shutdown, destruction, and async notification helper support.

A group represents one notification consumer, such as one inotify or fanotify file descriptor.

## Lifetime

`fsnotify_alloc_group()` allocates and initializes a group with:

- refcount 1
- notification queue lock/list/waitqueue
- unlimited default max events
- mark mutex and mark list
- backend ops
- flags

User groups are allocated with accounted GFP.

`fsnotify_get_group()` increments the group refcount. `fsnotify_put_group()` decrements it and calls final destruction when the count reaches zero.

Final destruction calls backend private cleanup, drops memcg, destroys the mark mutex, and frees the group.

## Shutdown And Destruction

`fsnotify_group_stop_queueing()` sets `group->shutdown` under the notification lock so no new events enter the queue.

`fsnotify_destroy_group()` performs full teardown:

1. Stop queueing.
2. Clear all marks by group.
3. Wait for marks pinned by userspace waits.
4. Wait for asynchronous mark destruction.
5. Flush queued notifications.
6. Free the overflow event.
7. Drop the final group reference.

## Async Notification

`fsnotify_fasync()` wires a descriptor into the group fasync list so queue insertion can deliver `SIGIO`.

## Design Notes

Group destruction is deliberately staged around mark refs and SRCU-delayed mark freeing. This prevents backend queues from being flushed while event delivery or permission waits can still hold mark/group references.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/group.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/inotify/Kconfig -->
# File Research: sources/os/linux/linux/fs/notify/inotify/Kconfig

## Role

This Kconfig file defines `CONFIG_INOTIFY_USER`, the userspace inotify interface.

## Configuration

`INOTIFY_USER` is a boolean option labeled "Inotify support for userspace". It selects `FSNOTIFY` and defaults to enabled.

The help text describes inotify as a file and directory monitoring API using a single open descriptor whose events are readable and poll/select-able. It notes improvements over dnotify, including multiple file events, one-shot support, and unmount notification.

## Design Notes

The config entry makes inotify userspace support a direct fsnotify client and keeps it enabled by default for normal Linux builds.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/inotify/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/inotify/Makefile -->
# File Research: sources/os/linux/linux/fs/notify/inotify/Makefile

## Role

This Makefile builds the inotify userspace implementation when `CONFIG_INOTIFY_USER` is enabled.

## Objects

It links two objects into the fsnotify/inotify portion of the kernel:

- `inotify_fsnotify.o`
- `inotify_user.o`

## Design Notes

The split mirrors the subsystem boundary: fsnotify backend event handling is separate from syscall and fd operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/inotify/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/inotify/inotify.h -->
# File Research: sources/os/linux/linux/fs/notify/inotify/inotify.h

## Role

This private inotify header defines inotify event and mark structures, user-mask conversion helpers, and cross-file declarations.

## Data Structures

`struct inotify_event_info` wraps a generic fsnotify event with:

- inotify mask
- watch descriptor
- rename sync cookie
- optional name length and name bytes

`struct inotify_inode_mark` wraps a generic fsnotify mark with the inotify watch descriptor.

## Mask Helpers

`INOTIFY_USER_MASK` limits userspace-visible bits to `IN_ALL_EVENTS`.

`inotify_mark_user_mask()` converts an internal fsnotify mark back to userspace bits and adds `IN_EXCL_UNLINK` or `IN_ONESHOT` based on internal mark flags.

## Declarations

The header declares:

- `inotify_ignored_and_remove_idr()`
- `inotify_handle_inode_event()`
- `inotify_fsnotify_ops`
- `inotify_inode_mark_cachep`

With `CONFIG_INOTIFY_USER`, it also provides ucounts helpers for instances and watches.

## Design Notes

The file keeps inotify's public watch-descriptor model separate from generic fsnotify mark mechanics.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/inotify/inotify.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/inotify/inotify_fsnotify.c -->
# File Research: sources/os/linux/linux/fs/notify/inotify/inotify_fsnotify.c

## Role

This file implements the inotify backend operations that plug into generic fsnotify. It converts inode events into queued inotify events and frees inotify-specific group/event/mark resources.

## Event Merging

`event_compare()` treats two events as mergeable when mask, watch descriptor, name length, and name match. `FS_IN_IGNORED` events never merge.

`inotify_merge()` compares only the new event with the last queued event, matching historical inotify adjacent-duplicate behavior.

## Event Handling

`inotify_handle_inode_event()` receives a mark-selected fsnotify event, allocates an `inotify_event_info` sized for an optional name, and populates mask, wd, cookie, and name.

Important behavior:

- It skips events racing with mark removal when wd is `-1`.
- Allocation is charged to the monitoring group's memcg, not the target process.
- Allocation failure queues overflow notification.
- `IN_ISDIR` is stripped from `IN_MOVE_SELF` and `IN_DELETE_SELF` for compatibility.
- One-shot marks are destroyed after event handling.

The event is queued through `fsnotify_add_event()` with duplicate merge support.

## Mark And Group Cleanup

When a mark is freed, `inotify_freeing_mark()` queues `IN_IGNORED` and removes the watch descriptor from the idr.

Group private cleanup checks for leaked idr entries, destroys the idr, and decrements the inotify instance ucount.

Event and mark free callbacks release `inotify_event_info` allocations and `inotify_inode_mark` cache entries.

## Design Notes

This file is the narrow translation layer from fsnotify's generic inode events to inotify's watch-descriptor event stream.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/inotify/inotify_fsnotify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/inotify/inotify_user.c -->
# File Research: sources/os/linux/linux/fs/notify/inotify/inotify_user.c

## Role

This file implements inotify userspace syscalls, descriptor file operations, watch descriptor idr management, per-user limits, sysctls, and initialization.

## Sysctls And Limits

It registers `fs/inotify` sysctls for:

- `max_user_instances`
- `max_user_watches`
- `max_queued_events`

At init, max watches are calculated from 1% of addressable memory using an estimated watch cost and clamped to `[8192, 1048576]`. Default queued events are 16384 and default instances are 128.

## File Operations

The inotify fd supports fdinfo, poll, read, fasync, release, ioctl, and no-op seek.

`inotify_poll()` reports readable state when the notification queue is non-empty.

`inotify_read()` waits unless nonblocking, removes queued events one at a time, copies `struct inotify_event` plus padded names to userspace, and destroys events after copying.

`FIONREAD` sums the exact bytes currently queued. With checkpoint/restore enabled, `INOTIFY_IOC_SETNEXTWD` adjusts the idr cursor.

Release destroys the fsnotify group.

## Path And Permission Checks

`inotify_add_watch()` validates mask bits, fd type, `IN_MASK_ADD`/`IN_MASK_CREATE` incompatibility, path lookup flags, read permission, and LSM notification permission before updating marks.

## Watch Descriptor Management

Each group has an idr protected by `idr_lock`.

New marks are allocated from `inotify_inode_mark_cachep`, initialized, assigned cyclic watch descriptors, charged to user watch ucounts, and attached as inode marks.

Existing marks can be replaced or extended. Mask/flag changes recalculate the inode fsnotify mask only when needed.

Removal finds a wd, destroys the fsnotify mark, and drops the lookup reference.

When a mark is ignored/freed, the code queues `IN_IGNORED`, removes it from idr, and decrements user watch count.

## Syscalls

Implemented syscalls are:

- `inotify_init1`
- `inotify_init`
- `inotify_add_watch`
- `inotify_rm_watch`

`inotify_init1()` validates flags against `IN_CLOEXEC` and `IN_NONBLOCK`, allocates a group with an overflow event, charges an instance ucount, and returns an anonymous inode fd.

## Initialization

`inotify_user_setup()` verifies bit layout compatibility between inotify and fsnotify constants, creates the mark cache, sets defaults, and registers sysctls.

## Design Notes

The file preserves inotify's watch-descriptor ABI while delegating event delivery, queueing, and mark lifetime to fsnotify.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/inotify/inotify_user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/mark.c -->
# File Research: sources/os/linux/linux/fs/notify/mark.c

## Role

This file implements fsnotify mark and connector lifetime, locking, attachment, detachment, lookup, destruction, mask recalculation, and superblock watcher accounting.

It is the concurrency core for inotify, fanotify, and other fsnotify users.

## Locking Model

The documented lock order is:

1. `group->mark_mutex`
2. `mark->lock`
3. `mark->connector->lock`

Group mutex protects the group's mark list and private limits. Mark lock protects masks, flags, group/object references. Connector lock protects the watched object's mark list.

Mark lists are protected for lockless dispatch by `fsnotify_mark_srcu`.

## Connectors

A connector is attached to each watched object and holds the ordered hlist of marks. Objects include inode, vfsmount, superblock, and mount namespace.

Inode connectors are additionally tracked on the superblock's inode connector list so unmount can find watched inodes.

Connectors update aggregate object masks and watched-object counters. Inode connectors may hold an inode reference unless all marks are evictable.

## Mask Recalculation

`__fsnotify_recalc_mask()` combines attached mark masks and ignore masks into the object aggregate mask. It also determines whether an inode reference is needed.

`fsnotify_recalc_mask()` updates masks, adjusts inode references, and sets child dentry flags when a directory starts watching children.

## Mark Attachment

`fsnotify_add_mark_locked()` adds a mark to the group list, then inserts it into the object's connector list ordered by group priority and address. Duplicate group marks are rejected unless the group allows duplicates.

Adding the first mark creates a connector with `cmpxchg()` so concurrent attachers converge safely.

## Mark Detachment And Freeing

`fsnotify_detach_mark()` marks a mark detached and removes it from the group list while leaving object-list removal to reference teardown.

`fsnotify_put_mark()` removes the mark from the connector list when refcount reaches zero, detaches/freeing connectors when empty, recalculates masks, queues connectors for SRCU-delayed freeing, and queues marks for delayed destruction.

`fsnotify_free_mark()` marks a mark no longer alive and invokes backend `freeing_mark()`.

## Group/Object Clearing

`fsnotify_clear_marks_by_group()` detaches all marks for a group or all marks of a selected object type.

`fsnotify_destroy_marks()` destroys all marks attached to one object connector and detaches the connector from the object to avoid pinning inodes during teardown.

## Unmount Handling

`fsnotify_unmount_inodes()` repeatedly finds a living watched inode from the superblock connector list, sends `FS_UNMOUNT`, clears its marks, and drops the inode.

## User Wait Support

Permission-event paths can call `fsnotify_prepare_user_wait()` to pin marks safely, drop SRCU while waiting for userspace, then reacquire SRCU with `fsnotify_finish_user_wait()`.

## Design Notes

This file balances fast SRCU read-side dispatch with safe asynchronous destruction. Marks can be removed by group teardown, object teardown, unmount, explicit user action, or refcount drop, and the code is structured to tolerate those paths racing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/mark.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/notification.c -->
# File Research: sources/os/linux/linux/fs/notify/notification.c

## Role

This file implements generic fsnotify notification queue operations and rename-cookie allocation.

Groups such as inotify and fanotify use these helpers to queue, peek, remove, overflow, and flush events.

## Cookies

`fsnotify_get_cookie()` returns an atomic increasing 32-bit cookie used to pair related events such as rename-from and rename-to.

## Event Destruction

`fsnotify_destroy_event()` ignores null and per-group overflow events. For normal events, it warns if the event is still queued and then calls the backend `free_event()` callback.

## Queue Insertion

`fsnotify_insert_event()` is the central queue insertion helper. Under `notification_lock`, it:

- refuses events after group shutdown
- switches to the overflow event if the queue is full or the incoming event is already overflow
- queues the overflow event only once
- optionally merges with existing queued events
- appends the event
- optionally inserts it into a backend merge structure
- wakes readers and sends async SIGIO

Return values distinguish queued, merged, and dropped/overflow/shutdown outcomes.

## Queue Removal And Flush

The file provides helpers to remove a queued event, peek at the first event, remove the first event, and flush all queued notifications during group teardown.

Queue length is maintained with `group->q_len`.

## Design Notes

The queue layer is generic but leaves policy hooks to backends: merging and auxiliary hash insertion are callback-driven, and event memory ownership remains with backend `free_event()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/notification.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nsfs.c -->
# File Research: sources/os/linux/linux/fs/nsfs.c

## Role

This file implements `nsfs`, the pseudo filesystem used to represent Linux namespaces as file objects. It supports namespace file opening, proc namespace paths, namespace ioctls, exportable file handles, and namespace active-reference helpers.

## Namespace Paths And Files

`nsfs_get_root()` returns the nsfs root path. `ns_get_path_cb()` and `ns_get_path()` construct paths from stashed namespace dentries. `open_namespace_file()` and `open_namespace()` open namespace file objects and consume namespace references.

Dentries use dynamic names like `mnt:[ino]` or `net:[ino]`.

Inode eviction drops the active namespace reference and calls the namespace operation `put()`.

## Ioctls

`ns_ioctl()` implements namespace fd operations including:

- get owning user namespace
- get parent namespace
- get namespace type
- get owner uid for user namespaces
- translate pids/tgids into or out of pid namespaces
- get namespace id
- get mount namespace id
- extensible mount namespace info
- get next/previous mount namespace fd and optional info

Validation separates known fixed ioctls from extensible mount namespace ioctls. Sequential mount namespace traversal requires permission to see all namespaces.

## Mount Namespace Info

`copy_ns_info_to_user()` supports extensible struct sizing. It fills known fields and copies only the size supported by both userspace and kernel.

## Exportfs Support

`nsfs_encode_fh()` encodes namespace id, type, and inode number into an nsfs file handle.

`nsfs_fh_to_dentry()` decodes handles through namespace-tree lookup, validates trailing bytes and type fields, checks namespace visibility/security, resurrects stashed namespace dentries when allowed, and returns the dentry.

Export operations also define open and permission hooks.

## Pseudo Filesystem Setup

`nsfs_init_fs_context()` initializes a pseudo fs with nsfs super operations, export operations, dentry operations, and stashed operations. `nsfs_init()` mounts it internally and clears `SB_NOUSER` so it can be exposed.

## Active Reference Helpers

`nsproxy_ns_active_get()` and `nsproxy_ns_active_put()` adjust active references for all namespaces contained in an nsproxy.

## Design Notes

nsfs is both a proc-facing namespace fd filesystem and an exportable object namespace. The stashed dentry design lets namespace objects reappear as files when later referenced by sockets, ioctls, or handles.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nsfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/ntfs/Kconfig

## Role

This Kconfig file defines build options for the legacy Linux NTFS filesystem driver.

## Options

`NTFS_FS` is a tristate option that selects `NLS` and `FS_IOMAP`. It builds as module `ntfs` when selected as `M`.

`NTFS_DEBUG` depends on `NTFS_FS` and enables additional consistency checks and debug messages. The help warns that enabled debug messages can significantly slow the system.

`NTFS_FS_POSIX_ACL` depends on `NTFS_FS`, selects `FS_POSIX_ACL`, and enables Linux-only POSIX ACL support for NTFS, with the note that Windows ignores these ACLs.

## Design Notes

The driver now depends on iomap infrastructure, and ACL support is explicit rather than implied by core NTFS support.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/Makefile -->
# File Research: sources/os/linux/linux/fs/ntfs/Makefile

## Role

This Makefile builds the Linux NTFS filesystem module/object set.

## Objects

`obj-$(CONFIG_NTFS_FS)` builds `ntfs.o`.

The `ntfs-y` list includes address-space operations, attributes, collation, directory handling, file handling, indexes, inode/MFT logic, runlists, superblock code, unicode/upcase support, attrlists, extended attributes, bitmap/LCN allocation, logfile, reparse, compression, iomap, debug, sysctl, quota, object id, and block-device I/O modules.

When `CONFIG_NTFS_DEBUG` is enabled, `-DDEBUG` is added.

## Design Notes

The Makefile shows NTFS as one monolithic filesystem module split internally by metadata, namespace, allocation, I/O, and support subsystems.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ntfs/aops.c -->
# File Research: sources/os/linux/linux/fs/ntfs/aops.c

## Role

This file defines NTFS address-space operations and page-cache handling for regular NTFS data and MFT mappings. It uses iomap for normal buffered reads, readahead, writeback, bmap, and swap activation.

## Read Path

`ntfs_read_folio()` handles page-cache folio reads. It rejects unsupported encrypted attributes with `-EOPNOTSUPP`, delegates compressed non-resident streams to `ntfs_read_compressed_block()`, and otherwise calls `iomap_read_folio()` with NTFS iomap read ops.

The custom read end I/O handler zeroes the part of a folio past `initialized_size` when a bio crosses that boundary, then completes iomap folio read accounting.

## Readahead

`ntfs_readahead()` skips resident files and compressed files, then calls `iomap_readahead()` for non-resident uncompressed mappings.

## Block Mapping

`ntfs_bmap()` maps logical filesystem blocks to physical device blocks for suitable non-resident, unencrypted, non-MST-protected `$DATA` attributes.

It checks initialized size and file size to report holes, looks up the runlist under the runlist read lock, handles error LCNs, converts clusters to block units, and returns 0 for holes/errors/truncation cases.

The function documents the usual `bmap()` ambiguity where physical block 0 cannot be distinguished from hole/error.

## Writeback

`ntfs_writepages()` rejects volume shutdown, ignores resident files, rejects encrypted files, and uses `iomap_writepages()` with NTFS writeback ops.

MFT writeback uses a separate `ntfs_mft_writepages` operation in the MFT address-space table.

## Swap Activation

`ntfs_swap_activate()` delegates swapfile validation/mapping to `iomap_swapfile_activate()` using NTFS read iomap ops.

## Address-Space Tables

`ntfs_aops` provides normal NTFS mapping operations: read, readahead, writepages, dirty, bmap, migration, partial uptodate, error removal, release, invalidate, and swap activation.

`ntfs_mft_aops` is similar but uses MFT-specific writepages and omits swap activation.

## Design Notes

The file is the bridge between NTFS runlist/attribute semantics and Linux's iomap/page-cache APIs, with explicit exclusions for encrypted and compressed paths that require special handling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ntfs/aops.c -->