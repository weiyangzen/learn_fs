# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/xdp.c

## Purpose
Implements IDPF XDP integration for split queue mode. It registers RX queue metadata with the kernel XDP core, manages dedicated XDP Tx queues, completes XDP transmissions through splitq completion queues, implements `ndo_xdp_xmit`, exposes XDP RX metadata operations for RSS hash and hardware timestamp, and handles XDP program/XSK pool setup through the netdev BPF hook.

## Important APIs, Types, And Functions
`idpf_xdp_rxq_info_init()`, `idpf_xdp_rxq_info_init_all()`, `idpf_xdp_rxq_info_deinit()`, and `idpf_xdp_rxq_info_deinit_all()` register or unregister `xdp_rxq_info` for each RX queue, attach page-pool or XSK memory models, and set splitq XDP SQ pointers. `idpf_xdp_copy_prog_to_rqs()` RCU-replaces RX queue BPF programs.

`idpf_xdpsqs_get()` converts a tail range of Tx queues into XDP SQs by assigning completion queues, clearing refill queues, setting XDP/NOIRQ flags, initializing libeth XDP SQ locks and timers, and setting thresholds. `idpf_xdpsqs_put()` reverses timer/lock state and clears flags. `idpf_xdpsq_poll()` parses 4-byte completion descriptors, `idpf_xdpsq_complete()` releases completed frames, and libeth macros generate bulk flush/xmit/timer helpers. `idpf_xdp_xmit()` is the netdev XDP transmit entry point. `idpf_xdp_set_features()` advertises metadata and XSK operations. `idpf_xdp()` handles `XDP_SETUP_PROG` and `XDP_SETUP_XSK_POOL`.

## Control Flow
RX queue setup iterates `idpf_q_vec_rsrc` groups with `idpf_rxq_for_each()`, selecting splitq or singleq queue arrays. For each RX queue, XDP RXQ info is registered against the netdev, queue index, NAPI ID, and optional XSK fragment size. Splitq queues also receive the vport's XDP SQ array and count so XDP redirect/transmit paths can find output queues.

When XDP is enabled, `idpf_xdpsqs_get()` prepares a dedicated set of Tx queues from `xdp_txq_offset` to `num_txq`. During transmit, libeth bulk helpers call `idpf_xdp_tx_prep()` to lock the XDP SQ and expose descriptor ring state, `idpf_xdp_tx_xmit()` from `xdp.h` fills descriptors, and `idpf_xdp_tx_finalize()` sets RS/tail/timer. Completion polling parses completion queue entries, releases XDP frame resources, decrements pending counters, and updates queue clean indices.

Program setup takes the fast path when removing, when netdev is not registered, or when enabling/disabling state does not change. Otherwise it stores the requested program in user config and initiates a soft reset with queue change so XDP SQ resources can be recalculated. XSK pool setup is delegated to `idpf_xsk_pool_setup()`.

## State And Persistence
State touched here includes per-RX `xdp_rxq_info`, RX queue `xdp_prog` RCU pointers, RX XSK memory model, RX page-pool attachment, RX queue pointers to XDP SQs, XDP Tx queue flags, timers, libeth locks, completion queue clean index and generation bit, Tx queue pending and xdp_tx counters, BPF program references in vport and user config, and netdev XDP feature flags. Program state persists in memory across vport reset through `cfg->user_config.xdp_prog`.

## Dependencies And Integration Points
The file depends on `idpf.h`, PTP helpers for RX timestamp extension, `idpf_virtchnl.h` for queue model state, `xdp.h`, `xsk.h`, Linux BPF/XDP APIs, libeth XDP helpers, page-pool/XSK memory models, NAPI IDs, and netdev feature advertising. It integrates with virtchnl queue configuration because XDP SQs are regular Tx queues flagged as XDP/NOIRQ and mapped through the queue/vector logic in `idpf_virtchnl.c`.

## Risks
XDP is restricted to split Tx queue mode; unsupported modes must return `-EOPNOTSUPP`. Queue accounting is sensitive: enabling XDP needs spare Tx queues, and failure to decrease regular SQs returns `-ENOSPC`. Completion parsing must correctly handle generation bits and ring wrap or frames can leak or be double-completed. BPF program references must be incremented, replaced under RCU, and released on old programs. XSK queues use a different memory model and must not detach page-pool state on deinit. Timestamp metadata depends on valid PTP queue flag and cached PHC time.

## Test Signals
Signals include loading/unloading XDP programs on up/down vports, soft reset success when XDP queue count changes, `ndo_xdp_xmit` success and `-ENETDOWN` when carrier/link is down, XDP redirect and TX completion under ring wrap, XSK pool setup, RX hash metadata returning `-ENODATA` when hash is absent, RX timestamp metadata with and without PTP valid bits, BPF reference leak checks, and traffic tests that verify regular Tx/Rx queues still work after XDP enable/disable.
