# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/uap_event.c

## Purpose
`uap_event.c` handles firmware events for AP/uAP interfaces. It reports station association/deauthentication to cfg80211, creates and removes station nodes, initializes peer 11n aggregation state, tracks BSS active/idle/start state, parses AP capability TLVs, handles BA/AMSDU/scan/TX-status/power-save/radar/channel events, and forwards shared events to generic mwifiex handlers.

## Important APIs, Types, and Functions
The main public function is `mwifiex_process_uap_event`. The local `mwifiex_check_uap_capabilities` parses BSS-start event TLVs to set AP HT/VHT/WMM state and queue priorities. Important structures include `struct mwifiex_assoc_event`, `struct station_info`, `struct mwifiex_sta_node`, `struct host_cmd_ds_11n_batimeout`, and firmware event buffers `adapter->event_body` and `adapter->event_skb`.

## Control Flow and Integration
On `EVENT_UAP_STA_ASSOC`, the handler allocates `station_info`, extracts association request IEs from `TLV_TYPE_UAP_MGMT_FRAME` events, calls `cfg80211_new_sta`, adds a station node, and, when AP 11n is enabled, parses HT capabilities and initializes per-TID AMPDU permission and RX sequence state. `EVENT_UAP_STA_DEAUTH` notifies cfg80211, deletes RX reorder and TX BA state for the peer, removes WMM RA list entries, and deletes the station node.

`EVENT_UAP_BSS_IDLE` marks media and port closed, cleans TX/RX queues, and removes all station nodes. `EVENT_UAP_BSS_ACTIVE` opens media/port. `EVENT_UAP_BSS_START` sets port closed until active, updates netdev MAC from event body, resets histograms, and parses capability TLVs. Shared events update `adapter->tx_buf_size`, respond to ADDBA, delete BA streams, process BA timeout, handle ext scan reports, parse TX status, drive power-save sleep/awake transitions, process channel/radar/BT coexistence/TX pause/multichannel/RXBA sync, and report remain-on-channel expiration to cfg80211.

## State and Persistence Behavior
Persistent driver state includes `priv->media_connected`, `priv->port_open`, `priv->ap_11n_enabled`, `priv->ap_11ac_enabled`, `priv->wmm_enabled`, station list contents, per-peer AMPDU/RX sequence state, `adapter->tx_buf_size`, `adapter->ps_state`, `adapter->pps_uapsd_mode`, wakeup flags, `adapter->tx_lock_flag`, histograms, and remain-on-channel config. Firmware event contents are consumed from adapter event buffers.

## Dependencies and Risks
Dependencies include cfg80211 station and remain-on-channel APIs, WMM setup, 11n BA/reorder helpers, radar/11h handlers, TX status parsing in `txrx.c`, NULL-packet power-save flow in `sta_tx.c`, and station utilities in `util.c`. Risks include trusting event-body layout/length for association IEs and BSS MAC updates, station-info allocation failures, cleanup ordering during idle/deauth, and power-save state transitions that can leave `tx_lock_flag` or wake flags inconsistent.

## Test Signals
Exercise station assoc/deauth events, malformed association event lengths, AP start/active/idle ordering, WMM/HT/VHT capability parsing, BA add/delete/timeout, AMSDU control, ext scan, TX status, PS_SLEEP/PS_AWAKE with NULL packet generation, radar/channel report events, remain-on-channel expiration, and queue cleanup on BSS idle.
