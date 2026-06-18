# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/key.c

Purpose: Translates mac80211 key operations into firmware `SEC_KEY_CMD` add, remove, and modify operations. It computes firmware key flags and station masks for pairwise, group, AP, STA, MLO, IGTK, and BIGTK cases.

Important APIs/types/functions: `iwl_mld_add_key()`, `iwl_mld_remove_key()`, `iwl_mld_update_sta_keys()`, `iwl_mld_remove_ap_keys()`, `iwl_mld_track_bigtk()`, `iwl_mld_beacon_protection_enabled()`, plus internal helpers `iwl_mld_get_key_flags()`, `iwl_mld_get_key_sta_mask()`, `iwl_mld_add_key_to_fw()`, and `iwl_mld_remove_key_from_fw()`.

Control flow: Add/remove computes a station mask and key flags, handles IGTK replacement limits, sends `SEC_KEY_CMD` add/remove unless resuming from WoWLAN, updates `key->hw_key_idx`, and tracks IGTK/BIGTK pointers in the link. AP group keys target internal multicast/broadcast stations depending on key index; STA group keys use the AP STA. Per-link keys use a single link station ID, while non-link pairwise keys use the full station mask. Station mask changes send firmware MODIFY commands for pairwise keys when station links change.

State/persistence: Tracks one firmware-installed IGTK per link (`mld_link->igtk`), two BIGTK pointers per STA link, global `mld->num_igtks`, and mac80211 `key->hw_key_idx` as the indicator that a key is in firmware. During WoWLAN resume, firmware is assumed to have already handled rekey state.

Dependencies/integration: Depends on mac80211 key/cipher structures, MLD VIF/link/STA mappings, internal AP broadcast/multicast station allocation, and the datapath firmware key API.

Risks: Returning zero station mask drops or rejects operations; missing internal AP STAs prevent AP group key installation. Firmware supports fewer concurrent IGTKs than mac80211 can expose, requiring replacement logic. TKIP MIC key offsets must match nl80211 layout. Resume shortcuts assume firmware key state is authoritative after WoWLAN.

Test signals: Tests should cover station mask computation for AP group, STA group, pairwise MLO, and link-specific keys; IGTK replacement and max-count behavior; BIGTK tracking; WoWLAN resume no-op behavior; and pairwise key MODIFY during link station remapping.
