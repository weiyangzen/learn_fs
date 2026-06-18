# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dfs.c

Purpose: Processes ath9k DFS/radar PHY error payloads, filters false radar pulses, detects chirping signatures, feeds the DFS pattern detector, and reports radar to mac80211.

Important APIs/functions: Public API is `ath9k_dfs_process_phyerr()`. Internal helpers parse FFT max bins for chirp detection (`ath9k_check_chirping()`), convert hardware duration units to microseconds, postprocess bandwidth/RSSI/duration into `struct pulse_event`, and call the `dfs_pattern_detector`.

Control flow: RX code calls `ath9k_dfs_process_phyerr()` for PHY errors. Non-radar PHY errors, zero data length, invalid bandwidth info, and unusable RSSI are counted and discarded. The last three bytes of the payload provide pulse BW info and primary/extension durations. RSSI is sanitized from signed 8-bit hardware values. Primary, extension, or dual-channel events choose the correct duration and RSSI. Width is converted to usec; pulses in chirp-width range are checked against a sequence of FFT max-bin deltas. Accepted pulses are sent to the pattern detector for the primary channel and, in HT40 extension cases, again for the extension frequency offset by +/-20 MHz. Detector matches call `ieee80211_radar_detected()`.

State/persistence: Uses `sc->dfs_detector`, `sc->dfs_prev_pulse_ts`, `sc->debug.stats.dfs_stats`, `ah->curchan`, and current channel flags. No allocation occurs in this file.

Dependencies/integration: Depends on `dfs_pattern_detector`, mac80211 radar notification, ath RX status, channel helpers, `dfs_debug.h` counters, and hardware-specific DFS payload layout.

Risks: DFS correctness is regulatory-sensitive. Payload parsing assumes at least three trailer bytes after nonzero `rs_datalen`; malformed shorter packets would be risky. Chirp detection tolerances and HT40 primary/extension swaps affect false positives/negatives. DFS and spectral share PHY error reports.

Test signals: Radar PHY errors for primary, extension, and dual-channel pulses; signed RSSI discard cases; invalid BW info and zero length; chirp and non-chirp FCC pulse patterns; HT40 plus/minus frequency mapping; detector match leading to mac80211 radar notification.
