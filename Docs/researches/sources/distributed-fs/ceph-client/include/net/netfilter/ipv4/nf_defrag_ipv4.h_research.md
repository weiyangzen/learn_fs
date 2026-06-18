<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_defrag_ipv4.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_defrag_ipv4.h

## Purpose
`ipv4/nf_defrag_ipv4.h` declares per-netns enable/disable hooks for IPv4 fragment reassembly needed by conntrack and netfilter users.

## Important APIs, types, and functions
It declares `nf_defrag_ipv4_enable` and `nf_defrag_ipv4_disable`.

## Control flow
Netfilter modules call enable when they need IPv4 defragmentation in a namespace and disable when releasing their reference.

## State and persistence
Reference/state tracking is in the implementation and per network namespace.

## Dependencies and integration points
It depends on `struct net` and integrates IPv4 fragment handling with netfilter/conntrack.

## Risks and test signals
Risks include unbalanced enable/disable, namespace teardown with active users, and fragment memory pressure. Tests should cover module load/unload, namespace lifecycle, fragmented IPv4 conntrack, and repeated enable calls.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_defrag_ipv4.h` completely for this pass (9 lines, 226 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_defrag_ipv4.h -->
