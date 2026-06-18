# File Research: sources/block-storage/util-linux/libmount/src/monitor.h

This private header defines the internal monitor data model shared by `monitor.c` and the backend implementations. It is not the public libmount API; it exposes only implementation structs and helper prototypes used inside `libmount/src`.

`struct monitor_entry` represents one monitored source. It stores a private backend fd, an external identifier (`id`, normally `-1` unless the backend supports multiple instances such as fanotify namespace fds), a display path returned to callers, a public `MNT_MONITOR_TYPE_*`, desired epoll events, backend operations, backend-private data, enabled/active booleans, and a list link. `active` means an accepted event is ready for `mnt_monitor_next_change()`.

`struct libmnt_monitor` owns a refcount, the top-level public epoll fd, the list of entries, a pointer to the last entry returned by `mnt_monitor_next_change()`, and `kernel_veiled`, which tells kernel-monitor backends to suppress events when a libmount userspace utab operation is active.

`struct monitor_opers` is the backend vtable. `op_get_fd` lazily opens or returns the backend fd, `op_close_fd` closes backend resources, `op_free_data` releases backend-private data, `op_process_event` validates and drains backend events, and `op_next_fs` optionally returns filesystem details for the last event. The helper prototypes (`monitor_modify_epoll`, `monitor_get_entry`, `monitor_new_entry`, `free_monitor_entry`) are the common entry-management API used by backend files.
