# sources/distributed-fs/ceph-client/net/bridge/br_stp_if.c

## Purpose
`br_stp_if.c` connects the STP state machine to bridge and port lifecycle/configuration. It initializes ports, enables/disables STP on bridges and ports, coordinates optional userspace STP helper startup, recalculates bridge IDs, and applies bridge/port priority and path-cost changes.

## Important APIs, types, and functions
- `br_init_port()` initializes port ID, designated info, blocking state, pending flags, and offloaded ageing time.
- `br_stp_enable_bridge()` / `br_stp_disable_bridge()` start/stop bridge-level STP timers/work and enable/disable all ports.
- `br_stp_enable_port()` / `br_stp_disable_port()` transition individual ports and clean timers/FDB/multicast state.
- `br_stp_set_enabled()` owns STP enable/disable requests and rejects STP when MRP is active.
- `br_stp_start()` and `br_stp_stop()` choose user STP or kernel STP and call `/sbin/bridge-stp` in auto mode for `init_net`.
- `br_stp_change_bridge_id()`, `br_stp_recalculate_bridge_id()`, `br_stp_set_bridge_priority()`, `br_stp_set_port_priority()`, and `br_stp_set_path_cost()` update identifiers and recompute state.

## Control flow
Enabling a bridge takes `br->lock`, starts the hello timer for kernel STP, schedules FDB GC, generates config BPDUs, and enables running/up ports. `br_stp_set_enabled()` starts from no-STP by trying the userspace helper in auto mode; success or explicit user mode sets `BR_USER_STP`, otherwise kernel STP starts timers and runs port selection.

Disabling a port designates it locally, sets disabled state, notifies netlink, deletes its STP timers, flushes FDB entries if no backup port is configured, disables multicast, recomputes root/designated state, and if the bridge becomes root, calls `br_become_root_bridge()`.

Bridge ID changes update the FDB local MAC, netdevice hardware address, any port designated/root IDs that referenced the old address, then recompute STP state. Automatic bridge ID recalculation picks the lowest member port MAC unless the user set a bridge MAC.

## State and persistence
All state is in bridge/port STP fields, timers, FDB, multicast context, and `stp_helper_active`. The userspace helper execution is transient; no file-backed persistence is maintained by this code.

## Dependencies and integration points
The file integrates with RTNL callers, `call_usermodehelper()`, switchdev ageing-time offload through `__set_ageing_time()`, FDB address/flush helpers, multicast port enable/disable, MRP exclusion, rtnetlink notifications, and netdevice address assignment.

## Risks and edge cases
Userspace helper startup is only attempted in `init_net` auto mode; failure falls back to kernel STP except explicit user mode. Port priority is limited by `BR_PORT_BITS`, so high bits are dropped into the port ID layout. Disabling a port with a backup port avoids FDB flush. Locking spans state-machine recomputation and helper-active changes must not race lifecycle.

## Test signals
Test STP enable/disable with helper present/missing/failing, explicit user mode, MRP conflict, port up/down enable paths, bridge MAC auto recalculation, user-set MAC preservation, port priority/path cost bounds, and FDB flush behavior with/without backup ports.
