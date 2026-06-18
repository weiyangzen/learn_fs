# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_catas.c

## Purpose
`mthca_catas.c` polls the firmware catastrophic-error buffer, dispatches fatal device events, logs diagnostic words, and optionally schedules PCI-level device restart.

## Important APIs, types, and functions
`mthca_start_catas_poll()` maps the catastrophic buffer and starts a timer. `poll_catas()` scans for nonzero error words. `handle_catas()` marks the device inactive, dispatches `IB_EVENT_DEVICE_FATAL`, decodes error type, logs the buffer, and queues reset work unless `catas_reset_disable` is set. `catas_reset()` restarts queued devices under `mthca_device_mutex`. `mthca_stop_catas_poll()`, `mthca_catas_init()`, and `mthca_catas_cleanup()` manage timer, list, and workqueue lifecycle.

## Control flow
Probe code starts polling after firmware reports the catastrophic buffer address. The timer runs every five seconds. On first detected error, the device is marked inactive and added to a global reset list; ordered work removes devices from the list and calls `__mthca_restart_one()`.

## State and persistence
State includes per-device mapped MMIO buffer address/size, timer, list node, global reset list, global spinlock, ordered workqueue, and module parameter `catas_reset_disable`. Firmware persists the error words until reset or cleanup.

## Dependencies and integration points
It depends on firmware data collected by `mthca_QUERY_FW()`, PCI BAR0 mapping, RDMA event dispatch, main-driver restart/remove/probe code, and global device mutex serialization.

## Risks
`mthca_stop_catas_poll()` unconditionally `list_del()`s the device list node after timer deletion; correctness depends on initialization and reset-list state. Restart invalidates `dev` while work still holds only the PCI pointer after the call. Fatal event dispatch races with user verbs and teardown. Polling interval means detection is delayed.

## Test signals
Inject catastrophic buffer words of each type, verify fatal IB event delivery, logging, no-reset module parameter behavior, successful and failed restart, remove while timer/reset work is pending, repeated catastrophic detections, and lockdep coverage around `mthca_device_mutex` plus `catas_lock`.
