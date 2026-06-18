# sources/distributed-fs/ceph-client/net/smc/smc_wr.c

Purpose: Owns SMC-R RDMA work-request infrastructure for LLC/CDC sends, RDMA write helpers, receive queue demultiplexing, completion processing, memory allocation, DMA mapping, and link teardown coordination.

Important APIs/types/functions: `struct smc_wr_tx_pend` tracks pending send WRs. TX APIs include `smc_wr_tx_get_free_slot()`, `smc_wr_tx_get_v2_slot()`, `smc_wr_tx_put_slot()`, `smc_wr_tx_send()`, `smc_wr_tx_v2_send()`, `smc_wr_tx_send_wait()`, `smc_wr_reg_send()`, and `smc_wr_tx_wait_no_pending_sends()`. RX APIs include `smc_wr_rx_register_handler()`, `smc_wr_rx_post_init()`, and CQ handlers. Lifecycle APIs allocate/free link and link-group memory, remember QP attributes, create links, and setup/kill device tasklets.

Control flow: Senders reserve a bitmap slot, fill a WR buffer and pending context, then post to the QP. Send CQ interrupts schedule a tasklet, which polls completions, finds the pending slot by WR ID, clears buffers/masks, wakes waiters, invokes completion handlers, and schedules link-down on fatal status. Receive CQ tasklets poll completions, locate the RX buffer by WR ID modulo queue size, demultiplex by SMC message type through a handler hash, repost receive WRs, or schedule link-down on retry/flush errors. Link creation maps buffers for DMA, initializes SGEs/IB WRs, wait queues, completions, and percpu references.

State and persistence behavior: State is per link and per device: WR IDs, pending arrays, masks, buffers, SGEs, IB WR descriptors, DMA addresses, v2 shared buffers, wait queues, tasklets, registration state, and percpu references. It is in-memory and must be drained/unmapped before link/device destruction.

Dependencies and integration points: Depends on RDMA ib verbs, SMC core link/link-group state, SMC CDC/LLC handlers registered elsewhere, tasklets for CQ bottom halves, DMA mapping APIs, and link-down scheduling.

Risks and test signals: Risks include WR slot leaks, completion races, use-after-free during link teardown, incorrect v2 large-buffer clearing, DMA map/unmap imbalance, RX handler registration order, and missed CQ notifications. Test high WR slot pressure, send-wait timeouts, MR registration success/failure, CQ error statuses, RX repost failures, SMC-Rv2 large messages, link teardown with pending WRs, and RDMA device removal.
