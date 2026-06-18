# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/htc_pipe.c

## Purpose
`htc_pipe.c` implements the pipe-oriented HTC backend, used by message-based HIFs such as USB. Unlike mailbox HTC, it sends SKBs through HIF pipes, matches TX completions through per-endpoint lookup queues, receives complete SKBs from HIF, stores endpoint 0 control responses in a small buffer, and uses simpler per-service credit allocation.

## Important APIs, types, and functions
TX path functions include `htc_try_send()`, `get_htc_packet_credit_based()`, `get_htc_packet()`, `htc_issue_packets()`, `ath6kl_htc_pipe_tx()`, `ath6kl_htc_pipe_tx_complete()`, and `htc_send_packets_multiple()`. Control packet helpers allocate SKB-backed HTC control packets. Credit setup functions include `htc_setup_target_buffer_assignments()`, `htc_get_credit_alloc()`, and `htc_process_credit_report()`. RX functions include `ath6kl_htc_pipe_rx_complete()`, `htc_process_trailer()`, packet-container pool helpers, and `do_recv_completion()`. Lifecycle and service functions include `ath6kl_htc_pipe_create()`, `ath6kl_htc_pipe_wait_target()`, `ath6kl_htc_pipe_start()`, `ath6kl_htc_pipe_stop()`, `ath6kl_htc_pipe_conn_service()`, and `ath6kl_htc_pipe_attach()`.

## Control flow and integration
Create allocates `htc_target`, initializes endpoint states, creates a small pool of `htc_packet` containers for RX adaptation, allocates `ath6kl_device`, and asks HIF for default control pipes. Target wait polls `pipe.ctrl_response_valid`, validates `HTC_MSG_READY`, stores target credit count/size, assigns service credit budgets, and connects pseudo endpoint 0. Service connection sends a connect message over endpoint 0, waits for a control response captured by RX completion, validates response, configures endpoint callbacks/credits, maps WMI service to uplink/downlink HIF pipes, and optionally disables credit flow control.

TX queues are bounded by endpoint `max_txq_depth`; overflow packets are passed to `tx_full`. The drain path either consumes HTC credits or uses HIF pipe free queue count, pushes an HTC header into the SKB, records the packet in `ep->pipe.tx_lookup_queue`, and calls `ath6kl_hif_pipe_send()`. HIF TX completion parses the SKB header for endpoint id, finds the corresponding `htc_packet`, restores the SKB by removing the HTC header, completes to upper callbacks, and retriggers queue draining when credit flow is disabled. RX completion validates header and length, processes credit trailers, captures endpoint 0 control messages before setup complete, wraps data SKBs in temporary HTC packet containers, calls endpoint RX callbacks, and returns the container to the pool.

## State and persistence behavior
Persistent pipe state includes endpoint TX queues, RX queues, per-endpoint pipe IDs, TX lookup queues, credit-flow enablement, target credit size/count, static service credit allocation array, endpoint 0 control response buffer/valid flag, `HTC_OP_STATE_SETUP_COMPLETE`, and the packet-container pool. There is no mailbox interrupt state. Stop flushes RX/TX queues, resets endpoints, and clears setup-complete.

## Dependencies and integration points
The backend depends on pipe HIF operations (`pipe_send`, `pipe_get_default`, `pipe_map_service`, and free queue count), SKB headroom manipulation, upper endpoint callbacks, and HIF completion paths calling `ath6kl_htc_pipe_tx_complete()`/`ath6kl_htc_pipe_rx_complete()`. It shares protocol structures with mailbox HTC through `htc.h`.

## Risks and test signals
Risks include SKB headroom assumptions for pushing HTC headers, TX lookup failures if completions race with flush, endpoint id trust in completed SKBs, control response polling timeouts, RX packet container pool exhaustion, trailer validation, credit allocation imbalance, and minimal/no-op activity and credit setup hooks. Test signals include USB/pipe firmware boot, endpoint 0 ready/connect/setup sequence, TX completion lookup under flush, non-credit-flow endpoints under HIF queue pressure, malformed RX headers/trailers, RX before `ar->htc_target` initialization, and repeated stop/start cleanup.
