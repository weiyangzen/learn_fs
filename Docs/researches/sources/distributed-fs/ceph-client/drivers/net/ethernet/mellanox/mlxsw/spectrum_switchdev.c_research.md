# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_switchdev.c

## Purpose

`spectrum_switchdev.c` is the mlxsw Spectrum bridge, FDB, MDB, VLAN, and VXLAN switchdev offload implementation. It translates Linux bridge and switchdev events into hardware FIDs, flood tables, learning state, STP state, multicast database entries, static/dynamic FDB records, and NVE/VXLAN mappings. It is the main L2 integration point between netdevice topology and Spectrum hardware forwarding.

## Important APIs, Types, And Functions

`struct mlxsw_sp_bridge` owns global bridge state, FDB notification delayed work, ageing time, a single VLAN-aware bridge guard, bridge-device list, MID bitmap, and per-ASIC bridge ops. `struct mlxsw_sp_bridge_device` mirrors a Linux bridge and tracks bridge ports, MDB list/rhashtable, VLAN-awareness, multicast state, router state, and ops. `struct mlxsw_sp_bridge_port` mirrors a bridge member with refcount, STP state, flags, mrouter state, and either LAG id or system port. `struct mlxsw_sp_bridge_vlan` groups port VLANs per bridge port.

Public entry points include `mlxsw_sp_switchdev_init()`, `mlxsw_sp_switchdev_fini()`, `mlxsw_sp_port_bridge_join()`, `mlxsw_sp_port_bridge_leave()`, `mlxsw_sp_bridge_vxlan_join()`, `mlxsw_sp_bridge_vxlan_leave()`, `mlxsw_sp_bridge_device_is_offloaded()`, `mlxsw_sp_rif_fdb_op()`, and `mlxsw_sp_bridge_port_stp_state()`. Internal ops implement 802.1Q, 802.1D, and 802.1AD bridge behavior, including Spectrum-2 egress ethertype differences.

## Control Flow

Initialization allocates `mlxsw_sp_bridge`, installs bridge ops, sets default FDB ageing time, registers switchdev notifiers, and initializes FDB notification work. Bridge join obtains or creates a bridge device and bridge port, calls the bridge type's `port_join`, replays router/netdevice enslavement, and unwinds in reverse on failure. VLAN-aware bridges replay switchdev VLAN objects; VLAN-unaware bridges attach a default or VLAN-upper VID to an 802.1D FID. 802.1AD joins additionally change VLAN classification and, on Spectrum-2, egress ethertype.

VLAN add creates or finds a port VLAN, programs VLAN membership/PVID, obtains the bridge FID, sets UC/MC/BC flood membership, maps port/VID to FID, sets learning and STP, and links the port VLAN into the bridge VLAN list. VLAN delete reverses this, flushes FDB and MDB state as needed, unmaps the FID, and releases bridge-port references.

FDB programming uses SFD register records for port, LAG, router, and tunnel entries. Hardware FDB notifications are polled by delayed work using SFN queries, converted to bridge/VXLAN switchdev notifications, and reprogrammed as dynamic entries. Static FDB events from switchdev are deferred to workqueues and either program local/LAG entries or tunnel entries. VXLAN events translate Linux VXLAN FDB records to NVE flood IPs or tunnel unicast entries and report offload state back to switchdev.

MDB handling allocates MID/PGT entries, tracks member and mrouter ports with refcounts, writes multicast SFD records when multicast snooping is enabled, and updates mrouter inclusion when bridge or port mrouter attributes change.

## State And Persistence

State is in memory plus hardware forwarding tables. The bridge object stores live bridge devices, bridge ports, VLAN groupings, MDB hash/list state, pending FDB notification work, and ageing time. Hardware persistence includes FID allocations and VNI bindings, flood table membership, STP and learning bits per VID, PGT/MID multicast groups, SFD FDB/MDB records, NVE IPv6 KVDL mappings, and VXLAN offload state. Notifier work items hold device references with `netdev_hold()` until processed.

## Dependencies And Integration Points

The file depends on Linux switchdev, bridge, VLAN, VXLAN, workqueue, RTNL, and netdevice APIs. Internally it integrates with Spectrum FID management, NVE/VXLAN helpers, router RIF replay, LAG helpers, SPAN respin, port VLAN state, flood table programming, PGT/MID allocation, and hardware register packing in `reg.h`.

## Risks And Edge Cases

Only one VLAN-aware bridge is supported; attempts to create another fail. VLAN filtering and protocol cannot be changed after a bridge is offloaded. Locked bridge-port flags are rejected on VLAN uppers or ports with VLAN uppers. Error unwinds must reverse partially programmed FID flood state, learning/STP state, PVID changes, switchdev replay, NVE bindings, and MDB mrouter additions. Dynamic FDB notifications may refer to invalid ports or stale FIDs; the code removes unprocessable entries to stop repeated notifications. VXLAN support rejects non-default remote port/VNI, remote interface, multicast MAC, and multicast destination IP. Hardware has one FDB while Linux has bridge and VXLAN FDBs, so tunnel FDB programming depends on matching bridge FDB ownership.

## Test Signals

Useful tests include 802.1D, 802.1Q, and 802.1AD bridge joins/leaves; VLAN add/delete with PVID and untagged changes; LAG bridge membership replay; STP, learning, flooding, locked, MAB, and mrouter attributes; bridge ageing bounds; MDB add/delete and multicast-snooping toggles; dynamic FDB learning/ageing from hardware notifications; static FDB add/delete; VXLAN bridge join/leave and VLAN-to-VNI remap; VXLAN FDB add/delete/offload notifications; and failure injection for FID, PGT, SFD, switchdev replay, and NVE operations. No local executable tests were run for this research item.
