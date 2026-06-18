# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libeth/xdp.c

## Purpose
`libeth/xdp.c` implements common XDP infrastructure: shared XDPSQ locking, cleanup timer setup, XDP_TX exception handling, `ndo_xdp_xmit` unwind helpers, XDP buffer stash/return, fragment attachment, program exception handling, bulk frame returns, XDP queue thresholds, and netdev XDP feature advertising.

## Important APIs, Types, and Functions
Key exports include `libeth_xdpsq_share`, `__libeth_xdpsq_get/put/lock/unlock()`, `libeth_xdpsq_init_timer()`, `libeth_xdp_tx_exception()`, `libeth_xdp_xmit_return_bulk()`, `libeth_xdp_load_stash()`, `libeth_xdp_save_stash()`, `__libeth_xdp_return_stash()`, `libeth_xdp_return_buff_slow()`, `libeth_xdp_buff_add_frag()`, `libeth_xdp_prog_exception()`, `libeth_xdp_return_buff_bulk()`, `libeth_xdp_queue_threshold()`, `__libeth_xdp_set_features()`, and `libeth_xdp_set_redirect()`.

## Control Flow
XDPSQ share get/put toggles a static key and initializes a lock when sharing is needed. XDP_TX exception handling either preserves unsent frames for retry or drops/returns remaining frames via XSk, native XDP, or ndo_xmit-specific return helpers. Rx helpers convert between an on-stack `libeth_xdp_buff` and a persistent stash, attach page frags, and route invalid actions or redirect failures through trace/free logic. Module init attaches XDP ops to base `libeth`; exit detaches them.

## State and Persistence Behavior
State includes the global static key for XDPSQ sharing, per-queue lock/timer/stash objects owned by consumers, netdev XDP feature fields, and static-call attachment into `libeth_tx_complete_any()`.

## Dependencies and Integration Points
The file integrates Linux XDP, BPF tracepoints, XSk helpers from `xsk.c`, netmem, skb shared-info fragments, netdev feature APIs, and base `libeth` static calls. Consumer drivers use these helpers to share common XDP hotpath mechanics while retaining hardware-specific descriptor programming.

## Risks and Edge Cases
- `libeth_xdp_queue_threshold(0)` would produce nonsensical threshold behavior; callers should pass real descriptor counts.
- Exception helpers must not double-free multi-buffer frames; `FIRST` and `MULTI` flags drive ownership.
- XSk redirect `-ENOBUFS` with need-wakeup changes verdict to aborted to stop polling.
- Feature advertisement must match actual driver support for zerocopy and scatter-gather.

## Test Signals
XDP_TX partial send/drop/retry paths, multi-frag return, invalid XDP action trace, redirect failure with and without XSk need-wakeup, stash save/load/return, queue threshold for power-of-two and non-power-of-two counts, netdev feature flags for XSK zerocopy, and module load/unload attach behavior.
