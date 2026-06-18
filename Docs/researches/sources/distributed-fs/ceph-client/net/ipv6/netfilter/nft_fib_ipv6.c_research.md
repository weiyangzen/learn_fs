# sources/distributed-fs/ceph-client/net/ipv6/netfilter/nft_fib_ipv6.c

Purpose: Implements IPv6 nftables `fib` expression evaluation, returning output interface, output interface name, or address type based on IPv6 FIB lookups and nft fib flags.

Important APIs, types, and functions: Exported evaluators are `nft_fib6_eval_type()` and `nft_fib6_eval()`. `nft_fib6_flowi_init()` maps nft flags and packet headers to `flowi6`. `nft_fib6_lookup()` wraps `fib6_lookup()`. Helper functions handle link-local lookup flags, l3mdev master devices, ICMPv6 skip behavior, and multipath sibling device matching. `nft_fib6_select_ops()` chooses expression ops based on requested result.

Control flow: Packet evaluation safely fetches the IPv6 header from the skb. Type evaluation builds a flow for destination or source reverse lookup, includes mark/iif/oif/l3mdev as requested, checks local address on a specific device, calls `fib6_lookup()`, maps reject/anycast/local/multicast/unicast/error cases to route types, and stores the type. Interface evaluation may fast-path `nft_fib_can_skip()`, skips certain unspecified-source ICMPv6 link-local cases, does the lookup, ignores reject/anycast/local routes, then stores either the nexthop device or the requested oif if any sibling route uses it.

State and persistence: Per-expression state is `struct nft_fib` from nft core. Runtime state is a stack `flowi6` and `fib6_result`; results are written to nft registers.

Dependencies and integration: Depends on nftables core, IPv6 FIB/routing, l3mdev, netdevice state, skb marks, and route type constants. Registered as family-specific expression alias `"fib"` for IPv6.

Risks and test signals: Risks include route result mapping differences, link-local oif handling, multipath sibling matching, l3mdev/VRF behavior, and safe skb header access. Tests should cover daddr/saddr lookups, mark-sensitive routing, iif/oif flags, local/anycast/reject routes, link-local destinations, VRFs, multipath, malformed short skbs, and `NFT_FIB_RESULT_*` op selection.
