# sources/distributed-fs/ceph-client/include/net/vxlan.h

## Purpose

`vxlan.h` defines VXLAN, VXLAN-GBP, VXLAN-GPE, and remote-checksum-offload wire layouts plus the kernel state structures for VXLAN sockets, devices, VNIs, forwarding entries, per-VNI stats, configuration, feature checks, and switchdev offload notifications.

## Important APIs, types, and functions

Wire structures include `struct vxlanhdr`, `struct vxlanhdr_gbp`, and `struct vxlanhdr_gpe`. Core state types include `struct vxlan_sock`, `union vxlan_addr`, `struct vxlan_rdst`, `struct vxlan_config`, `struct vxlan_vni_stats_pcpu`, `struct vxlan_vni_node`, `struct vxlan_vni_group`, and `struct vxlan_dev`. Helpers include `vxlan_dev_create()`, `vxlan_features_check()`, `vxlan_headroom()`, `vxlan_hdr()`, `vxlan_vni()`, `vxlan_vni_field()`, `vxlan_rco_start()`, `vxlan_rco_offset()`, `vxlan_compute_rco()`, `vxlan_get_sk_family()`, `vxlan_addr_any()`, `vxlan_addr_multicast()`, `netif_is_vxlan()`, `vxlan_fdb_find_uc()`, `vxlan_fdb_replay()`, `vxlan_fdb_clear_offload()`, `vxlan_flag_attr_error()`, `vxlan_fdb_nh_path_select()`, and `vxlan_build_gbp_hdr()`.

## Control flow

Netlink configuration creates a `vxlan_dev` with VNI, endpoints, UDP port, flags, aging, MTU, and offload settings. Receive sockets hash VNIs to VXLAN devices or per-VNI nodes. Transmit paths compute headroom, build VXLAN/VXLAN-GPE/GBP headers, select remote destinations from FDB or nexthop, and use UDP tunnel transmit helpers. Feature checks disable checksum/GSO features when encapsulated layout or inner protocol is not suitable. Switchdev users replay or clear FDB offload state through notifier-friendly structures.

## State and persistence behavior

Persistent state includes per-net VXLAN device lists, RCU pointers to IPv4/IPv6 sockets, VNI rhashtables, FDB/MDB rhashtables, aging timers, GRO cells, per-VNI percpu stats, destination caches, and VXLAN config flags. `vxlan_sock` and remote destinations are refcounted/RCU managed.

## Dependencies and integration points

It depends on VLAN protocol helpers, rhashtable, UDP tunnel APIs, dst metadata, RTNL, switchdev, nexthop, IPv4/IPv6, and netlink extack. It integrates with the VXLAN netdevice driver, UDP tunnel offload notifications, bridge/switchdev FDB offload, collect-metadata tunnels, and nexthop groups.

## Risks and test signals

Risks include endian mistakes in VNI field conversion, feature-offload acceptance for malformed encapsulation, incompatible flag combinations with VXLAN-GPE, RCU/refcount bugs in socket/VNI/FDB tables, remote-checksum offset overflow, and inaccurate per-VNI stats. Tests should cover VNI encode/decode on both endian modes, GBP/GPE header construction, IPv4/IPv6 and multicast endpoints, VNIFILTER, FDB replay/offload clear, nexthop path selection, feature fallback, aging timers, and netlink attempts to mutate immutable flags.
