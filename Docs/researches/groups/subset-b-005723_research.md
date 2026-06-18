# subset-b-005723 Research

Grouped source research for Linux fsnotify/fanotify/inotify core notification code, namespace filesystem support, and NTFS address-space operations. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/fanotify/fanotify.h -->
# sources/distributed-fs/ceph-client/fs/notify/fanotify/fanotify.h

## Purpose

`fanotify.h` is the private fanotify backend contract shared by fanotify event production, queueing, user-copy, mark handling, fdinfo reporting, and filesystem error reporting. It defines the concrete in-memory event types layered on `struct fsnotify_event`, the compact file-handle/name packing format used for fid events, permission-event state, fanotify mark metadata, and helper accessors that hide the variant-specific layouts from the syscall and backend code.

## Important APIs, Types, and Functions

Important types are `struct fanotify_fh`, `struct fanotify_info`, `struct fanotify_event`, `struct fanotify_fid_event`, `struct fanotify_name_event`, `struct fanotify_error_event`, `struct fanotify_path_event`, `struct fanotify_mnt_event`, `struct fanotify_perm_event`, and `struct fanotify_mark`. The event type enum distinguishes fixed fid events, variable fid+name events, path events, permission path events, overflow events, filesystem error events, and mount events. Accessor helpers include `fanotify_fh_buf()`, `fanotify_info_*_fh_len()`, `fanotify_info_*_fh()`, `fanotify_info_name*()`, `fanotify_event_fsid()`, `fanotify_event_object_fh()`, `fanotify_event_info()`, `fanotify_event_path()`, and `FANOTIFY_*()` container casts. Policy helpers include `fanotify_is_perm_event()`, `fanotify_is_error_event()`, `fanotify_is_mnt_event()`, `fanotify_is_hashed_event()`, `fanotify_mark_user_flags()`, and `fanotify_get_response_errno()`.

## Control Flow

This header has no standalone runtime flow, but it defines the shape that runtime code follows. Event allocation code initializes the embedded `fanotify_event` with `fanotify_init_event()`, sets `type`, `mask`, hash, pid, and variant fields, then queue/read/free paths use the accessor helpers to serialize the correct metadata. The `fanotify_info` setters must be called in order: directory file handle, optional second directory file handle, optional object file handle, name, then second name. That ordering makes the variable buffer offsets deterministic for later user-copy.

## State and Persistence Behavior

The structures are transient kernel objects. Events live in fsnotify group queues or fanotify permission wait lists until read, merged, answered, canceled, or freed. Permission events persist longer than notification events because they wait for userspace response and carry `response`, `state`, `fd`, `recv_pid`, range, and optional audit response data. Marks persist while attached to fsnotify connectors and cache the mark fsid for fid reporting. File handles may be inline or external-buffer backed, so freeing code must honor `FANOTIFY_FH_FLAG_EXT_BUF`.

## Dependencies and Integration Points

The header depends on `linux/fsnotify_backend.h`, `linux/exportfs.h`, `linux/path.h`, slab allocation, hash list support, and public fanotify response structures. It integrates with `fanotify_user.c` for user ABI serialization and syscall validation, fanotify backend code for event allocation/merging/freeing, `fdinfo.c` for mark display, and generic fsnotify group/mark queues. It also encodes assumptions from exportfs, such as `MAX_HANDLE_SZ`, file-handle type, and fsid reporting.

## Risks and Edge Cases

Risks are mostly ABI and lifetime related. Variable-length fid/name layout relies on byte-sized length fields, alignment, and strict setter ordering. Missing or malformed file handles affect user-visible fid records. Permission-event state transitions must avoid double free or lost wakeups. Hash bit partitioning assumes event type count stays within `FANOTIFY_EVENT_TYPE_BITS`. Error events intentionally report even a zero object file handle, which differs from normal fid events.

## Test Signals

Useful signals include fanotify selftests for fid/name/rename records, filesystem error events, permission responses, pre-content range info, mount attach/detach events, fdinfo output, and queue overflow. Kernel build tests should catch layout and `BUILD_BUG_ON()` assumptions. Runtime stress should cover long names, weak/strong fsids, inline versus external file handles, permission cancellation, and event merging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/fanotify/fanotify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/fanotify/fanotify_user.c -->
# sources/distributed-fs/ceph-client/fs/notify/fanotify/fanotify_user.c

