# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/testmode.h

Purpose: Provides the public compile-time interface for ath10k nl80211 testmode support.

Important APIs and types: With `CONFIG_NL80211_TESTMODE`, declares `ath10k_testmode_destroy()`, `ath10k_tm_event_wmi()`, and `ath10k_tm_cmd()`. Without testmode, supplies inline no-op stubs returning no consumption or success.

Control flow, state, and persistence: The header owns no state. Its stubs let common call sites compile without ifdefs when testmode is disabled.

Dependencies and integration points: Includes `core.h` for ath10k/mac80211 types and is consumed by WMI event dispatch, cfg80211 testmode command registration, and teardown paths.

Risks: The disabled stub for `ath10k_tm_cmd()` returns success, so callers must ensure it is not exposed when cfg80211 testmode is unavailable. Prototype drift would break event consumption or command routing.

Test signals: Build both `CONFIG_NL80211_TESTMODE=y` and disabled configurations, verify WMI event paths do not consume events in disabled builds, and confirm cfg80211 testmode commands dispatch in enabled builds.
