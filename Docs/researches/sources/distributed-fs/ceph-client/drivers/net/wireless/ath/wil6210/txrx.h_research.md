# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/txrx.h

## Purpose
This header defines the legacy TX/RX descriptor ABI, shared ring helper routines, EAPOL key structures, skb control-buffer layouts, and exported TX/RX data-path entry points for wil6210. It is the common contract between legacy DMA code, enhanced DMA code, interrupt/reorder logic, WMI setup, and the netdev transmit path.

## Important APIs, Types, and Functions
- Descriptor address helpers: `wil_desc_addr()` and `wil_desc_addr_set()` encode/decode 48-bit DMA addresses used by legacy descriptors.
- Legacy descriptor structures: `struct vring_tx_mac`, `struct vring_tx_dma`, `struct vring_rx_mac`, `struct vring_rx_dma`, `struct vring_tx_desc`, `struct vring_rx_desc`, `union wil_tx_desc`, `union wil_rx_desc`, and `union wil_ring_desc`.
- Bit definitions: MAC/DMA TX fields, RX error/status bits, TSO descriptor type constants, and EAPOL key constants define the hardware-facing wire format.
- SKB metadata: `struct skb_rx_info`, `wil_skb_rxdesc()`, `wil_skb_get_cid()`, and `wil_skb_set_cid()` store descriptor and CID state inside `skb->cb`.
- Ring helpers: `wil_ring_is_empty()`, `wil_ring_next_tail()`, `wil_ring_advance_head()`, `wil_ring_is_full()`, `wil_ring_used_tx()`, `wil_ring_avail_tx()`, and `wil_get_min_tx_ring_id()` abstract cursor math for both DMA modes.
- Packet helpers: `wil_skb_get_da()`, `wil_skb_get_sa()`, `wil_need_txstat()`, `wil_consume_skb()`, `wil_is_back_req()`, and `wil_val_in_range()`.
- Public prototypes: RX delivery/reorder/BAR, TX data init, legacy ops initialization, and TX latency accounting.

## Control Flow
The header has no runtime control flow of its own, but its inline helpers are on hot paths. RX code decodes descriptor bitfields through `wil_rxdesc_*()` helpers, stores the descriptor in `skb->cb`, and later recovers CID/security/reorder parameters. TX code computes used/available slots with ring helpers before writing descriptors and advancing `swhead`. Completion code uses `wil_consume_skb()` to optionally report Wi-Fi ACK status to sockets that requested it.

## State and Persistence Behavior
The header defines in-memory hardware/shared-memory layouts. State is transient and includes descriptor ownership bits, ring cursor fields in `struct wil_ring`, per-descriptor mapping state in `struct wil_ctx`, and `skb->cb` metadata. The layouts are packed and must remain aligned with firmware/hardware expectations; changing them changes the device ABI.

## Dependencies and Integration Points
It includes `wil6210.h` and `txrx_edma.h`, so it bridges shared private driver state with both descriptor formats. It depends on Linux SKB, Ethernet, IEEE 802.11, DMA, checksum, and socket ACK APIs. `wil_get_min_tx_ring_id()` integrates with eDMA by reserving ring 0 for RX when enhanced DMA is active.

## Risks
The descriptor structs and masks are hardware ABI; wrong bit positions or packing cause silent data corruption. `skb->cb` space is limited and shared with eDMA status storage, so additions can overflow or alias metadata. Ring cursor helpers assume power-of-two-sized circular rings and one empty slot. Include ordering is tight because this file references enhanced descriptor types through `union wil_tx_desc`.

## Test Signals
Compile-time signals include descriptor size assertions in users and structure packing warnings. Runtime signals include descriptor hex dumps, correct CID/TID/MID extraction, ACK status delivery for sockets requesting Wi-Fi status, correct ring availability under wraparound, and successful operation in both legacy and eDMA builds.
