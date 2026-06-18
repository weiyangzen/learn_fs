# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum.c

## Purpose

`spectrum.c` is the main Mellanox/NVIDIA Spectrum Ethernet switch driver body. It binds Spectrum-1 through Spectrum-4 PCI/core drivers, selects generation-specific operation tables, initializes shared switch subsystems, creates and removes netdev ports, handles port split/unsplit, transmits and receives CPU-port packets, manages VLAN membership and PVID state, programs traps and CPU policers, registers devlink resources, tracks sampling triggers and shared IPv6 KVDL addresses, and reacts to Linux netdevice topology events for bridge, VLAN, LAG, OVS, macvlan, l3mdev, and VxLAN integration.

The file is the orchestration layer for many specialized modules. It does not implement every subsystem itself, but it owns the ordering and rollback between KVDL, PGT, LAG, FID, policer, trap, buffer, SPAN, switchdev, counter, ACL action, NVE, ACL, router, PTP, dpipe, port mapping, and netdev registration.

## Important APIs, Types, and Functions

Driver registration objects include `mlxsw_sp1_driver`, `mlxsw_sp2_driver`, `mlxsw_sp3_driver`, `mlxsw_sp4_driver`, matching PCI ID tables, firmware revision/filename declarations, config profiles, and `mlxsw_sp_module_init()` / `mlxsw_sp_module_exit()`.

Device lifecycle entry points are `mlxsw_sp1_init()`, `mlxsw_sp2_init()`, `mlxsw_sp3_init()`, `mlxsw_sp4_init()`, the common `mlxsw_sp_init()`, and `mlxsw_sp_fini()`. The generation-specific init functions populate operation pointers in `struct mlxsw_sp`, such as switchdev, KVDL, ACL key/action, ACL TCAM, multicast routing TCAM, NVE, shared-buffer, port-speed, PTP, SPAN, policer, trap, matchall, router, and FID core ops.

Port and netdev APIs include `mlxsw_sp_port_create()`, `mlxsw_sp_port_remove()`, `mlxsw_sp_ports_create()`, `mlxsw_sp_ports_remove()`, `mlxsw_sp_port_open()`, `mlxsw_sp_port_stop()`, `mlxsw_sp_port_xmit()`, `mlxsw_sp_port_change_mtu()`, `mlxsw_sp_port_set_mac_address()`, `mlxsw_sp_port_vlan_create()`, `mlxsw_sp_port_vlan_destroy()`, `mlxsw_sp_port_vlan_set()`, `mlxsw_sp_port_pvid_set()`, `mlxsw_sp_port_admin_status_set()`, and port split/unsplit helpers.

Networking integration is exposed through `mlxsw_sp_port_netdev_ops`, `mlxsw_sp_netdevice_event()`, `mlxsw_sp_port_dev_check()`, `mlxsw_sp_port_dev_lower_find()`, `mlxsw_sp_lower_get()`, parsing controls `mlxsw_sp_parsing_depth_inc()`, `mlxsw_sp_parsing_depth_dec()`, and `mlxsw_sp_parsing_vxlan_udp_dport_set()`.

State-sharing helpers include flow counter allocation/query/free, sampling trigger parameter set/unset/lookup, IPv6 address KVDL index get/put, trap initialization, LAG setup and membership transitions, and devlink resource registration.

## Control Flow

Module load registers four mlxsw core drivers, then their PCI drivers. On a device match, the generation-specific init function fills `struct mlxsw_sp` with the proper ops table and calls `mlxsw_sp_init()`.

Common initialization starts by storing core and bus pointers, initializing parsing state, and reading the base MAC. It then initializes KVDL, PGT, LAG, FID core, policers, traps, devlink traps, buffers, SPAN, switchdev, counter pool, ACL flexible actions, the IPv6-address hash table, NVE, port-range registers, ACL, router, optional PTP clock/state, netdevice notifier, dpipe, port module information, sampling trigger hash table, and finally ports. Each failure path unwinds in reverse order.

Port creation maps a module/lane set to a local port, assigns the Ethernet SWID, obtains port label information, initializes the core port and netdev, allocates per-CPU stats, sets MAC, features, MTU limits, TX headroom, system-port mapping, advertised speeds, maximum speed, admin-down state, buffers, ETS, multicast TC mode, DCB, FIDs, qdiscs, VLAN filters, NVE, default PVID, default VID 4095 VLAN, VLAN classification, PTP shaper work, overheat baseline, and finally registers the netdev and starts periodic stats work. Removal cancels work, unregisters the netdev, clears PTP configuration, flushes VLANs, and unwinds the same hardware state.

