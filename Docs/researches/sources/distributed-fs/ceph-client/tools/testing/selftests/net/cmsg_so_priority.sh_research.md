# sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_so_priority.sh

Purpose: this script validates that `SO_PRIORITY` set by cmsg (`-Q`) and by setsockopt (`-P`) maps into VLAN egress priority and can be observed by tc flower filters. It covers IPv4 and IPv6 UDP, ICMP/ICMPv6, and raw traffic over a VLAN device.

Important APIs and commands: it requires `jq`, uses `ip netns`, `tc qdisc clsact`, `tc filter flower` with `vlan_prio`, JSON tc stats, a dummy lower device, a VLAN interface with `egress-qos-map 0:0 ... 7:7`, permanent neighbor entries, and `./cmsg_sender`.

Control flow: after creating the namespace and dummy/vlan devices, the script adds IPv4 and IPv6 addresses and static neighbors for normal and raw destinations. `create_filter` installs a flower egress filter on the lower dummy for a handle/priority/protocol/destination tuple. For each family, protocol, and priority 0..7, it checks the filter counter starts at zero, sends once with cmsg priority and expects one packet, then sends once with setsockopt priority and expects two packets.

State and persistence: all state is namespace-local tc, link, VLAN, address, and neighbor configuration. It is removed by `cleanup_ns`.

Dependencies and integration points: depends on `cmsg_sender`, tc flower, VLAN support, JSON output from tc, jq, and `ping_group_range` for ICMP. It also relies on priority-to-VLAN-qos propagation through the VLAN egress-qos-map.

Risks and test signals: the test is counter based, so extra matching packets can cause false failures. Raw traffic uses different destination addresses to avoid overlapping neighbor/filter state. Strong signals are tc JSON packet counters exactly 0, 1, then 2 for each filter.
