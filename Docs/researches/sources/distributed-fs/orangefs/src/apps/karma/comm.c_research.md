# sources/distributed-fs/orangefs/src/apps/karma/comm.c

## Purpose
`comm.c` is Karma's OrangeFS communication and data acquisition layer. It initializes the PVFS system interface, discovers configured file systems, builds the GUI filesystem list, tracks the active fsid, retrieves server statfs snapshots, and retrieves performance counter samples for the traffic page.

## Important APIs, Types, and Functions
Important global state includes parsed `PVFS_util_tab *tab`, `gui_comm_fslist`, current `PVFS_credential cred`, `cur_fsid`, internal/visible stat arrays, server BMI address arrays, error details, and performance history buffers. The local `struct PVFS_mgmt_perf_stat` adapts raw performance monitor data to Karma's older graph expectations.

`gui_comm_setup()` parses pvfstab, initializes `gui_comm_fslist`, calls `PVFS_sys_initialize()`, adds every configured filesystem with `PVFS_sys_fs_add()`, populates the GTK list store, generates default credentials, and selects the default filesystem. `gui_comm_set_active_fs()` updates the window title, counts servers, resizes internal arrays, obtains server addresses with `PVFS_mgmt_get_server_array()`, and allocates performance history structures. `gui_comm_stats_retrieve()` calls `gui_comm_stats_collect()` and copies internal stats to a stable visible buffer. `gui_comm_traffic_retrieve()` calls `gui_comm_perf_collect()` and summarizes raw counters into per-server `gui_traffic_raw_data`.

## Control Flow
Startup builds the list of configured filesystems before any page timers retrieve data. The active-fs setter is also invoked from the FS selection dialog. Status retrieval runs on a five-second timer from `karma.c`; traffic retrieval runs on a one-second timer. Management calls that return `-PVFS_EDETAIL` are treated as partial success: per-server errors are reported to the message pane and retrieval continues.

## State and Persistence
No disk persistence is created here. Runtime state is substantial and global: active fsid, reusable stat arrays, visible copies protected only by single-threaded GTK flow, performance IDs/end times, previous metadata counters, and server address arrays. `meta_read_prev` and `meta_write_prev` are process-global deltas and are not per-server, which affects traffic calculations when multiple servers are present or when active FS changes.

## Dependencies and Integration Points
The file integrates GTK list models with OrangeFS utility, system, management, server-config, BMI address, credential, and error-detail APIs. It feeds `fsview.c` through `gui_comm_fslist`, `status.c`/`details.c` through stat snapshots, `traffic.c` through raw traffic snapshots, and `karma.c` through timer callbacks.

## Risks and Edge Cases
Several allocations are unchecked or only assert-checked. Resizing in `gui_comm_set_active_fs()` frees `internal_perf[0]` and other arrays only when previous stats exist, but partial allocation failure paths are not handled. When `internal_stats` already exists with the same server count, `gui_comm_set_active_fs()` returns early after updating `cur_fsid`, leaving `internal_addrs` and performance buffers from the previous filesystem if two filesystems have the same server count. `visible_stats` is allocated once and copied using `visible_stat_ct`; if server count changes after initial allocation, it is not resized. `meta_read_prev`/`meta_write_prev` are global rather than per-server. The code uses `assert()` for config assumptions and fixed-size message buffers that can truncate server names/errors.

## Test Signals
Run Karma with pvfstab containing one filesystem, multiple filesystems with different server counts, and multiple filesystems with the same server count to catch stale address reuse. Inject `PVFS_EDETAIL` and full management failures. Exercise active FS switching while timers are running. Validate traffic deltas per server and after switching filesystems. Leak and allocation-failure testing should focus on setup, active-fs resize, and perf retrieval buffers.
