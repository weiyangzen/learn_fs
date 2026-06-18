# sources/distributed-fs/ceph-client/include/uapi/linux/tc_act/tc_nat.h

## Purpose
Defines the legacy TC NAT action ABI for address rewriting with a mask and direction flag.

## Important APIs, Types, and Constants
`struct tc_nat` embeds `tc_gen` plus `old_addr`, `new_addr`, `mask`, and `flags`. `TCA_NAT_FLAG_EGRESS` selects egress behavior. Attributes include parameters, timing, and padding.

## Control Flow, State, and Persistence
Runtime action rewrites matching IPv4 address bits according to old/new/mask and direction, then generic action state tracks counters.

## Dependencies and Integration Points
Depends on `<linux/pkt_cls.h>` and `<linux/types.h>`. Integrates with TC action chains; checksum correction may require `tc_csum`.

## Risks and Test Signals
Risks include IPv4-only scope, checksum staleness, mask confusion, and overlap with conntrack NAT. Test ingress/egress rewrites, mask boundary cases, checksum follow-up, and dump/delete behavior.
