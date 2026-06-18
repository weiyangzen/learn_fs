# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_vid_1.sh

Purpose: validates routing over VLAN ID 1 on host and router interfaces. VLAN 1 can have special bridge/default-PVID associations, so this script exercises plain routed VLAN uppers with ID 1.

Key functions are `h1_create`, `h2_create`, `router_create`, `ping_ipv4`, and `ping_ipv6`. Hosts create VRFs manually and use `vlan_create $h1 1 vrf-h1` and `vlan_create $h2 1 vrf-h2`; router ports `$rp1` and `$rp2` each create `$rp*.1` VLAN devices with IPv4 and IPv6 addresses.

Control flow creates host VLAN uppers in VRFs, adds routes via router VLAN addresses, creates router VLAN uppers and addresses, enables forwarding, then runs pings. State is VLAN ID 1 netdevices, VRFs, routes, and forwarding sysctls. Risks include VLAN 1 treatment differing from other VLAN IDs, route deletion requiring matching nexthop parameters, and cleanup order if VLAN devices fail to create. Test signals are IPv4 ping from `$h1.1` to H2 and IPv6 ping from `$h1.1` to H2.
