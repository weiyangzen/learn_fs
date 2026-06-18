# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_switchdev.c

## Purpose
`cpsw_switchdev.c` implements switchdev notifier handling for the CPSW switch-mode driver. It translates bridge STP state, bridge flags, VLAN objects, MDB objects, and FDB events into ALE port state and table updates.

## Important APIs, Types, And Functions
The file exposes `cpsw_switchdev_register_notifiers()` and `cpsw_switchdev_unregister_notifiers()`. Internal helpers include `cpsw_port_stp_state_set()`, `cpsw_port_attr_br_flags_set/pre_set()`, `cpsw_port_attr_set()`, PVID helpers, `cpsw_port_vlan_add()`, `cpsw_port_vlan_del()`, `cpsw_port_mdb_add()`, `cpsw_port_mdb_del()`, `cpsw_port_obj_add()`, `cpsw_port_obj_del()`, `cpsw_fdb_offload_notify()`, async `cpsw_switchdev_event_work()`, and notifier callbacks for atomic and blocking switchdev chains.

## Control Flow
Blocking notifier events handle port VLAN/MDB object add/delete and port attributes synchronously through switchdev helper dispatch filtered by `cpsw_port_dev_check()`. Atomic switchdev events either dispatch port attributes or allocate work for FDB add/delete, copy the FDB address, hold the netdev, and queue work on `system_long_wq`. The work item takes RTNL, ignores non-user or local FDB entries, maps local MAC entries to host port, programs ALE unicast add/delete with optional VLAN flag, notifies switchdev of offload on add, releases copied address and netdev reference, and frees work state.

## State And Persistence
Persistent state is mostly ALE hardware state: port STP state, VLAN member/untag/multicast masks, port PVID registers, multicast database entries, and static FDB unicast entries. No long-lived private state exists beyond queued work items. Bridge multicast-flood flags modify unregistered multicast masks across ALE VLAN entries.

## Dependencies And Integration Points
It depends on Linux bridge and switchdev APIs, workqueues, netdevice references, `cpsw_ale`, `cpsw_priv`, and `cpsw_switchdev.h`. It is registered by `cpsw_new.c` after common device setup and unregistered during remove.

## Risks
FDB events are asynchronous, so object lifetime is protected by copying the MAC address and holding the netdev; any new FDB fields would need similar handling. VLAN/PVID handling must distinguish CPU bridge master objects from physical port objects. `cpsw_port_attr_br_flags_pre_set()` accepts only learning and multicast flood masks, but learning is not acted on in the set path; this may rely on hardware learning defaults elsewhere. ALE errors from some cleanup operations are intentionally ignored. Queued work must be drained indirectly by notifier unregister and device teardown ordering.

## Test Signals
Test bridge enslave in switch mode, STP state transitions, `bridge vlan add/del` including PVID and untagged flags on ports and bridge master, `bridge mdb add/del`, static FDB add/delete with and without VID, offload notifications, multicast flood flag changes, rapid port unregister while FDB work is pending, and non-CPSW devices passing through notifiers untouched.
