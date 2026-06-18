# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx.c

Purpose: implements the main SFC transmit path for SKBs and XDP frames, including queue selection, checksum-type selection integration, copybreak/PIO paths, descriptor push batching, and single-completion handling.

Important functions: `__efx_enqueue_skb()` maps or copies one skb to a TX queue, handling TSOv1, TSOv2, software TSO fallback, PIO, copybreak, DMA mapping, timestamps, queue stopping, and doorbells. `efx_hard_start_xmit()` is the netdev transmit entry point and diverts PTP timestamp packets. `efx_xdp_tx_buffers()` maps XDP frames on per-CPU XDP TX queues. `efx_xmit_done_single()` completes one packet by walking descriptors until the SKB-final buffer. `efx_init_tx_queue_core_txq()` binds a driver TX queue to the core netdev queue.

Control flow: normal SKB TX computes `segments`, attempts hardware TSO when needed, falls back to software GSO only for queue restrictions, otherwise may use PIO or copybreak for short/fragmented packets, then maps remaining data through `efx_tx_map_data()`. It records timestamps, pessimistically stops queues near thresholds, marks `xmit_pending`, and pushes all channel queues when xmit-more batching ends. Error unwind frees partially enqueued buffers and consumes the skb.

State and dependencies: uses per-queue insert/read/write counters, copy-buffer pages, optional PIO buffer, XDP queue arrays, netdev queue state, PTP helpers, NIC-specific descriptor push functions, and thresholds from `efx`. State is volatile queue state only.

Risks and test signals: risks include queue stop/wake races, partial DMA mapping unwind, PIO alignment assumptions, XDP queue mode locking, and PTP packets bypassing pending doorbells. Test high-rate TX with `xmit_more`, GSO/TSO on and off, copybreak fragmented packets, PTP timestamp TX, XDP_TX/redirect in dedicated and borrowed queue modes, DMA mapping failures, and reset on spurious completion.
