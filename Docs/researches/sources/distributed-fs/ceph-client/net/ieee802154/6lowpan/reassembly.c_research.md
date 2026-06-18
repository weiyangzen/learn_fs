## sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/reassembly.c

Purpose: 6LoWPAN fragment reassembly for IEEE 802.15.4, built on Linux inet-frag infrastructure. It parses FRAG1/FRAGN headers, queues fragments by tag/size/source/destination, reassembles complete IPv6 datagrams, decompresses or accepts the restored network payload, and exposes per-net sysctls for fragment thresholds/timeouts.

Important APIs/types/functions: `lowpan_frag_rcv()` is the RX entry. It peeks IEEE 802.15.4 addresses, parses fragment metadata with `lowpan_get_cb()`, handles FRAG1 payload dispatch through `lowpan_invoke_frag_rx_handlers()`, rejects oversized datagrams, finds the queue with `fq_find()`, and queues the skb. `lowpan_frag_queue()` computes byte offsets, validates last/length consistency, inserts via `inet_frag_queue_insert()`, tracks meat/memory, and calls `lowpan_frag_reasm()` when first and last fragments cover the full datagram. `lowpan_frag_expire()` kills incomplete queues. `lowpan_net_frag_init()` initializes `inet_frags`, sysctl, and pernet operations.

Control flow and state: per-net state lives in `net_ieee802154_lowpan(net)->fqdir`. Queue keys combine `d_tag`, `d_size`, source, and destination. Fragment payload offsets are `d_offset << 3`. Reassembly clears fragment tree pointers, restores skb dev and timestamps, and returns `1` to the caller when a complete skb is available.

Dependencies and integration points: depends on `inet_frag`, IPv6 fragment thresholds/timeouts, jhash/rhashtable params, sysctl, IEEE 802.15.4 header parsing, lowpan IPHC decompression, and the RX file's IPv6 dispatch helper.

Risks: ownership is subtle: queued or errored fragments are consumed, while a `1` return hands a complete skb back to the caller. The code contains `BUILD_BUG_ON()` checks because inet-frag reuses `skb->cb`, so callback area size changes are critical. Hashing assumes the compare key size is a multiple of `u32`.

Test signals: fragmented IPv6 over 802.15.4, duplicate/overlap/corrupt-end rejection, timeout cleanup, sysctl threshold changes, per-net namespace creation/destruction, FRAG1 IPHC and uncompressed IPv6 payloads, and MTU rejection above `IPV6_MIN_MTU`.
