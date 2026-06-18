<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_dccp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_dccp.c

## Purpose
`xt_dccp.c` implements the deprecated `dccp` match for DCCP packets. It matches source and destination port ranges, DCCP packet type masks, and optional DCCP option presence.

## Important APIs, Types, and Functions
`dccp_mt()` is the match function. `dccp_find_option()` parses options using a global `dccp_optbuf` protected by `dccp_buflock`. `match_types()` and `match_option()` implement type and option subchecks. `dccp_mt_check()` validates `XT_DCCP_VALID_FLAGS` and inversion flags. `dccp_mt_reg[]` registers IPv4 and IPv6 matches with `.proto = IPPROTO_DCCP`.

## Control Flow, State, and Persistence
Fragments are rejected. The DCCP base header is read with `skb_header_pointer()`, and missing or malformed headers set `par->hotdrop`. Port, type, and option predicates are gated by `info->flags` and inverted by `info->invflags`. Option parsing uses `dh->dccph_doff` to derive the option span and walks one-byte and length-bearing options safely.

## Dependencies and Integration Points
The module depends on x_tables, IPv4/IPv6 iptables registration, `linux/dccp.h`, and skb header access helpers. `dccp_mt_init()` allocates the option buffer, warns once that the match is scheduled for removal in 2027, then registers both matches.

## Risks and Test Signals
Risks include option-length parsing on malformed packets, global option buffer contention, hotdrop behavior for truncated headers, and deprecation/removal impact on userspace rules. Tests should cover all flag combinations, invalid invflags, fragments, short headers, bogus data offsets, option search with one-byte and variable-length options, IPv4/IPv6 registration, allocation failure, and module unload freeing `dccp_optbuf`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_dccp.c -->
