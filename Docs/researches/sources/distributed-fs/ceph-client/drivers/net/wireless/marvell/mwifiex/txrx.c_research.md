# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/txrx.c

## Purpose
`txrx.c` is the generic data-path dispatcher shared by all mwifiex buses and roles. It routes RX buffers to STA or uAP handlers, prepares and sends TX packets through role-specific TxPD builders and bus `host_to_card` operations, drains the deferred TX queue, completes TX accounting/freeing, wakes netdev queues, and processes firmware TX-status events for EAPOL/action-management acknowledgements.

## Important APIs, Types, and Functions
Key APIs are `mwifiex_handle_rx_packet`, `mwifiex_process_tx`, `mwifiex_process_tx_queue`, `mwifiex_write_data_complete`, and `mwifiex_parse_tx_status_event`. The local `mwifiex_host_to_card` retries/dequeues queued packets. Important data structures are `struct rxpd`, `struct txpd`, `struct mwifiex_txinfo`, `struct mwifiex_rxinfo`, `struct mwifiex_tx_param`, `adapter->tx_data_q`, `adapter->tx_queued`, `adapter->tx_pending`, `priv->wmm_tx_pending[]`, and `priv->ack_status_frames`.

## Control Flow and Integration
RX handling reads BSS number/type from firmware `rxpd`, finds the matching private interface, initializes skb RX control metadata, and dispatches to `mwifiex_process_uap_rx_packet` for AP role or `mwifiex_process_sta_rx_packet` otherwise. Missing interface state drops the packet.

TX starts in `mwifiex_process_tx`, which rejects empty or insufficient-headroom SKBs. uAP packets update destination station TX stats and call `mwifiex_process_uap_txpd`; station packets call `mwifiex_process_sta_txpd`. If `adapter->data_sent` or `tx_lock_flag` is set, the fully prepared SKB is queued on `adapter->tx_data_q` and accounted in `tx_queued`. Otherwise it is sent through USB endpoint `priv->usb_port` or generic data type. Return handling distinguishes no-resource, busy, hard failure, in-progress, malformed, and synchronous success. Busy during PPS/UAPSD can clear the last-packet flag and unlock TX.

`mwifiex_process_tx_queue` repeatedly dequeues while transport is not blocked. It passes `next_pkt_len` hints for bus aggregation and requeues at the head on EBUSY. Completion resolves `priv` from TXCB, updates netdev trans_start, handles bridged-packet accounting, skips normal stats for aggregate wrapper SKBs, updates success/error counters, decrements pending counts, and wakes WMM netdev queues below `LOW_TX_PENDING`. TX-status events remove ack SKBs from an IDR and notify cfg80211 or `skb_complete_wifi_ack`.

## State and Persistence Behavior
This file mutates transport gating (`data_sent` is owned by bus callbacks but observed here), deferred queue contents, atomic queue counters, per-interface TX stats, per-WMM pending counts, bridged-packet counters, debug failure counters, and ack-status IDR entries. SKB ownership is transferred to transport, queued internally, or freed on completion.

## Dependencies and Risks
Dependencies include STA/uAP TxPD/RX handlers, bus `if_ops`, WMM queue mappings, netdev queue APIs, cfg80211 management TX status, and the ack-status lock/IDR. Risks are queue accounting imbalance on aggregate versus non-aggregate paths, SKB ownership on mixed synchronous/asynchronous bus returns, EBUSY requeue ordering, and keeping `tx_lock_flag` consistent with power-save NULL packet semantics.

## Test Signals
Probe RX BSS dispatch, TX with insufficient headroom, USB/non-USB sends, EBUSY requeue, aggregate completion, bridged packet accounting, netdev queue wakeups, TX timeout counter reset, EAPOL/action ACK reporting, and queue draining after bus completion clears `data_sent`.
