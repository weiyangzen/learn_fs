# sources/distributed-fs/ceph-client/net/openvswitch/vport.h

## Purpose
`vport.h` defines the Open vSwitch virtual port abstraction shared by datapath code and vport implementations. It declares port lifecycle, configuration, stats, receive, send, and type registration APIs.

## Important APIs and Types
`struct vport_portids` stores an RCU-protected array of netlink upcall portids plus a reciprocal divisor for hash selection. `struct vport` stores netdevice pointer and tracker, datapath pointer, upcall portids, datapath port number, global and datapath hash nodes, vport ops, per-CPU upcall stats, detach list, and RCU head. `struct vport_parms` carries userspace creation parameters and datapath-internal creation fields. `struct vport_ops` is the type interface: create, destroy, optional set/get options, send, owner module, and list node.

Public functions cover subsystem init/exit, add/delete, locate, stats, options, upcall port ids, upcall port selection, allocation/free, receive, send, ops registration, and helper accessors. `vport_priv()` and `vport_from_priv()` implement aligned private storage after `struct vport`.

## Control Flow and Integration
Datapath command handlers create vports through `ovs_vport_add()`, implementations allocate objects with `ovs_vport_alloc()`, receive paths call `ovs_vport_receive()`, and action output calls `ovs_vport_send()`. Implementations register `struct vport_ops` with `ovs_vport_ops_register()`, which fills owner with `THIS_MODULE`.

## State and Persistence
The header declares runtime structures only. RCU annotations and comments establish lifetime rules for upcall port ids and vports. Per-CPU upcall stats use `u64_stats_sync`.

## Dependencies
It depends on Linux tunnel, netlink, Open vSwitch UAPI, skb, reciprocal division, spinlock/stat helpers, and `datapath.h`.

## Risks
Implementations must obey the ops contract: create under OVS mutex, destroy after detaching and with proper RCU grace before final free, and send must consume the skb. Private data alignment must remain consistent with allocation in `vport.c`. Upcall port id users must hold RCU or OVS lock.

## Test Signals
Build coverage across all vport types, lifecycle tests, RCU/lockdep checks, upcall stats reporting, private data use in tunnel modules, and packet output behavior validate this abstraction.
