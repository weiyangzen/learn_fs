# sources/distributed-fs/ceph-client/net/ipv4/igmp_internal.h

## Purpose
`igmp_internal.h` provides the small internal interface needed to fill IPv4 multicast-address rtnetlink messages from IGMP membership state.

## Important APIs, Types, And Functions
`struct inet_fill_args` carries netlink port id, sequence number, event type, netlink flags, namespace id, and interface index for address message generation. `inet_fill_ifmcaddr` is declared for filling a multicast address message for a given `net_device` and `ip_mc_list`.

## Control Flow
The header has no executable logic. `igmp.c` implements `inet_fill_ifmcaddr`, using this argument bundle when constructing `RTM_NEWMULTICAST` or `RTM_DELMULTICAST` notifications.

## State And Persistence
No state is owned by the header. It defines a call contract for stack or caller-owned arguments.

## Dependencies And Integration Points
It depends on forward-declared kernel networking types from includers: `struct sk_buff`, `struct net_device`, and `struct ip_mc_list`. Its integration point is rtnetlink multicast address notification generation in `igmp.c`.

## Risks
Risk is low and mostly contractual. Field changes must stay synchronized with `inet_fill_ifmcaddr` callers and any future users. Missing include context can break compilation because this header does not include all type declarations itself.

## Test Signals
Build coverage and multicast address notification tests are sufficient. Validate that `inet_fill_ifmcaddr` messages include expected event, flags, interface index, multicast address, and cacheinfo fields.