## Purpose

`fanotify_user.c` implements fanotify's userspace-facing file descriptor and syscall layer. It creates fanotify groups, validates `fanotify_init()` and `fanotify_mark()` flags, reads notification records to userspace, accepts permission responses through `write()`, manages permission-event watchdog warnings, enforces per-user group/mark/queue accounting, and translates fsnotify/fanotify event objects into the fanotify metadata ABI.

## Important APIs, Types, and Functions

Key entry points are `SYSCALL_DEFINE2(fanotify_init)` and `SYSCALL_DEFINE5/SYSCALL32_DEFINE6(fanotify_mark)`. File operations are `fanotify_read()`, `fanotify_write()`, `fanotify_poll()`, `fanotify_ioctl()`, and `fanotify_release()`. Event serialization is handled by `fanotify_event_len()`, `get_one_event()`, `copy_event_to_user()`, `copy_info_records_to_user()`, `copy_fid_info_to_user()`, `copy_pidfd_info_to_user()`, `copy_error_info_to_user()`, `copy_range_info_to_user()`, and `copy_mnt_info_to_user()`. Mark logic uses `fanotify_find_path()`, `fanotify_events_supported()`, `fanotify_test_fsid()`, `fanotify_test_fid()`, `fanotify_add_mark()`, `fanotify_add_new_mark()`, `fanotify_remove_mark()`, and `fanotify_mark_update_flags()`. Permission responses flow through `process_access_response()`, `process_access_response_info()`, and `finish_permission_event()`.

## Control Flow

`fanotify_init()` validates privilege and flag combinations, allocates an fsnotify group with fanotify ops, assigns priority from class, configures fid/mount/pidfd/fd-error modes, allocates a merge hash and overflow event, initializes wait queues/lists, applies user limits, and returns an anon inode file. `fanotify_mark()` validates the requested command, mark type, mask, group mode, permission class, fsid/fid support, path permissions, LSM hook, and namespace capabilities before adding, removing, or flushing marks on inodes, mounts, superblocks, or mount namespaces. On read, `get_one_event()` dequeues the next queue item, marks permission events as reported, unhashes mergeable events, and `copy_event_to_user()` emits metadata plus optional fd, pidfd, fid, error, range, or mount info records. Permission events are moved to `access_list` and later completed by `fanotify_write()` responses, release-time allow, or copy failure deny.

## State and Persistence Behavior

Persistent per-fd state is in `struct fsnotify_group`: fanotify flags, event fd flags, merge hash, overflow event, access wait queue, permission access list, watchdog list node, user namespace, memcg, and ucounts. Marks persist through generic fsnotify connectors and hold optional fsid metadata. Queue state persists until read; permission events persist after read until userspace writes a valid response. The watchdog periodically scans `access_list` and rate-limits warnings for pids that fail to respond for more than `watchdog_timeout`. Sysctl defaults initialize max queued events, max user groups, max user marks, and watchdog timeout.

## Dependencies and Integration Points

The file integrates deeply with generic fsnotify group, mark, queue, and connector helpers, fanotify backend ops, anon inode files, exportfs file-handle encoding/decoding capability checks, VFS path lookup and permission checks, LSM `security_path_notify()`, pidfd creation, memcg accounting, ucounts, user namespaces, mount namespaces, and public fanotify UAPI structs. Mount events require `FAN_REPORT_MNT` groups and `FAN_MARK_MNTNS`; fid events require exportfs-capable filesystems.

## Risks and Edge Cases

High-risk areas include ABI size calculations, partial user-copy cleanup, permission-event state transitions, fd/pidfd install ordering, and mark validation compatibility. Unprivileged groups must not receive fds or other pids. `FAN_REPORT_PIDFD` and `FAN_REPORT_TID` remain mutually exclusive. Weak fsids are allowed only for inode marks and cannot be mixed across filesystems or btrfs subvolumes. Pre-content events require filesystem opt-in and are not generated for directories. Ignore-mask semantics intentionally reject downgrades from new to old semantics or from surviving modify to non-surviving behavior.

## Test Signals

