# sources/distributed-fs/ceph-client/drivers/hwmon/occ/sysfs.c

Purpose: common non-hwmon control/status sysfs group for OCC devices. It exposes OCC active state, master status, throttling/error indicators, state/mode/IP status, OCC count, GPU throttle bits, and transfer error state.

Important APIs/types/functions: `occ_active_store()` toggles common activation. `occ_sysfs_show()` reads indexed status attributes from the latest poll response. `occ_error_show()` returns `occ->error`. `occ_sysfs_poll_done()` sends sysfs notifications when selected status bits change. `occ_setup_sysfs()` and `occ_shutdown_sysfs()` create/remove the group.

Control flow: setup creates attributes directly on `occ->bus_dev->kobj`, separate from the hwmon device. Reads poll through `occ_update_response()` when active; inactive reads return `0` for `occ_active` and `-ENODATA` values for status-like attributes. After every poll, common code calls `occ_sysfs_poll_done()`, which compares current header fields with previous cached fields and calls `sysfs_notify()` for changed error-relevant attributes.

State and persistence: previous status/error fields live in `struct occ` and are updated after each poll. The sysfs group persists for the transport device lifetime, even while hwmon sensor attributes can be inactive.

Dependencies and integration: depends on sysfs, hwmon sensor-device attributes for indexed control files, bitops, hweight, and `common.h` response layout. `occ_active` bridges userspace activation to `occ_active()`.

Risks: `occ_error_show()` ignores the return value of `occ_update_response()` and reports the stored error. Notifications are intentionally absent for `occ_state`, so listeners must poll it. Inactive status attributes return a negative integer string rather than a read error, except invalid indices.

Test signals: sysfs group creation/removal, active toggling, inactive reads, changed-bit notifications for master/DVFS/memory/quick-drop/VDD/GPU/IP/mode/error, OCC count behavior on master versus non-master, and interaction with common polling rate limits.
