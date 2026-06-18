<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_ipcomp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_ipcomp.c

## Purpose
`xt_ipcomp.c` implements the `ipcomp` match for IP Payload Compression Protocol packets. It matches the Compression Parameter Index range.

## Important APIs, Types, and Functions
`comp_mt()` reads `struct ip_comp_hdr` and calls `cpi_match()` against `struct xt_ipcomp`. `comp_mt_check()` validates inversion flags. Registration covers IPv4 and IPv6 with `.proto = IPPROTO_COMP`.

## Control Flow, State, and Persistence
Non-initial fragments are ignored. The IPComp header is fetched with `skb_header_pointer()`, missing headers hotdrop the packet, and CPI is compared in host order against `spis[0]` and `spis[1]` with optional inversion. No state is stored.

## Dependencies and Integration Points
The module depends on x_tables, IPv4/IPv6 protocol registration, and IPComp header definitions. It complements but does not inspect xfrm policy or decompression state.

## Risks and Test Signals
Risks include truncation hotdrops, endian mistakes on CPI, fragments hiding the header, and confusion with ESP SPI matching. Tests should cover CPI boundaries, inversion, fragments, short headers, IPv4/IPv6, and invalid inversion flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_ipcomp.c -->
