<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_defrag_ipv6.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_defrag_ipv6.h

## Purpose
`ipv6/nf_defrag_ipv6.h` declares IPv6 fragment reassembly hooks and per-netns fragment state used by conntrack/netfilter.

## Important APIs, types, and functions
It declares enable/disable, global init/cleanup, `nf_ct_frag6_gather`, and `struct nft_ct_frag6_pernet` containing sysctl header and fragment queue directory.

## Control flow
Users enable IPv6 defrag for a namespace. Packet paths call gather to reassemble or queue fragments before conntrack processing. Init/cleanup manage global IPv6 fragment infrastructure.

## State and persistence
Per-netns state includes fragment sysctl registration and fqdir. Runtime fragment queues live in the implementation.

## Dependencies and integration points
It depends on skb, types, `struct net`, fragment control types, and netfilter. It integrates IPv6 fragmentation with conntrack and nftables.

## Risks and test signals
Risks include fragment queue memory limits, namespace cleanup ordering, unbalanced enable/disable, overlapping fragment handling, and user identifier mismatches. Tests should cover fragmented IPv6 flows, namespace teardown, sysctl registration, and memory pressure.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_defrag_ipv6.h` completely for this pass (22 lines, 523 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv6/nf_defrag_ipv6.h -->
