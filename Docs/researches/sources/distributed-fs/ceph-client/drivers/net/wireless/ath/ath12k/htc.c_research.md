# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/htc.c

## Purpose

`htc.c` implements the ath12k Host Target Communications layer. It frames outbound skbs with HTC headers, manages target transmit credits, parses inbound HTC headers/trailers, receives control messages on endpoint 0, connects services to HTC endpoints and HIF/CE pipes, waits for target readiness, starts HTC setup completion, and initializes endpoint state.

## Important APIs, Types, and Functions

Allocation and send helpers include `ath12k_htc_alloc_skb()`, local `ath12k_htc_build_tx_ctrl_skb()`, `ath12k_htc_prepare_tx_skb()`, and `ath12k_htc_send()`. They reserve HTC header space, enforce 4-byte alignment, push headers, consume credits, map TX DMA, and send through `ath12k_ce_send()`.

Receive/control helpers include `ath12k_htc_process_credit_report()`, `ath12k_htc_process_trailer()`, `ath12k_htc_suspend_complete()`, `ath12k_htc_wakeup_from_suspend()`, and `ath12k_htc_rx_completion_handler()`. They parse trailer records, add endpoint credits, complete control waits, handle suspend/wakeup events, dispatch endpoint RX callbacks, and poll CE TX completions for interrupt-disabled pipes.

Service setup uses `ath12k_htc_wait_target()`, `ath12k_htc_connect_service()`, `ath12k_htc_start()`, and `ath12k_htc_init()`. It parses target READY credit counts/sizes, divides credits among WMI endpoints, connects endpoint 0 as a pseudo control service, sends CONNECT_SERVICE messages for real services, maps service IDs to UL/DL pipes through HIF, and sends SETUP_COMPLETE_EX.

## Control Flow

Initialization sets up `tx_lock`, resets every endpoint to unused with credit flow enabled, derives `wmi_ep_count` from preferred hardware mode, connects the pseudo endpoint-0 control service locally, and initializes `ctl_resp`.

Target wait blocks on `ctl_resp` for the READY message. If it times out, it manually services every CE engine once and waits again. READY parsing validates message ID, credit count, and credit size, then stores credit state and computes WMI service credit allocations.

Service connection either handles the reserved control service locally or builds a control skb, sets connect flags, disables credit flow for non-WMI-control services, sends on endpoint 0, waits for a response, validates message/service status, records assigned endpoint and max message size, copies callbacks, maps the service to HIF pipes, and initializes endpoint credits.

Normal TX pushes an HTC header, checks and deducts endpoint credits if flow control is enabled, fills endpoint ID/payload length/sequence/control flags, DMA maps the skb, and submits to CE. DMA or CE send failures unmap and restore credits before pulling the header back off.

RX completion pulls the HTC header, validates endpoint and payload length, parses optional trailers and credit reports, handles endpoint-0 control messages by copying into `control_resp_buffer` and completing waiters, or dispatches non-control skbs to endpoint callbacks and transfers skb ownership.

## State and Persistence Behavior

Persistent HTC state includes endpoint table entries, endpoint callbacks, service IDs, CE pipe IDs, sequence numbers, per-endpoint TX credits, flow-control flags, `control_resp_buffer`, `control_resp_len`, completion `ctl_resp`, total target credits, service allocation table, target credit size, and WMI endpoint count. `tx_lock` serializes endpoint credit and sequence updates.

TX skbs carry DMA addresses in `ATH12K_SKB_CB`. On successful CE send, ownership moves to CE completion; on RX dispatch, ownership moves to the endpoint callback.

## Dependencies and Integration Points

HTC depends on CE transport (`ath12k_ce_send()`, CE service/poll helpers), HIF service-to-pipe mapping, mac80211/Linux skb/DMA/completion APIs, ath12k boot/debug flags, WMI preferred hardware mode, and endpoint users such as WMI, HTT, NMI, pktlog, and test services.

## Risks and Edge Cases

- `ath12k_htc_send()` checks `eid >= ATH12K_HTC_EP_COUNT` after computing `ep = &htc->endpoint[eid]`; invalid `eid` values could index before validation if ever supplied by a caller.
- Credit report validation warns "too long" when `record->hdr.len < sizeof(report)`; the message text is inverted, though the error behavior is correct.
- `ath12k_htc_wait_target()` ignores the return value from `ath12k_htc_setup_target_buffer_assignments()`, so invalid `wmi_ep_count` could leave no credit allocation but still return success.
- Endpoint 0 duplicate control message handling completes the same completion and drops the skb; unsolicited firmware behavior is treated as fatal/warn but not an immediate crash.
- Only WMI control services keep credit flow enabled; other services depend on CE/backpressure rather than target credits.
- Timeout paths after `ath12k_htc_send()` do not own the skb anymore, so service connect timeout cleanup relies on later CE completion.

## Test Signals

Useful tests include target READY timeout/poll fallback, invalid READY payloads, service connect success/failure/status codes, multi-WMI endpoint credit allocation for single/DBS/DBS-SBS modes, TX credit exhaustion and restoration on CE send failure, trailer credit report parsing, suspend ACK/NACK events, invalid endpoint RX frames, and DMA mapping fault injection.
