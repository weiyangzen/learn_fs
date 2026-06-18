# Research: sources/distributed-fs/ceph-client/fs/notify/fanotify/fanotify.c

## Purpose

This file is the core fanotify fsnotify backend. It filters fsnotify events against fanotify marks, allocates the appropriate fanotify event representation, merges compatible queued events, handles permission-event waits, and frees event/group/mark resources.

## Important APIs, Types, and Functions

Equality and hashing helpers include `fanotify_path_equal()`, `fanotify_hash_path()`, `fanotify_hash_fsid()`, `fanotify_fh_equal()`, `fanotify_hash_fh()`, `fanotify_fid_event_equal()`, `fanotify_info_equal()`, `fanotify_name_event_equal()`, and `fanotify_error_event_equal()`. `fanotify_should_merge()` and `fanotify_merge()` implement queue coalescing with `FANOTIFY_MAX_MERGE_EVENTS`.

Permission flow is handled by `fanotify_get_response()`. Event mask filtering is handled by `fanotify_group_event_mask()`. File-handle support is provided by `fanotify_encode_fh_len()` and `fanotify_encode_fh()`. Event identity decisions use `fanotify_report_child_fid()`, `fanotify_fid_inode()`, and `fanotify_dfid_inode()`.

Allocation paths include `fanotify_alloc_path_event()`, `fanotify_alloc_mnt_event()`, `fanotify_alloc_perm_event()`, `fanotify_alloc_fid_event()`, `fanotify_alloc_name_event()`, `fanotify_alloc_error_event()`, and the dispatcher `fanotify_alloc_event()`. Delivery is handled by `fanotify_handle_event()`. Free paths include `fanotify_free_group_priv()`, per-event-type free helpers, `fanotify_free_event()`, `fanotify_freeing_mark()`, and `fanotify_free_mark()`. The exported backend vtable is `fanotify_fsnotify_ops`.

## Control Flow

Fsnotify calls `fanotify_handle_event()`. The handler verifies compile-time mask equivalence with `BUILD_BUG_ON`, derives a user-visible event mask through `fanotify_group_event_mask()`, prepares user waits for permission events, obtains cached fsid for FID mode, allocates a matching event object, queues it with `fsnotify_insert_event()`, and for permission events waits in `fanotify_get_response()` until userspace allows, denies, supplies a custom errno, or the waiter is interrupted.

Mask filtering considers report mode (`FAN_REPORT_MNT`, path mode, FID mode), object availability, mark masks, ignore masks, and whether event flags should be visible to userspace. Allocation selects event type based on group flags and data: permission path events, filesystem error events, name/FID events for directory and rename reporting, plain FID events, path events, or mount-id events. Merge logic hashes comparable event identity and never merges permission or mount events.

## State and Persistence Behavior

Fanotify state is held in `fsnotify_group` private data, notification queues, merge hash buckets, memcg charging context, mempools for error events, refcounted paths, pids, file handles, and mark accounting. Permission events carry state transitions `FAN_EVENT_INIT`, `FAN_EVENT_REPORTED`, `FAN_EVENT_ANSWERED`, and `FAN_EVENT_CANCELED`. No data is persisted on disk; state persists until userspace reads/responds, queues merge, overflow handling occurs, or group/mark teardown frees resources.

## Dependencies and Integration Points

The file depends on the fsnotify backend ABI, exportfs file-handle encoding, fanotify internal types from `fanotify.h`, audit hooks, memcg charging, wait queues, pid references, mount/path/dentry/inode data extraction, and user namespace/ucount accounting. It is paired with `fanotify_user.o`, which creates groups, reads events, and supplies permission responses.

## Risks

Permission-event races are high risk: interruption before userspace reads the event, cancellation after reporting, and answer/wakeup races must preserve correct frees and access decisions. Event merging must not merge events that userspace needs to distinguish, especially directory-vs-file events, rename records, permission events, and events without stable file handles. FID encoding failures intentionally degrade to invalid handles for some events; filesystem exportfs behavior affects fanotify semantics. Memory allocation policy differs for unlimited queues and limited queues, with security implications for lost events and OOM behavior. Refcounting of paths, pids, external file-handle buffers, mempool objects, and ucounts must match allocation type.

## Test Signals

Exercise path, FID, directory-FID, name, target-FID, rename, mount, overflow, permission, pre-access, and filesystem-error events. Verify merge behavior for identical paths/FIDs/names/errors and non-merge behavior for permission, mount, directory flag changes, and rename distinctions. Test userspace allow/deny/custom-errno/audit responses, signal interruption, group teardown while waiting, file-handle encode failure, no-fsid or weak-fsid marks, memory pressure, memcg charging, and mark/group accounting on free.
