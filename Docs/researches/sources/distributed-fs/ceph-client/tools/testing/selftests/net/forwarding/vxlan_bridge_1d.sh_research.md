# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_bridge_1d.sh

## Purpose

This selftest validates VXLAN behavior on a non-VLAN-filtering 802.1D bridge over an IPv4 underlay. It covers host reachability, flooding to multiple remote VTEPs, static unicast FDB selection, tunnel TTL/TOS/ECN behavior, reapplying bridge/VTEP configuration in a different order, and dynamic VXLAN learning and aging.

## Important APIs, Types, and Functions

The script uses `lib.sh` helpers, `ip`, `bridge`, `tc`, `$MZ`, `ping_do`, `payload_template_calc_checksum`, `payload_template_expand_checksum`, `link_stats_rx_errors_get`, and namespace helpers. Major functions include `switch_create`, `vrp2_create`, `ns_init_common`, `reapply_config`, `vxlan_flood_test`, `test_flood`, `vxlan_fdb_add_del`, `test_unicast`, `vxlan_ping_test`, `test_ttl`, `test_tos`, `test_ecn_encap`, `vxlan_encapped_ping_do`, `test_ecn_decap`, and `test_learning`.

## Control Flow

Setup creates local hosts `h1`/`h2`, bridge `br1`, underlay routes through `rp1`/`rp2`, remote namespaces `ns1` and `ns2`, and VXLAN devices using multicast-like all-zero FDB entries for remote VTEPs. The default `ALL_TESTS` first validates base reachability and tunnel metadata, then calls `reapply_config` to detach VXLAN and underlay local IP state and reattach them before repeating flooding and unicast tests and running learning coverage.

## State and Persistence Behavior

The script creates temporary VRF and namespace networking state, `clsact` qdiscs, `tc flower` counters, bridge FDB entries, VXLAN device attributes, and generated traffic. `test_learning` temporarily enables VXLAN learning and short bridge/VXLAN aging timers, verifies learned self/master FDB entries, deletes and re-learns them, waits for aging, toggles bridge port learning, then restores nolearning and default aging.

## Dependencies and Integration Points

It integrates with the forwarding selftest harness, Linux bridge, VXLAN, veth, network namespaces, `tc`, `mausezahn`, ping, and ethtool-visible offload behavior. The test is sensitive to both pure software datapath and hardware offload paths because comments explicitly handle `skip_hw`/`skip_sw` counter behavior.

## Risks and Edge Cases

Counter tests tolerate small stray packet counts for ping-based checks but require exact flood/unicast distribution. Hardware offload can double-count trapped traffic, so the script dynamically chooses `skip_sw` or `skip_hw`. ECN decapsulation tests craft raw inner IPv4 packets and expect one invalid ECN combination to increment VXLAN RX errors. The 60-second learning aging phase is timing-sensitive.

## Test Signals

Signals include successful pings to local and both remote hosts, flood counters of 10 packets on all intended destinations, unicast counters only on the selected target, TTL 99 and TOS inheritance matches on egress, all ECN mapping cases, RX error accounting for invalid ECN decap, and learned FDB presence/deletion/aging behavior.
