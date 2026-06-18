
# sources/distributed-fs/ceph-client/include/uapi/linux/if_link.h

## Purpose

`if_link.h` is the major rtnetlink netdevice UAPI contract. It defines interface statistics layouts, generic `IFLA_*` link attributes, nested attributes for bridge, VLAN, MACVLAN, VRF, MACsec, XFRM, IPVLAN, VXLAN, Geneve, bareudp, PPP, GTP, bonding, SR-IOV VFs, IPoIB, HSR/PRP, stats, XDP, TUN, rmnet, MCTP, DSA, and OVPN link types. The source was read as a complete 2057-line file.

## Important APIs, Types, and Functions

Key structures include `rtnl_link_stats`, `rtnl_link_stats64`, `rtnl_hw_stats64`, `rtnl_link_ifmap`, `ifla_bridge_id`, `ifla_cacheinfo`, `ifla_vlan_flags`, `ifla_vlan_qos_mapping`, `tunnel_msg`, `ifla_vxlan_port_range`, `ifla_geneve_port_range`, many `ifla_vf_*` structs, `ifla_port_vsi`, `if_stats_msg`, and `ifla_rmnet_flags`. Important enums define top-level `IFLA_*`, address-family payloads, bridge/bridge-port controls, per-link-type netlink attributes, MACsec validation/offload values, VXLAN/Geneve DF policies, bonding and VF management attributes, stats filters, XDP attach attributes and flags, and TUN/rmnet/MCTP/DSA/OVPN attributes. There are no functions; this is an ABI declaration file.

## Control Flow

There is no executable control flow. Runtime flow is external: user space sends rtnetlink messages carrying these attributes; kernel rtnetlink handlers parse nested attributes according to the active link kind; replies use the same IDs and structures for dumps, stats, and events.

## State and Persistence Behavior

The file does not own state. It defines persistent UAPI numeric IDs and struct layouts that kernel networking code and user-space tools must treat as stable. Some attributes configure kernel-resident netdevice state, such as bridge timers, VLAN policy, tunnel endpoints, VF trust/rate/VLAN settings, XDP attachment, and TUN persistence, but storage lives in the owning networking subsystems.

## Dependencies and Integration Points

It includes `linux/types.h` and `linux/netlink.h` and is consumed by iproute2-style tools, rtnetlink users, network drivers, virtual link modules, bridge/bond/VLAN/tunnel code, XDP/BPF attachment paths, and stats dump handlers.

## Risks and Edge Cases

This file is ABI-critical: renumbering enum values, changing struct field order, or changing integer widths breaks user space. Risk is high around nested attribute validation, endian-marked fields, obsolete aliases, bridge timer units in `USER_HZ`, VF list bounds, XDP flag compatibility, and old tunnel flags that exhausted `__be16` space.

## Test Signals

Useful signals include UAPI header compile tests, rtnetlink selftests for every link kind touched, iproute2 compatibility tests, netlink policy validation tests for nested attrs, bridge/VLAN/tunnel/XDP integration tests, and struct size/offset checks for stats and VF structs on 32-bit and 64-bit builds.
