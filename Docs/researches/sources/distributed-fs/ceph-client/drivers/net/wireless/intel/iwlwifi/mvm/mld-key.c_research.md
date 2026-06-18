# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mld-key.c

## Purpose
Implements security key programming for the newer MLD firmware security command path. It translates mac80211 key configuration into `SEC_KEY_CMD` add/remove commands, chooses the firmware station mask that should own each key, builds firmware key flags for cipher, multicast, MFP, key size, and SPP A-MSDU, and handles AP-link/client-link group key corner cases.

## Important APIs, Types, And Functions
`iwl_mvm_get_sec_sta_mask()` selects target firmware station ids for pairwise, GTK, IGTK, BIGTK, AP, and station modes. `iwl_mvm_get_sec_flags()` converts `ieee80211_key_conf` cipher and flags to `IWL_SEC_KEY_FLAG_*` bits. `iwl_mvm_mld_send_key()` constructs the ADD flavor of `struct iwl_sec_key_cmd`, including WEP key offset quirks, TKIP MIC keys, TX PN, and duplicate WEP unicast/multicast programming. `iwl_mvm_sec_key_add()` is the public add helper used by `mac80211.c` when `SEC_KEY_CMD` exists. `iwl_mvm_sec_key_del()`, `iwl_mvm_sec_key_del_pasn()`, and private delete helpers send REMOVE commands. `iwl_mvm_sec_key_remove_ap()` iterates mac80211 keys to asynchronously remove AP group keys for a link.

## Control Flow
On key add, `__iwl_mvm_mac_set_key()` in `mac80211.c` calls `iwl_mvm_sec_key_add()` when firmware exposes `SEC_KEY_CMD`. The add path computes the station mask and flags, removes any old IGTK tracked on the same link, sends the add command, records the active IGTK pointer if relevant, and sets `hw_key_idx` to a non-invalid dummy value because this API does not allocate legacy hardware key indexes. Delete follows the same mask/flag computation, clears tracked IGTK state, sends remove, and sends a second WEP remove with toggled multicast flag when required. AP key removal during link teardown walks mac80211 keys and skips pairwise keys, already-invalid keys, and keys for other links.

## State And Persistence
The file persists little state directly. It updates per-link `mvmvif->link[link_id]->igtk` for active IGTK/BIGTK-like management protection keys and uses `keyconf->hw_key_idx` as a validity marker for mac80211/restart flows. The firmware stores actual key material and station-mask association. The add command seeds firmware TX PN from `keyconf->tx_pn`; RX PN tracking for pairwise data keys is still allocated by the common key path in `mac80211.c`.

## Dependencies And Integration Points
Depends on mac80211 key semantics, MVM vif/link/station mapping, `iwl_mvm_sta_fw_id_mask()` from `mld-sta.c`, firmware `SEC_KEY_CMD` structures in `fw/api/datapath.h`, and MVM command submission. It is selected by the common key callback in `mac80211.c` based on firmware command version, so old and new key APIs coexist.

## Risks
The target station mask is the highest-risk part: AP group keys must land on bcast or mcast internal stations by key index, client group keys may need the AP station without a mac80211 `sta`, and removal may happen after the AP station pointer has already been cleared. A zero station mask is rejected, so link teardown ordering can surface as key removal failures. IGTK pointer replacement is stateful and must stay synchronized with firmware deletion. WEP double-programming/removal can leave asymmetric state if the second command fails. Async AP key removal marks keys invalid after best-effort command submission, so firmware failure is not strongly recovered here.

## Test Signals
Exercise WPA2/WPA3 pairwise keys, GTK rekey, IGTK/BIGTK installation and replacement, beacon protection, AP group keys, station group keys with and without `sta`, PASN key delete, WEP compatibility, and link teardown after AP station removal. Firmware logs should show successful `SEC_KEY_CMD` add/remove; mac80211 should not repeatedly try to remove already-invalid keys. Restart tests should verify dummy `hw_key_idx` and IGTK tracking do not cause duplicate stale keys.
