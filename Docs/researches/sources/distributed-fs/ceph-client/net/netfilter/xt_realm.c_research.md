<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_realm.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_realm.c

## Purpose
`xt_realm.c` implements matching on the routing realm associated with the packet destination route.

## Important APIs, Types, and Functions
`realm_mt()` reads `dst->tclassid` from `skb_dst(skb)` and compares it with `struct xt_realm_info.id` and `mask`. `realm_mt_reg` registers an IPv4 alias match.

## Control Flow, State, and Persistence
Each packet must have a dst entry. The matcher applies the configured mask to the route class id and compares it with the requested id, then applies inversion. It does not persist any state.

## Dependencies and Integration Points
The module depends on route lookup having attached an skb dst and on routing realms/classids configured by routing policy. It integrates with x_tables and dst metadata.

## Risks and Test Signals
Risks include packets before route lookup, missing dst entries, policy routing changes, and mask/id confusion. Tests should cover matched and unmatched realms, inversion, no dst, masked subfields, local and forwarded routes, and route updates while rules remain loaded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_realm.c -->
