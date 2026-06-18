<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_mark.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_mark.c

## Purpose
`xt_mark.c` implements packet mark manipulation and matching. It provides the `MARK` target for `skb->mark` updates and the `mark` match for testing mark values.

## Important APIs, Types, and Functions
`mark_tg()` updates `skb->mark` using `struct xt_mark_tginfo2.mark` and `mask`. `mark_mt()` compares `(skb->mark & mask)` to the configured mark with optional inversion. `mark_tg_reg[]` registers target aliases for IPv4, IPv6, and ARP; `mark_mt_reg` registers the protocol-unspecified match.

## Control Flow, State, and Persistence
The target computes `(skb->mark & ~mask) ^ mark`, writes it to the skb, and continues traversal. The match reads the current mark and compares selected bits. Packet marks persist with the skb through later hooks and routing decisions but are not connection-persistent unless other modules save them.

## Dependencies and Integration Points
It integrates with routing, tc, policy routing, connmark, and other subsystems that consume `skb->mark`. Registration covers multiple x_tables families.

## Risks and Test Signals
Risks include xor/mask semantics, interactions with route lookup timing, mark overwrite order across tables, and ARP versus IP family differences. Tests should cover masked set, clear, toggled-looking cases, match inversion, multiple rules in sequence, IPv4/IPv6/ARP targets, and interaction with connmark save/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_mark.c -->
