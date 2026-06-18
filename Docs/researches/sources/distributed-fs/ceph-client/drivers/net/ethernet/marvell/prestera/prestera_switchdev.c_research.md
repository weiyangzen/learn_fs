# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_switchdev.c

## Purpose
This file implements Prestera switchdev offload for Linux bridges. It maintains software bridge, bridge-port, VLAN, FDB, and MDB state, handles switchdev notifier events, programs Prestera hardware for bridge membership, VLAN membership, STP state, flooding, learning, locked ports, multicast database behavior, and forwards hardware FDB learn/age events back to the bridge.

## Important APIs, types, and functions
Public functions are `prestera_switchdev_init()`, `prestera_switchdev_fini()`, `prestera_bridge_port_join()`, and `prestera_bridge_port_leave()`. Internal state includes `struct prestera_switchdev`, `struct prestera_bridge`, `struct prestera_bridge_port`, `struct prestera_bridge_vlan`, `struct prestera_port_vlan`, `struct prestera_br_mdb_entry`, `struct prestera_br_mdb_port`, and `struct prestera_fdb_event_work`.

Important flows are bridge create/destroy, bridge-port add/ref/put, 802.1D and 802.1Q join/leave, VLAN add/delete, FDB add/delete and flush, MDB create/sync/delete, switchdev object/attribute notifier handling, asynchronous FDB workqueue processing, and Prestera FDB event reporting.

## Control flow
Initialization allocates `sw->swdev`, initializes the bridge list, creates an ordered workqueue, registers atomic and blocking switchdev notifiers, registers Prestera FDB hardware event handling, and sets default ageing time. Finalization unregisters FDB and switchdev handlers, destroys the workqueue, and frees state.

Bridge port join finds or creates a bridge object. VLAN-aware bridges are limited to one per switch; VLAN-unaware bridges allocate a hardware bridge ID. The port is refcounted as a `prestera_bridge_port`, marked offloaded through `switchdev_bridge_port_offload()`, and for VLAN-unaware bridges is added to the hardware bridge and configured with flood/learning/locked flags. Leave flushes FDB entries, resets PVID or deletes hardware bridge membership, unoffloads the port, flushes MDB state, resets bridge flags and STP, and drops references.

Attribute handling maps STP states to Prestera hardware states, applies bridge-port flags, validates ageing time range, rejects VLAN filtering changes on an existing bridge, toggles multicast-disabled state, and updates mrouter state. Object handling adds or deletes VLANs and MDB entries. VLAN add creates hardware VLAN membership, adjusts PVID, joins the software bridge VLAN, applies STP, and links `prestera_port_vlan` to `prestera_bridge_vlan`.

FDB notifier work is queued on `swdev_wq` to run under RTNL. User-added nonlocal FDB entries are programmed into hardware and reported as offloaded; deletes remove the hardware FDB entry. Hardware FDB learn/age events are converted to `SWITCHDEV_FDB_ADD_TO_BRIDGE` or `SWITCHDEV_FDB_DEL_TO_BRIDGE`.

MDB handling keeps a software MDB list per bridge, creates hardware MDB entries, tracks member bridge ports, and synchronizes flood-domain ports based on multicast enablement, mrouter presence, VLAN membership, and explicit MDB membership.

## State and persistence behavior
All bridge state is runtime-only. Hardware state persists in ASIC tables until explicit delete/flush calls or switch reset. Refcounts keep bridge ports alive while VLAN objects reference them. The global ordered workqueue serializes deferred FDB operations. Bridge objects are destroyed when their port list becomes empty. MDB state is enabled only when multicast is enabled and an mrouter exists; otherwise multicast falls back to flooding behavior.

## Dependencies and integration points
The file integrates Linux switchdev notifiers, bridge helpers, RTNL, netdev upper/lower traversal, LAG helpers, Prestera hardware APIs for bridges/VLAN/STP/FDB/MDB, flood-domain helpers, and Prestera FDB event handling. It also relies on `prestera_netdev_check()` and `prestera_port_dev_lower_find()` to map Linux devices to Prestera ports.

## Risks and edge cases
Only one VLAN-aware bridge is supported. VLAN filtering cannot change after bridge creation. Error unwind for VLAN joins must restore PVID and hardware VLAN state. MDB sync assumes `prestera_port_dev_lower_find()` returns a port before VLAN checks; missing lower ports can be risky. `prestera_switchdev_handler_init()` destroys `swdev_wq` on notifier registration failure, and the outer init error path also destroys it, creating possible double destroy on that path. FDB work allocates and copies MAC addresses in atomic context; allocation failure returns `NOTIFY_BAD`. LAG handling depends on valid `port->lag` for all member ports.

## Test signals
Test signals include bridge join/leave for VLAN-aware and VLAN-unaware bridges, rejection of a second VLAN-aware bridge, STP transitions and rollback, bridge flag programming and reset, ageing time limits, VLAN add/delete PVID transitions, user FDB add/delete offload notifications, hardware FDB learned/aged notifications, LAG FDB paths, MDB enable/disable with mrouter changes, multicast flood sync, notifier unregister/order teardown, and failure injection for workqueue/notifier/hardware calls.
