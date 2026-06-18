# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_mpls_l2vpn.sh

Purpose: builds a two-node Ethernet-over-MPLS L2VPN using tc actions rather than IP routing. It verifies plain Ethernet traffic can be encapsulated into MPLS, transported, decapsulated, and returned symmetrically.

Important functions are `ler1_create`, `ler2_create`, and `mpls_forward_eth`. Each LER installs ingress qdiscs on edge and MPLS-facing interfaces. Edge ingress uses `matchall`, `action mpls mac_push label ...`, `action vlan push_eth dst_mac ... src_mac ...`, and `mirred egress redirect`. MPLS ingress matches `protocol mpls_uc flower mpls_label ...`, pops outer Ethernet and MPLS (`protocol teb`), and redirects back to the edge.

Control flow creates H1/H2 VRFs, caches MPLS interface MACs, installs LER actions, pings IPv4 and IPv6 between hosts, then optionally repeats after `tc_offload_check` with `skip_sw` although local filters do not use `$tcflags`. State is tc qdiscs/actions and interface up/down state. Risks include MPLS action support, offload mismatch, MAC push/pop correctness, and cleanup if qdisc creation partially fails. Test signals are successful IPv4 and IPv6 pings through the MPLS L2VPN.
