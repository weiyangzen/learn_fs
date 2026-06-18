## sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/tx.c

Purpose: transmit path for IPv6 over IEEE 802.15.4 6LoWPAN. It builds address metadata during header creation, compresses IPv6 headers, emits IEEE 802.15.4 MAC headers, chooses single-frame or fragmented transmission, and updates lowpan TX statistics.

Important APIs/types/functions: `lowpan_header_create()` stores source/destination IEEE 802.15.4 addresses in private headroom, selecting broadcast, neighbor short address, or extended EUI-64 address. `lowpan_header()` copies that metadata, calls `lowpan_header_compress()`, computes datagram size and offset, initializes `mac_cb`, sets ack request based on broadcast/default policy, and calls `wpan_dev_hard_header()`. `lowpan_xmit()` ensures headroom/tailroom and skb exclusivity, invokes `lowpan_header()`, peeks the resulting WPAN header, compares payload to `ieee802154_max_payload()`, then either queues the skb directly to the WPAN device or calls `lowpan_xmit_fragmented()`. Fragment helpers build FRAG1/FRAGN headers and allocate per-fragment skbs.

Control flow and state: per-lowpan `fragment_tag` increments for each fragmented datagram. Fragmentation sends FRAG1 with the MAC header copied from the master skb, then FRAGN skbs with fresh WPAN headers and 8-byte aligned offsets. On full success the original skb is consumed; on error it is freed.

Dependencies and integration points: depends on IPv6/NDISC neighbor table, lowpan compression, IEEE 802.15.4 header generation and max payload calculation, mac802154 control block, and backing WPAN device head/tailroom.

Risks: `lowpan_skb_priv()` assumes sufficient headroom reserved for `struct lowpan_addr_info`; callers outside normal header creation can trip `WARN_ON_ONCE`. Fragment size math depends on `ieee802154_max_payload()` and network header length; underflow would be severe if payload capacity were smaller than required headers. Neighbor short-address reads require locking around `n->lock`.

Test signals: IPv6 unicast via extended address, broadcast via short broadcast, neighbor short-address optimization, single-frame transmit, multi-fragment transmit/reassembly peer tests, headroom expansion path, and TX stats/tag increments.
