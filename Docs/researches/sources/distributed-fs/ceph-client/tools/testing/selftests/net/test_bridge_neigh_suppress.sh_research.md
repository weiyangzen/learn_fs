# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_bridge_neigh_suppress.sh

## Purpose
`test_bridge_neigh_suppress.sh` validates bridge neighbor suppression on VXLAN ports. It covers ARP and IPv6 Neighbor Solicitation suppression, unicast neighbor solicitation/reply behavior, and per-port versus per-VLAN suppression controls across two VLANs.

## Important APIs, Types, And Functions
Setup functions include `setup_topo_ns()`, `setup_topo()`, `setup_host_common()`, `setup_h1()`, `setup_h2()`, `setup_sw_common()`, `setup_sw1()`, `setup_sw2()`, `setup()`, and `cleanup()`. Test functions include `neigh_suppress_arp()`, `neigh_suppress_uc_arp()`, `neigh_suppress_ns()`, `neigh_suppress_uc_ns()`, `neigh_vlan_suppress_arp()`, and `neigh_vlan_suppress_ns()`, with common helpers for each protocol. `icmpv6_header_get()` builds a raw NS payload for mausezahn.

## Control Flow
The topology creates host namespaces `h1`/`h2`, switch namespaces `sw1`/`sw2`, VLAN subinterfaces 10 and 20, VLAN-aware bridges, VXLAN ports with tunnel mappings, and static all-zero VXLAN FDB entries. Tests install tc flower counters on VXLAN egress or host ingress/egress, run `arping`, `ndisc6`, or raw `mausezahn` traffic, toggle `neigh_suppress` and `neigh_vlan_suppress`, install bridge FDB and neighbor entries, and verify whether requests leave the VXLAN port.

## State, Persistence, And Dependencies
State is temporary namespaces, veths, VLAN subinterfaces, bridges, VXLAN devices, bridge FDB entries, neighbor table entries, tc filters, and host link states. The script depends on root, `ip`, `bridge`, `tc`, `arping`, `ndisc6`, `jq`, `mausezahn`, and iproute2 support for `neigh_vlan_suppress`.

## Integration Points
The test exercises bridge neighbor suppression decisions at the intersection of L2 FDB lookup, L3 neighbor entries on SVI interfaces, VXLAN tunnel VLAN mapping, and per-port/per-VLAN bridge attributes.

## Risks
Exact packet counter checks are sensitive to unexpected background traffic. The IPv6 raw packet helper hardcodes checksums and target address bytes for the test prefixes. Several paths depend on host link down/up behavior and delayed neighbor discovery timing. Tool version checks are required for newer bridge attributes.

## Test Signals
Passing signals are expected `arping`/`ndisc6` results, tc counters not increasing when suppression should occur, counters increasing when suppression is disabled or not configured for that VLAN, successful unicast ARP/NS reply delivery, and correct independence between VLAN 10 and VLAN 20 suppression state.
