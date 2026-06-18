# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/time-sync.c

## Purpose

`time-sync.c` supports firmware-assisted timestamping for 802.11 timing measurement and FTM frames. It queues a pending management frame, matches firmware time measurement notifications by peer and dialog token, converts firmware 10 ns timestamps into adjusted PTP time, and reports the completed frame through mac80211 RX or TX status paths.

## Important APIs and functions

Public functions are `iwl_mvm_init_time_sync()`, `iwl_mvm_time_sync_msmt_event()`, `iwl_mvm_time_sync_msmt_confirm_event()`, and `iwl_mvm_time_sync_config()`. Internal helpers `iwl_mvm_is_skb_match()`, `iwl_mvm_time_sync_find_skb()`, and `iwl_mvm_get_64_bit()` match frames and combine high/low timestamp words.

## Control flow and state

Initialization sets up `mvm->time_sync.frame_list`. TX/RX code queues candidate frames through the inline helper in the header. When a measurement event arrives, the code dequeues frames until it finds one matching the notification peer address and dialog token, discarding obsolete frames. RX measurement events fill `skb_hwtstamps(skb)->hwtstamp` with T2 and `IEEE80211_SKB_RXCB(skb)->ack_tx_hwtstamp` with T3, then inject the frame via `ieee80211_rx_napi()`. Confirmation events fill TX hwtstamp T1 and ACK hwtstamp T4, then report via `ieee80211_tx_status_ext()`.

Configuration validates firmware capability, enforces a single active peer unless reconfiguring the same address, validates the protocol mask for TM/FTM only, sends `WNM_80211V_TIMING_MEASUREMENT_CONFIG_CMD`, updates active state and peer address on success, and purges queued frames when disabling.

## Dependencies and integration

The file depends on firmware time-sync notifications and config command structures, mac80211 SKB timestamp/status APIs, PTP adjustment via `iwl_mvm_ptp_get_adj_time()`, and action-frame parsers `ieee80211_is_timing_measurement()` / `ieee80211_is_ftm()`.

## Risks

Only one SKB is expected in the queue, but the code tolerates extra frames by dropping nonmatches. Risks include losing timestamps if notifications arrive after queue purge, matching the wrong frame if dialog tokens collide with the same peer, accepting only one active peer, and unit conversion mistakes from 10 ns firmware timestamps to nanoseconds. The frame-list queue must be purged when disabling to avoid stale reports.

## Test signals

Tests should cover config capability rejection, unsupported protocol mask rejection, second-peer rejection, disable purge, RX and TX notification matching, obsolete SKB discard, FTM versus timing-measurement dialog token extraction, and timestamp conversion through the PTP adjustment function.
