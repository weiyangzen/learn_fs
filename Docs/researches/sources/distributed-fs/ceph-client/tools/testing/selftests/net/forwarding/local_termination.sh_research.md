
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/local_termination.sh

Purpose: Validates which unicast, multicast, link-local, VLAN, bridge, and PTP packets are locally terminated by a NIC/bridge/VLAN stack.

Important APIs/functions: constants for test addresses and raw packet payloads; `send_raw`, `send_uc_ipv4`, `check_rcv`, `mc_route_prepare/destroy`, `run_test`; topology helpers for standalone, VLAN, bridge, macvlan, and VLAN-over-bridge scenarios.

Control flow: each scenario builds a topology, starts tcpdump on the receive interface, sends primary-MAC, macvlan-MAC, unknown unicast, joined/unknown IPv4/IPv6 multicast, promisc/allmulti cases, link-local STP/LLDP, and PTP over L2/IPv4/IPv6. It stops tcpdump and matches packet text against expected receipt/nonreceipt patterns.

State/persistence: creates VRFs, VLAN devices, bridge `br0`, macvlan `macvlan0`, multicast routes, multicast memberships via mtools, tcpdump temp files, and toggles promisc/allmulti flags. Cleanup removes topology and route-rule state.

Dependencies/integration: requires mtools (`REQUIRE_MTOOLS=yes`), tcpdump, mausezahn, `has_unicast_flt`, multicast helpers, and `lib.sh`.

Risks: tcpdump text patterns are version-sensitive. Unknown multicast tests are marked xfail in selected cases. PTP checks are skipped for bridge receiver scenarios. Hardware unicast filtering capability changes expectations.

Test signals: per-packet-type `check_rcv` pass/fail logs across standalone, VLAN, VLAN-aware/unaware bridge, VLAN over bridged port, and VLAN over bridge scenarios.