Strong signals are fanotify selftests for init flag matrices, unprivileged fid-only groups, pidfd reporting, fd error reporting, permission allow/deny/custom errno/audit info, pre-content range records, fs error reports, rename fid records, mount namespace marks, mark flush/remove/update semantics, ignored masks, evictable inode marks, and release while permission events are pending. Stress should cover queue overflow, merge hash removal, slow permission responders, deleted paths returning `EOPENSTALE`, and filesystems without exportfs fid support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/fanotify/fanotify_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/fdinfo.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/fdinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/fdinfo.h -->
# sources/distributed-fs/ceph-client/fs/notify/fdinfo.h

## Purpose

`fdinfo.h` is the small declaration gate for fsnotify fdinfo support. It exposes fanotify and inotify fdinfo hooks to their file operation tables when procfs support is enabled and provides `NULL` fallbacks when procfs is disabled.

## Important APIs, Types, and Functions

The header declares `inotify_show_fdinfo(struct seq_file *, struct file *)` under `CONFIG_INOTIFY_USER` and `fanotify_show_fdinfo(struct seq_file *, struct file *)` under `CONFIG_FANOTIFY`. Without `CONFIG_PROC_FS`, both names are defined as `NULL` so file operation initializers remain simple.

## Control Flow

There is no executable control flow. Preprocessor branches select declarations or null constants based on build configuration.

## State and Persistence Behavior

The file owns no state and only controls compile-time linkage of procfs diagnostics.

## Dependencies and Integration Points

It depends on `linux/proc_fs.h` and forward declarations of `seq_file` and `file`. It integrates with `inotify_user.c` and `fanotify_user.c` file operation tables, and with `fdinfo.c` for the actual implementations.

## Risks and Edge Cases

The main risk is build-configuration mismatch: references to fdinfo functions must disappear cleanly when procfs or either notifier is disabled. The `NULL` fallback is intentional for file operations that accept a missing fdinfo hook.

## Test Signals

Kernel build coverage with `CONFIG_PROC_FS` on and off, and with inotify/fanotify individually enabled or disabled, is the primary signal. Runtime fdinfo tests only apply when procfs and the relevant notifier are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/fdinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/fsnotify.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/fsnotify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/fsnotify.h -->
# sources/distributed-fs/ceph-client/fs/notify/fsnotify.h

## Purpose

`fsnotify.h` is the private core header for fsnotify connector access and teardown helpers. It defines the RCU connector pointer type, object-specific connector accessors, superblock lookup helpers, mark clearing wrappers, and declarations shared by `fsnotify.c`, `mark.c`, `group.c`, and notifier backends.

## Important APIs, Types, and Functions

The key type is `fsnotify_connp_t`, an RCU pointer to `struct fsnotify_mark_connector`. Inline accessors map a connector to an inode, mount, superblock, or mount namespace: `fsnotify_conn_inode()`, `fsnotify_conn_mount()`, `fsnotify_conn_sb()`, and `fsnotify_conn_mntns()`. Other helpers include `fsnotify_object_sb()`, `fsnotify_connector_sb()`, `fsnotify_sb_marks()`, `fsnotify_clear_marks_by_inode()`, `fsnotify_clear_marks_by_mount()`, `fsnotify_clear_marks_by_sb()`, and `fsnotify_clear_marks_by_mntns()`. Declarations cover queue flushing, SRCU, group comparison, inode unmount scanning, connector destruction, dentry flag updates, and connector cache init.

## Control Flow

There is no independent runtime flow. The inline helpers are used on hot paths to translate generic connector state into object-specific fields and to route teardown calls to `fsnotify_destroy_marks()`.

## State and Persistence Behavior

The header does not own storage. It documents how connectors are embedded into watched objects and how mark lists are reached through object fields. The clear helpers initiate destruction of all marks attached to an object but the actual lifetime is handled asynchronously in `mark.c`.

## Dependencies and Integration Points

It depends on `linux/fsnotify.h`, `linux/srcu.h`, list types, and local mount internals. It is included by generic fsnotify implementation files and backend fdinfo/user code that need connector object access.

## Risks and Edge Cases

The main risks are invalid object-type assumptions and missing `NULL` checks for superblocks without fsnotify info. Mount connectors require `real_mount()` conversion. The mount-namespace connector path does not map to a superblock, so callers using `fsnotify_object_sb()` must handle `NULL`.

