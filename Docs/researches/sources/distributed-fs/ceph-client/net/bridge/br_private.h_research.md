# sources/distributed-fs/ceph-client/net/bridge/br_private.h

## Purpose
`br_private.h` is the central internal contract for the Linux bridge driver. It defines core bridge/port/VLAN/FDB/MDB state, feature option bits, skb control-block layout, inline helpers, subsystem prototypes, and compile-time stubs for optional bridge features.

## Important APIs, types, and functions
- Core types: `struct net_bridge`, `struct net_bridge_port`, `struct net_bridge_vlan`, `struct net_bridge_vlan_group`, `struct net_bridge_fdb_entry`, `struct net_bridge_mdb_entry`, `struct net_bridge_port_group`, `struct net_bridge_mcast`, and `struct br_input_skb_cb`.
- Identity and STP helpers: `bridge_id`, `mac_addr`, `port_id`, `br_is_root_bridge()`, `br_port_get_rcu()`, `br_port_get_rtnl()`, `br_port_get_check_rcu()`, and `br_port_get_check_rtnl()`.
- VLAN helpers: `br_vlan_should_use()`, `br_vlan_valid_id()`, `br_vlan_valid_range()`, `br_get_pvid()`, `br_vlan_flags()`, `br_vlan_get_state()`, `br_vlan_set_state()`, and `br_vlan_state_allowed()`.
- Multicast helpers: router/querier checks, VLAN multicast-context predicates, source/group mode helpers, and no-op stubs when `CONFIG_BRIDGE_IGMP_SNOOPING` is off.
- Option APIs: `br_opt_get()`, `br_opt_toggle()`, `br_boolopt_toggle()`, `br_boolopt_multi_toggle()`, and `br_boolopt_multi_get()`.
- Subsystem prototypes cover device setup, FDB, forwarding, bridge interface management, input, multicast, VLAN, MST, netfilter, STP, MRP, CFM, netlink, sysfs, switchdev, and ARP/ND proxy suppression.

## Control flow
This header does not run control flow directly, but it shapes all bridge subsystem interactions. Data-plane files use `BR_INPUT_SKB_CB()` for per-packet forwarding metadata. Control-plane files mutate `struct net_bridge` and `struct net_bridge_port` fields declared here. Optional features are hidden behind compile-time stubs so call sites can stay mostly unconditional while unsupported operations return `-EOPNOTSUPP`, no-op, or default values.

## State and persistence
The declared state is in-memory kernel state. `struct net_bridge` owns bridge-wide timers, FDB/MDB tables, VLAN group, multicast context, STP identity/timers, option bits, switchdev hardware-domain state, and optional MRP/CFM lists. `struct net_bridge_port` owns per-port flags, VLAN group, backup port, STP state/timers/statistics, multicast context, sysfs name, netpoll, and switchdev offload metadata. RCU, spinlocks, atomics, seqcounts, refcounts, rhashtables, hlists, rbtrees, timers, delayed work, and per-CPU stats encode lifetime and concurrency expectations.

## Dependencies and integration points
The header ties the bridge to netdevice, rtnetlink, VLAN, route/dst, IPv6 fib, tc skb extensions, rhashtable, netpoll, switchdev, netfilter, sysfs, multicast, MRP, CFM, and UAPI bridge definitions. It is included by nearly every bridge implementation file and is the primary place where optional features present a uniform internal API.

## Risks and edge cases
Because this file defines shared layout and inline locking assumptions, mistakes have broad blast radius. Risks include using VLAN master/context entries as active entries without `br_vlan_should_use()`, reading RCU pointers without the required protection, changing option enum order in ways that break bit semantics, and relying on optional feature stubs without checking `-EOPNOTSUPP` where user-visible behavior matters.

## Test signals
Broad bridge regression coverage should compile multiple config matrices: VLAN filtering on/off, multicast snooping on/off, bridge netfilter on/off, sysfs on/off, switchdev on/off, MRP/CFM on/off, IPv6 on/off, and TC skb extensions on/off. Runtime tests should stress concurrent port/VLAN/FDB/MDB changes, RCU-protected port deletion, netlink dump races, and data-plane forwarding metadata.
