<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_udp.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_udp.c

This file implements RFC6282 UDP next-header compression and uncompression for 6LoWPAN. It is the functional NHC implementation in this group and registers `nhc_udp` for `NEXTHDR_UDP` with id `0xf0` and mask `0xf8`.

`udp_compress()` examines UDP source and destination ports and emits the shortest supported port encoding: both inline, destination 8-bit compressed, source 8-bit compressed, or both 4-bit compressed in the `0xf0b0` range. The checksum is always emitted inline. `udp_uncompress()` reads the id/port-mode byte, reconstructs ports, rejects checksum-elided packets as unsupported, infers UDP length from the 802.15.4 datagram size when available or from remaining skb length otherwise, and pushes a rebuilt `struct udphdr` into the skb after ensuring writable headroom with `skb_cow()`.

Control flow is invoked by the NHC core under the registry lock. Compression writes header-compression bytes via `lowpan_push_hc_data()` and leaves the core to pull the original UDP header. Uncompression consumes compressed fields with `lowpan_fetch_skb()`, then prepends the full UDP header. State is transient in the skb; there is no persistent module state beyond registration.

Dependencies include UDP header helpers, skb headroom/linear data rules, lowpan device callbacks, IEEE802154 datagram size metadata, and byte-order conversions. Risks include malformed short packets, checksum-elision rejection, wrong inferred length for fragmented or non-802.15.4 frames, and registry conflict with RFC7400 UDP stub. Tests should cover all four port modes, invalid/truncated compressed headers, checksum-elided receive, 802.15.4 `d_size` length inference, non-802154 fallback length, and full compress/uncompress round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_udp.c -->
