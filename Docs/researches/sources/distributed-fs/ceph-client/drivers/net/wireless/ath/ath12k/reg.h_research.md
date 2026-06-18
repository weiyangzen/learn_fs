# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/reg.h

## Purpose

`reg.h` defines ath12k's regulatory data model and public regulatory APIs. It describes firmware-derived country/status values, regulatory rules, complete regulatory event information including 6 GHz AP/client matrices, PHY capability flags, validation status, and functions implemented in `reg.c`.

## Important APIs And Types

- Constants define regulatory update timeout and frequency boundaries separating 2 GHz and 5 GHz handling.
- `enum ath12k_dfs_region` maps firmware DFS domains; `enum ath12k_reg_cc_code` maps firmware country-setting status codes.
- `struct ath12k_reg_rule` is the compact firmware rule representation: start/end frequency, max bandwidth, power, antenna gain, flags, PSD state, and PSD EIRP.
- `struct ath12k_reg_info` owns parsed regulatory event state for one PHY, including 2/5 GHz rules, extended 6 GHz AP and client rules, bandwidth limits, domains, client type, AP usability flags, and PHY bitmap.
- `enum ath12k_reg_phy_bitmap` disables 11ax/11be when firmware marks them unavailable; `enum ath12k_reg_status` reports validate/drop/fallback.
- Function declarations cover init/free, regdomain building/updating, scan channel-list programming, reg-info reset/validation, event handling, and AP power conversion.

## Control Flow And Integration

WMI regulatory event parsers fill `ath12k_reg_info` and call validation/handling. `reg.c` builds cfg80211 `ieee80211_regdomain` objects from these structures, stores them on `ath12k_base`, and updates mac80211. MAC code calls channel-list and TPC helpers downstream of this regulatory state.

## State And Persistence

The struct contains many owned pointers to rule arrays; `ath12k_reg_reset_reg_info()` must free the 2/5 GHz pointers and all extended 6 GHz AP/client pointers. The state is transient per firmware event but may be cached as default/new regdomain state in `ath12k_base`.

## Risks And Test Signals

Risks are pointer ownership mistakes, matrix index mistakes for 6 GHz AP/client rules, and ABI drift with WMI regulatory events. Test signals include parser/build coverage for classic and extended regulatory events, 6 GHz LPI/SP/VLP behavior, no-11ax/no-11be flags, invalid pdev fallback/drop decisions, and cleanup under repeated country changes.
