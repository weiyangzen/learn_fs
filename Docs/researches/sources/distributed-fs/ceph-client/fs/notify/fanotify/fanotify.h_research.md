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
