# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wow.c

## Purpose
`wow.c` implements ath10k wake-on-wireless support for mac80211 suspend/resume. It advertises supported WoWLAN triggers, programs per-vdev wake events and packet patterns through WMI, configures network-list-offload/PNO scans for net-detect wakeups, coordinates target suspend/wakeup completions, and bridges device wakeup capability to the Linux device power-management core.

## Important APIs, Types, and Functions
- `ath10k_wowlan_support` is the base `struct wiphy_wowlan_support`. It advertises disconnect and magic-packet wakeups, pattern limits from `wmi.h`, and a maximum packet offset. `ath10k_wow_init()` later augments it for net-detect and adjusts limits for native Wi-Fi decap.
- `ath10k_wow_vif_cleanup()` disables every `WOW_EVENT_MAX` wake event for a vdev and deletes all configured firmware patterns from `0` to `ar->wow.max_num_patterns - 1`.
- `ath10k_wow_cleanup()` applies that per-vdev cleanup across `ar->arvifs` while `ar->conf_mutex` is held.
- `ath10k_wow_convert_8023_to_80211()` rewrites cfg80211 Ethernet-style packet patterns into 802.11 + RFC1042 positions for firmware running in native Wi-Fi RX decapsulation mode.
- `ath10k_wmi_pno_check()` validates and converts `struct cfg80211_sched_scan_request` into `struct wmi_pno_scan_req`, including SSIDs, channels, RSSI thresholds, scan plans, passive/active behavior, hidden-network marking, random MAC parameters, delay, and dwell times.
- `ath10k_vif_wow_set_wakeups()` chooses wake events based on vdev type and requested `struct cfg80211_wowlan`, programs PNO if requested, converts and installs packet patterns, and enables the final event mask through WMI.
- `ath10k_wow_set_wakeups()` loops over all ath10k vifs and applies the requested wakeups.
- `ath10k_vif_wow_clean_nlo()` and `ath10k_wow_nlo_cleanup()` disable firmware PNO after resume when NLO had been enabled.
- `ath10k_wow_enable()` sends `ath10k_wmi_wow_enable()` and waits up to `3 * HZ` for `ar->target_suspend`.
- `ath10k_wow_wakeup()` sends `ath10k_wmi_wow_host_wakeup_ind()` and waits up to `3 * HZ` for `ar->wow.wakeup_completed`.
- `ath10k_wow_op_suspend()`, `ath10k_wow_op_resume()`, and `ath10k_wow_op_set_wakeup()` are the mac80211 PM operation entry points declared in `wow.h`.
- `ath10k_wow_init()` validates firmware/service support, publishes `ar->hw->wiphy->wowlan`, and marks the device wakeup-capable.

## Control Flow
Suspend starts in `ath10k_wow_op_suspend()`. The function locks `ar->conf_mutex`, verifies `ATH10K_FW_FEATURE_WOWLAN_SUPPORT`, clears stale wake events/patterns, programs new wakeups from the mac80211 `wowlan` request, waits for TX completion, enables firmware WoW, and finally suspends HIF. Failure after wakeup programming runs cleanup; failure after firmware WoW enable also sends a wakeup indication before cleanup. The mac80211 suspend callback returns `0` on success and `1` for most failures, matching this driver's PM callback convention.

Wakeup programming is vdev-aware. AP vdevs wake on deauth/disassoc/probe/auth/assoc/HTT/RA-match events; IBSS additionally wakes on beacon events; STA vdevs wake on disconnect-related events when requested, magic packets when requested, PNO detection when net-detect is requested, and packet-pattern matches when patterns are supplied. Once the bitmap is built, each selected WMI wake event is enabled individually.

Pattern handling first converts cfg80211's packed bitmask into a byte mask. If firmware is in `ATH10K_HW_TXRX_NATIVE_WIFI` decap mode, Ethernet patterns below the Ethernet header length are transformed into 802.11 header/SNAP positions; patterns after the Ethernet header are shifted by `WOW_HDR_LEN - ETH_HLEN`. Converted patterns are bounded by `WOW_MAX_PATTERN_SIZE` and installed with incremental pattern IDs.

Resume starts in `ath10k_wow_op_resume()`. It resumes HIF, sends the firmware host-wakeup indication, disables NLO if it had been enabled, and if an error remains, either moves an ON device to `ATH10K_STATE_RESTARTING` or reports an unrecoverable state error.

## State and Persistence Behavior
The file mutates `ar->wow.wowlan_support`, `ar->hw->wiphy->wowlan`, `ar->nlo_enabled`, device wakeup capability/enabled state, firmware wake-event state, firmware pattern tables, firmware PNO configuration, and suspend/wakeup completions. Firmware-side state is intentionally cleaned before suspend programming and cleaned/disabled again on errors or resume. There is no disk persistence; the state is runtime PM and firmware state.

`ar->conf_mutex` is asserted or held across all multi-step hardware state transitions. `ar->target_suspend` and `ar->wow.wakeup_completed` completions are reinitialized before waiting, avoiding stale completions from prior suspend/resume cycles.

## Dependencies and Integration Points
`wow.c` integrates with mac80211/cfg80211 through `struct ieee80211_hw`, `struct cfg80211_wowlan`, `struct cfg80211_pkt_pattern`, and scheduled-scan requests. It integrates with firmware through WMI helpers from `wmi-ops.h` and WMI constants/types from `wmi.h`, including WoW wake events, PNO limits, and pattern-size limits. It integrates with HIF for bus suspend/resume, with ath10k MAC code for TX drain, and with Linux PM through `device_set_wakeup_capable()` and `device_set_wakeup_enable()`.

## Risks and Edge Cases
- PNO programming sets `ar->nlo_enabled = true` before validating and successfully configuring the PNO request. If validation fails, no NLO wake event is added, but resume cleanup may still attempt to disable NLO.
- `ath10k_vif_wow_set_wakeups()` does not propagate an error from `ath10k_wmi_wow_config_pno()` because the return value is not assigned around that call. A PNO configuration failure could leave net-detect silently disabled.
- Pattern conversion assumes the old pattern buffer is valid for `ETH_HLEN - old->pkt_offset` when `pkt_offset < ETH_HLEN`; cfg80211 limits and earlier checks are important for avoiding malformed offsets.
- Patterns larger than `WOW_MAX_PATTERN_SIZE` are skipped rather than failing the suspend request, which can surprise users if they expected all patterns to be armed.
- Every vdev receives the same `wowlan` request, so multi-vdev configurations rely on vdev-type filtering rather than per-interface wake policy.
- Suspend and resume depend on firmware completion events arriving within three seconds. Missing completions force PM failure or device restart.

## Test Signals
Relevant test signals include `iw phy` WoWLAN capability reporting, successful suspend/resume with magic-packet wake, disconnect wake, pattern wake, and net-detect wake; logs for `failed to issue wow`, `failed to add pattern`, timeout messages, and NLO cleanup failures; confirmation that HIF suspend/resume pairs are balanced; and suspend/resume behavior in native Wi-Fi decap mode where pattern offsets are reduced by `WOW_MAX_REDUCE`. Firmware/service combinations without `ATH10K_FW_FEATURE_WOWLAN_SUPPORT`, `WMI_SERVICE_WOW`, or `WMI_SERVICE_NLO` should be tested for graceful feature suppression.
