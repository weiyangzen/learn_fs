# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_asymmetric_ipv6.sh

## Purpose

This is the IPv6 counterpart of the asymmetric VXLAN routing test. It builds two L2 VXLAN segments over an IPv6 underlay, routes host traffic through VLAN SVIs and macvlan gateway addresses, and validates local, remote same-VLAN, and remote cross-VLAN connectivity.

## Important APIs, Types, and Functions

It uses `lib.sh` helpers for VRFs, namespace execution, ping, cleanup, forwarding, and MAC discovery, plus `$ARPING` even though the packet path uses IPv6 neighbor entries rather than ARP addresses. Local helpers mirror the IPv4 script: `hx_create`, `switch_create`, `spine_create`, `ns_switch_create`, `macs_populate`, `macs_initialize`, `ping_ipv6`, and `arp_decap`.

## Control Flow

`setup_prepare` assigns six interfaces, creates local host VRFs, creates the local bridge with `vx10` and `vx20`, sets IPv6 VTEP loopback routes through `rp1`/`rp2` and `v1`/`v2`, initializes `ns1`, enables forwarding in the namespace, and installs static FDB/neighbor entries. The test list runs `ping_ipv6` and `arp_decap`, then the exit trap destroys the namespace, spine, VXLANs, SVIs, VRFs, and forwarding state.

## State and Persistence Behavior

Runtime state is entirely temporary: IPv6 addresses and routes, VXLAN devices with `udp6zerocsumrx` and `udp6zerocsumtx`, VLAN bridge membership, macvlan gateway devices, static FDB entries, noarp external-learn neighbor entries, veth links, and netns `ns1`. No files are written.

## Dependencies and Integration Points

The test depends on IPv6 forwarding, Linux bridge VLAN filtering, VXLAN over IPv6, netns/veth, `ip neigh`, and kselftest forwarding helpers. It integrates with the kernel VXLAN and bridge datapath by validating that IPv6-encapsulated VXLAN traffic decapsulates and forwards correctly through VLAN-aware bridge and SVI routing constructs.

## Risks and Edge Cases

The namespace-side SVI setup uses the same IPv6 address on `vlan10`/`vlan10-v` and `vlan20`/`vlan20-v`, which makes the intended virtual gateway behavior sensitive to kernel duplicate-address handling and DAD suppression. Missing `udp6zerocsum*` support or disabled IPv6 forwarding causes false failures. Neighbor deletion in `arp_decap` intentionally stresses decapsulation of discovery traffic despite the IPv4-oriented function name.

## Test Signals

Success is all `ping6_test` calls passing for local and remote host pairs, followed by the same ping matrix passing after remote neighbor entries are removed and restored on the SVI devices.
