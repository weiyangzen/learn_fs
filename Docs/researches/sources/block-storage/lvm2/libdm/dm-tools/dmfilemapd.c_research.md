# File Research: sources/block-storage/lvm2/libdm/dm-tools/dmfilemapd.c

## Purpose
Implements `dmfilemapd`, a small daemon that keeps dm-stats filemap regions synchronized with a changing file. It monitors a file by path or inode, reacts to inotify changes, updates dm-stats regions from the file descriptor, and exits when the monitored group disappears or the file no longer has relevant regions.

## Main Responsibilities
- Parse daemon arguments: file descriptor, stats group id, absolute path, follow mode, optional foreground flag, and optional log verbosity.
- Set libdm logging behavior for foreground/background operation.
- Monitor file modifications/deletions through inotify.
- Track allocated block count with `fstat()` and use it as a heuristic for deciding when file extents may have changed.
- Recompute stats regions with `dm_stats_update_regions_from_fd()`.
- In inode-follow mode, detect unlink-and-final-close shutdown conditions.
- Daemonize safely while preserving the monitored file descriptor.

## Key Functions
- `_parse_args()` validates and stores runtime configuration in `struct filemap_monitor`.
- `_setup_logging()` installs dmfilemapd-specific logging callbacks.
- `_is_open()` and `_is_open_in_pid()` scan `/proc/*/fd` for deleted open-file references, used only as a heuristic for inode-follow shutdown.
- `_filemap_monitor_set_notify()` creates a nonblocking inotify instance and watches the path for `IN_MODIFY` and `IN_DELETE_SELF`.
- `_filemap_monitor_get_events()` drains inotify events, marks deletion, requests extent checks on modification, and reopens/re-watches path-followed files.
- `_filemap_monitor_check_file_unlinked()` determines whether the original file descriptor still matches the path or has become deleted/anonymous.
- `_daemonize()` calls `setsid()`, forks, optionally redirects stdio to `/dev/null`, and closes stray fds while preserving the monitored fd.
- `_update_regions()` calls `dm_stats_update_regions_from_fd()`, counts returned regions, updates group id if the leader changed, and records region count.
- `_dmfilemapd()` is the main loop: bind stats handle, set notify, list stats, process events, update regions, check termination conditions, and sleep between iterations.
- `main()` parses args, configures logging, optionally daemonizes, and runs the daemon.

## Modes
- `inode`: follows the opened inode. If the file is unlinked, the daemon continues while another process still holds it open and exits once it appears closed.
- `path`: follows the pathname. On events, the daemon closes and reopens the path so replacement files can be tracked.

## Edge Cases and Invariants
- The path argument must be absolute.
- The daemon assumes at least one region exists at startup and obtains the exact count after the first update.
- Inotify is nonblocking; `EAGAIN` and `EINTR` are nonfatal.
- Deleted-file open detection via `/proc` is explicitly heuristic and can miss short-lived opens or produce false positives for reused paths.
- `dm_stats_group_present()` disappearing is a normal exit condition.
- Zero updated regions is treated as “file contains no extents” and exits the loop.
