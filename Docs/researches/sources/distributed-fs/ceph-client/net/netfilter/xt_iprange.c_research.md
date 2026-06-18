<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_iprange.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_iprange.c

## Purpose
`xt_iprange.c` implements source and destination IP address range matching for IPv4 and IPv6. It lets iptables rules match inclusive address intervals without requiring prefix-shaped masks.

## Important APIs, Types, and Functions
`iprange_mt4()` compares IPv4 source/destination addresses with `struct xt_iprange_mtinfo`. `iprange_mt6()` performs IPv6 comparisons using `memcmp()` over `struct in6_addr`. Registration is in `iprange_mt_reg[]`.

## Control Flow, State, and Persistence
The match checks each enabled flag independently: source range, destination range, and their inversion bits. IPv4 addresses are converted with `ntohl()` for numeric range comparison; IPv6 addresses use lexicographic network-byte-order comparison. The module keeps no state.

## Dependencies and Integration Points
It integrates with x_tables, IPv4/IPv6 header access, and UAPI range structures. It is protocol-family-specific because address width differs.

## Risks and Test Signals
Risks include IPv6 lexicographic range assumptions, inclusive boundary handling, inverted source/destination logic, and invalid ranges supplied by userspace. Tests should cover min, max, inside, outside, inverted checks, IPv4 endian boundaries, IPv6 low/high byte transitions, and source plus destination combined rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_iprange.c -->
