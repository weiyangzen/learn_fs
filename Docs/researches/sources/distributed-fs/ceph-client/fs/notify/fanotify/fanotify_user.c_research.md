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
