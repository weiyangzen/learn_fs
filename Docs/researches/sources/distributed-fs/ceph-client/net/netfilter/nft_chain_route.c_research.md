# sources/distributed-fs/ceph-client/net/netfilter/nft_chain_route.c

## Purpose
`nft_chain_route.c` registers nftables `route` chain types for IPv4, IPv6, and inet local-output hooks. Route chains run nftables rules and then force route recalculation if rules changed routing-relevant packet fields such as addresses, mark, TOS/flow label, or hop limit.

## Important APIs, Types, and Functions
Hook wrappers are `nf_route_table_hook4()`, `nf_route_table_hook6()`, and `nf_route_table_inet()`. Chain type descriptors are `nft_chain_route_ipv4`, `nft_chain_route_ipv6`, and `nft_chain_route_inet`. Lifecycle APIs are `nft_chain_route_init()` and `nft_chain_route_fini()`.

## Control Flow, State, and Persistence
IPv4 local-output hook setup records source address, destination address, skb mark, and TOS before running `nft_do_chain()`. If the verdict is `NF_ACCEPT` and any of those fields changed, it calls `ip_route_me_harder()` and converts route failure into `NF_DROP_ERR(err)`.

IPv6 records source and destination addresses, mark, hop limit, and the first header word containing version, traffic class, and flow label. After accepted rule evaluation, it calls `nf_ip6_route_me_harder()` if any saved field differs. The inet route hook dispatches to the IPv4 or IPv6 hook based on `state->pf`; unknown families simply run the chain with generic packet info.

Persistent state is only registered chain type metadata. Route recalculation side effects occur per packet.

## Dependencies and Integration Points
The file integrates nftables local-output route chains with IPv4/IPv6 routing helpers, nft packet-info setup, and netfilter local-out hook semantics. It relies on rule expressions that may modify packet headers or skb mark.

## Risks and Test Signals
Risks include missing a field that should trigger reroute, rerouting after packet modifications that changed header pointers, IPv6 first-word unaligned access assumptions, inet dispatch for optional family builds, and correct drop-error propagation. Tests should modify each watched field separately, leave fields unchanged, trigger route helper failure, run IPv4 and IPv6 inet route chains, and verify non-accept verdicts do not reroute.
