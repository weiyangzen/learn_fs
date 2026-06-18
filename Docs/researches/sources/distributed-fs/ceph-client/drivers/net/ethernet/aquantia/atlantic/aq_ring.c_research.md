<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ring.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ring.c

Purpose: implements shared TX/RX ring memory allocation, DMA buffer lifecycle, TX cleanup, RX refill/clean, XDP receive/transmit handling, hardware timestamp RX cleanup, and per-ring software stats.

Important APIs/functions: `aq_ring_tx_alloc`, `aq_ring_rx_alloc`, `aq_ring_init`, `aq_ring_update_queue_state`, `aq_ring_tx_clean`, `aq_xdp_xmit`, `aq_ring_rx_clean`, `aq_ring_rx_fill`, `aq_ring_rx_deinit`, `aq_ring_free`, `aq_ring_hwts_rx_alloc/free/clean`, and `aq_ring_fill_stats_data`.

Control flow: allocation creates software buffer rings and coherent descriptor rings. RX fill allocates or reuses pages, DMA maps them, and advances software tail. Hardware receive ops populate buffer metadata; `aq_ring_rx_clean` selects skb or XDP path, validates descriptor chains, handles errors, syncs DMA for CPU, extracts PTP timestamps, builds skb/XDP buffers, applies VLAN/checksum/RSS metadata, and submits GRO or XDP actions. TX clean walks completed descriptors, unmaps DMA, frees SKBs or returns XDP frames, and wakes queues when space returns.

State and persistence: `aq_ring_s` owns descriptor memory, DMA addresses, head/tail pointers, page reuse parameters, XDP RX queue metadata, and u64 stats. State is volatile and freed on ring deinit.

Dependencies and integration: used by `aq_vec`, `aq_nic`, `aq_ptp`, and hardware ops. Integrates Linux DMA API, page allocator, NAPI, GRO, XDP/BPF, VLAN, checksum, and PTP timestamp extraction.

Risks: descriptor-chain validation is critical for jumbo/LRO/multibuffer XDP; page reuse relies on reference counts and correct DMA sync; TX cleanup must avoid freeing incomplete packets; XDP redirects must flush; hardware timestamp ring uses a special allocation size. Test signals include jumbo/LRO RX, XDP PASS/TX/DROP/REDIRECT with fragments, DMA mapping failures, small-packet checksum workaround, queue stop/wake, and PTP timestamped RX/TX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ring.c -->
