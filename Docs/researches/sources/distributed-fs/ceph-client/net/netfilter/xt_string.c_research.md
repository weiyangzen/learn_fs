<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_string.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_string.c

## Purpose
`xt_string.c` implements payload string matching using the kernel textsearch API. It supports configurable search algorithms and offsets.

## Important APIs, Types, and Functions
`string_mt()` calls `skb_find_text()` with a precompiled `struct ts_config`. `string_mt_check()` validates offsets and prepares the textsearch configuration from `struct xt_string_info`; `string_mt_destroy()` releases it with `textsearch_destroy()`.

## Control Flow, State, and Persistence
At rule insertion, userspace pattern and algorithm fields are compiled into a textsearch config. Packet evaluation searches the skb data between configured `from_offset` and `to_offset`; finding a match returns true unless inverted. The compiled textsearch config persists for the rule lifetime.

## Dependencies and Integration Points
The module depends on x_tables, skb text search support, and textsearch algorithm modules such as bm or kmp. It registers aliases for IPv4, IPv6, and ebtables-style use.

## Risks and Test Signals
Risks include offset validation, algorithm module availability, fragmented/nonlinear skb scanning, payload encoding assumptions, and expensive searches on large packets. Tests should cover several algorithms, match and no-match payloads, offsets, inversion, nonlinear skbs, invalid ranges, missing algorithms, and destroy cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_string.c -->
