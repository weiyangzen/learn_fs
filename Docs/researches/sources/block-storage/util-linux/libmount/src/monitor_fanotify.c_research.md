# File Research: sources/block-storage/util-linux/libmount/src/monitor_fanotify.c

This file implements the fanotify-based kernel mount table monitor. It is compiled only when `HAVE_STRUCT_FANOTIFY_EVENT_INFO_HEADER` is available; otherwise `mnt_monitor_enable_fanotify()` returns `-ENOTSUP`. The backend targets modern Linux fanotify mount-namespace notifications and can report affected mount IDs, unlike the classic `/proc/self/mountinfo` epoll monitor.

The compatibility block defines missing `FAN_MNT_ATTACH`, `FAN_MNT_DETACH`, `FAN_REPORT_MNT`, `FAN_MARK_MNTNS`, and `struct fanotify_event_info_mnt` for build environments older than the target kernel API. Backend-private data stores the watched namespace fd plus a buffer, current pointer, and remaining byte count for parsed fanotify records.

`fanotify_get_fd()` creates a nonblocking close-on-exec fanotify fd with `FAN_REPORT_MNT`, then marks the mount namespace fd with `FAN_MARK_ADD | FAN_MARK_MNTNS` for attach and detach events. `fanotify_process_event()` reads into the private buffer and initializes iteration state. If `mn->kernel_veiled` is set and `MNT_PATH_UTAB ".act"` exists, it drains all pending fanotify data and reports no accepted event, allowing libmount userspace updates to hide duplicate kernel notifications.

`fanotify_next_fs()` parses one buffered fanotify record at a time. It validates `FAN_EVENT_OK()` and metadata version, extracts the mount event info, resets the supplied `libmnt_fs` while preserving its statmount reference, sets `uniq_id` from `mnt_id`, and marks the fs as attached or detached based on `meta->mask`. The buffer pointer advances with `FAN_EVENT_NEXT()`, returning `1` when no more event data remains.

`mnt_monitor_enable_fanotify()` supports multiple fanotify monitors on one `libmnt_monitor`, keyed by namespace fd. Passing `ns < 0` opens `/proc/self/ns/mnt` privately and uses that path as the event name; passing an fd uses `/proc/self/fd/<fd>` as the path and treats the fd as application-owned. Disable paths remove the entry from epoll and close only the fanotify fd.
