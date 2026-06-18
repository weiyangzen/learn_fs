# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_asymmetric.sh

## Purpose

This selftest builds an IPv4 asymmetric VXLAN routing topology with two bridge VLANs, two L2 VNIs, local and remote hosts, a routed underlay spine, and a peer switch inside `ns1`. It validates that the Linux bridge, VXLAN devices, SVIs, macvlan gateway addresses, static FDB entries, and external-learn neighbor entries support local and remote cross-subnet forwarding in an EVPN-like asymmetric model.

## Important APIs, Types, and Functions

The script is driven by kselftest forwarding helpers from `lib.sh`: `vrf_prepare`, `vrf_create`, `forwarding_enable`, `ping_test`, `mac_get`, `in_ns`, `tc_rule_stats_get`, and `tests_run`. Local helpers include `hx_create`/`hx_destroy` for host VRFs, `switch_create`/`switch_destroy`, `spine_create`/`spine_destroy`, namespace setup helpers, `macs_populate`, `macs_initialize`, `ping_ipv4`, `arp_decap`, `arp_suppression_compare`, and `arp_suppression`. It requires `$ARPING`.

## Control Flow

`setup_prepare` maps six test interfaces, enables VRF and forwarding support, creates the two local hosts, builds the local bridge/VXLAN/SVI switch, creates a veth underlay into `ns1`, builds a spine VRF between the local and namespace VTEPs, creates the remote namespace switch and hosts, then pre-populates FDB and neighbor state on both VTEPs. `tests_run` executes `ping_ipv4`, `arp_decap`, and `arp_suppression`; `trap cleanup EXIT` tears everything down in reverse order.

## State and Persistence Behavior

All state is ephemeral kernel networking state: VRFs, bridge `br1`, VXLAN devices `vx10` and `vx20`, VLAN devices, macvlans with the shared gateway MAC `00:00:5e:00:01:01`, static bridge FDB entries, external-learn neighbor entries, routes, veth pairs, `ns1`, and temporary `tc` filters. The script also changes IPv4 reverse-path filtering with `sysctl_set` and restores it with `sysctl_restore`.

## Dependencies and Integration Points

The test integrates with the forwarding kselftest framework, `iproute2`, bridge VLAN/FDB commands, ARP tooling, `tc flower`, VRF support, VXLAN, macvlan, network namespaces, and veth. It is a user-space regression probe for kernel bridge VXLAN decapsulation, ARP suppression, neighbor lookup, and external-learn FDB behavior.

## Risks and Edge Cases

The topology depends on exact static MAC and neighbor programming; missing cleanup can leave conflicting bridge/VXLAN objects. Hardware offload behavior can affect counter visibility, so the ARP suppression check focuses on `tc` rule deltas. `arp_decap` deliberately removes neighbors to force ARP decapsulation behavior. Reverse-path filtering must be disabled on the SVI/macvlan path or valid asymmetric traffic can be dropped.

## Test Signals

Passing signals are five IPv4 ping paths covering local-to-local, same-VLAN remote, and cross-VLAN remote traffic; successful ping after deleting SVI neighbors; and ARP suppression counter deltas of 0, 1, 2, and 3 for the four neighbor/suppression states.
