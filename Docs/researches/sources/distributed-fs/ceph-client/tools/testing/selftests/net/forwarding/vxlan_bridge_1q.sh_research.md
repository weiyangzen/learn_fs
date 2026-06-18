# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1q.sh

## Purpose

This selftest validates VXLAN devices attached to an 802.1Q VLAN-filtering bridge over an IPv4 underlay. VLAN 10 and VLAN 20 are mapped to separate VXLAN devices and VNIs, and the test verifies VLAN-scoped local switching, remote flooding, static unicast forwarding, VXLAN learning, FDB aging, and PVID/VLAN membership effects.

## Important APIs, Types, and Functions

The script uses `lib.sh`, `vlan_create`, bridge VLAN/FDB commands, `$MZ`, `tc`, and network namespace helpers. Key functions are `h1_create`, `h2_create`, `switch_create`, `ns_init_common`, `reapply_config`, `ping_ipv4`, `vxlan_flood_test`, `test_flood`, `vxlan_fdb_add_del`, `test_unicast`, `test_pvid`, `__test_learning`, and `test_learning`.

## Control Flow

Setup creates VLAN subinterfaces on local hosts, a VLAN-filtering `br1`, two VXLAN devices `vx10` and `vx20`, tagged local bridge ports, all-zero flood FDB entries for two remote VTEPs, remote namespaces with matching VLAN bridges and VXLAN devices, and cached remote MACs. The default test list runs reachability and flood/unicast checks, reapplies VXLAN/local-IP configuration, repeats checks, then tests learning and PVID mutation.

## State and Persistence Behavior

Temporary state includes VLAN subinterfaces, bridge VLAN membership, VXLAN devices, bridge FDB entries with VLAN-qualified master entries, `tc` qdiscs/counters, namespace veths, and generated packets. `test_learning` modifies VXLAN learning and aging timers, verifies self and VLAN-qualified bridge FDB entries, deletes entries, waits for aging, and restores nolearning/default timers.

## Dependencies and Integration Points

It integrates with Linux bridge VLAN filtering, VXLAN VNI mapping, bridge FDB learning, the forwarding kselftest library, mausezahn, `tc`, and network namespaces. It is a regression test for VLAN-aware bridge offload and software datapath behavior.

## Risks and Edge Cases

Flood counter logic temporarily marks the local destination VLAN untagged so the same ICMP filters can see local and VXLAN traffic. Hardware offload can affect `skip_sw`/`skip_hw` counter installation. PVID toggling verifies that removing PVID or deleting VLAN membership suppresses remote flooding without breaking local delivery. The learning age-out uses sleeps and can be timing-sensitive.

## Test Signals

Passing signals are VLAN 10 and 20 local/remote pings, exact flood distribution only to the matching VNI devices, static unicast delivery to one selected local or remote destination, learned FDB entry presence and aging, learning-off suppression of bridge FDB population, and PVID/VLAN deletion/re-addition affecting remote flooding as expected.
