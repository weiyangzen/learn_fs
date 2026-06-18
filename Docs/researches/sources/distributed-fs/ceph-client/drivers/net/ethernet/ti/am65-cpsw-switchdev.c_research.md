# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-switchdev.c

## Purpose
Implements switchdev offload translation for AM65 CPSW switch mode. It maps bridge attributes, VLAN objects, MDB objects, and FDB add/delete notifications into CPSW ALE operations, and registers the switchdev notifier blocks used by the main NUSS driver.

## Important APIs, Types, and Functions
The exported APIs are `am65_cpsw_switchdev_register_notifiers` and `am65_cpsw_switchdev_unregister_notifiers`. Internal functions include `am65_cpsw_port_stp_state_set`, bridge-flag validators/setters, `am65_cpsw_port_vlan_add/del`, `am65_cpsw_port_mdb_add/del`, `am65_cpsw_port_obj_add/del`, `am65_cpsw_switchdev_event`, `am65_cpsw_switchdev_blocking_event`, and asynchronous `am65_cpsw_switchdev_event_work`. `struct am65_cpsw_switchdev_event_work` carries deferred FDB events plus a held netdev reference.

## Control Flow
Blocking notifier events handle bridge object add/delete and attribute set synchronously through switchdev helper dispatch, first filtering devices with `am65_cpsw_port_dev_check`. STP bridge states are converted to ALE port states. Bridge flags currently validate only learning and multicast flood masks, and implement multicast flood through ALE unregistered multicast control. VLAN add determines whether the object is for the CPU/bridge master or a front-panel port, computes ALE membership/untag/mcast masks, adds/modifies the ALE VLAN, optionally installs the CPU unicast entry, and updates PVID. VLAN delete removes the ALE VLAN membership, optional CPU unicast, PVID, and broadcast multicast entry. MDB add/delete programs ALE multicast entries for CPU or physical port masks.

Non-blocking FDB notifications are copied under RCU into `am65_cpsw_switchdev_event_work`, including a private address copy and `dev_hold`. The work item runs under RTNL, ignores non-user/local entries, maps the port's own MAC to host port when needed, adds or deletes ALE unicast entries, emits an offloaded notification on add, then frees the address, work, and netdev reference.

## State and Persistence
The module has no durable software table of its own. Persistent offload state is in the CPSW ALE: port states, VLAN memberships, PVID registers, multicast entries, unregistered multicast flood settings, and FDB unicast entries. Temporary FDB state lives in queued work until processed.

## Dependencies and Integration Points
Depends on Linux bridge/switchdev notifier APIs, workqueues, RTNL, `am65-cpsw-nuss.h`, `am65-cpsw-switchdev.h`, and `cpsw_ale.h`. It is registered/unregistered by `am65-cpsw-nuss.c` only for multi-port switch-capable builds, while bridge membership and switch-mode eligibility are tracked in the main driver.

## Risks and Test Signals
Risks include notifier lifetime races, missed `dev_put`/address free on uncommon paths, stale ALE entries when bridge objects are removed in unusual order, unsupported bridge flags being accepted or rejected incorrectly, CPU-port VLAN semantics, and duplicate FDB offload notifications. Test signals include Linux bridge VLAN filtering, PVID/untagged changes, MDB joins/leaves, STP state transitions, multicast flood toggles, static FDB add/delete, port enslave/release, and module unload/remove while FDB work is pending.
