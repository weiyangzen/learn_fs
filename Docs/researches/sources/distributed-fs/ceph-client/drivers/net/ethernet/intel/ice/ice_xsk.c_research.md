# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_xsk.c

## Purpose
Implements AF_XDP zero-copy support for the `ice` driver. It handles XSK pool setup/teardown, queue-pair disable/enable around pool changes, zero-copy Rx buffer allocation, zero-copy Rx processing with XDP actions, AF_XDP Tx descriptor production, wakeup handling, IRQ/NAPI helpers, and ring cleanup.

## Important APIs and Functions
- `ice_xsk_pool_setup()` attaches or detaches an XSK pool to a queue ID, optionally disabling and re-enabling the live queue pair.
- `ice_realloc_rx_xdp_bufs()` allocates/frees the per-descriptor `xdp_buff` pointer array depending on pool presence.
- `ice_alloc_rx_bufs_zc()` and `__ice_alloc_rx_bufs_zc()` populate Rx descriptors from XSK fill/recycle buffers and bump tails.
- `ice_clean_rx_irq_zc()` is the zero-copy NAPI Rx loop; it consumes descriptors, builds multi-buffer XDP state, runs XDP, handles PASS/TX/REDIRECT/DROP/ABORT, refills buffers, updates wakeup state and stats.
- `ice_xmit_zc()` pulls AF_XDP Tx descriptors into the hardware XDP Tx ring.
- `ice_xsk_wakeup()` implements `ndo_xsk_wakeup`.
- IRQ/NAPI helpers include `ice_qvec_toggle_napi()`, `ice_qvec_dis_irq()`, `ice_qvec_cfg_msix()`, and `ice_qvec_ena_irq()`.
- Cleanup helpers free outstanding XSK Rx/XDP Tx buffers and complete AF_XDP Tx frames.

## Control Flow
Pool setup validates VSI type and queue bounds, maps or unmaps DMA, and if XDP is active temporarily disables the queue pair, reallocates the Rx XDP buffer array, then re-enables the queue pair and schedules NAPI for newly attached pools. Rx zero-copy loops until budget or descriptor exhaustion, syncs buffers for CPU, coalesces fragments, runs XDP, converts PASS packets to SKBs, and updates need-wakeup. Tx zero-copy first cleans completions, checks carrier/running state, peeks a bounded batch from the AF_XDP Tx ring, handles hardware ring wrap, marks RS, updates tail, and stats.

## State and Persistence
State is ring-local: `rx_ring->xdp_buf`, `rx_ring->xsk` partial multi-buffer head, ring indices, `xdp_ring->xdp_tx_active`, `tx_buf` types, XSK pool DMA mapping, need-wakeup flags, and q_vector interrupt/NAPI state. No persistent configuration survives queue teardown except pool association through the XSK subsystem.

## Dependencies and Integration Points
Depends on Linux XDP/AF_XDP APIs, `libeth_xdp`, BPF trace helpers, `ice_txrx`, `ice_txrx_lib`, queue-pair enable/disable, MSI-X/interrupt programming, NAPI, DMA mapping, netdev carrier/running state, and the driver XDP program path.

## Risks
- Pool changes while interface is up require precise queue disable/re-enable; failures can leave queues stopped or pool DMA state mismatched.
- Multi-buffer handling must preserve/free partial `first` buffers correctly.
- Need-wakeup behavior depends on correctly identifying allocation failure or empty rings.
- Tx completion distinguishes XSK_TX buffers from AF_XDP user descriptors; wrong `tx_buf->type` accounting can leak or double-complete.
- Queue ID bounds must cover both Rx and Tx real/driver queue counts.

## Test Signals
Test pool attach/detach while interface up/down, invalid queue IDs, PF and SF allowed versus VF rejected, XDP PASS/TX/REDIRECT/DROP/ABORT, multi-buffer packets, need-wakeup mode, Tx ring wrap, carrier down wakeup, cleanup with outstanding Rx and Tx buffers, and interrupt/NAPI disable/enable during XSK transitions.
