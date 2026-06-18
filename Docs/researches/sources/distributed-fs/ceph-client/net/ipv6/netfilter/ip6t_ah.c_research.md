# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_ah.c

Purpose: Implements the IPv6 xtables `ah` match for IPsec Authentication Header fields.

Important APIs/types/functions: Uses `ah_mt6`, `ah_mt6_check`, `spi_match`, `struct ip6t_ah`, `ipv6_find_hdr`, `skb_header_pointer`, and `ipv6_authlen`.

Control flow: The match locates an AH extension header, hotdrops on parse errors other than no-header, safely reads the AH header, computes header length, and checks SPI range, optional header length, inversion flags, and reserved-field policy. Checkentry rejects unknown inversion bits.

State and persistence: Stateless beyond per-rule match data.

Dependencies/integration: Registers one xt match for `NFPROTO_IPV6`; depends on IPv6 extension-header parsing and ip6tables match ABI.

Risks and test signals: Risks include header-length mismatch and hotdrop behavior on malformed extension chains. Tests should cover absent AH, truncated AH, SPI ranges with inversion, reserved bits, auth length matching, and unknown invflags.
