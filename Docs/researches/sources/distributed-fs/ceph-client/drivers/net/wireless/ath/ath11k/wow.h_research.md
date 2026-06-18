# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/wow.h

## Purpose
`ath11k/wow.h` declares the ath11k WoW state container, retry/pattern constants, RFC1042 header layout used for native Wi-Fi pattern conversion, and public suspend/resume/wakeup helpers. It also provides no-op inline stubs when `CONFIG_PM` is disabled.

## Important APIs, Types, And Constants
- `struct ath11k_wow` stores `max_num_patterns`, `wakeup_completed`, and the per-device `wiphy_wowlan_support` advertised to cfg80211.
- `struct rfc1042_hdr` models the LLC/SNAP header inserted between the 802.11 header and Ethernet type during pattern conversion.
- `ATH11K_WOW_RETRY_NUM`, `ATH11K_WOW_RETRY_WAIT_MS`, and `ATH11K_WOW_PATTERNS` define firmware suspend retry behavior and default pattern capacity.
- Under `CONFIG_PM`, exported functions include `ath11k_wow_init()`, `ath11k_wow_op_suspend()`, `ath11k_wow_op_resume()`, `ath11k_wow_op_set_wakeup()`, `ath11k_wow_enable()`, and `ath11k_wow_wakeup()`.
- Without PM, initialization, enable, and wakeup become successful stubs so non-PM builds can compile callers without carrying suspend code.

## Control Flow And State Behavior
This header has no executable flow beyond compile-time selection. Its state definition is embedded in `struct ath11k` and initialized by `ath11k_wow_init()` in `wow.c`; `wakeup_completed` is completed by WMI event handling outside this file when firmware acknowledges wakeup.

## Dependencies And Integration Points
The declarations depend on ath11k core types, mac80211 `ieee80211_hw`, cfg80211 `cfg80211_wowlan`, Linux completions, and `wiphy_wowlan_support`. The header is included by WoW implementation and by ath11k core/MAC code that registers PM callbacks or performs firmware wake transitions.

## Risks And Edge Cases
- The stubs cover only init/enable/wakeup, not mac80211 operation callbacks, so callers must still gate suspend/resume callback use on PM support.
- `ATH11K_WOW_PATTERNS` must remain compatible with firmware pattern slots and `wow.c` cleanup loops.
- `struct rfc1042_hdr` is packed and part of offset arithmetic; changing it breaks native Wi-Fi WoW pattern conversion.

## Test Signals
Build with `CONFIG_PM=y` and `CONFIG_PM=n`, verify wiphy WoW registration only when firmware advertises service support, confirm completion initialization before wake waits, and exercise pattern conversion for RFC1042 header length assumptions.
