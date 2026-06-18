# sources/distributed-fs/ceph-client/tools/include/uapi/linux/fanotify.h

Purpose: defines the fanotify userspace ABI for filesystem event monitoring and permission decisions. It includes event masks, initialization/mark flags, variable-length event records, permission response records, and iteration helpers.

Important APIs/types: event bits include access, modify, open, close, move, create/delete, exec, overflow, filesystem error, permission events, pre-access, mount attach/detach, child events, rename, and directory events. Init flags define notification/content classes and report formats (`FAN_REPORT_FID`, `FAN_REPORT_NAME`, `FAN_REPORT_PIDFD`, `FAN_REPORT_MNT`). Mark flags target inodes, mounts, filesystems, and mount namespaces. Structures include `fanotify_event_metadata`, `fanotify_event_info_header`, FID/pidfd/error/range/mount info records, `fanotify_response`, and audit-rule response info. Macros `FAN_EVENT_NEXT` and `FAN_EVENT_OK` walk event buffers.

Control flow, state, and persistence: userspace calls `fanotify_init`, adds marks, reads event buffers containing metadata plus optional info records, and writes `fanotify_response` for permission events. Kernel state persists in fanotify groups and marks until removed or the fd closes.

Dependencies and integration points: depends on Linux integer/fsid types and integrates with VFS, mount notifications, audit, file handles, pidfds, and permission mediation services.

Risks and test signals: risks include buffer-walk bugs, unsupported flag combinations, stale deprecated `FAN_ALL_*` masks, missing permission replies, and variable-length FID/name parsing errors. Tests should exercise each report mode, permission allow/deny including `FAN_DENY_ERRNO`, queue overflow, mount events, rename old/new FIDs, and mixed metadata records.
