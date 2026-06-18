
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/q_in_vni.sh

Purpose: Tests 802.1ad service VLAN bridging over a VXLAN VNI for IPv4 underlay, including local and two remote namespace VTEPs.

Important APIs/functions: `h1_create/destroy`, `h2_create/destroy`, `rp1_set_addr/unset_addr`, `switch_create/destroy`, `vrp2_create/destroy`, `ns_init_common`, `ns1_create/destroy`, `ns2_create/destroy`, `ping_ipv4`, `test_all`.

Control flow: creates H1/H2 VLAN subinterfaces, switch bridge `br1` with VLAN protocol 802.1ad and VXLAN `vx100`, route peer `rp2`, two veth-backed netns VTEPs each with bridge `br2`, VXLAN, and VLAN host side. Runs pings from H1 to local H2 and two remote namespace hosts.

State/persistence: creates VXLAN devices, bridges, VLANs, veth pairs, netns `ns1`/`ns2`, routes, FDB flood entries, tc qdiscs, forwarding sysctls, and exported `VXPORT`.

Dependencies/integration: depends on network namespaces, VXLAN, bridge VLAN filtering with 802.1ad, `in_ns` helper, and `lib.sh`.

Risks: cleanup must move veth peers back before deleting namespaces. VXLAN UDP port defaults to 4789 but can be overridden. Remote namespace helpers source `lib.sh` with `NUM_NETIFS=0`.

Test signals: pings from H1 to 192.0.2.2, 192.0.2.3, and 192.0.2.4 succeed.
