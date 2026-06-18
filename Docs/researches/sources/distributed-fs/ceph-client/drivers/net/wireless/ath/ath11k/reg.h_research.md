# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/reg.h

Purpose: Declares the ath11k regulatory API and firmware DFS-region/PHY-flag constants used to translate WMI regulatory information into Linux cfg80211 regdomains and firmware scan-channel lists.

Important APIs, types, and constants: `enum ath11k_dfs_region` maps firmware DFS domains such as FCC, ETSI, MKK, CN, KR, and undefined values. `ATH11K_REG_PHY_BITMAP_NO11AX` is a firmware PHY bitmap flag that maps to `NL80211_RRF_NO_HE`. Public functions initialize/free regulatory state, reset decoded regulatory info, handle regdomain and channel-list work, build regdomains, update cfg80211 regd, update firmware scan channel lists, convert 6 GHz AP power type, handle WMI channel-list events, and send country code updates.

Control flow: Core/MAC setup calls `ath11k_reg_init()` during wiphy registration. WMI event handling calls `ath11k_reg_handle_chan_list()` with decoded firmware regulatory info. Workqueue callbacks declared here apply cfg80211 updates and firmware channel-list updates. User regulatory hints eventually call `ath11k_reg_set_cc()` through the notifier in `reg.c`.

State and persistence behavior: The header owns no state, but its APIs manipulate per-radio/per-base regulatory domains, stored WMI regulatory info, DFS region state, channel update queues, and wiphy regulatory settings. These are runtime-only and freed by `ath11k_reg_free()`.

Dependencies and integration points: Includes Linux kernel and cfg80211 regulatory headers and forward-declares ath11k core types. It integrates WMI regulatory event decoding with cfg80211, mac80211, 11d scan control, and firmware scan-channel programming.

Risks and edge cases: DFS-region mappings must match firmware semantics and country compliance requirements. `ath11k_reg_build_regd()` callers must pass a valid `cur_regulatory_info` with owned rule arrays and a valid AP power/vdev type for 6 GHz rules. Workqueue callbacks must only be scheduled while the owning `ath11k` remains alive.

Test signals: Compile users after changing function signatures or enum values. Runtime validation should cover DFS region mapping, 6 GHz AP power conversion, country-code set, regulatory event handling, channel-list update work, and regulatory cleanup during device removal/recovery.