## Test Signals

Build coverage across all fsnotify users is important because most behavior is inline. Runtime tests that clear marks by inode, mount, superblock, and mount namespace validate the wrapper paths indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/fsnotify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/group.c -->
# sources/distributed-fs/ceph-client/fs/notify/group.c

## Purpose

`group.c` owns allocation, reference counting, shutdown, and final destruction of `struct fsnotify_group`. A group is the per-user/per-backend notification endpoint that owns marks, queued events, wait queues, backend-private data, and backend operations.

## Important APIs, Types, and Functions

Important functions are `fsnotify_alloc_group()`, `fsnotify_get_group()`, `fsnotify_put_group()`, `fsnotify_group_stop_queueing()`, `fsnotify_destroy_group()`, and `fsnotify_fasync()`. Internal helpers are `__fsnotify_alloc_group()` and `fsnotify_final_destroy_group()`.

## Control Flow

Group allocation zeroes and initializes the group, sets refcount and `user_waits`, initializes notification and mark locks/lists, assigns ops/flags, and defaults `max_events` to `UINT_MAX`. Destruction first stops queueing, clears all marks by group, waits for marks pinned by userspace permission waits, waits for asynchronous mark destruction, flushes queued notifications, frees the per-group overflow event, then drops the final reference. Final destroy invokes backend `free_group_priv`, drops memcg, destroys `mark_mutex`, and frees the group.

## State and Persistence Behavior

Group state persists for the lifetime of a fanotify/inotify file descriptor or other backend endpoint. `shutdown` prevents future queue insertion. `notification_list`, `marks_list`, `overflow_event`, fasync state, memcg, and backend-private fields are owned through the group. Refcounting allows marks and external users to keep the group alive until asynchronous cleanup finishes.

## Dependencies and Integration Points

It depends on generic fsnotify backend definitions, mark cleanup in `mark.c`, notification queue cleanup in `notification.c`, memcg references, wait queues, fasync, and backend ops supplied by fanotify/inotify/dnotify-style users.

## Risks and Edge Cases

The risky sequence is teardown while permission events or mark destruction are in progress. The group must stop queueing early, wait for `user_waits`, and wait for mark SRCU reapers before flushing notifications so no handler can still enqueue or reference the group. Overflow events are special and cannot be freed by generic event destruction.

## Test Signals

Tests should close fanotify/inotify descriptors with queued normal events, overflow events, pending permission events, and active marks. Race tests should remove marks while closing groups and verify no leaks, use-after-free, or stuck waiters. Fasync behavior is covered by SIGIO readiness tests for inotify users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/inotify/Kconfig -->
# sources/distributed-fs/ceph-client/fs/notify/inotify/Kconfig

## Purpose

This Kconfig entry exposes userspace inotify support as `CONFIG_INOTIFY_USER`. Enabling it selects the generic fsnotify infrastructure and compiles the inotify syscall/file-descriptor implementation.

## Important APIs, Types, and Functions

The relevant symbol is `INOTIFY_USER`, a boolean option defaulting to `y` and selecting `FSNOTIFY`. The help text documents inotify as a single-fd, pollable event interface for files and directories and points to `Documentation/filesystems/inotify.rst`.

## Control Flow

There is no runtime control flow. Kconfig resolution ensures `FSNOTIFY` is enabled whenever inotify userspace support is selected.

## State and Persistence Behavior

The file owns no runtime state. It controls whether inotify syscalls, caches, sysctls, and file operations are built into the kernel.

## Dependencies and Integration Points

It integrates with the fsnotify core by selecting `FSNOTIFY`, and with the inotify Makefile by controlling `obj-$(CONFIG_INOTIFY_USER)`.

## Risks and Edge Cases

Disabling this symbol removes userspace inotify support even if fsnotify remains available to other backends. Default `y` preserves long-standing userspace expectations.

## Test Signals

Configuration tests should verify that enabling the option builds `inotify_fsnotify.o` and `inotify_user.o`, and disabling it removes inotify syscalls/fdinfo hooks while fanotify or other fsnotify users can still build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/inotify/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/inotify/Makefile -->
# sources/distributed-fs/ceph-client/fs/notify/inotify/Makefile

## Purpose

