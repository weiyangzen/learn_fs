# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_xsk.c

## Purpose
`ixgbe_xsk.c` implements AF_XDP zero-copy support for ixgbe. It binds an `xsk_buff_pool` to a queue, allocates user-memory-backed RX buffers, runs XDP on received frames, constructs SKBs for `XDP_PASS`, transmits AF_XDP descriptors on the XDP TX ring, and returns completed frames to the AF_XDP core.

## Important APIs, types, and functions
- Pool lookup/setup: `ixgbe_xsk_pool()`, `ixgbe_xsk_pool_setup()`, internal enable/disable helpers.
- RX allocation and cleaning: `ixgbe_alloc_rx_buffers_zc()`, `ixgbe_clean_rx_irq_zc()`, `ixgbe_xsk_clean_rx_ring()`.
- XDP execution: `ixgbe_run_xdp_zc()` handles `XDP_REDIRECT`, `XDP_TX`, `XDP_DROP`, `XDP_PASS`, and invalid/aborted actions.
- TX path: `ixgbe_xmit_zc()`, `ixgbe_clean_xdp_tx_irq()`, `ixgbe_xsk_clean_tx_ring()`, and `ixgbe_xsk_wakeup()`.
- External APIs used include `xsk_pool_dma_map()`, `xsk_buff_alloc()`, `xsk_tx_peek_desc()`, `xsk_tx_release()`, `xsk_tx_completed()`, `xdp_do_redirect()`, and NAPI wakeup helpers.

## Control flow and integration
Pool enable validates queue bounds, DMA maps the AF_XDP pool, disables the target ring if the interface is running, marks the queue in `adapter->af_xdp_zc_qps`, re-enables the ring, and wakes NAPI. Disable performs the inverse and unmaps DMA. RX refill pulls `xdp_buff` objects from the pool and posts their DMA addresses into hardware descriptors. RX cleaning reads completed descriptors, handles multi-buffer discard cases, syncs DMA for CPU, runs XDP, either redirects/transmits/drops/frees the buffer, or builds an SKB and passes it into the normal receive path.

TX zero-copy peeks user descriptors from the AF_XDP pool, syncs raw DMA for device, fills ixgbe advanced TX descriptors, advances `next_to_use`, rings the tail, and releases descriptors to the pool. TX completion distinguishes normal XDP frames from AF_XDP frames by `tx_bi->xdpf`; AF_XDP frames are counted and reported through `xsk_tx_completed()`.

## State and persistence behavior
Runtime state is stored in queue bitmaps, `rx_ring->xsk_pool`, ring descriptor arrays, `next_to_use`, `next_to_clean`, `rx_buffer_info[].xdp`, discard flags, `tx_buffer_info`, per-ring stats, and AF_XDP need-wakeup flags. No on-disk persistence exists, but DMA mappings and hardware descriptor state must stay synchronized across ring disable/enable and cleanup.

## Dependencies
The file depends on ixgbe ring/NAPI helpers, XDP/BPF APIs, AF_XDP socket driver APIs, DMA attributes, memory barriers, and netdev carrier/state helpers.

## Risks
- Queue validation must match both real RX/TX queue counts and XDP queue counts, or user memory can be bound to a wrong ring.
- Descriptor memory ordering is critical around RX writeback and tail updates.
- `XDP_PASS` copies UMEM-backed data into a new SKB; allocation failures must leave the pool and descriptor ring recoverable.
- Need-wakeup logic affects busy-poll/user wakeups and can cause stalls if set or cleared incorrectly.
- TX completion must not return AF_XDP frames through `xdp_return_frame()` or leak normal XDP frame DMA mappings.

## Test signals
Exercise AF_XDP zero-copy bind/unbind on running and stopped devices, RX `XDP_PASS`, `DROP`, `TX`, and `REDIRECT`, need-wakeup mode, TX completion and wakeup, queue bounds failures, interface reset while pools are attached, and stress runs that wrap ring indices.
