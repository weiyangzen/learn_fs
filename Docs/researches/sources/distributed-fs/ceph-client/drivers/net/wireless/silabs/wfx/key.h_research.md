# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/key.h

Purpose: Declares the WFx mac80211 key callback.

Important APIs and types: Exports `wfx_set_key(struct ieee80211_hw *, enum set_key_cmd, struct ieee80211_vif *, struct ieee80211_sta *, struct ieee80211_key_conf *)`.

Control flow and integration: `main.c` installs this callback in `ieee80211_ops`; `key.c` implements firmware key-table programming and removal.

State and persistence: No state is declared here; implementation uses `wdev->key_map` and `key->hw_key_idx`.

Dependencies: Depends on mac80211 key abstractions.

Risks and test signals: Build tests should keep signature aligned with current mac80211 API; runtime tests should cover both SET_KEY and DISABLE_KEY callbacks.

Test signals: Source read size: 19 lines, 438 bytes.