The inotify Makefile wires the userspace inotify implementation into the kernel build when `CONFIG_INOTIFY_USER` is enabled.

## Important APIs, Types, and Functions

The only build rule is `obj-$(CONFIG_INOTIFY_USER) += inotify_fsnotify.o inotify_user.o`.

## Control Flow

There is no runtime control flow. Kbuild includes the backend event handling object and the syscall/file operation object based on the config symbol.

## State and Persistence Behavior

The file owns no runtime state and only affects compiled objects.

## Dependencies and Integration Points

It integrates with `Kconfig`'s `INOTIFY_USER` symbol and with the parent fs/notify build. Both objects are required: `inotify_fsnotify.o` supplies fsnotify ops and event allocation/freeing, while `inotify_user.o` supplies syscalls and fd operations.

## Risks and Edge Cases

Dropping either object would produce missing symbols or a half-built inotify implementation. The simple rule relies on the config symbol selecting generic fsnotify.

## Test Signals

Build `CONFIG_INOTIFY_USER=y` and confirm both objects are compiled/linked; build with it disabled and confirm neither object is included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/inotify/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/inotify/inotify.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/inotify/inotify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/inotify/inotify_fsnotify.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/inotify/inotify_fsnotify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/inotify/inotify_user.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/inotify/inotify_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/mark.c -->
# sources/distributed-fs/ceph-client/fs/notify/mark.c

## Purpose

`mark.c` implements fsnotify mark and connector lifetime, locking, reference counting, mask recalculation, object attachment, group attachment, lookup, clearing, unmount scanning, and asynchronous destruction. It is the concurrency core that makes inode/mount/superblock/mount-namespace watch lists safe for lockless SRCU event delivery.

## Important APIs, Types, and Functions

Key exported functions include `fsnotify_get_mark()`, `fsnotify_put_mark()`, `fsnotify_prepare_user_wait()`, `fsnotify_finish_user_wait()`, `fsnotify_detach_mark()`, `fsnotify_free_mark()`, `fsnotify_destroy_mark()`, `fsnotify_compare_groups()`, `fsnotify_unmount_inodes()`, `fsnotify_add_mark_locked()`, `fsnotify_add_mark()`, `fsnotify_find_mark()`, `fsnotify_clear_marks_by_group()`, `fsnotify_destroy_marks()`, `fsnotify_init_mark()`, `fsnotify_wait_marks_destroyed()`, and `fsnotify_init_connector_caches()`. Internal helpers manage connector allocation, sb info attachment, watched-object counters, inode references, mask recalculation, connector detachment, and reaper work.

## Control Flow

Adding a mark initializes group state, inserts the mark on the group's list under `group->mark_mutex`, attaches or creates an object connector, inserts the mark into the connector list sorted by group priority/address, updates superblock watched-object counters, sets the connector pointer, and recalculates object masks. Event delivery walks connector lists under `fsnotify_mark_srcu`; permission waits can pin marks with `fsnotify_prepare_user_wait()`, drop SRCU while waiting for userspace, then reacquire SRCU and put marks. Destroy paths detach a mark from the group list, drop the list reference, eventually remove it from the connector list on final put, detach empty connectors from objects, drop inode refs outside spinlocks, queue connectors and marks for SRCU-delayed free, and run delayed work reapers.

## State and Persistence Behavior

Persistent state includes object connector pointers in inodes, mounts, superblocks, and mount namespaces; connector mark lists; object aggregate masks; sb `fsnotify_sb_info` watched-object counters and inode connector list; mark flags/masks/refcounts; and global destroy queues. Inode connectors may hold inode references unless all attached marks are evictable. Superblock deletion waits for watched-object counters to fall to zero. Destroyed marks remain allocated until both refcount and SRCU grace period permit final backend free.

## Dependencies and Integration Points

It depends on fsnotify backend structures, VFS inode/mount/sb/mntns fields, SRCU, workqueues, slab caches, refcounts, spinlocks/mutexes, and atomic counters. Backends call it to create/destroy marks; `fsnotify.c` reads connector lists and aggregate masks; fdinfo walks group marks; superblock teardown calls unmount cleanup.

## Risks and Edge Cases

