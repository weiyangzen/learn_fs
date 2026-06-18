# sources/distributed-fs/ceph-client/net/ipv6/rpl.c

## Purpose

`rpl.c` implements address compression and decompression for IPv6 RPL Source Routing Headers. It converts between expanded `struct ipv6_rpl_sr_hdr` segment address arrays and compressed segment data that omits the shared prefix with the packet destination address.

## Important APIs, Types, And Functions

The exported helpers are `ipv6_rpl_srh_decompress()` and `ipv6_rpl_srh_compress()`. They operate on `struct ipv6_rpl_sr_hdr`, `struct in6_addr`, and the `cmpri` / `cmpre` compression fields. Internal helpers are `ipv6_rpl_addr_decompress()`, `ipv6_rpl_addr_compress()`, `ipv6_rpl_segdata_pos()`, `ipv6_rpl_srh_calc_cmpri()`, and `ipv6_rpl_srh_calc_cmpre()`.

`IPV6_PFXTAIL_LEN(x)` computes the copied suffix length for an omitted prefix length, and `IPV6_RPL_BEST_ADDR_COMPRESSION` is the all-but-one-byte compression result used when a segment fully shares the destination prefix.

## Control Flow

Decompression copies fixed header fields, computes an expanded header length for `n + 1` full IPv6 addresses, clears compression fields, then reconstructs the first `n` addresses with `cmpri` and the final address with `cmpre`. Compression first finds the longest common prefix between the destination and all non-final segments (`cmpri`) and between the destination and final segment (`cmpre`). It then computes packed segment length and padding, copies fixed fields, stores compression values, and writes only the suffix bytes for each segment.

## State And Persistence Behavior

The file is stateless. It writes only caller-provided output buffers and does not allocate memory, retain references, or modify global/per-net state. Correctness depends on callers providing buffers sized for the compressed or decompressed result and a valid segment count `n`.

## Dependencies And Integration Points

It depends on `<net/rpl.h>` for the RPL SRH layout and is used by RPL lightweight tunnel code to compress the inline source routing header before inserting it into packets. The compression format is coupled to `rpl_iptunnel.c`, which validates uncompressed SRHs from netlink and then calls `ipv6_rpl_srh_compress()` while building packets.

## Risks And Edge Cases

The helpers trust the caller's segment count and buffer sizing, so validation must happen before entry. Prefix length arithmetic is byte-oriented, not bit-oriented; this matches the implementation's compressed-byte model but would be dangerous if used with arbitrary bit prefix lengths. The "best compression" value is 15 rather than 16, so a fully matching address still contributes one suffix byte. Header length and padding are recomputed during compression, so callers must not reuse stale lengths from partially initialized headers.

## Test Signals

Round-trip tests should cover no shared prefix, partial shared prefixes, full shared prefix, different final-segment compression, padding when compressed data is not 8-byte aligned, and segment counts of one and several hops. Integration tests should verify that RPL tunnel insertion produces valid packets that downstream RPL parsing can decompress to the original segment list.
