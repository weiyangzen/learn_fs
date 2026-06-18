
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/q_in_vni_ipv6.sh

Purpose: IPv6 version of the 802.1ad-in-VXLAN VNI test, using IPv6 underlay and IPv6 tenant addresses.

Important APIs/functions: mirrors `q_in_vni.sh` with IPv6 addresses; key functions include `switch_create`, `ns_init_common`, `ns1_create`, `ns2_create`, `ping_ipv6`, and `test_all`.

Control flow: builds local H1/H2 VLAN subinterfaces, bridge `br1` with VXLAN `vx100` using IPv6 local/remote addresses and zero-checksum options, peer router `rp2`, and two remote namespaces with their own bridges/VXLANs/VLAN host sides. Runs ping6 from H1 to local and remote tenant addresses.

State/persistence: creates IPv6 routes, VXLAN devices with `udp6zerocsumrx/tx`, netns, veth pairs, 802.1ad bridges, VLANs, tc qdiscs, FDB entries, and forwarding sysctls.

Dependencies/integration: depends on IPv6 VXLAN support, bridge VLAN filtering, namespace execution via `in_ns`, and `lib.sh`.

Risks: IPv6 zero-checksum options and route ordering can vary by kernel. As with IPv4, namespace cleanup depends on moving veth peers back to init netns.

Test signals: ping6 from H1 to 2001:db8:1::2, 2001:db8:1::3, and 2001:db8:1::4 succeeds, with test output including configured UDP port.