The lock order is strict: `group->mark_mutex`, then `mark->lock`, then `connector->lock`. Violating it risks deadlock. Connector detachment must handle concurrent group clear, object clear, event delivery, and evictable inode marks. A concurrent attach/detach can delay clearing inode refs to avoid losing required pins. Group priority sorting is required for fanotify classes and ignore-mask correctness. `fsnotify_clear_marks_by_group()` cannot safely free arbitrary list entries after dropping the mutex, so it repeatedly frees the first selected mark.

## Test Signals

Signals include lockdep coverage, KASAN/KCSAN race testing, fanotify/inotify mark add/remove/flush stress, unmount with watched inodes, inode eviction with evictable and non-evictable marks, permission waits during close, priority ordering across notification classes, and watched-object counter assertions during superblock deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/mark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/notification.c -->
# sources/distributed-fs/ceph-client/fs/notify/notification.c

## Purpose

`notification.c` implements generic fsnotify event queue operations. It generates rename synchronization cookies, inserts events with optional backend merge/hash hooks, handles queue overflow, wakes waiters and fasync listeners, removes/peeks queued events, destroys events through backend ops, and flushes group queues during teardown.

## Important APIs, Types, and Functions

Public functions are `fsnotify_get_cookie()`, `fsnotify_destroy_event()`, `fsnotify_insert_event()`, `fsnotify_remove_queued_event()`, `fsnotify_peek_first_event()`, `fsnotify_remove_first_event()`, and `fsnotify_flush_notify()`. `fsnotify_insert_event()` is the core queueing primitive used by higher-level add/overflow helpers.

## Control Flow

`fsnotify_insert_event()` takes `notification_lock`, rejects insertion if the group is shutting down, substitutes the per-group overflow event if the queue is full or the event already is overflow, optionally asks the backend merge hook to coalesce with a queued event, appends the selected event, calls the optional insert hook for backend hash tables, releases the lock, wakes blocking readers, and sends SIGIO. Readers call peek/remove under the same lock, then destroy or retain events according to backend semantics. Flush repeatedly removes and destroys all queued events.

## State and Persistence Behavior

The queue is `group->notification_list` protected by `notification_lock`; `group->q_len` tracks length and `group->max_events` enforces limits. Overflow events are per-group singleton objects and are not freed by generic destroy. Rename cookies are generated by a global atomic counter. Event lifetime after removal is the caller's responsibility.

## Dependencies and Integration Points

It depends on fsnotify groups, backend `free_event` ops, wait queues, fasync, spinlocks, and generic list operations. Fanotify adds merge hash hooks; inotify supplies a merge hook for consecutive duplicate events.

## Risks and Edge Cases

Overflow handling must queue only one overflow event while it is already queued. Destroying an event still on a list is a bug and guarded by lock-checked warnings. Merge hooks run under `notification_lock`, so they must be bounded. Queue shutdown must prevent new events from being appended during group teardown.

## Test Signals

Signals include queue overflow tests, duplicate merge tests, poll/read wakeups, fasync notification, group shutdown while producers race, and flush with queued normal and overflow events. Fanotify hash-table tests indirectly validate insert/unhash symmetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/notification.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nsfs.c -->
# sources/distributed-fs/ceph-client/fs/nsfs.c

## Purpose

`nsfs.c` implements the namespace pseudo filesystem used for namespace file descriptors such as `/proc/<pid>/ns/*`. It provides stable dentries/inodes for namespace objects, namespace ioctls, namespace path opening helpers, exportfs file-handle support, pseudo-fs initialization, and active-reference helpers for namespace proxy state.

## Important APIs, Types, and Functions

Important exported helpers include `nsfs_get_root()`, `ns_get_path_cb()`, `ns_get_path()`, `open_namespace_file()`, `open_namespace()`, `open_related_ns()`, `ns_get_name()`, `proc_ns_file()`, `ns_match()`, `is_current_namespace()`, `nsfs_init()`, `nsproxy_ns_active_get()`, and `nsproxy_ns_active_put()`. The main file op is `ns_ioctl()`. Exportfs support is provided by `nsfs_encode_fh()`, `nsfs_fh_to_dentry()`, `nsfs_export_open()`, and `nsfs_export_permission()`. Stashed dentry integration uses `nsfs_init_inode()`, `nsfs_put_data()`, and `nsfs_stashed_ops`.

