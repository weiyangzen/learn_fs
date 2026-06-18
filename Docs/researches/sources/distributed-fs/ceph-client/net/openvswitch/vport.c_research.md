# sources/distributed-fs/ceph-client/net/openvswitch/vport.c

## Purpose
`vport.c` is the core Open vSwitch vport subsystem. It registers vport type implementations, allocates and frees vports, locates ports by name, stores upcall port ids and statistics, receives packets into the datapath, and sends packets out through vport ops with MTU and MAC-protocol checks.

## Important APIs, Types, and Functions
`ovs_vport_init()` allocates a 1024-bucket global `dev_table`; `ovs_vport_exit()` frees it. `__ovs_vport_ops_register()` and `ovs_vport_ops_unregister()` maintain the global type list under OVS mutex. `ovs_vport_lookup()` finds ops by `enum ovs_vport_type`; `ovs_vport_add()` creates a vport through ops, holds the module, hashes it by namespace/name, and can request autoload of `vport-type-%d`.

`ovs_vport_alloc()` allocates `struct vport` plus optional private storage, initializes per-vport upcall stats, datapath pointer, port number, ops, and initial upcall port ids. `ovs_vport_free()` releases RCU-protected portids, per-CPU upcall stats, and the vport. `ovs_vport_del()` removes the vport from the global name hash, drops the module reference, and calls type-specific destroy.

`ovs_vport_get_stats()` reads netdevice stats into OVS UAPI stats. `ovs_vport_get_upcall_stats()` aggregates per-CPU success/failure counters into nested netlink attributes. `ovs_vport_set_upcall_portids()` validates and replaces an RCU-protected `struct vport_portids`; `ovs_vport_find_upcall_portid()` selects a port id by skb hash and reciprocal division. `ovs_vport_get_options()` and `ovs_vport_set_options()` dispatch type-specific configuration.

`ovs_vport_receive()` initializes OVS skb control block fields, scrubs packets crossing net namespaces while preserving mark, extracts a flow key with `ovs_flow_key_extract()`, and calls `ovs_dp_process_packet()`. `ovs_vport_send()` validates the outgoing MAC protocol against the netdevice type, checks non-GSO packets against MTU, sets skb device, clears timestamps, and dispatches the vport send op.

## Control Flow
Datapath vport commands call `ovs_vport_add()` and `ovs_vport_del()`. Receive paths from internal devices, physical netdev RX handlers, or tunnel netdevices call `ovs_vport_receive()`. Packet misses use upcall port ids maintained here. Action output paths call `ovs_vport_send()` to transmit or inject packets through the selected vport type.

## State and Persistence
State is in memory: global vport type list, global name hash table, per-vport netdevice pointer/reference, datapath pointer, port id array, per-CPU upcall stats, and private data. Port id arrays and vports are RCU-managed. Module references keep vport type modules loaded while ports exist.

## Dependencies and Integration Points
It depends on `datapath.h`, `flow.c` extraction, `flow_netlink.c` stats/options serialization indirectly, and internal/netdev vport implementations. It integrates with datapath port hash tables, generic-netlink vport commands, and action output.

## Risks
Name hashing must include net namespace to avoid cross-netns conflicts. Upcall PID arrays must be nonempty, u32-aligned, and no larger than CPU count. Receive consumes skbs on errors. MTU checks must account for VLAN headers and GSO. Module autoload returns `-EAGAIN` so callers retry after loading. Locking is split between OVS mutex for writes and RCU for lookup/receive.

## Test Signals
Vport add/delete for internal, netdev, and tunnels; module autoload; duplicate type registration; duplicate name lookup; upcall PID distribution; cross-netns receive scrubbing; MTU drop warnings; and packet ingress/egress through each vport type are key signals.
