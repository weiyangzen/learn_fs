# sources/distributed-fs/ceph-client/net/mac80211/airtime.c

Purpose: this file estimates RX, reported TX, and expected TX airtime for mac80211 frames. It converts rate information for legacy, HT, VHT, HE, and EHT encodings into microsecond duration estimates used by scheduling/accounting paths, including TXQ airtime fairness.

Important data and APIs: compile-time macros generate `airtime_mcs_groups[]`, a table of per-MCS average packet durations for stream count, guard interval, and channel width combinations. `struct mcs_group` stores a shift and up to 14 rate durations. Exported functions are `ieee80211_calc_rx_airtime()`, `ieee80211_calc_tx_airtime()`, and `ieee80211_calc_expected_tx_airtime()`. Internal helpers include `ieee80211_calc_legacy_rate_duration()`, `ieee80211_get_rate_duration()`, `ieee80211_fill_rate_info()`, and `ieee80211_fill_rx_status()`.

Control flow: legacy rates are calculated from bitrate, short preamble, CCK status, payload length, preamble/PLCP, and SIFS constants. Non-legacy status is mapped to an MCS table group by encoding, NSS/streams, GI, and bandwidth. The table duration is shifted back, scaled from `AVG_PKT_SIZE` to actual length, divided down from 1024-usec units, and combined with an overhead estimate. `ieee80211_calc_tx_airtime()` iterates `info->status.rates`, computes duration for each retry rate, multiplies by retry count, and stops when a rate is invalid. `ieee80211_calc_expected_tx_airtime()` uses a station's last TX rate when present, applies aggregation overhead reduction heuristics for non-legacy AMPDU, and otherwise falls back to the lowest configured basic rate for the interface.

State and persistence behavior: the only persistent data is the static const rate-duration table. The functions read current wiphy bands, BSS channel context, basic rates, and station `last_rate`/`last_rate_info`; they do not mutate state.

Dependencies and integration: it depends on `<net/mac80211.h>`, `ieee80211_i.h`, and `sta_info.h`. TX scheduling calls expected airtime from `tx.c`, and exported RX/TX calculators can be used by other mac80211 paths or modules. The code relies on nl80211 `rate_info` flags and `ieee80211_rx_status` encoding conventions.

Risks: this is an estimator, not a PHY simulator. Incorrect group index calculation can read wrong table entries; guard checks reject unsupported stream counts and MCS indexes. EHT 320 MHz and high MCS handling must stay aligned with nl80211 enum values. Expected TX aggregation heuristics may under- or over-estimate airtime, affecting fairness rather than correctness.

Test signals: unit tests around known rate/length combinations, boundary tests for every bandwidth/GI/encoding, invalid MCS/NSS handling, TX retry summation, expected-airtime fallback without station, and scheduler behavior under mixed legacy/HE/EHT traffic.
