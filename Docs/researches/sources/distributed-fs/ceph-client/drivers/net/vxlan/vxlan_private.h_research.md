<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_private.h -->
# sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_private.h

## Purpose
`vxlan_private.h` is the internal header shared by the VXLAN implementation files. It defines the private per-net and FDB data structures, hash helpers, address helpers, VNI-filter lookup helper, and cross-file function prototypes for core, VNI-filter, multicast, and MDB modules.

## Important APIs, Types, and Functions
- `struct vxlan_net` stores per-network-namespace VXLAN state: device list, UDP socket hash buckets, and nexthop notifier.
- `struct vxlan_fdb_key` and `struct vxlan_fdb` define the forwarding database key and entry, including rhashtable node, RCU head, timestamps, remotes list, state/flags, nexthop linkage, and owning VXLAN device pointer.
- `NTF_VXLAN_ADDED_BY_USER` marks user-added FDB entries beyond standard neighbor flags.
- Hash helpers `vni_head()` and `vs_head()` select VNI and socket hash buckets.
- Remote helpers `first_remote_rcu()` and `first_remote_rtnl()` return the first non-nexthop remote destination under the relevant locking context.
- Address helpers `vxlan_addr_equal()`, `vxlan_nla_get_addr()`, `vxlan_nla_put_addr()`, `vxlan_addr_is_multicast()`, and `vxlan_addr_size()` abstract IPv4/IPv6 support, with IPv6-disabled fallbacks.
- `vxlan_vnifilter_lookup()` retrieves a per-VNI node from a device VNI group using `vxlan_vni_rht_params`.
- Prototypes expose FDB update/delete/create, transmit, VNI-in-use validation, VNI-filter init/update/stats, multicast join/leave/group-used, and MDB netdevice/datapath APIs.

## Control Flow
This header does not implement high-level control flow, but it is on the hot path for both RX and TX. `vxlan_core.c` uses the hash helpers for socket/VNI lookup, FDB operations, and remote selection. `vxlan_vnifilter.c` uses the exported rhashtable params and lookup contract to maintain per-VNI state. `vxlan_multicast.c` uses address helpers and VNI group access. `vxlan_mdb.c` uses address helpers and `vxlan_xmit_one()` for multicast replication.

## State and Persistence Behavior
The structures declared here describe in-memory runtime state only. `struct vxlan_net` is allocated per net namespace by pernet operations; `struct vxlan_fdb` instances are allocated, inserted, aged, notified, and RCU-freed by `vxlan_core.c`. Address helper behavior changes with `CONFIG_IPV6`: without IPv6, IPv6 netlink addresses are rejected with `-EAFNOSUPPORT`.

## Dependencies and Integration Points
The header includes `linux/rhashtable.h` and relies on VXLAN public structures from `<net/vxlan.h>` included by users. It forms the internal ABI among `vxlan_core.c`, `vxlan_vnifilter.c`, `vxlan_multicast.c`, and `vxlan_mdb.c`. Its prototypes also reflect the public integration of VXLAN internals with netdevice operations and bridge/MDB rtnetlink.

## Risks and Edge Cases
- Inline helpers encode locking expectations: `first_remote_rcu()` is for RCU readers and `first_remote_rtnl()` for RTNL contexts. Using the wrong helper can produce lifetime or lockdep bugs.
- `first_remote_*()` returns `NULL` for nexthop-backed FDB entries; callers must handle nexthop state separately.
- IPv6-disabled helper variants reject IPv6 netlink input and only compare IPv4 addresses; new code must not assume IPv6 fields are valid without compile-time guards.
- `vxlan_vnifilter_lookup()` uses `rcu_dereference_rtnl()` and assumes callers are in an RTNL-compatible context or otherwise follow established lookup rules.

## Test Signals
- Build-test VXLAN with and without `CONFIG_IPV6`.
- Exercise FDB entries with normal remotes and nexthop-backed remotes to verify `first_remote_*()` caller behavior.
- Add/delete VNI-filter entries and ensure `vxlan_vnifilter_lookup()` correctly gates RX dispatch and stats.
- Netlink-test IPv4 and IPv6 address parsing/serialization paths, including short/invalid attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/vxlan/vxlan_private.h -->
