# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_tx.c

## Purpose

`gve_tx.c` implements the legacy GQI TX datapath, including TX ring allocation/free/start/stop, QPL FIFO management for copy-mode transmit, raw-addressing DMA mapping, SKB descriptor construction, TX completion cleanup, queue stop/wake behavior, XDP TX, and AF_XDP TX polling.

## Important APIs, types, and functions

- Lifecycle: `gve_tx_alloc_rings_gqi`, `gve_tx_free_rings_gqi`, `gve_tx_start_ring_gqi`, `gve_tx_stop_ring_gqi`.
- QPL FIFO: `gve_tx_fifo_init`, `gve_tx_fifo_release`, `gve_tx_alloc_fifo`, `gve_tx_free_fifo`, `gve_skb_fifo_bytes_required`.
- Descriptor fill: `gve_tx_fill_pkt_desc`, `gve_tx_fill_mtd_desc`, `gve_tx_fill_seg_desc`, `gve_tx_add_skb_copy`, `gve_tx_add_skb_no_copy`.
- Queue control: `gve_tx_avail`, `gve_can_tx`, `gve_maybe_stop_tx`, `gve_tx`, `gve_tx_put_doorbell`.
- Completion and stats: `gve_clean_tx_done`, `gve_clean_xdp_done`, `gve_tx_poll`, `gve_xdp_poll`, `gve_tx_load_event_counter`, `gve_tx_clean_pending`.
- XDP/AF_XDP: `gve_xdp_xmit_gqi`, `gve_xdp_xmit_one`, `gve_xdp_tx_flush`, `gve_xsk_tx`, `gve_xsk_tx_poll`.

## Control flow and state

Ring allocation creates descriptor memory, buffer-state metadata, queue resources, and optionally a QPL-backed FIFO mapped with `vmap()`. Normal transmit chooses a TX ring from SKB queue mapping, ensures descriptor and FIFO capacity, fills descriptors either by copying into the QPL FIFO or DMA-mapping SKB linear/frags, updates BQL timestamping and `tx->req`, and rings the doorbell unless `xmit_more` defers it. Completion polling reads NIC event counters, cleans `tx->info` entries from `tx->done`, unmaps DMA or frees FIFO space, consumes SKBs, updates packet/byte counters, and wakes stopped queues when space returns.

Persistent runtime state is per ring: `req`, `done`, descriptor ring, `info[]`, FIFO head/available count, QPL pages, event counter indexes, `netdev_txq`, XDP lock, clean lock, and counters. The state is rebuilt on queue reallocation and drained on stop.

## Dependencies and integration points

The file depends on legacy descriptors from `gve_desc.h`, common structures from `gve.h`, QPL page helpers from `gve_main.c`, netdev BQL/queue APIs, DMA mapping, XDP/AF_XDP APIs, and NAPI scheduling from `gve_main.c`. `gve_rx.c` invokes `gve_xdp_tx_flush()` after RX-side XDP_TX; `gve_main.c` dispatches SKB TX to `gve_tx()` for GQI queues.

## Risks and test signals

Risks include FIFO accounting/padding bugs, descriptor count underestimation for GSO/frags/metadata, DMA unmap leaks on partial mapping failure, queue stopped without doorbell flush, event-counter wrap assumptions, and AF_XDP completion mismatch. Tests should cover copy and raw-addressing TX, checksum and TSO descriptors, SKBs with max frags and L4 hash metadata, DMA mapping failure unwind, BQL stop/wake, XDP_XMIT flush behavior, XSK TX completion, and TX timeout recovery.
