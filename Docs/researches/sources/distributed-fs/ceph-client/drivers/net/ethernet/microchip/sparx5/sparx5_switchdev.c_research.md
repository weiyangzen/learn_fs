## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_switchdev.c

### Purpose
`sparx5_switchdev.c` implements Linux switchdev and netdevice notifier integration for bridge offload, FDB programming, VLAN objects, MDB multicast groups, bridge flags, STP state, ageing, and mrouter behavior.

### Important APIs, Types, And Functions
Exports are `sparx5_register_notifier_blocks()` and `sparx5_unregister_notifier_blocks()`. Important internals include bridge join/leave, `sparx5_port_attr_set()`, `sparx5_netdevice_event()`, asynchronous FDB work handling, VLAN add/delete handlers, MDB allocation/free/get, `sparx5_handle_port_mdb_add/del()`, and switchdev blocking/nonblocking notifier callbacks.

### Control Flow
Bridge join enforces a single hardware bridge, marks the port bridged, offloads bridge port, removes standalone host MACT entry, unsyncs multicast list, and enables UC/MC/BC flooding. Leave reverses those changes, restores standalone CPU copy, resets VLAN state, syncs multicast, and disables flooding. Switchdev FDB events are copied under atomic context into ordered workqueue items, then applied under RTNL. Blocking object events program VLAN membership and MDB PGID masks synchronously. MDB add allocates a PGID on first group, applies mrouter ports, optionally enables CPU copy for host entries, updates port masks, and learns MACT to the multicast PGID.

### State, Persistence, And Dependencies
State lives in bridge masks (`bridge_mask`, `bridge_fwd_mask`, `bridge_lrn_mask`), `hw_bridge_dev`, per-port VLAN/mrouter flags, `mdb_entries` list protected by `mdb_lock`, PGID map, MACT hardware, VLAN hardware, and flood PGID masks. Dependencies include Linux bridge/switchdev notifier APIs, MACT, VLAN, PGID helpers, and ordered workqueues.

### Integration Points
This file is the main bridge offload path for the driver. It cooperates with netdev RX marking, multicast sync, VLAN programming, ageing timer programming, and PGID/MACT hardware updates.

### Risks
MDB lookup returns a pointer after dropping `mdb_lock`, then callers lock again, which can be safe only if switchdev serialization prevents concurrent free. Workqueue allocation and `dev_hold()`/`dev_put()` pairing must be correct for FDB events. The driver supports only one hardware bridge. VLAN-unaware mode maps vid 0 to 1, which must remain consistent across FDB/MDB/VLAN paths.

### Test Signals
Test bridge join/leave, rejection of second bridge, STP state transitions and forwarding masks, flood flag toggles, VLAN-aware/unaware adds and deletes, FDB add/delete for host and port entries, MDB host/port/mrouter combinations, ageing updates, notifier registration unwind, and ordered workqueue shutdown.
