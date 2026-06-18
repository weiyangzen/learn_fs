## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sar.h

Purpose: public SAR interface for rtw88. It defines the power-unit conversion factor and the argument structure used to query per-rate/per-path SAR limits.

Important APIs/types: `RTW_COMMON_SAR_FCT` documents cfg80211 `NL80211_SAR_TYPE_POWER` units as 2 fractional bits. `struct rtw_sar_arg` contains `sar_band`, `path`, and `rs` rate-section indexes. The header declares `rtw_sar_capa`, `rtw_query_sar()`, and `rtw_set_sar_specs()`.

Control flow and state: no runtime flow. The state contract is that callers supply indexes matching rtw88 SAR band/rate/path enums and receive an s8 PHY power adjustment.

Dependencies and integration: includes `main.h` for core rtw88 types and is consumed by regulatory/cfg80211 setup and PHY TX power calculation code.

Risks and test signals: the main risk is caller/index mismatch because the struct is compact and unvalidated at query time beyond source handling. Build coverage plus exercising cfg80211 SAR set/query paths and verifying `rtw_sar_capa` range count are the primary signals.
