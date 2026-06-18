## sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/rx.c

Purpose: receive path for IEEE 802.15.4 6LoWPAN packets. It registers an `ETH_P_IEEE802154` packet handler, validates candidate MAC frames, maps the skb to the associated lowpan netdevice, dispatches 6LoWPAN headers, performs IPHC decompression or fragment handling, and queues resulting IPv6 packets to the network stack.

Important APIs/types/functions: `lowpan_rcv()` is the packet_type callback. `lowpan_rx_h_check()` verifies data frame type, intra-PAN addressing, dispatch availability, and excludes NALP/reserved dispatch values. Dispatch handlers include `lowpan_rx_h_iphc()`, `lowpan_rx_h_frag()`, `lowpan_rx_h_ipv6()`, and unsupported ESC/HC1/DFF/BC0/MESH handlers. `lowpan_iphc_decompress()` peeks 802.15.4 addresses and calls `lowpan_header_decompress()`. `lowpan_give_skb_to_device()` sets `ETH_P_IPV6`, updates lowpan RX stats, and calls `netif_rx()`.

Control flow and state: the handler drops non-802.15.4, other-host, invalid, unbound, or down-lowpan packets. It share-checks the skb, swaps `skb->dev` to the lowpan device, unshares skbs for FRAG1/IPHC paths that mutate data, then runs handlers in likely order: IPHC, fragment, uncompressed IPv6, unsupported dispatches. Result codes determine whether skb is delivered, dropped, or already consumed.

Dependencies and integration points: depends on mac802154 helpers, `ieee802154_hdr_peek_addrs()`, generic lowpan dispatch helpers, fragment reassembly, and lowpan netdevice private linkage from `core.c`.

Risks: dispatch byte access is only safe after `lowpan_rx_h_check()` validates `skb->len`. Result-code fallthrough intentionally frees for `RX_DROP_UNUSABLE` and returns `NET_RX_DROP`; altering switch flow can leak/double-free. Unsupported dispatches are rate-limited warnings but still drops.

Test signals: receive compressed IPHC, uncompressed IPv6, fragmented datagrams, reserved dispatch drops, unsupported dispatch warnings, missing/down lowpan device drops, shared skb unshare behavior, and lowpan RX stats increments.
