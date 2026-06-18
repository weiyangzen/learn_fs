# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_vlan_upper.sh

Purpose: tests routing through VLAN upper devices on a VLAN-aware bridge. H1 uses VLAN 555, H2 uses VLAN 777, and the router presents `br1.555` and `br1.777` as L3 interfaces over the same bridge.

Important functions are `router_create`, `respin_config`, `ping_ipv4`, and `ping_ipv6`. The bridge is created with `vlan_filtering 1`, both switch ports are enslaved, bridge self and port VLANs are added, then `vlan_create br1 555` and `vlan_create br1 777` create routed upper devices. The script depends on `lib.sh` for VRF, VLAN, address, and ping helpers.

Control flow creates hosts and bridge VLAN uppers, enables forwarding, verifies dual-stack reachability, detaches both bridge slave ports, waits, reattaches them, reapplies VLAN membership, and verifies reachability again. State is bridge membership, bridge VLAN table, VLAN upper devices, routes, addresses, and forwarding sysctls. Risks include VLAN membership being lost across remastering, bridge MAC/address interactions, and cleanup order between VLAN uppers and bridge deletion. Test signals are successful pings from H1 to H2 over IPv4 and IPv6 before and after `respin_config`.
