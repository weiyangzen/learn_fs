<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_sctp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_sctp.c

## Purpose
`xt_sctp.c` implements SCTP packet matching by source/destination port and chunk type conditions.

## Important APIs, Types, and Functions
`sctp_mt()` reads `struct sctphdr` and optional chunks. Chunk matching is handled by helpers for "all", "any", and "only" chunk semantics against `struct xt_sctp_info`. `sctp_mt_check()` validates flags and inversion masks. Registration covers IPv4 and IPv6 with `.proto = IPPROTO_SCTP`.

## Control Flow, State, and Persistence
Fragments are rejected. The matcher reads the SCTP common header, checks port ranges, then if chunk matching is requested walks the chunk list using length fields and validates chunk boundaries. It applies requested chunk type bitmaps and inversion. No state is persisted.

## Dependencies and Integration Points
The module depends on x_tables, SCTP header definitions, skb safe-copy helpers, and IPv4/IPv6 registration. It assumes transport-header offset is already computed by x_tables.

## Risks and Test Signals
Risks include malformed chunk lengths, zero-length chunk loops, truncated skbs, fragment behavior, and subtle all/any/only semantics. Tests should cover source/destination port boundaries, each chunk matching mode, inverted chunk matches, malformed chunk length, multiple chunks with padding, short headers hotdrop, fragments, and IPv4/IPv6 paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_sctp.c -->
