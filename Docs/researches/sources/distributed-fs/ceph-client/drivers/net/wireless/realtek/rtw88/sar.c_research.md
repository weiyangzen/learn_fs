## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sar.c

Purpose: implements cfg80211 SAR power-limit support for rtw88. It converts userspace/regulatory SAR power specs into per-RF-path/per-rate-section power offsets used by PHY TX power programming.

Important APIs/functions: `rtw_query_sar()` returns the active SAR limit for a path/rate/band argument or the chip maximum when no SAR source is active. `rtw_set_sar_specs()` validates `NL80211_SAR_TYPE_POWER`, converts each cfg80211 frequency-range sub-spec through `rtw_sar_to_phy()`, and applies it via `rtw_apply_sar()`. `rtw_sar_capa` exposes four common frequency ranges.

Control flow: a cfg80211 SAR request is expanded across all `RTW_RF_PATH_MAX` paths and `RTW_RATE_SECTION_NUM` rate sections. The conversion accounts for cfg80211's 0.25 dBm factor, chip TX gain index factor, chip max power index, and current base power tables before reprogramming TX power for the current channel.

State and persistence: mutates `rtwdev->hal.sar`, including source and per-path/rate/common-band arrays. Source locking prevents replacing an active non-`NONE` source with a different source.

Dependencies and integration: depends on `phy.h` for `rtw_phy_set_tx_power_level()` and base tables in `hal`. Integrated with cfg80211 SAR capability advertisement.

Risks and test signals: risks include unit conversion mistakes, invalid band index handling, and source contention returning `-EBUSY`. Test with cfg80211 SAR commands, inspect power table changes per band, and verify regulatory power limits with RF measurements.
