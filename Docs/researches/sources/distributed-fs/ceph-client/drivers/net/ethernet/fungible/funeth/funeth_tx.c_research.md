# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_tx.c

## Purpose
Implements the funeth transmit path for skbs and XDP frames, including DMA mapping, hardware descriptor construction, checksum/TSO/USO/encapsulation offload metadata, kTLS descriptor extension, Tx completion reclaim, queue stop/wake flow control, and Tx queue resource lifecycle.

## Important APIs and Functions
Exported to the rest of funeth are `fun_start_xmit()`, `fun_txq_napi_poll()`, `fun_xdp_tx()`, `fun_xdp_xmit_frames()`, `funeth_txq_create()`, `fun_txq_create_dev()`, and `funeth_txq_free()`. Core helpers include `fun_map_pkt()`, `fun_write_gl()`, `write_pkt_desc()`, `fun_tls_tx()`, `fun_unmap_pkt()`, `fun_txq_reclaim()`, and purge/create/free helpers.

## Control Flow
`fun_start_xmit()` selects the queue from skb mapping, optionally checks kTLS sequence state, writes descriptors, advances `prod_cnt`, stops the netdev queue if space falls below worst-case, timestamps, and rings the SQ doorbell unless `xmit_more` defers it. Descriptor construction maps the linear area and frags, fills offload metadata for encapsulated TSO, TCP TSO, UDP LSO, or checksum partial, writes gather entries across ring wrap, and records the skb in per-descriptor state. NAPI reclaim reads hardware head writeback with barriers, unmaps packet segments, frees skbs, updates completed queue accounting, and wakes stopped queues when at least one quarter empty.

## State and Persistence
`struct funeth_txq` holds descriptor ring, info array, DMA address, hardware writeback pointer, doorbell, producer/consumer counters, queue stats, netdev queue, hardware SQ id, ETH id, IRQ pointer, and init state. XDP queues reuse the Tx queue structure but store `xdp_frame` pointers and may not have an IRQ-backed netdev queue.

## Dependencies and Integration Points
Depends on DMA mapping, skb and XDP APIs, TCP/IP header helpers, TLS device helpers, hardware Tx request structures, and SQ creation/binding from `fun_queue`/`funeth_main.c`. Integrates with ethtool stats through `funeth_txq_stats` and with Rx XDP_TX via `fun_xdp_tx()`.

## Risks and Test Signals
Risks include DMA unwind mistakes, descriptor ring wrap bugs, missing barriers around hardware head/writeback, offload metadata errors for encapsulated packets, TLS `next_seq` drift, XDP queue full handling, and purge after hardware queue destruction. Test with TSO/USO/checksum offload, tunneled GSO, fragmented skbs, kTLS fallback/resync, netdev queue stop/wake under saturation, XDP_TX/XDP_REDIRECT, and teardown while descriptors are outstanding.
