# sources/distributed-fs/ceph-client/samples/fanotify/fs-monitor.c

Purpose: user-space sample that subscribes to `FAN_FS_ERROR` events for a filesystem and prints error and file-handle metadata.

Important APIs/functions: `fanotify_init(FAN_CLASS_NOTIF | FAN_REPORT_FID)`, `fanotify_mark(... FAN_MARK_FILESYSTEM, FAN_FS_ERROR, ...)`, `FAN_EVENT_OK`, `FAN_EVENT_NEXT`, `fanotify_event_info_error`, and `fanotify_event_info_fid`.

Control flow: requires a path argument, initializes fanotify, marks the filesystem, then continuously reads events into a buffer. `handle_notifications` validates event masks/fds and iterates variable-length info records for error and FID details.

State and persistence: fanotify file descriptor and stack buffer; output is printed to stdout. No persistence.

Dependencies and integration: depends on fanotify filesystem error reporting and UAPI definitions, with local fallback definitions for older libc headers.

Risks: infinite loop with fatal `errx` on read/mark failures. File handle decoding only recognizes `FILEID_INO32_GEN` and invalid superblock errors. Requires privileges sufficient for filesystem marks.

Test signals: run against a filesystem path as root or with appropriate capabilities, inject or provoke fs errors on a supporting filesystem, and inspect printed error count and FID records.
