<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_tcpudp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_tcpudp.c

## Purpose
`xt_tcpudp.c` provides the core built-in matches for TCP, UDP, UDP-Lite, ICMP, and ICMPv6. It handles port ranges, TCP flag and option matching, and ICMP type/code matching.

## Important APIs, Types, and Functions
`tcp_mt()` matches TCP ports, flags, and optional TCP option presence using `tcp_find_option()`. `udp_mt()` matches UDP/UDP-Lite source and destination ports. `icmp_match()` and `icmp6_match()` match type/code ranges with `icmp_type_code_match()` and `icmp6_type_code_match()`. Checkentry functions validate inversion masks. `tcpudp_mt_reg[]` registers all protocol/family combinations.

## Control Flow, State, and Persistence
TCP and UDP paths reject fragments; TCP offset 1 fragments are hotdropped. Headers are read with `skb_header_pointer()`, and truncated requested headers hotdrop. TCP checks source/destination port ranges, masked flags, and requested option. UDP checks port ranges. ICMP and ICMPv6 check type/code ranges and inversion. The module stores no persistent state.

## Dependencies and Integration Points
It depends on x_tables, IPv4/IPv6 protocol registration, TCP/UDP/ICMP header definitions, and safe skb access. These matches are fundamental iptables protocol matches.

## Risks and Test Signals
Risks include hotdrop decisions for tinygrams, TCP option parsing, ICMP wildcard semantics differing between IPv4 and IPv6, inversion flag validation, and fragmented packets. Tests should cover TCP ports/flags/options, UDP and UDP-Lite ports, ICMP any and ranged codes, ICMPv6 type/code, invalid invflags, truncated headers, TCP offset-1 fragments, ordinary fragments, and IPv4/IPv6 registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_tcpudp.c -->