## Control Flow

Namespace paths are created through `path_from_stashed()` using the namespace's stashed dentry and the global `nsfs_mnt`; this consumes or transfers namespace references depending on the helper. `ns_ioctl()` first validates the command and permissions, then handles related namespace opening, type/owner/id queries, pid translation relative to pid namespaces, mount namespace info, and next/previous mount namespace iteration with optional info copy and fd publication. Exportfs encoding writes namespace id/type/inum into a file handle; decoding validates the handle, looks up the namespace in the namespace tree under RCU, checks visibility/ownership rules, obtains a reference, and recreates a path from the stashed dentry.

## State and Persistence Behavior

Global state is `nsfs_mnt` and `nsfs_root_path`. Each nsfs inode stores `struct ns_common *` in `i_private`, uses the namespace inode number, and takes an active namespace reference in `nsfs_init_inode()`. Eviction drops the active ref, clears the inode, and calls the namespace put operation. Stashed dentries allow namespace file descriptors and bind mounts to preserve access to namespaces after tasks exit, and can resurrect namespace subtrees when other objects still pin them.

## Dependencies and Integration Points

The file integrates with proc namespace operations, namespace-specific `get/put/get_parent` callbacks, mount namespace tree iteration, pid/user/net/ipc/time/uts/cgroup namespace internals, pseudo fs helpers, exportfs, fd helpers, seq path display, and VFS file opening. It deliberately clears `SB_NOUSER` on the mounted nsfs superblock so namespace file handles can be user-visible where allowed.

## Risks and Edge Cases

Visibility and lifetime checks are critical. Some exportfs decoding is intentionally racy around active references but relies on `nsfs_init_inode()` resurrection behavior. PID namespace decoding rejects inactive current pid namespaces without a child reaper. Next/previous mount namespace ioctls require `may_see_all_namespaces()`. Extensible ioctl size handling must be forward/backward compatible. Namespace references are consumed by path creation helpers, so double put or leaked references are key risks.

## Test Signals

Signals include proc namespace fd open/readlink/ioctl tests, user namespace owner uid queries, pid translation ioctls, mount namespace info and next/previous iteration, permission checks without namespace visibility, bind-mounted namespace lifetime after task exit, exportfs file-handle encode/decode/open, and namespace teardown with active nsproxy references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nsfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/ntfs/Kconfig

## Purpose

This Kconfig file declares the legacy NTFS filesystem driver and its optional debugging and POSIX ACL support.

## Important APIs, Types, and Functions

Symbols are `NTFS_FS`, `NTFS_DEBUG`, and `NTFS_FS_POSIX_ACL`. `NTFS_FS` is a tristate that selects `NLS` and `FS_IOMAP`. `NTFS_DEBUG` depends on `NTFS_FS` and enables extra consistency checks/debug messages. `NTFS_FS_POSIX_ACL` depends on `NTFS_FS` and selects `FS_POSIX_ACL`.

## Control Flow

There is no runtime control flow. Kconfig selects dependencies and controls whether the NTFS driver is built in, modular, or omitted, and whether debug/ACL code paths are compiled.

## State and Persistence Behavior

The file owns no runtime state. It influences compiled feature availability and module build output.

## Dependencies and Integration Points

It integrates with the NTFS Makefile, NLS subsystem, iomap infrastructure, POSIX ACL support, and optional debug/sysctl behavior documented in the help text.

## Risks and Edge Cases

Selecting `FS_IOMAP` is required by the current NTFS address-space and iomap code. The ACL help text notes Linux-only ACL behavior that Windows ignores, which can surprise dual-boot or shared-media users. Debug support can be expensive when enabled at runtime.

## Test Signals

Build matrix coverage should include built-in, module, debug, and ACL combinations. Mount/read/write tests should run with `NTFS_FS=m/y`; ACL-specific xattr/permission tests apply only when ACL support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/ntfs/Makefile

## Purpose

The NTFS Makefile assembles the legacy NTFS driver object from its component source files and enables debug compilation flags when requested.

## Important APIs, Types, and Functions

