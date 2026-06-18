# File Research: sources/block-storage/util-linux/libmount/src/monitor_utab.c

This file implements the userspace mount table monitor based on inotify. It watches libmount's private utab event file machinery rather than the kernel mount table directly. The default watched logical file is `mnt_get_utab_path()` (`/run/mount/utab` in normal builds), and the actual event file is `<utab>.event`.

Backend-private data stores the currently watched path, which may be the final event file or an ancestor directory. `userspace_add_watch()` first attempts to watch `<utab>.event` for `IN_CLOSE_WRITE | IN_DELETE_SELF`. If it does not exist, it walks up parent directories and watches the nearest existing directory for `IN_CREATE | IN_ISDIR | IN_DELETE_SELF`, remembering the chosen path to avoid redundant watches. This allows the monitor to survive missing `/run/mount` components and later event-file creation.

`userspace_monitor_get_fd()` opens a nonblocking close-on-exec inotify fd and installs the initial watch. `userspace_process_event()` drains the inotify buffer. `IN_CLOSE_WRITE` on the final event file is the meaningful change signal and returns success. Directory creation or self-delete events trigger watch re-evaluation; if a new watch replaces an old watch descriptor, the old watch is removed. `IN_DELETE_SELF` also frees saved backend data so the watch path can be rebuilt.

`mnt_monitor_enable_userspace()` creates or toggles the single userspace entry of type `MNT_MONITOR_TYPE_USERSPACE`. The filename parameter is honored only on first enable; subsequent toggles reuse the existing entry. Disabling removes the entry from epoll and closes the inotify fd, but keeps the entry available for re-enable.
