<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_tcpmss.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_tcpmss.c

## Purpose
`xt_tcpmss.c` implements matching on the TCP Maximum Segment Size option.

## Important APIs, Types, and Functions
`tcpmss_mt()` consumes `struct xt_tcpmss_match_info`, reads `struct tcphdr`, walks TCP options, and compares an MSS option value against `mss_min` and `mss_max`. `tcpmss_mt_reg[]` registers IPv4 and IPv6 TCP-only matches.

## Control Flow, State, and Persistence
Fragments are ignored. The TCP header is fetched safely; truncated or malformed headers hotdrop. If no MSS option is present, the result is the configured invert value. If an MSS option is found with the correct length, the inclusive range comparison determines the result. No state is persisted.

## Dependencies and Integration Points
The module depends on x_tables, TCP option layout, skb header access, and protocol restriction to TCP. It only observes MSS; MSS clamping is implemented in a different target.

## Risks and Test Signals
Risks include malformed TCP data offsets, option length parsing, missing MSS on non-SYN packets, fragments, and range boundaries. Tests should cover SYN with MSS below/inside/above range, no MSS, inverted no-MSS behavior, short headers hotdrop, malformed doff, option padding, IPv4/IPv6, and fragments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_tcpmss.c -->
