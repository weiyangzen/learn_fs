# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_switchdev.c

## Purpose
This file connects ICSSM switch mode to Linux switchdev. It handles STP state changes, static FDB add/delete notifications, host MDB add/delete notifications, and registration of normal and blocking switchdev notifiers.

## Important APIs, types, and functions
- `struct icssm_sw_event_work` carries deferred FDB event data, a held netdev reference, and a copied `switchdev_notifier_fdb_info`.
- `icssm_prueth_sw_set_stp_state()` and `_get_stp_state()` access shared-RAM STP state through `prueth->fdb_tbl`.
- `icssm_prueth_sw_attr_set()` handles `SWITCHDEV_ATTR_ID_PORT_STP_STATE`; state changes trigger dynamic FDB purge.
- `icssm_prueth_sw_switchdev_event()` handles nonblocking switchdev events and defers FDB add/delete work.
- `icssm_sw_event_work()` performs static FDB add/delete under RTNL and calls `SWITCHDEV_FDB_OFFLOADED` after successful user-added FDB offload.
- `icssm_prueth_switchdev_obj_add()` and `_del()` update firmware multicast filter bins for host MDB entries.
- `icssm_prueth_sw_blocking_event()` handles blocking object and attr updates.
- `icssm_prueth_sw_register_notifiers()` and `_unregister_notifiers()` install/remove notifier blocks stored in `struct prueth`.

## Control flow
For STP attr events, switchdev invokes the handler and the driver writes the new state into the FDB shared-memory STP byte. If the state changed, dynamic FDB entries are purged asynchronously. For FDB events, the notifier allocates work from atomic context, copies the notifier payload and MAC address, holds the netdev, and schedules `system_long_wq`. The worker runs under RTNL, ignores events when the interface/FDB is down, ignores non-user-added or local FDB additions, calls the switch FDB implementation, signals offload for accepted additions, then frees copied memory and drops the netdev reference. MDB events hash the multicast address using the EMAC hash helper and allow/disallow the corresponding firmware multicast bin, avoiding disallow when another bridge multicast address collides in the same bin.

## State and persistence behavior
State changes affect firmware-shared FDB/STP/multicast table memory and queued work items. Work items persist only until processed. Notifier registrations persist for the platform device lifetime and are removed in driver remove.

## Dependencies and integration points
The file depends on Linux switchdev, workqueue, netdevice reference tracking, RTNL, and local ICSSM PRU/FDB/switch APIs. It is called from the registration path in `icssm_prueth.c` and calls into `icssm_prueth_switch.c` and multicast helpers in `icssm_prueth.c`.

## Risks and edge cases
- FDB event allocation uses GFP_ATOMIC; failure returns `NOTIFY_BAD` for allocation errors and can drop offload updates.
- The FDB worker assumes copied `fdb_info.addr` is valid and frees it after use.
- MDB delete handles hash collisions only against bridge multicast addresses, not necessarily all port-local multicast state.
- STP and FDB paths no-op when `prueth->fdb_tbl` is NULL, so down interfaces can miss offload state transitions.
- `icssm_prueth_sw_set_stp_state()` uses `port - 1` to choose port1/port2 state; invalid port values would write the wrong field.

## Test signals
Use Linux bridge tests for STP state transitions, static FDB add/delete, `bridge fdb show` offloaded flag, MDB joins/leaves, multicast hash collision cases, notifier registration/unregistration during driver remove, and event delivery while ports are down/up.
