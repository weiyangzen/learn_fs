# sources/distributed-fs/ceph-client/drivers/net/usb/lg-vl600.c

## Purpose
`lg-vl600.c` is a `usbnet` minidriver for the Ethernet data interface of the LG VL600 LTE modem. The device looks CDC Ethernet-like but requires proprietary framing, so this file binds through CDC helpers and translates modem frame headers to normal Linux Ethernet SKBs.

## Important APIs, Types, And Functions
`struct vl600_frame_hdr` is the outer batch header with length, serial, packet count, dummy fields, and magic. `struct vl600_pkt_hdr` is per-packet metadata and deliberately matches Ethernet header size and `h_proto` offset. `struct vl600_state` stores a partially assembled RX SKB.

`vl600_bind()` allocates state, calls `usbnet_cdc_bind()`, marks `IFF_NOARP`, and enables multicast for IPv6 NDP. `vl600_unbind()` frees the partial RX buffer. `vl600_rx_fixup()` validates magic, assembles fragments, splits packet batches, reconstructs Ethernet addresses, fixes inbound IPv6 ethertype, and returns/clones SKBs for usbnet. `vl600_tx_fixup()` adds frame/packet headers, forces the packet protocol field to IPv4 as the modem expects, pads to 4-byte alignment, and reallocates SKB storage when needed.

## Control Flow
`usbnet_probe()` uses `vl600_info` for the single product/interface match. RX fixup either stores an incomplete frame in `current_rx_buf`, delivers cloned intermediate packets with `usbnet_skb_return()`, or returns the last packet to usbnet. TX fixup rejects non-Ethernet SKBs, detects already-encapsulated frames, creates needed headroom/tailroom, writes headers, and returns an encapsulated frame.

## State And Persistence Behavior
Runtime state is the partial RX buffer plus a static TX serial counter. The driver writes no persistent device storage. Netdev flags set at bind persist for the interface lifetime.

## Dependencies And Integration Points
The file depends on usbnet, USB CDC helpers, Ethernet helpers, and module USB registration. It integrates through `.bind`, `.unbind`, `.status = usbnet_cdc_status`, `.rx_fixup`, `.tx_fixup`, and `FLAG_RX_ASSEMBLE | FLAG_WWAN`.

## Risks And Test Signals
Risks are malformed proprietary lengths, bad magic, oversized fragments, short headers, packet lengths beyond the buffer, clone/copy allocation failures, and special ARP/IPv6 reconstruction behavior. Tests should cover fragmented and multi-packet RX batches, IPv6 ethertype repair, ARP address copy, malformed frame drops, TX padding, headroom/tailroom reuse, and unbind cleanup.
