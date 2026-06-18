<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_switchdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_switchdev.c

## Purpose

`icssg_switchdev.c` implements Linux switchdev notifier handling for ICSSG switch mode. It translates bridge STP state, bridge port flags, FDB events, VLAN objects, and MDB objects into ICSSG firmware port-state, VLAN table, PVID, and FDB updates.

## Important APIs, Types, and Functions

Exported functions are `prueth_switchdev_register_notifiers()` and `prueth_switchdev_unregister_notifiers()`. Important local pieces include `struct prueth_switchdev_event_work`, `prueth_switchdev_attr_set()`, STP and bridge flag helpers, `prueth_switchdev_event()`, async `prueth_switchdev_event_work()`, VLAN add/delete helpers, MDB add/delete helpers, object add/delete callbacks, and blocking notifier handling.

## Control Flow

Registration installs one atomic switchdev notifier and one blocking notifier. Attribute events may be handled directly through `switchdev_handle_port_attr_set()`. FDB add/delete events allocate work, copy the FDB address, hold the netdev, and process under RTNL in `system_long_wq`; user-added FDB entries matching the port MAC are programmed via `icssg_fdb_add_del()` and add events notify `SWITCHDEV_FDB_OFFLOADED`. Blocking object events synchronously dispatch VLAN and MDB add/delete to firmware table helpers.

## State and Persistence Behavior

The file mutates firmware port state, VLAN membership/untag masks, PVID values, and FDB/MDB entries. It does not own long-lived state except notifier blocks stored in `struct prueth` and temporary work items.

## Dependencies and Integration Points

It depends on Linux switchdev, bridge flags/VLAN/MDB objects, netdevice helpers, workqueues, `prueth_dev_check()` from the main driver, and config helpers `icssg_set_port_state()`, `icssg_vtbl_modify()`, `icssg_set_pvid()`, `icssg_get_pvid()`, `icssg_fdb_add_del()`, and `icssg_fdb_lookup()`.

## Risks and Edge Cases

`prueth_switchdev_attr_br_flags_set()` checks `mask` rather than `val`, so multicast flooding enable/disable semantics should be verified against intended bridge flag handling. FDB add/delete filters to entries equal to `emac->mac_addr`, which may ignore learned/static entries for other MACs depending on switchdev expectations. VLAN IDs above `0xff` are ignored because firmware paths support only 256 VLAN IDs. Async FDB work must balance `dev_hold()`/`dev_put()` and free copied addresses on all paths.

## Test Signals

Bridge tests should cover STP disabled/blocking/listening/forwarding states, multicast flood flag changes, VLAN add/delete with PVID and untagged flags on bridge and port devices, MDB host/port add/delete, static FDB add/delete, switchdev offload notifications, and notifier unregister during device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_switchdev.c -->