Transmit flow checks core queue availability, pads the skb, handles special PTP timestamp-as-data requirements, possibly inserts the default VLAN tag, transmits via `mlxsw_core_skb_transmit()`, and updates per-CPU TX counters. RX listeners attach the skb to the correct netdev, set forwarding marks for marked trap paths, update per-CPU RX counters, and pass traffic to GRO.

Netdevice notifier flow validates topology before linking uppers, applies bridge/LAG/OVS/VLAN/macvlan/VxLAN state on `NETDEV_CHANGEUPPER`, handles LAG lower-state distribution/collector changes, invalidates SPAN entries on unregister, and respins SPAN on every event. The VxLAN paths enforce bridge constraints and join/leave NVE offload on VxLAN device up/down or bridge membership changes.

## State and Persistence Behavior

Persistent in-kernel state lives in `struct mlxsw_sp`: port pointers, base MAC, MAC mask, LAG table, port mapping array and pending mapping events, sample-trigger rhashtable, subsystem handles, operation tables, parsing state, IPv6 address rhashtable, PGT flags, and LAG PGT base. Each `struct mlxsw_sp_port` stores netdev identity, per-CPU stats, DCB and link state, port mapping, delayed stats work, VLAN list/default VLAN, flow blocks, PTP port state, maximum speed, headroom, and module overheat baseline.

Hardware state is programmed through many registers: port admin, MAC, MTU, SWID, VLAN membership/PVID/classification/learning, STP, module lane mapping, system-port mapping, speed capabilities, ETS/shapers, trap groups, CPU policers, LAG hashing/membership, PGT base, parsing depth/VXLAN UDP port, flow counters, IPv6 address KVDL entries, and PTP timestamp forwarding. None of this is persisted across driver reload; it is rebuilt from firmware resources, devlink profile settings, current netdev topology, and kernel configuration.

Reference-counted state includes sampling trigger nodes, IPv6 KVDL address nodes, parsing-depth users, and LAG objects. Delayed work is used for periodic hardware stats and PTP shaper updates. Port mapping events are queued under a spinlock and processed in workqueue context.

## Dependencies and Integration Points

The file integrates with the mlxsw core, PCI bus glue, firmware/resource/profile infrastructure, devlink, Linux netdev, switchdev, bridge/VLAN/LAG/VXLAN APIs, traffic control offload APIs, PTP, psample, rhashtable, and all Spectrum subsystem files declared in `spectrum.h`. It calls register pack/query/write helpers from `reg.h`, CPU-port TX header helpers, environment/module helpers from `core_env`, and generation-specific ops from Spectrum-1/2/3/4 modules.

## Risks and Edge Cases

- Initialization ordering is fragile: moving KVDL, PGT, LAG, SPAN, switchdev, ACL, router, or notifier setup can break assumptions called out in comments.
- Several cleanup paths call hardware writes and ignore failures during teardown. That is typical for driver unwinding but can hide partially stale device state after error injection.
- `mlxsw_sp_port_lag_join()` returns immediately when no free LAG member index is found without dropping the reference acquired by `mlxsw_sp_lag_get()`, which is a leak-prone path worth checking against surrounding kernel history.
- PTP timestamp-as-data TX mutates skbs by adding VLAN tags; regressions here can affect checksum/headroom assumptions and default VID behavior.
- `mlxsw_sp_port_ovs_leave()` and related VLAN loops use unsigned `u16` decrement patterns that rely on break conditions; changes need care to avoid wraparound loops.
- Netdevice event replay and validation paths are complex and recursive over uppers. Missing a replay after de-enslavement can leave bridge/router/FID state inconsistent.
- Parsing-depth refcounting writes hardware only on first increment and final decrement. Leaked references keep the increased parsing depth indefinitely; premature decrement can disturb VXLAN/NVE users.
- Resource registration assumes core resource validity. Older firmware or partial resource discovery failures tend to surface as `-EIO` during feature initialization.

## Test Signals

High-value tests include Spectrum module load/unload for all supported PCI IDs, port creation/removal with module mapping events, devlink resource display and size override tests, port split/unsplit, netdev open/close, PTP TX/RX timestamping, VLAN add/kill, bridge join/leave with VLAN-aware and VLAN-unaware modes, LAG create/join/leave/lower-state changes, OVS master join/leave, VXLAN bridge join/up/down validation, TC flower/matchall/qdisc offload toggles, parsing-depth users, sampling trigger reference sharing, IPv6 NVE address KVDL refcounts, and fault injection across each init label to verify reverse unwinding.
