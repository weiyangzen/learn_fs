# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/key.h

Purpose: Declares the MLD key-management API and provides the restart cleanup iterator that invalidates mac80211 key hardware indices.

Important APIs/types/functions: `iwl_mld_add_key()`, `iwl_mld_remove_key()`, `iwl_mld_remove_ap_keys()`, `iwl_mld_update_sta_keys()`, `iwl_mld_cleanup_keys_iter()`, `iwl_mld_track_bigtk()`, and `iwl_mld_beacon_protection_enabled()`.

Control flow: The inline cleanup iterator is called by VIF restart cleanup and marks each key as not present in hardware with `STA_KEY_IDX_INVALID`. The rest of the header exposes key add/remove/update hooks used mainly by mac80211 callback code and station/link lifecycle code.

State/persistence: No independent state is stored in the header. Its APIs mutate key hardware indices, link IGTK/BIGTK pointers, AP early keys, and firmware key table state in `key.c` callers.

Dependencies/integration: Includes `mld.h`, mac80211, and firmware STA definitions. It forms the boundary between `mac80211.c`, `iface.c`, AP code, and the key firmware command implementation.

Risks: Any cleanup path that forgets `iwl_mld_cleanup_keys_iter()` may leave mac80211 believing keys remain installed after restart. Callers must honor the invariant that key update operations happen with wiphy locking and valid VIF/STA/link mappings.

Test signals: Restart/recovery tests should ensure all keys have invalid hardware indices after VIF cleanup and that reconfiguration later reinstalls keys through the normal `set_key` path.
