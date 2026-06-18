# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_symmetric.sh

## Purpose

This selftest builds an IPv4 symmetric VXLAN routing topology. Unlike the asymmetric test, same-subnet traffic uses L2 VNIs while routed cross-subnet remote traffic uses a separate L3 VNI on VLAN 4001 with static routes through the remote VTEP.

## Important APIs, Types, and Functions

It uses forwarding helpers from `lib.sh` and local helpers `hx_create`, `switch_create`, `spine_create`, `ns_switch_create`, `__l2_vni_init`, `l2_vni_init`, `__l3_vni_init`, `l3_vni_init`, and `ping_ipv4`. It configures `vx10`, `vx20`, and `vx4001`.

## Control Flow

`setup_prepare` creates local hosts and switch, an underlay veth to `ns1`, a spine VRF, remote namespace hosts and switch, then installs L2 VNI FDB/neighbor entries and L3 VNI FDB/neighbor/route entries on both VTEPs. `ping_ipv4` validates local switching, same-VLAN remote traffic, and cross-VLAN remote traffic. Cleanup removes the namespace, spine, VTEP, bridge, VRF, and host state.

## State and Persistence Behavior

The script creates temporary bridge/VXLAN/SVI/macvlan/VRF/netns state. L3 VNI state includes `vlan4001`, `vx4001`, static FDB entries for the remote L3 VNI MAC, noarp neighbor entries for VTEP IPs on `vlan4001`, and per-host `/32` routes in `vrf-green` via the remote VTEP.

## Dependencies and Integration Points

It depends on bridge VLAN filtering, VXLAN, VRF routing, macvlan gateway addresses, veth namespaces, IPv4 routing, and the forwarding kselftest framework. It exercises the kernel path where bridged L2 VXLAN and routed L3 VNI traffic coexist on the same bridge.

## Risks and Edge Cases

Static programming must match both local and namespace MACs exactly. The L3 VNI has no `remote` argument on creation; delivery relies on FDB entries and routes. Reverse-path filtering is disabled for SVI/macvlan devices to avoid drops in the symmetric routing path.

## Test Signals

Success is the five IPv4 ping checks passing: local-to-local, remote same-VLAN for both VLANs, and remote cross-VLAN in both directions.
