## sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/txrx.c

Purpose: this is common Prism54 mac80211 TX/RX handling shared by p54 transports. It translates mac80211 skbs into p54 firmware frames, manages firmware RAM address allocation for outstanding TX frames, processes RX data/control frames, accounts queue pressure, updates survey/statistics, and reports TX status back to mac80211.

Important functions: `p54_tx_80211()` builds p54 data headers, ratesets, retry counts, crypto metadata, padding, and queue/backlog values before calling `p54_tx()`. `p54_assign_address()` reserves firmware memory windows and sets `req_id`. `p54_free_skb()` and `p54_find_and_unlink_skb()` release outstanding TX state. `p54_rx()` dispatches data versus control frames. `p54_rx_data()` builds `ieee80211_rx_status` and calls `ieee80211_rx_irqsafe()`. `p54_rx_frame_sent()` maps firmware TXDONE into mac80211 TX status. `p54_rx_stats()` updates noise and survey counters. `p54_rx_eeprom_readback()` and trap handling complete firmware command side effects.

Control flow: outgoing frames are queued in `tx_pending`, allocated into firmware RAM in address order under `tx_queue.lock`, and passed to the transport `priv->tx`. Firmware TXDONE returns the same `req_id`, allowing lookup and status completion. Incoming data frames are validated for FCS and mode, trimmed to 802.11 payload, then handed to mac80211. Control frames update EEPROM/stat completions, beacon loss/rfkill traps, or TX completion.

State and persistence: key mutable state includes `tx_queue`, `tx_pending`, per-queue `tx_stats`, `beacon_req_id`, EEPROM/stat completions, TSF high/low tracking, survey raw counters, power-save override, and current RSSI conversion data. State persists only in driver memory and is protected by spinlocks where shared with interrupt/URB contexts.

Dependencies and integration: depends on mac80211, p54 LMAC structures, transport callbacks, firmware memory layout (`rx_start`/`rx_end`), and common p54 configuration. Crypto handling depends on mac80211 key metadata and p54 firmware expectations for WEP/TKIP/CCMP.

Risks and tests: address allocator fragmentation and 32-entry limits can stall TX. `skb->cb` reuse for driver data is order-sensitive. TKIP IV/MIC mutation must be reversed for TX status. Test signals include saturated queue behavior, TXDONE matching, beacon queue completion, RX FCS/decrypt flags, scan/stat completions, power-save beacon TIM workaround, and survey counter sanity.
