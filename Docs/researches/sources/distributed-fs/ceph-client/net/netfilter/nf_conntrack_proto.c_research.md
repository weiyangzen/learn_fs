<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto.c

## Purpose
Provides the protocol-family glue for core conntrack: L4 protocol lookup, IPv4/IPv6 hook registration, confirmation-time helper/seqadj execution, original-destination sockopts, per-net hook reference counting, bridge conntrack registration, and per-net protocol timeout initialization.

## Important APIs, Types, and Functions
Exports `nf_l4proto_log_invalid()`, `nf_ct_l4proto_log_invalid()`, `nf_ct_l4proto_find()`, `nf_confirm()`, `nf_ct_netns_get()`, `nf_ct_netns_put()`, `nf_ct_bridge_register()`, and `nf_ct_bridge_unregister()`. Lifecycle functions are `nf_conntrack_proto_init()`, `nf_conntrack_proto_fini()`, and `nf_conntrack_proto_pernet_init()`. `getorigdst()` and `ipv6_getorigdst()` back `SO_ORIGINAL_DST` and `IP6T_SO_ORIGINAL_DST`.

## Control Flow
`nf_ct_l4proto_find()` maps TCP, UDP, ICMP, ICMPv6, SCTP, GRE, or generic trackers. `nf_confirm()` retrieves the skb conntrack, skips VRF postrouting and related replies, computes the L4 offset, invokes any helper, applies seqadj when needed, and confirms the entry. `nf_ct_netns_get()` enables defrag and registers PRE_ROUTING/LOCAL_OUT/confirm hooks per family; `nf_ct_netns_put()` unregisters them when per-net users drop to zero.

## State and Persistence
State is global `nf_ct_proto_mutex`, global `nf_ct_bridge_info`, per-net `nf_conntrack_net` users for IPv4/IPv6/bridge, and per-net protocol timeout structures initialized here. Hook registration persists while namespace user counts are nonzero. TCP fixup resets max window tracking when hooks are newly enabled for existing established entries.

## Dependencies and Integration Points
Depends on netfilter hooks, IPv4/IPv6 defrag, conntrack core, helpers, seqadj, NAT helper declarations, bridge conntrack, sockopt registration, route/IP headers, and per-protocol init functions. It is the entry point used by nftables, iptables, OVS, bridge, and flow-table paths to enable conntrack in a namespace.

## Risks
Hook user counts and bridge module references must remain balanced. Confirmation ordering matters because helpers may mangle packets before seqadj and final confirmation. `SO_ORIGINAL_DST` tuple reconstruction only supports TCP/SCTP and depends on socket locking. IPv6 extension parsing in `nf_confirm()` must avoid handing helpers non-first fragments.

## Test Signals
Validate IPv4/IPv6 conntrack enable/disable cycles, bridge autoload, `SO_ORIGINAL_DST` for redirected TCP/SCTP, helper execution before confirmation, seqadj after NAT helper mangling, VRF postrouting skip, and sysctl-driven invalid packet logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto.c -->
