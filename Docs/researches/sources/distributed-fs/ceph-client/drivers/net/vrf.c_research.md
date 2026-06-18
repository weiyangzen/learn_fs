# sources/distributed-fs/ceph-client/drivers/net/vrf.c

## Purpose
`vrf.c` implements the Linux VRF netdevice driver. A VRF device acts as an L3 master that binds traffic to a routing table, supports enslaved interfaces, redirects local output through VRF-aware routes/netfilter/qdisc paths, tags ingress packets as L3 slave traffic, manages per-netns VRF table mappings and strict-mode sysctl, and registers l3mdev/rtnetlink integration.

## Important APIs, Types, And Functions
Core state is `struct net_vrf`, `struct netns_vrf`, `struct vrf_map`, and `struct vrf_map_elem`. TX/output paths include `vrf_xmit()`, `vrf_process_v4_outbound()`, `vrf_process_v6_outbound()`, `vrf_ip_out()`, `vrf_ip6_out()`, `vrf_output()`, and `vrf_output6()`. RX/l3mdev paths include `vrf_l3_rcv()`, `vrf_ip_rcv()`, `vrf_ip6_rcv()`, `vrf_l3_out()`, `vrf_link_scope_lookup()`, and `vrf_fib_table()`. Lifecycle and integration use `vrf_setup()`, `vrf_dev_init()`, `vrf_newlink()`, `vrf_dellink()`, slave add/delete helpers, pernet ops, sysctl handler, notifier, and rtnl link ops.

## Control Flow
Module init registers notifier, pernet state, l3mdev table lookup, and rtnl kind `vrf`. Creating a VRF validates `IFLA_VRF_TABLE`, registers the netdev, creates IPv4/IPv6 dst entries, records table-to-ifindex mapping, and adds l3mdev FIB rules once per namespace. Enslaving ports marks them L3 slaves, links upper/lower devices, and cycles devices to flush route/neighbor state. TX performs VRF-table route lookup and either reinjects local traffic or strips the temporary Ethernet header and runs local-out/output paths. Ingress rewrites skb device/iif to the VRF for most packets, handles IPv6 NDISC/link-local exceptions, updates stats, mirrors to packet taps, and invokes pre-routing netfilter.

## State And Persistence
Per-device state stores table ID, ifindex, and cached IPv4/IPv6 dsts. Per-netns state stores automatic FIB-rule status, strict mode, shared-table counts, sysctl header, and hash map of table associations. Strict mode prevents table sharing when enabled and can be enabled only if no table is shared.

## Dependencies And Integration Points
Integrates with rtnetlink, netdevice upper/lower APIs, l3mdev, fib rules, IPv4/IPv6 route lookup, multicast route rule families, netfilter, conntrack untracked state, neighbour output, packet taps, pernet generic storage, sysctl, and ethtool drvinfo.

## Risks
Correctness depends on careful manipulation of `skb->dev`, `skb_iif`, dst, netfilter, conntrack, and protocol control blocks. IPv6 NDISC/link-local handling is subtle. Table sharing map updates must match strict-mode semantics. Direct versus redirected output paths can change packet visibility and hook ordering.

## Test Signals
Test create/delete, invalid table IDs, enslave/unslave rejections, strict_mode transitions, IPv4/IPv6 local and forwarded traffic, multicast/link-local/NDISC behavior, packet captures, netfilter ordering, qdisc versus no-qdisc paths, XFRM traffic, namespace teardown, and unregister of enslaved ports.
