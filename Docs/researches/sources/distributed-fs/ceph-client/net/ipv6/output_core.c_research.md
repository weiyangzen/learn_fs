# sources/distributed-fs/ceph-client/net/ipv6/output_core.c

Purpose: Provides small IPv6 output helpers needed by static components and packet offload paths, including fragment ID selection, first-fragment-option location, and local output entry points.

Important APIs, types, and functions: Exported functions are `ipv6_proxy_select_ident()`, `ipv6_select_ident()`, `ip6_find_1stfragopt()`, `__ip6_local_out()`, and `ip6_local_out()`. `__ipv6_select_ident()` currently returns a random 32-bit ID. `ip6_find_1stfragopt()` scans extension headers and returns where a Fragment header should be inserted.

Control flow: ID helpers read addresses from parameters or skb headers and return a network-order random ID. `ip6_find_1stfragopt()` walks Hop-by-Hop, Routing, and Destination Options headers, respecting Mobile IPv6 HAO and routing-header ordering, and rejects malformed/oversize chains. `__ip6_local_out()` fixes payload length, initializes `IP6CB(skb)->nhoff`, passes through l3mdev output handling, sets protocol, and invokes the local-output netfilter hook with `dst_output` continuation. `ip6_local_out()` calls the lower helper and runs `dst_output()` when netfilter returns pass-through `1`.

State and persistence: No persistent state. It mutates skb payload length, control block next-header offset, protocol, and possibly skb returned by l3mdev processing.

Dependencies and integration: Depends on IPv6 header helpers, l3mdev, netfilter local-output hook, route dst output, and random number generation. It is a central integration point for generated IPv6 packets such as rejects, duplicates, raw sends, and ping.

Risks and test signals: Risks include incorrect extension-header insertion offsets, malformed option chain handling, and local-output hook return handling. Tests should cover header chains with hop/routing/destination options, Mobile IPv6 HAO when enabled, malformed short options, l3mdev enslaved devices, netfilter drop/stolen/pass verdicts, and UFO proxy ID selection on non-linear skbs.
