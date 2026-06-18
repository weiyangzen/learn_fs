<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsdvb-debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/smsdvb-debugfs.c

## Purpose
`smsdvb-debugfs.c` provides optional debugfs visibility into Siano DVB statistics. It creates a debugfs directory for USB Siano DVB devices and exposes a `stats` file that blocks or polls until the next statistics update is captured from the DVB response path.

## Important APIs, Types, and Functions
The private `struct smsdvb_debugfs` holds a kref, spinlock, one `PAGE_SIZE` text buffer, byte count, read-state flag, and waitqueue. Formatting functions are `smsdvb_print_dvb_stats()`, `smsdvb_print_isdb_stats()`, and `smsdvb_print_isdb_stats_ex()`. File operations are `smsdvb_stats_open()`, `smsdvb_stats_poll()`, `smsdvb_stats_read()`, and `smsdvb_stats_release()`. Public integration functions are `smsdvb_debugfs_create()`, `smsdvb_debugfs_release()`, `smsdvb_debugfs_register()`, and `smsdvb_debugfs_unregister()`.

## Control Flow
Module init in `smsdvb-main.c` calls `smsdvb_debugfs_register()`, creating `<debugfs>/usb/smsdvb`. On each DVB client creation, `smsdvb_debugfs_create()` checks that the root exists and the core device is USB, allocates debug state, creates a per-device directory named by `coredev->devpath`, creates the `stats` file, and installs print callbacks into `smsdvb_client_t`.

When the DVB response path updates statistics, it invokes the relevant print callback. The callback locks the debug state, refuses to overwrite an unread snapshot, emits key/value lines with `sysfs_emit_at()`, stores `stats_count`, unlocks, and wakes the waitqueue. A reader opening `stats` resets the snapshot state; `read()` blocks unless nonblocking, returns the buffered snapshot, and then marks EOF for the open instance.

## State and Persistence Behavior
State is per DVB client and transient. It stores only the latest unread formatted statistics page for the current open/read cycle. `kref` prevents freeing while file operations are active. There is no persistence beyond the debugfs lifetime.

## Dependencies and Integration Points
This file depends on debugfs, usb debug root, DVB headers, `smscoreapi.h`, and `smsdvb.h`. It is compiled only when enabled by config and otherwise replaced by no-op inline functions in `smsdvb.h`. It is tightly coupled to statistics structures from `smscoreapi.h` and callback slots in `smsdvb_client_t`.

## Risks and Test Signals
The one-page buffer and `sysfs_emit_at()` limit output size, but additions should watch for truncation. The design intentionally drops new stats if a previous snapshot is unread. `smsdvb_debugfs_create()` creates the file without checking `debugfs_create_*` errors, which is common for debugfs but worth noting. It only supports USB-root placement; comments flag missing SDIO-style support.

Test signals include successful creation/removal of `<debugfs>/usb/smsdvb/<devpath>/stats`, blocking reads that wake after statistics requests, poll returning readable once `stats_count` is set, no use-after-free during concurrent remove/read, and callbacks being cleared on release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsdvb-debugfs.c -->
