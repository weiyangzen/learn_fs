# sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_dup_ipv6.c

Purpose: Implements IPv6 packet duplication for TEE-like netfilter targets and nftables `dup`. It copies an skb, routes the copy toward a configured gateway/interface, and transmits it without consuming the original packet.

Important APIs, types, and functions: `nf_dup_ipv6()` is the exported duplication API. `nf_dup_ipv6_route()` builds a `flowi6`, performs `ip6_route_output()`, attaches the dst, sets output device/protocol, and reports route success. The module uses `current->in_nf_duplicate` as a recursion guard.

Control flow: `nf_dup_ipv6()` disables bottom halves, checks recursion, copies the skb with `GFP_ATOMIC`, clears conntrack state and marks it untracked when conntrack is enabled, decrements hop limit for prerouting/local-in duplicates, routes to the gateway, and emits through `ip6_local_out()`. On route or allocation failure it frees the copy. The original skb continues through its caller's rule path.

State and persistence: No persistent state. Temporary cloned skb state is adjusted: conntrack reset, optional hop-limit decrement, dst replacement, output dev, protocol, and recursion flag around output.

Dependencies and integration: Depends on IPv6 routing/output, netfilter hook numbers, conntrack reset helpers, and consumers in xt/nft duplication modules. It must integrate safely with local-output netfilter because the duplicated skb re-enters output.

Risks and test signals: Risks include recursion loops, hop-limit underflow behavior, route lookup to link-local gateways without correct oif, and copied skb metadata leakage. Tests should duplicate from prerouting and local-in, verify original delivery continues, verify conntrack is not inherited, test unreachable gateways, explicit oif, and rules that could recursively match duplicates.
