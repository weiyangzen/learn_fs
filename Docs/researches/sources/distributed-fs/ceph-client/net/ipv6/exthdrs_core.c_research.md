# sources/distributed-fs/ceph-client/net/ipv6/exthdrs_core.c

## Purpose
Provides small reusable IPv6 extension-header parsing primitives that are needed by both full IPv6 and static/library users. It classifies extension-header protocol numbers, skips extension header chains, locates TLVs, and finds a requested header or terminal protocol.

## Important APIs, Types, and Functions
Exports `ipv6_ext_hdr()`, `ipv6_skip_exthdr()`, `ipv6_find_tlv()`, and `ipv6_find_hdr()`. `ipv6_skip_exthdr()` reports final next header and fragment offset. `ipv6_find_hdr()` supports flags such as `IP6_FH_F_FRAG`, `IP6_FH_F_AUTH`, and `IP6_FH_F_SKIP_RH`.

## Control Flow
`ipv6_ext_hdr()` performs fixed protocol classification. `ipv6_skip_exthdr()` walks known extension headers from a caller-provided offset, bounds the number of parsed headers, treats non-first fragments as the end of parseable data, handles AH length specially, and returns `-1` for truncation or `NEXTHDR_NONE`. `ipv6_find_tlv()` validates an option header span and scans TLVs with PAD1/PADN semantics. `ipv6_find_hdr()` optionally starts at an inner IPv6 header, walks headers until the target or terminal protocol is found, handles fragments specially, and returns precise errno for malformed or absent headers.

## State and Persistence
No persistent state. All state is local parse cursor data and caller-provided output fields for offsets, fragment offsets, and flags.

## Dependencies and Integration Points
Depends on skb header accessors, IPv6/AH/fragment header formats, and exported symbols for ICMPv6, netfilter, XFRM, tunnels, and packet classifiers. `icmp.c`, `fou6.c`, `esp6.c`, and other IPv6 subsystems use these helpers to avoid open-coded parsing.

## Risks and Test Signals
Risks include semantic shortcuts that intentionally scan past headers despite RFC ordering concerns, truncated header handling, non-first fragment interpretation, AH stop conditions, and extension-header count limits. Test signals include packets with chained hop/destination/routing/AH/fragment headers, truncated skbs, nested IPv6 offsets, first and later fragments, `NEXTHDR_NONE`, and callers requesting target and terminal modes.
