## sources/distributed-fs/ceph-client/drivers/dma-buf/sync_debug.c

### Purpose
`sync_debug.c` creates the `debugfs/sync` directory and exposes debug/validation views for software sync timelines. It tracks live timelines globally and provides `info` and `sw_sync` debugfs files.

### Important APIs, Types, And Functions
The public helpers for the software sync implementation are `sync_timeline_debug_add()` and `sync_timeline_debug_remove()`. Internals include global `sync_timeline_list_head`, `sync_timeline_list_lock`, `sync_status_str()`, `sync_print_fence()`, `sync_print_obj()`, `sync_info_debugfs_show()`, `DEFINE_SHOW_ATTRIBUTE(sync_info_debugfs)`, and `sync_debugfs_init()`.

### Control Flow, State, And Persistence
`sync_debugfs_init()` runs as a `late_initcall`, creates `debugfs/sync`, then creates `info` and `sw_sync` with `debugfs_create_file_unsafe()` because entries are never removed. Timeline add/remove operations splice timeline objects into a global list under a spinlock. The `info` show path disables IRQs while walking the global list, then prints each timeline name/value and its active fences under the timeline lock.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on `CONFIG_DEBUG_FS`, `seq_file`, debugfs, `sync_debug.h`, and `sw_sync_debugfs_fops` from `sw_sync.c`. It integrates with fence timestamps and status via `dma_fence_get_status_locked()` and `dma_fence_parent()`. Risks include debugfs lifetime assumptions, holding the global list lock while printing many timelines, lock nesting with per-timeline locks, and stale timeline list membership if create/free paths diverge. Test signals include mounting debugfs, reading `sync/info` with no timelines and with active/signaled/error fences, concurrent timeline open/close while reading, and verifying `sync/sw_sync` file operations are reachable.
