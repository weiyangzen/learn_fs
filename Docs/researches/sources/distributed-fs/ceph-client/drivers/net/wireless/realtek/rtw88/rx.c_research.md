## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rx.c

Purpose: common rtw88 receive descriptor parsing, mac80211 RX status population, RX statistics accounting, RSSI/EVM/SNR update, and scan-time channel correction.

Important APIs/functions: `rtw_rx_stats()` accounts unicast data bytes globally and per VIF. `rtw_rx_query_rx_desc()` decodes `struct rtw_rx_desc`, identifies C2H packets, locates PHY status and 802.11 header, calls chip-specific `query_phy_status`, and fills `ieee80211_rx_status`. `rtw_update_rx_freq_from_ie()` corrects scan result channel/frequency from beacon/probe-response IEs when packet status has an invalid channel.

Control flow: HCI RX paths pass a descriptor pointer into `rtw_rx_query_rx_desc()`. For non-C2H frames it decodes length/error/encryption/rate/bandwidth/TSF, optionally parses PHY status, builds mac80211 rate/encoding/signal fields, updates address-matched PHY statistics, and leaves the caller to deliver the skb. Address matching iterates active VIFs by BSSID and destination/beacon rules.

State and persistence: updates `rtwdev->stats`, per-VIF stats, `dm_info` packet counters/EWMA metrics, station average RSSI, and `pkt_stat`/`rx_status` transient state. No durable storage is used.

Dependencies and integration: depends on mac80211/cfg80211 helpers, `fw.h` for scan-offload feature checks, `ps.h`, `debug.h`, `util.h` inline BSSID selection, and chip `query_phy_status`.

Risks and test signals: descriptor offset math is safety-critical for aggregated USB/SDIO packets. Rate-to-mac80211 mapping, scan channel correction, and C2H bypass are key risks. Test with RX under scan/offload, encrypted traffic, malformed descriptor fuzzing, and monitor RSSI/rate fields.
