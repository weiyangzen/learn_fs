# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_among.c

## Purpose
Implements the legacy ebtables `among` match, which checks source and/or destination MAC addresses against compact wormhash tables and can optionally bind MAC matches to IPv4 addresses from IP or ARP payloads.

## Important APIs, Types, And Functions
Important routines are `ebt_among_mt`, `ebt_among_mt_check`, `ebt_mac_wormhash_contains`, `ebt_mac_wormhash_check_integrity`, `get_ip_src`, `get_ip_dst`, `poolsize_invalid`, `wormhash_offset_invalid`, and `wormhash_sizes_valid`. The module registers an `xt_match` named `among`, with variable runtime match size.

## Control Flow
Validation checks that embedded source/destination wormhash offsets are aligned, ordered, within the match blob, correctly sized after `EBT_ALIGN`, non-overflowing, and internally monotonic. Runtime matching extracts source/destination MACs and optional IP addresses from IPv4 or ARP payloads, then performs bucketed tuple searches. Positive and negated source/destination membership tests are applied independently.

## State And Persistence Behavior
All match data is immutable per-rule data supplied by userspace and stored inside the ebtables rule blob. No counters or persistent state are maintained by this module.

## Dependencies And Integration Points
Depends on ebtables among UAPI layout, `x_tables`, Ethernet/IP/ARP header helpers, and the ebtables compat path, which has special handling for `matchsize == -1` because this match embeds variable-sized data.

## Risks And Test Signals
Risks are malformed variable-length blobs, offset arithmetic overflows, ARP/IP header truncation, and compat-size translation. Tests should include empty, source-only, destination-only, both-hash, MAC-only, MAC/IP, negated, malformed offset, bad poolsize, non-monotonic table, fragmented/truncated IP/ARP, and 32-bit compat rule loading.
