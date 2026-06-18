# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/htc.c

Purpose: implements the ath10k Host-Target Control protocol. HTC frames WMI, HTT, pktlog, and other services over HIF pipes; connects services; manages TX credits; parses trailers; dispatches completions; and supports high-latency TX bundling.

Important APIs/types/functions: exported entry points include `ath10k_htc_init`, `ath10k_htc_wait_target`, `ath10k_htc_start`, `ath10k_htc_connect_service`, `ath10k_htc_send`, `ath10k_htc_send_hl`, `ath10k_htc_stop_hl`, `ath10k_htc_setup_tx_req`, completion handlers, notification, skb allocation, and trailer processing. Internal helpers handle control skbs, headers, credits, lookaheads, bundles, pktlog, and endpoint reset.

Control flow: init creates EP0 control state. `wait_target` waits for READY and records target credit/bundle sizes. `connect_service` sends CONNECT_SERVICE, waits for EP0 response, maps service to HIF pipes, and installs endpoint callbacks. TX pushes HTC headers, consumes credits, maps DMA for non-HL, and sends through HIF. RX validates headers/trailers, processes credit/lookahead records, trims trailers, and dispatches payloads.

State and persistence: volatile state lives in `struct ath10k_htc` and endpoints: service IDs, pipe IDs, callbacks, credits, sequence numbers, bundle queues, control response buffer, completion, and target credit/bundle parameters. No persistence exists.

Dependencies/integration: depends on HIF, skbuff control blocks, ath10k workqueues, firmware HTC ABI, and endpoint callbacks from HTT/WMI/pktlog layers.

Risks: malformed trailers can affect credits/lookaheads; credit accounting must balance every error path; EP0 has one shared response buffer; HL bundling has delicate skb ownership; required callbacks are assumed after setup; DMA unmap timing includes hardware-specific delay.

Test signals: READY timeout/polling, invalid READY, service connect success/fail, unsupported pipe mapping, malformed trailers, credit reports, lookahead bundles, wedged TX, DMA failures, invalid EIDs, unconnected endpoints, trailer-only frames, and HL bundle stop/drain behavior.
