# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wow.h

## Purpose
`wow.h` declares the small ath10k per-device Wake-on-Wireless state container and the PM entry points implemented by `wow.c`. It also provides a no-op initializer when power management is not compiled in.

## Important APIs and Types
- `struct ath10k_wow` stores `max_num_patterns`, the `wakeup_completed` completion used by resume wakeup handshaking, and the `wiphy_wowlan_support` instance exported to cfg80211.
- Under `CONFIG_PM`, the header declares `ath10k_wow_init()`, `ath10k_wow_op_suspend()`, `ath10k_wow_op_resume()`, and `ath10k_wow_op_set_wakeup()`.
- Without `CONFIG_PM`, `ath10k_wow_init()` is a static inline stub returning `0`. The suspend/resume/set_wakeup operation declarations are not exposed in that build mode.

## Control Flow
The header participates in driver initialization by allowing common ath10k setup code to call `ath10k_wow_init()` unconditionally. In PM-enabled builds the real implementation initializes cfg80211 wake capabilities and device wakeup support; in non-PM builds the inline stub makes initialization a no-op. mac80211 operation tables can use the declared suspend/resume/set_wakeup functions only when PM code is built.

## State and Persistence Behavior
The only state defined here is in-memory per-device WoW state embedded in the larger `struct ath10k`. `max_num_patterns` comes from firmware/driver capability setup, `wakeup_completed` synchronizes firmware resume acknowledgement, and `wowlan_support` is copied or adjusted before being assigned to the wiphy. No state is persisted beyond the runtime device lifetime.

## Dependencies and Integration Points
The declarations depend on ath10k core type declarations, mac80211's `struct ieee80211_hw`, cfg80211's `struct cfg80211_wowlan`, kernel completions, and `struct wiphy_wowlan_support`. `wow.c`, `core.c`, and MAC operation setup are the primary consumers.

## Risks and Edge Cases
- Build guards must stay aligned with operation-table setup. Referencing suspend/resume symbols when `CONFIG_PM` is disabled would fail because only `ath10k_wow_init()` has a stub.
- `struct ath10k_wow` exposes mutable `wowlan_support`; callers should treat it as per-device data, not a global constant, because `wow.c` adjusts limits for native Wi-Fi decap and NLO support.
- Any change to `wakeup_completed` usage must preserve completion initialization and event signaling in the WMI event path.

## Test Signals
Build ath10k with and without `CONFIG_PM`. PM builds should expose WoWLAN capability when firmware supports it and should link suspend/resume callbacks. Non-PM builds should compile with the no-op init path and no unresolved WoW PM symbols.
