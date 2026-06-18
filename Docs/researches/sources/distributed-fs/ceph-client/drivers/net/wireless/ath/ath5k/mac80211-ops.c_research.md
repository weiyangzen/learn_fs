# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/mac80211-ops.c

## Purpose
`mac80211-ops.c` is the ath5k `struct ieee80211_ops` implementation. It translates mac80211 callbacks into ath5k queueing, interface bookkeeping, channel/power/retry configuration, beacon and BSSID updates, multicast/RX filter programming, hardware key programming, TSF access, survey reporting, antenna selection, and TX ring sizing.

## Important APIs and Control Flow
`ath5k_tx()` validates skb queue mapping and queues frames through `ath5k_tx_queue()`. Interface add/remove callbacks maintain `ah->nvifs`, AP/adhoc/mesh counts, beacon-buffer ownership (`bcbuf`, `bslot`, `avf->bbuf`), opmode, and BSSID mask/opmode. Adhoc is deliberately restricted to a single interface.

`ath5k_config()` handles channel changes via `ath5k_chan_set()`, TX power through `ath5k_hw_set_txpower_limit()`, retry limit propagation to all queues, and antenna mode restore. `ath5k_bss_info_changed()` responds to BSSID, beacon interval, slot timing, association, beacon content, and beacon enable changes, updating hardware BSSID, beacon filter, LED state, and beacon timers.

Filtering is split between `ath5k_prepare_multicast()` hash generation and `ath5k_configure_filter()` hardware programming. The latter preserves PHY error bits, supports mac80211 FIF flags, adds per-opmode filters, enables promiscuous mode for multiple STA interfaces, then writes RX and multicast filters. `ath5k_set_key()` handles supported WEP/TKIP/CCMP hardware keys and pushes IV/MMIC/management-TX policy back to mac80211. Remaining callbacks expose stats, EDCA queue config, TSF, survey counters, coverage class, antenna masks, and ring parameters.

## State, Dependencies, and Integration
Most mutations are protected by `ah->lock`; beacon updates also use `ah->block`. Persistent state includes interface counts, `ah->opmode`, `ah->assoc`, beacon buffers, BSSID/AID in `ath_common`, `ah->filter_flags`, `ah->fif_filter_flags`, TX queue limits, antenna mode, retry limits, survey counters, and LED state. Dependencies include mac80211/cfg80211 types, ath common key/regd helpers, base transmit/beacon/channel code, PCU functions, and hardware queue APIs.

## Risks and Test Signals
Risks include beacon-buffer leaks on add/remove errors, invalid multi-interface mode combinations, RX filter over/under-permissiveness, key offload mismatches, locking regressions, and ring size changes racing active TX. Test signals include multi-VIF AP/STA smoke tests, adhoc rejection behavior, association LED/filter changes, multicast reception, hardware crypto fallback, survey counter monotonicity, EDCA queue updates, and no stopped queue deadlock after `set_ringparam()`.
