# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_ipv6header.c

Purpose: Implements the IPv6 xtables `ipv6header` match, classifying which extension/header categories are present in a packet.

Important APIs/types/functions: Uses `ipv6header_mt6`, `ipv6header_mt6_check`, `struct ip6t_ipv6header_info`, `nf_ip6_ext_hdr`, `skb_header_pointer`, `ipv6_authlen`, and `ipv6_optlen`.

Control flow: Starting after the base IPv6 header, it walks extension headers while they are known IPv6 extension types, records masks for hop-by-hop, routing, fragment, AH, destination options, ESP, none, and final protocol, then applies soft mode or hard exact mode with inversion semantics. Checkentry restricts hard-mode `invflags` to all-zero or all-ones.

State and persistence: Stateless.

Dependencies/integration: xtables IPv6 match ABI and IPv6 extension-header definitions.

Risks and test signals: Risks include malformed extension-length handling, ESP/NONE terminal behavior, and hard-mode inversion compatibility with userspace. Tests should cover every extension mask, mixed chains, truncated headers, final upper-layer protocol mask, modeflag behavior, and invalid hard-mode invflags.
