# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/dual_vxlan_bridge.sh

## Purpose
`dual_vxlan_bridge.sh` tests two independent VXLAN-backed bridge services in one topology: an 802.1ad VLAN-filtering VXLAN bridge and an 802.1d-style VXLAN bridge carrying a VLAN subinterface. It verifies local hosts can reach remote hosts placed in separate network namespaces through VXLAN tunnels and bridge FDB flooding entries.

## Important APIs, Functions, and Control Flow
The script accepts `VXPORT` from the environment, defaulting to 4789. Host setup creates `$h1.10` and `$h2.20`, with tc `clsact` on host devices. `switch_create` builds `br1` as VLAN-filtering 802.1ad with PVID 100 and `br2` as VLAN-unaware, sets bridge MACs to physical switch-port MACs, configures underlay address/routes on `$rp1`, creates `vx100` and `vx200` with `nolearning`, `noudpcsum`, `tos inherit`, and static all-zero FDB append entries toward remote VTEPs. `$swp1` joins `br1`; `$swp2.20` joins `br2`.

`vrp2_create` creates the software underlay peer with veths `v1/v2` and `v3/v4`. `ns_init_common` is exported and run inside `ns1` and `ns2` to configure underlay addresses, `br3`, veth pair `w1/w2`, a VXLAN device, remote FDB entries, host VLAN endpoint, and routes. `ns1_create` configures the 802.1ad/VLAN 100 side; `ns2_create` configures the 802.1d/VLAN 20 side. `ping_ipv4` checks `$h1` to remote `192.0.2.3` and `$h2` to remote `192.0.2.4`.

## State, Dependencies, Integration Points, and Risks
State spans the root namespace, VRFs, two network namespaces, veths, VXLAN devices, bridge FDB entries, VLAN subinterfaces, underlay routes, and tc qdiscs. Dependencies include `lib.sh`, VXLAN kernel support, namespace support, `bridge fdb append`, and stable names `ns1`, `ns2`, `br1`, `br2`, `br3`, `vx100`, `vx200`. Cleanup moves namespace veth peers back before deleting namespaces. Risk is relatively high because a failed mid-setup can leave namespaces or named devices behind; static names also collide with parallel runs.

## Test Signals
The only data-plane signals are the two IPv4 `ping_test` calls, plus setup command failures captured by the kselftest helpers. `test_all` logs the UDP VXLAN port before invoking `tests_run`.
