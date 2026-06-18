# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mld-sta.c

## Purpose
Implements MLD firmware station management for iwlwifi MVM. It handles firmware station ids for peer links and internal stations, sends `STA_CONFIG_CMD`, removes stations with `STA_REMOVE_CMD`, creates and destroys TVQM queues, allocates per-link `iwl_mvm_link_sta` objects, restores station state after restart, and provides MLD variants of broadcast, multicast, sniffer, auxiliary, peer add/update/remove, and TX disable helpers.

## Important APIs, Types, And Functions
`iwl_mvm_sta_fw_id_mask()` returns a station mask for key and queue commands. `iwl_mvm_mld_send_sta_cmd()` submits versioned `STA_CONFIG_CMD`. Internal station helpers include `iwl_mvm_mld_add_int_sta_with_queue()`, `iwl_mvm_mld_add_bcast_sta()`, `iwl_mvm_mld_add_mcast_sta()`, `iwl_mvm_mld_add_snif_sta()`, `iwl_mvm_mld_add_aux_sta()`, and matching remove functions. Peer station helpers include `iwl_mvm_mld_alloc_sta_links()`, `iwl_mvm_mld_cfg_sta()`, `iwl_mvm_mld_add_sta()`, `iwl_mvm_mld_update_sta()`, `iwl_mvm_mld_rm_sta()`, and `iwl_mvm_mld_rm_sta_id()`. TX disable APIs are `iwl_mvm_mld_sta_modify_disable_tx()`, `iwl_mvm_mld_sta_modify_disable_tx_ap()`, and `iwl_mvm_mld_modify_all_sta_disable_tx()`.

## Control Flow
Internal station add allocates a driver station id, sends either `AUX_STA_CMD` or `STA_CONFIG_CMD`, then enables a TVQM queue because newer firmware requires stations to exist before queues. On queue-enable failure it removes the firmware station and deallocates driver state. Removal optionally flushes the station, removes the scheduler queue through `SCD_QUEUE_CONFIG_CMD` when required, frees the transport queue, sends `STA_REMOVE_CMD`, and deallocates the internal station.

Peer station add allocates one `iwl_mvm_link_sta` and firmware id per active mac80211 link unless in hardware restart. It initializes common station data with `iwl_mvm_sta_init()`, updates station data, then sends `STA_CONFIG_CMD` for every active link with MLD address, link address, link id, station type, AID, MFP, MIMO/SMPS, A-MPDU density/size, UAPSD, HE packet extension, HTC flags, ACK support, and trigger random allocation. In station-vif mode it records each link's AP station id. Error handling removes firmware stations already added and frees all allocated link objects.

Restart recovery uses `iwl_mvm_alloc_sta_after_restart()` to reconfigure existing link station ids and restore RCU mappings before reallocating queues. Peer removal flushes all active link tids, waits for queues to empty, disables all station queues, calls common station deletion, removes firmware station ids per link, and frees link objects. Removing by id is a lower-level path used when the caller already knows the firmware id.

## State And Persistence
The file owns per-link station mappings: `mvm_sta->link[link_id]`, `mvm->fw_id_to_mac_id[sta_id]`, and `mvm->fw_id_to_link_sta[sta_id]`. It persists internal station ids and queues in vif link state (`bcast_sta`, `mcast_sta`, `mgmt_queue`, `cab_queue`), global MVM state (`aux_sta`, `aux_queue`, `snif_sta`, `snif_queue`, `p2p_dev_queue`), and per-station TID queue ids. Firmware state persists station contexts and queues until explicit removal or restart. `ap_sta_id` in each vif link points to the peer station id used for station-mode AP link operations.

## Dependencies And Integration Points
Depends on mac80211 MLO active-link iteration, MVM station structures in `sta.h`, time-sync indirectly, TVQM queue helpers, transport queue free, firmware `STA_CONFIG_CMD`, `STA_REMOVE_CMD`, `AUX_STA_CMD`, `SCD_QUEUE_CONFIG_CMD`, common rate/AMPDU/HE helpers from `mac80211.c`, and key targeting from `mld-key.c`. It is used by `mld-mac80211.c` station-state, AP/IBSS, monitor, P2P ROC, and CSA/TX-blocking flows.

## Risks
Although `iwl_mvm_sta_fw_id_mask()` accepts a `filter_link_id`, this implementation currently returns only `mvmsta->deflink.sta_id`, so multi-link key/queue mask behavior depends on current firmware expectations and may need expansion. Allocation and RCU publication must stay paired; partially added multi-link stations are carefully unwound, but failures during later per-link removal return only the last remove result. Queue removal ordering is firmware-sensitive, and `sta_remove_requires_queue_remove` changes behavior. Restart recovery assumes old link station ids remain meaningful enough to rebuild firmware and queue state. TX disable helpers use async commands and iterate global station id arrays, so stale mappings would affect unrelated vifs.

## Test Signals
Create/remove MLD peer stations with one and multiple active links, AP and station roles, TDLS rejection paths through common state, restart recovery with queue reallocation, AP/GO bcast/mcast station lifetimes, monitor sniffer station lifetime, P2P/HS20 auxiliary station ROC, queue removal with and without `sta_remove_requires_queue_remove`, and CSA TX disable/enable. Watch firmware logs for `STA_CONFIG_CMD`, `STA_REMOVE_CMD`, queue config errors, empty-queue waits, and RCU/lockdep reports around station removal.
