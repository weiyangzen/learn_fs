# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera.h

## Purpose
`prestera.h` is the central public header for the Prestera switch driver. It defines core switch, port, device, event, interface, LAG, flood-domain, FDB/MDB, stats, phylink, router, and firmware abstractions plus cross-subsystem function declarations.

## Important APIs, Types, and Definitions
Major structures include `prestera_switch`, `prestera_device`, `prestera_port`, `prestera_lag`, port stats/caps/config/state, event payloads, `prestera_iface`, flood-domain/MDB types, and router state. Inline MMIO helpers `prestera_read()`/`prestera_write()` access PP registers. Prototypes cover device registration, port lookup/config, router init/fini, workqueue helpers, learning/flood/PVID/bridge lock, LAG lookup, MDB/flood-domain management, and netdev checks.

## Control Flow
The header provides only inline register access. Runtime flow is orchestrated by implementation files: the low-level device supplies `recv_pkt`, `recv_msg`, and `send_req`; the registered switch owns ports, event handlers, netdev notifier, devlink/trap/ACL/span/router/counter subsystems, and phylink state.

## State and Persistence
`prestera_switch` persists for the driver instance and aggregates global state. `prestera_port` persists per netdev and caches MAC/PHY config/state, VLANs, LAG membership, delayed stats, and phylink objects. Router, LAG, counter, ACL, and switchdev state are pointers managed by their subsystems.

## Dependencies and Integration Points
The header depends on notifier, skb/workqueue/phylink/devlink, Ethernet UAPI, and many forward-declared Prestera subsystems. It is included broadly by hardware, flow, ACL, counter, router, switchdev, and PCI/device files.

## Risks and Edge Cases
Because it is a wide shared contract, structure layout changes can affect many object files. Locking expectations are embedded in comments such as `state_mac_lock` and port list `rwlock_t`; users must respect them. Workqueue helpers imply deferred operations that need drain ordering at unload.

## Test Signals
Build all Prestera objects after any field/prototype change. Runtime signals include switch registration/unregistration, port discovery, phylink transitions, stats caching, LAG/VLAN/switchdev operations, router init/fini, and devlink/trap/ACL/counter interactions.
