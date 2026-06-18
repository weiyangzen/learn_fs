# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/htc_mbox.c

## Purpose
`htc_mbox.c` implements the mailbox/SDIO HTC backend. It handles target readiness, service connection, endpoint setup, TX credit distribution, asynchronous mailbox TX, optional scatter TX/RX bundling, mailbox RX lookahead processing, trailer parsing, control buffers, RX buffer flow control, start/stop/reset, and attachment of `ath6kl_htc_mbox_ops`.

## Important APIs, types, and functions
Credit functions include `ath6kl_credit_init()`, `ath6kl_credit_seek()`, `ath6kl_credit_update()`, `ath6kl_credit_redistribute()`, `ath6kl_credit_distribute()`, and `ath6kl_htc_mbox_credit_setup()`. TX functions include `ath6kl_htc_tx_prep_pkt()`, `ath6kl_htc_tx_issue()`, `htc_check_credits()`, `ath6kl_htc_tx_pkts_get()`, `ath6kl_htc_tx_bundle()`, `ath6kl_htc_tx_from_queue()`, `ath6kl_htc_tx_try()`, and `ath6kl_htc_mbox_tx()`. RX functions include `ath6kl_htc_rx_alloc()`, `ath6kl_htc_rx_fetch()`, `ath6kl_htc_rx_process_hdr()`, `ath6kl_htc_rx_process_packets()`, and the exported `ath6kl_htc_rxmsg_pending_handler()`. Lifecycle functions include `ath6kl_htc_mbox_create()`, `ath6kl_htc_mbox_wait_target()`, `ath6kl_htc_mbox_start()`, `ath6kl_htc_mbox_stop()`, `ath6kl_htc_mbox_cleanup()`, and `ath6kl_htc_mbox_attach()`.

## Control flow and integration
Create allocates `htc_target` and `ath6kl_device`, initializes locks/lists, calls `ath6kl_hif_setup()`, and allocates control buffers. `wait_target` polls endpoint 0 for `HTC_MSG_READY`, records target credits/credit size/version/bundle limits, enables scatter bundling if supported, and connects a pseudo control service. Service connection sends `HTC_MSG_CONN_SVC` synchronously over endpoint 0, waits for a response, assigns endpoint state, callbacks, max sizes, credit accounting, and thresholds. Start queues control RX buffers, initializes credit distribution, sends setup complete, and unmasks interrupts.

TX queues packets by endpoint, enforces max depth through `tx_full`, obtains credits, prepares HTC headers, optionally bundles with scatter requests, writes to mailbox asynchronously, and completes packets through upper callbacks. RX begins from a HIF mailbox lookahead, allocates buffers from endpoint queues or `rx_allocthresh`, fetches single or bundled packets, validates headers, parses trailers for credits/lookaheads, indicates packets to endpoint callbacks, and masks RX interrupts when buffers are unavailable.

## State and persistence behavior
State persists in endpoint TX/RX queues, free control TX/RX buffer lists, credit distribution list, target credit totals, bundle masks, scatter limits, `rx_st_flags`, `ep_waiting`, `chk_irq_status_cnt`, and endpoint stats. Stop sets `HTC_OP_STATE_STOPPING`, masks interrupts synchronously, flushes TX/RX queues, and resets control buffers. RX starvation persists as `HTC_RECV_WAIT_BUFFERS` until new buffers are added for the waiting endpoint.

## Dependencies and integration points
This backend depends on common HIF read/write, scatter, interrupt mask/unmask, RX control, debug/trace, target mailbox fields in `ar->mbox_info`, and upper endpoint callbacks provided by WMI/core. It is primarily used with SDIO mailbox transports.

## Risks and test signals
Risks include credit leaks on TX failure, scatter rollback correctness, trailer length validation, lookahead/header mismatch handling, RX starvation deadlock, endpoint 0 control buffer ownership, block/credit alignment disabling bundling, and queue flush races around stop. Test signals include HTC 2.0/2.1 ready negotiation, service connect failures, high-throughput bundled TX/RX, low-credit recovery, RX buffer exhaustion/unblock, firmware crash while polling, endpoint flush by tag, and repeated start/stop cycles.
