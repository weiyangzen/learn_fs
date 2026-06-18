
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_ovs.c

Purpose: Provides NAT execution support for Open vSwitch and TC conntrack action paths outside the normal netfilter hook traversal.

Important APIs and functions: Exported `nf_ct_nat()` applies requested or existing NAT to an skb/conntrack and returns the performed manipulations in `action`. Internal `nf_ct_nat_execute()` mirrors IPv4/IPv6 NAT hook logic, including ICMP/ICMPv6 related reply translation and new-flow NAT initialization.

Control flow: `nf_ct_nat()` ensures a NAT extension exists for unconfirmed conntracks, determines the manipulation type from existing NAT status or requested action bits, then calls `nf_ct_nat_execute()`. For related ICMP errors it calls the protocol-specific reply translators. For new flows it initializes NAT from `range` or null binding. It then calls `nf_nat_packet()` and may apply both source and destination NAT when status bits require it.

State and persistence: No local state. It mutates conntrack NAT extension/status and skb headers, and reports action bits to the caller.

Dependencies and integration: Used by OVS and TC conntrack code. Depends on skb protocol helpers, NAT core, NAT protocol translation functions, and conntrack status/confirmation state.

Risks: Because it emulates hook-specific behavior, hooknum/maniptype mapping must stay aligned with `HOOK2MANIP()`. Risks include double NAT ordering, related ICMP handling, unconfirmed extension allocation failure, action bit reporting, and `commit` semantics for related flows. Test signals include OVS/TC ct NAT for new and established flows, combined SNAT+DNAT, ICMP/ICMPv6 errors, VLAN protocol skb detection, and non-commit related behavior.
