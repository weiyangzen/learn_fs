# sources/distributed-fs/ceph-client/net/6lowpan/iphc.c

## Purpose
`net/6lowpan/iphc.c` implements RFC6282 IPv6 header compression and decompression for 6LoWPAN. It converts between full IPv6 headers and compact IPHC encodings, supports stateless and context-based address compression, handles multicast forms, delegates next-header compression to NHC modules, and adapts link-layer address reconstruction for IEEE802154, BTLE, EUI-48, and EUI-64 cases.

## Important APIs, types, and functions
The exported entry points are `lowpan_header_compress()` and `lowpan_header_decompress()`. Important helpers include context lookup (`lowpan_iphc_ctx_get_by_id()`, `lowpan_iphc_ctx_get_by_addr()`, `lowpan_iphc_ctx_get_by_mcast_addr()`), address reconstruction (`lowpan_iphc_uncompress_addr()`, `lowpan_iphc_uncompress_ctx_addr()`, multicast variants, and link-layer helpers), address compression (`lowpan_compress_addr_64()`, `lowpan_compress_ctx_addr()`, multicast variants), and traffic-class/flow-label compression/decompression (`lowpan_iphc_tf_compress()`, `lowpan_iphc_tf_decompress()`). Numerous `LOWPAN_IPHC_*` masks define dispatch byte fields.

## Control flow
Decompression consumes the IPHC bytes from the skb, optional CID byte, traffic class/flow label, optional inline next header, hop limit, source address, destination address, and optional NHC-compressed next-header data. It reconstructs an `ipv6hdr`, sets packet type for multicast versus host traffic, computes payload length, pushes the IPv6 header back onto the skb, and resets MAC/network headers. Context-based branches hold the per-device context-table spinlock while resolving and using a context.

Compression starts from an IPv6 skb, reserves a small local header buffer, looks up destination and source compression contexts under the context lock and copies selected context entries locally, emits CID if needed, compresses traffic class/flow label, tries NHC next-header compression, compresses hop limit, source address, destination address, and finally applies NHC compression if selected. It removes the IPv6 header from the skb and pushes the compact IPHC header in its place.

## State and persistence
The function-level state is transient skb/header data. Persistent runtime inputs are per-device IPHC contexts (`id`, active/compression flags, prefix, prefix length), link-layer addresses passed by callers, and registered NHC handlers. The code mutates skb data/headroom and packet type, but does not store data beyond debug traces.

## Dependencies and integration points
The implementation depends on `net/6lowpan.h` helpers for skb fetch/push and address utilities, `net/ipv6.h`, `nhc.h` registry functions, IEEE802154 address conversions, `lowpan_dev(dev)->ctx`, and callers in 6LoWPAN link-layer transmit/receive paths.

## Risks and invariants
Every compressed field fetch must bounds-check skb data; failures return `-EINVAL`/`-EIO`. Context ids must refer to active contexts, and compression must copy contexts out from under the lock before using them later. Link-local zero-padding checks and IID reconstruction must match RFC address forms. The local header buffer must be large enough for worst-case compressed output. Compression and decompression must remain symmetric across stateless, context, multicast, and NHC paths.

## Test signals
Use packet-level tests for full inline IPv6 headers, all TF modes, hop limits 1/64/255/inline, stateless link-local IID compression modes, context-based source/destination compression, multicast 8/32/48/128-bit forms, multicast context compression, IEEE802154 short/long address reconstruction, BTLE/EUI-48 cases, malformed truncated skbs, and NHC present/absent behavior. Verify round-trip packets with debug dumps and IPv6 payload length correctness.
