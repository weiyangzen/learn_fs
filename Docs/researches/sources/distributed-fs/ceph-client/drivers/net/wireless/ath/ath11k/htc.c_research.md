# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/htc.c

## Purpose
`htc.c` implements the ath11k HTC host-target control protocol over copy engine pipes. HTC wraps SKBs with endpoint headers, manages endpoint credit flow, receives control responses on endpoint 0, connects WMI/HTT services to target-assigned endpoints, handles HTC trailers/credit reports, and dispatches RX/TX completions to endpoint callbacks.

## Important APIs and functions
Exported APIs are `ath11k_htc_alloc_skb()`, `ath11k_htc_send()`, `ath11k_htc_tx_completion_handler()`, `ath11k_htc_rx_completion_handler()`, `ath11k_htc_wait_target()`, `ath11k_htc_connect_service()`, `ath11k_htc_start()`, and `ath11k_htc_init()`.

Internal helpers build aligned EP0 control SKBs, prepare HTC TX headers, process credit reports/trailers, handle suspend complete/NACK/wakeup messages, reset endpoint state, allocate WMI credits, and name services for diagnostics.

## Control flow
Initialization resets endpoint state, determines WMI endpoint count from hardware mode, connects the pseudo control service on EP0, and initializes the control-response completion. Boot waits for target READY, parses credits, optionally applies a shadow-register credit workaround, and sets WMI credit allocation. Service connection sends an EP0 connect request, waits for a response, validates it, fills endpoint state, maps service to HIF pipes, and disables credit flow for non-WMI control services or hardware without credit flow. Start sends setup-complete-extended.

Send flow pushes an HTC header, consumes credits if enabled, DMA maps the SKB, submits to CE, and restores credits/header on error. RX flow validates endpoint and payload length, processes trailers, handles EP0 control messages, or dispatches endpoint RX callbacks.

## State and persistence behavior
Mutable state lives in `struct ath11k_htc`: endpoint array, `tx_lock`, control response buffer/length, completion, total credits, service allocation table, target credit size, and WMI endpoint count. Each endpoint persists service id, pipe ids, callbacks, max sizes/depth, sequence number, credits, and credit-flow state. No disk persistence exists.

## Dependencies and integration points
HTC depends on `debug.h`, `hif.h`, CE send/poll/service functions, DMA mapping APIs, SKB control block fields, completions, spinlocks, and `ab->hw_params`/WMI hardware mode. CE tables call HTC completion handlers. WMI and DP/HTT connect services and send messages through this layer.

## Risks
Credit accounting is correctness-critical. EP0 control uses a single completion and shared response buffer, so wait/connect operations must remain serialized. Trailer parsing depends on target-provided data. `ath11k_htc_wait_target()` ignores the return from target buffer assignment, which could mask invalid WMI endpoint counts. DMA and CE error paths correctly restore credits/header, which is important.

## Test signals
Boot should show target ready, valid credits, successful WMI/HTT service connections, mapped UL/DL pipes, and setup complete. Runtime tests should include WMI/HTT traffic, credit starvation/replenishment, suspend complete/NACK, wakeup events, and CE poll paths. Invalid EID, trailer length, service timeout, or control reentrancy warnings are high-value failures.