The rule `obj-$(CONFIG_NTFS_FS) += ntfs.o` builds the module or built-in object. `ntfs-y` lists the component objects, including address-space operations, attributes, directory/file/inode logic, MFT handling, runlists, superblock, compression, iomap, quotas, object IDs, and block-device I/O. `ccflags-$(CONFIG_NTFS_DEBUG) += -DDEBUG` enables debug code.

## Control Flow

There is no runtime flow. Kbuild links the listed objects into `ntfs.o` when the config symbol is enabled.

## State and Persistence Behavior

The file owns no runtime state. It controls build composition and debug preprocessor state.

## Dependencies and Integration Points

It depends on Kconfig symbols and integrates all NTFS source modules into one driver. The inclusion of `iomap.o` and `aops.o` reflects the driver's use of iomap for page-cache and writeback operations.

## Risks and Edge Cases

Omitting an object from `ntfs-y` can silently remove a feature or cause missing symbols. The debug flag must remain conditional because `-DDEBUG` changes logging/checking behavior across all compiled NTFS objects.

## Test Signals

Build `CONFIG_NTFS_FS=y` and `m`, with and without `CONFIG_NTFS_DEBUG`, and verify `ntfs.o` links all listed objects. Runtime mount smoke tests catch missing object integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/aops.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/aops.c

## Purpose

`aops.c` implements NTFS address-space operations and page-cache handling. It provides folio read, readahead, writeback, block mapping, swap activation, and NTFS-specific read completion zeroing around initialized size, mostly through Linux iomap helpers.

## Important APIs, Types, and Functions

Important functions are `ntfs_read_folio()`, `ntfs_bmap()`, `ntfs_readahead()`, `ntfs_writepages()`, `ntfs_swap_activate()`, and the read completion helpers `ntfs_iomap_read_end_io()` and `ntfs_iomap_bio_submit_read()`. Exported operation tables are `ntfs_aops` and `ntfs_mft_aops`. The file defines `ntfs_iomap_bio_read_ops` to plug NTFS-specific bio completion into generic iomap read logic.

## Control Flow

Reads call `ntfs_read_folio()`, which rejects encrypted attributes, delegates compressed nonresident data streams to `ntfs_read_compressed_block()`, and otherwise calls `iomap_read_folio()` with NTFS read iomap ops. Submitted bios complete through `ntfs_iomap_read_end_io()`, which converts block status, iterates folios, zeroes bytes beyond `initialized_size` within partially initialized ranges, and finalizes folio read state. Readahead skips resident and compressed files, then calls `iomap_readahead()`. Writeback rejects shutdown volumes, ignores resident attributes, rejects encrypted files, and calls `iomap_writepages()`. `ntfs_bmap()` maps initialized, nonresident, nonencrypted, non-MST-protected data blocks from VCN to LCN under the runlist lock and returns device block numbers or zero for holes/errors.

## State and Persistence Behavior

The file operates on page-cache folios and NTFS inode state. It reads `initialized_size` and `i_size` under `size_lock`, reads runlists under `runlist.lock`, and uses volume geometry to convert clusters to block units. It does not persist metadata itself, but writeback through `ntfs_writeback_ops` persists dirty page-cache data. `ntfs_mft_aops` uses `ntfs_mft_writepages` for MFT-specific persistence.

## Dependencies and Integration Points

It depends on NTFS inode/volume helpers, runlist mapping, compression support, debug logging, iomap read/writeback/swap helpers, Linux writeback, folio, bio, and address-space APIs. Operation tables are installed on NTFS inodes by the broader NTFS inode/superblock code.

## Risks and Edge Cases

Encrypted I/O is unsupported and must fail consistently. Compressed streams bypass generic iomap read and lack readahead here. Reads crossing initialized size must zero the uninitialized tail to avoid stale data exposure. `bmap()` cannot distinguish holes from errors or a real physical block zero, so it logs and returns zero. Large physical block numbers can truncate on narrow `sector_t`. Writeback during volume shutdown returns `-EIO`.

## Test Signals

Signals include generic fsx/xfstests-style buffered read/writeback, sparse file reads, initialized-size boundary reads, compressed file reads, encrypted-file error paths, readahead behavior on resident/compressed/nonresident files, `bmap()` on allocated/hole/out-of-range blocks, swapfile activation, MFT writeback, shutdown writeback failure, and KASAN/KMSAN checks for stale data after partial reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/aops.c -->
