# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_xsk.c

## Purpose
`otx2_xsk.c` implements AF_XDP zero-copy support for RVU NIC queues. It maps user XSK pools for DMA, switches selected RX/TX queues into zero-copy operation, cleans/reinitializes receive queues, wakes NAPI, attaches pools to SQs, and pushes XSK TX descriptors into NIX send queues.

## Important APIs, Types, and Functions
Exports include `otx2_xsk_pool_setup()`, `otx2_xsk_pool_enable()`, `otx2_xsk_pool_disable()`, `otx2_xsk_pool_alloc_buf()`, `otx2_xsk_wakeup()`, `otx2_attach_xsk_buff()`, and `otx2_zc_napi_handler()`. Internal helpers include `otx2_xsk_ctx_disable()`, `otx2_clean_up_rq()`, and `otx2_xsk_sq_append_pkt()`.

## Control Flow
Pool enable validates queue bounds, DMA-maps the XSK pool, marks the zero-copy bitmap, drains and disables the old RQ context, reprograms RSS to remove the queue, and triggers NAPI wakeup. Disable detaches the SQ XSK pool, drains RQ state, clears the bitmap, unmaps DMA, and restores RSS participation. RX buffer allocation obtains `xdp_buff` objects from the XSK pool and stores them on the pool stack. TX NAPI peeks a batch of XSK TX descriptors, converts addresses to DMA, builds one-fragment SQEs, and flushes them.

## State and Persistence
State is kept in `pf->af_xdp_zc_qidx`, `otx2_pool->xsk_pool`, `otx2_pool->xdp[]/xdp_top`, and `otx2_snd_queue->xsk_pool`. Hardware RQ/aura/pool contexts are disabled and recreated around mode changes. DMA mappings persist while the pool is enabled.

## Dependencies and Integration Points
The file depends on XDP socket driver APIs, NIX/NPA mailbox helpers, RSS table programming, RX/TX cleanup in `otx2_txrx.c`, SQE descriptor helpers, and queue state from `otx2_txrx.h`. `otx2_txrx.c` calls `otx2_zc_napi_handler()` during TX completion/idle and treats AF_XDP frames specially on completion.

## Risks and Edge Cases
Queue IDs must be valid for both RX and TX. Mode switching while the interface is down is rejected or short-circuited. RSS must be updated so zero-copy RX queues are not used by normal traffic. XSK address alignment adjusts `xdp->data`; mistakes can corrupt packet data. A possible typo in non-CN10K RQ disable writes `rq_aq->sq.ena`/`sq_mask.ena` while `ctype` is RQ, which deserves platform-specific review.

## Test Signals
Run AF_XDP zero-copy bind/unbind, RX/TX traffic, need-wakeup behavior, queue wakeup with and without scheduled NAPI, RSS distribution before/after enable, interface-down setup errors, DMA map/unmap failure injection, and mixed XDP program actions on XSK-backed queues.
