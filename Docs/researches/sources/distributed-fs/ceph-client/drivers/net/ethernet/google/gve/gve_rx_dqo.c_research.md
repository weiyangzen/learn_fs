# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_rx_dqo.c

## Purpose

`gve_rx_dqo.c` implements the DQO RX datapath. It allocates/free DQO RX rings, posts RX buffer descriptors, consumes RX completion descriptors, supports page-pool/raw addressing, QPL, AF_XDP, XDP, header split, RSC/HW-GRO, checksum/hash metadata, and RX hardware timestamps.

## Important APIs, types, and functions

- Lifecycle: `gve_rx_alloc_ring_dqo`, `gve_rx_alloc_rings_dqo`, `gve_rx_free_ring_dqo`, `gve_rx_free_rings_dqo`, `gve_rx_start_ring_dqo`, `gve_rx_stop_ring_dqo`.
- Ring state: `gve_rx_init_ring_state_dqo`, `gve_rx_reset_ring_dqo`, `gve_rx_free_hdr_bufs`, `gve_rx_alloc_hdr_bufs`.
- Posting: `gve_rx_post_buffers_dqo`, `gve_rx_write_doorbell_dqo`.
- Metadata: `gve_rx_skb_csum`, `gve_rx_skb_hash`, `gve_rx_get_hwtstamp`, `gve_rx_skb_hwtstamp`, `gve_xdp_rx_timestamp`.
- SKB assembly and recycling: `gve_rx_append_frags`, `gve_skb_add_rx_frag`, `gve_rx_copy_ondemand`, `gve_rx_free_skb`.
- XDP/AF_XDP: `gve_xdp_tx_dqo`, `gve_xdp_done_dqo`, `gve_xsk_done_dqo`, `gve_rx_xsk_dqo`.
- Completion path: `gve_rx_dqo`, `gve_rx_complete_rsc`, `gve_rx_complete_skb`, `gve_rx_poll_dqo`.

## Control flow and state

Allocation builds a completion ring, buffer ring, buffer-state array, optional coherent header buffers, optional page pool or QPL, and queue resources. Posting computes available slots from buffer tail/head and completion free slots, allocates buffers through `gve_alloc_buffer()`, optionally attaches header-buffer DMA addresses, advances tail/free-slot counters, and rings the doorbell every `GVE_RX_BUF_THRESH_DQO` descriptors.

Polling reads completion descriptors until the generation bit says no work or packet budget is exhausted. After `dma_rmb()`, `gve_rx_dqo()` validates buffer ids/allocation state, handles RX errors, processes XSK buffers, copies split headers, syncs DMA, runs XDP where possible, appends frags or copybreak SKBs, and returns/reuses buffers. End-of-packet completions are finalized through checksum/hash/timestamp/RSC handling and GRO submission. Ring state includes buffer/completion indices, generation bit, `num_free_slots`, `rx->ctx`, buffer-state lists, page-pool/QPL state, and counters.

## Dependencies and integration points

The file depends on `gve_desc_dqo.h`, `gve_dqo.h`, buffer helpers in `gve_buffer_mgmt_dqo.c`, ptype LUT from adminq, PTP timestamp sync from `gve_ptp.c`, XDP metadata ops registered by `gve_main.c`, and DQO TX functions for XDP_TX and XSK TX polling. `gve_main.c` invokes this path for DQO queue formats.

## Risks and test signals

Risks include invalid buffer-id handling, completion generation wrap, `num_free_slots` drift, page-pool net_iov header access without header split, header-split overflow/unsplit fallback, RSC header manipulation leaks, timestamp expansion based on stale calibration, and buffer starvation in QPL copy-on-demand mode. Tests should include DQO RX ring wrap, RX error descriptors, header split on/off, HW-GRO/RSC packets, checksum/hash matrix, RX timestamping and XDP metadata, AF_XDP pass/drop/redirect/TX, copybreak, and allocation failure injection.
