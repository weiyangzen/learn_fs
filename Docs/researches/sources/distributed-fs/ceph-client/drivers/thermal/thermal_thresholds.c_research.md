# sources/distributed-fs/ceph-client/drivers/thermal/thermal_thresholds.c

## Purpose
`thermal_thresholds.c` implements user-defined thermal threshold lists used to request netlink notifications and update thermal trip windows when temperatures cross arbitrary user thresholds.

## Important APIs, Types, and Functions
The public API includes `thermal_thresholds_init`, `thermal_thresholds_flush`, `thermal_thresholds_exit`, `thermal_thresholds_handle`, `thermal_thresholds_add`, `thermal_thresholds_delete`, and `thermal_thresholds_for_each`. Internal helpers sort, find, evaluate raising/dropping crossings, and calculate next low/high boundaries.

## Control Flow
Initialization prepares `tz->user_thresholds`. Add either creates a sorted `user_threshold` entry or ORs an additional direction into an existing temperature. Delete removes a direction or frees the entry. Handle first updates low/high boundaries for hardware trip programming, then compares current and last temperatures to send up/down notifications only when a threshold was actually crossed.

## State and Persistence Behavior
Thresholds are heap-allocated list entries attached to the thermal zone and protected by the zone lock. They persist until explicit delete/flush or zone exit; there is no storage across reboot or driver removal.

## Dependencies and Integration Points
It depends on `thermal_core.h`, list sorting, netlink threshold notifications, and `__thermal_zone_device_update` reasons. Netlink command handlers are the main userspace mutation path.

## Risks and Edge Cases
Direction bitmasks must be validated by callers; this code accepts and stores the provided direction bits. Crossing detection needs a valid previous temperature and intentionally skips first samples and stable readings.

## Test Signals
Add/delete duplicate tests, sorted iteration, direction merge/split behavior, flush cleanup, first-sample no-event behavior, raising/dropping crossing notifications, and low/high boundary selection.
