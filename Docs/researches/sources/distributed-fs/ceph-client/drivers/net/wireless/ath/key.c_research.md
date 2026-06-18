<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/key.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/key.c

Purpose: Implements shared ath hardware key-cache programming, key slot reservation, TKIP MIC layout handling, and key deletion.

Important APIs/types/functions: Exports `ath_hw_keyreset()`, `ath_hw_keysetmac()`, `ath_key_config()`, and `ath_key_delete()`. Core internals are `ath_hw_set_keycache_entry()`, `ath_setkey_tkip()`, `ath_reserve_key_cache_slot_tkip()`, and `ath_reserve_key_cache_slot()`.

Control flow: `ath_key_config()` translates mac80211 cipher/key metadata into `ath_keyval`, chooses a MAC binding and key-cache index based on pairwise/group mode and vif type, programs WEP/TKIP/CCMP/clear entries, then marks key bitmaps. TKIP programming handles combined MIC hardware or split MIC layouts, writing an inverted partial key first and the real key last to avoid transient MIC errors. Deletion clears MAC binding for CCMP/TKIP keys that might still be referenced by queued frames, otherwise resets key registers, then clears key maps.

State and persistence: Writes hardware key-table registers and mutates `keymap`, `ccmp_keymap`, and `tkip_keymap`. State is hardware/driver runtime only.

Dependencies and integration points: Depends on mac80211 key flags, nl80211 cipher suites, ath register ops, key-table addresses from `reg.h`, and `ath_common` crypt capability flags.

Risks and test signals: Risks include index arithmetic for TKIP companion slots, allocation exhaustion, stale key entries for queued encrypted frames, multicast/unicast MAC matching mistakes, and unsupported cipher handling. Test signals are WEP/TKIP/CCMP association, AP group keys, IBSS per-station group keys, key rekey under traffic, and key-cache bitmap consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/key.c -->
