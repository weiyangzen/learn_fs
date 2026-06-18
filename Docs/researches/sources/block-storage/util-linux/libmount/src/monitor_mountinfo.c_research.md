# File Research: sources/block-storage/util-linux/libmount/src/monitor_mountinfo.c

This file implements the classic kernel mount table monitor based on epolling `/proc/self/mountinfo`. It is the portable fallback for detecting that the kernel mount table changed, but it does not identify which mount changed or how.

The backend operations are intentionally small. `mountinfo_get_fd()` opens the configured path read-only with `O_CLOEXEC` and reuses the fd after the first open. `mountinfo_close_fd()` closes it. `mountinfo_process_event()` accepts the event unless `mn->kernel_veiled` is enabled and `MNT_PATH_UTAB ".act"` exists, in which case it returns `1` so the top-level monitor treats the wakeup as not useful.

`mnt_monitor_enable_mountinfo()` creates a single entry of type `MNT_MONITOR_TYPE_MOUNTINFO` with path `_PATH_PROC_MOUNTINFO`. It uses `EPOLLIN | EPOLLET` rather than only `EPOLLPRI` or a passive fd because the top-level libmount monitor may itself be nested inside another epoll instance and callers need to identify which low-level fd fired. Since mountinfo would otherwise appear constantly readable, edge-triggered polling is paired with the initial drain in `monitor_modify_epoll()`.

`mnt_monitor_enable_kernel()` is a deprecated alias to `mnt_monitor_enable_mountinfo()`. `mnt_monitor_veil_kernel()` toggles duplicate suppression for kernel monitor backends during libmount-managed userspace table updates.
