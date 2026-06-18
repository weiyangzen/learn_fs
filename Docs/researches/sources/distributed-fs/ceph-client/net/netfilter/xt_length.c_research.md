<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_length.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_length.c

## Purpose
`xt_length.c` implements matching on packet length. It supports IPv4 total length and IPv6 payload plus header length semantics for layer 3 packet size.

## Important APIs, Types, and Functions
`length_mt()` handles IPv4, `length_mt6()` handles IPv6, both consuming `struct xt_length_info`. `length_mt_reg[]` registers family-specific `length` matches.

## Control Flow, State, and Persistence
The matcher compares the packet length against configured `min` and `max` bounds and applies inversion. It stores no state and performs no allocation.

## Dependencies and Integration Points
It depends on x_tables and packet header length fields supplied by skb/IP header state. It is family-specific because IPv4 and IPv6 expose lengths differently.

## Risks and Test Signals
Risks include off-by-one boundary behavior, IPv6 length interpretation, and differences between skb length and IP total length under offloads or extension headers. Tests should cover exact min/max, below/above range, inversion, IPv4 total length, IPv6 payload length plus header, and malformed packets already rejected by earlier hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_length.c -->
