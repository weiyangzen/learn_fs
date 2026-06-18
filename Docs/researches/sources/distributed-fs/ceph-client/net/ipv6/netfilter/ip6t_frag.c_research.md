# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_frag.c

Purpose: Implements the IPv6 xtables `frag` match for Fragment Header fields.

Important APIs/types/functions: Uses `frag_mt6`, `frag_mt6_check`, `id_match`, `struct ip6t_frag`, `ipv6_find_hdr`, and `skb_header_pointer`.

Control flow: The match locates the Fragment Header, hotdrops malformed parse errors, reads the header safely, and evaluates identification range plus flags for reserved bits, first fragment, more fragments, and last fragment. Unknown inversion flags are rejected at checkentry.

State and persistence: Stateless beyond rule parameters.

Dependencies/integration: Registers with xtables for IPv6 and depends on extension-header parsing.

Risks and test signals: Risks include ambiguity around non-first fragments and reserved bit handling. Tests should include no fragment header, truncated header, each flag combination, inverted ID ranges, malformed extension chains, and first/non-first/last fragment packets.
