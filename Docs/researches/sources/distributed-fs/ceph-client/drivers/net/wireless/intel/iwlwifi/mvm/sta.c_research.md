# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/sta.c

## Purpose

`sta.c` is the non-MLD iwlwifi MVM station-management implementation. It owns the host-side representation of mac80211 stations in firmware station IDs, sends `ADD_STA`, `REMOVE_STA`, `ADD_STA_KEY`, BAID, SCD queue, and channel-switch related commands, and maintains the driver state needed by TX/RX fast paths. It bridges mac80211 station lifecycle callbacks to firmware station table entries and also manages internal stations used for auxiliary scan/ROC, sniffer, broadcast, and multicast traffic.

The file also implements Dynamic Queue Allocation for older TX APIs and TVQM queue allocation for newer TX APIs. Its queue logic decides when a station/TID gets a dedicated queue, when queues are shared, how inactive queues are reclaimed, and how queues are restored after firmware restart.

## Important APIs, types, and functions

Key public station lifecycle APIs are `iwl_mvm_find_free_sta_id()`, `iwl_mvm_sta_init()`, `iwl_mvm_add_sta()`, `iwl_mvm_sta_send_to_fw()`, `iwl_mvm_rm_sta()`, `iwl_mvm_rm_sta_id()`, and `iwl_mvm_sta_del()`. Firmware station table state is tracked through `mvm->fw_id_to_mac_id[]`, with normal stations stored as RCU pointers and internal stations represented by `ERR_PTR(-EINVAL)`.

Queue APIs include `iwl_mvm_sta_ensure_queue()`, `iwl_mvm_add_new_dqa_stream_wk()`, `iwl_mvm_tvqm_enable_txq()`, and `iwl_mvm_realloc_queues_after_restart()`. Legacy DQA helpers include `iwl_mvm_find_free_queue()`, `iwl_mvm_sta_alloc_queue()`, `iwl_mvm_get_shared_queue()`, `iwl_mvm_redirect_queue()`, `iwl_mvm_remove_inactive_tids()`, and `iwl_mvm_inactivity_check()`.

Aggregation and reorder handling is centered on `iwl_mvm_sta_rx_agg()`, `iwl_mvm_sta_tx_agg_start()`, `iwl_mvm_sta_tx_agg_oper()`, `iwl_mvm_sta_tx_agg_stop()`, `iwl_mvm_sta_tx_agg_flush()`, `iwl_mvm_fw_baid_op()`, and the RX reorder buffer helpers. Key installation/removal is handled by `iwl_mvm_set_sta_key()`, `iwl_mvm_remove_sta_key()`, `iwl_mvm_update_tkip_key()`, `iwl_mvm_send_sta_key()`, and `iwl_mvm_send_sta_igtk()`.

Power-save and traffic-blocking helpers include `iwl_mvm_sta_modify_ps_wake()`, `iwl_mvm_sta_modify_sleep_tx_count()`, `iwl_mvm_rx_eosp_notif()`, `iwl_mvm_sta_modify_disable_tx_ap()`, `iwl_mvm_modify_all_sta_disable_tx()`, and `iwl_mvm_csa_client_absent()`.

## Control flow

Adding a station starts with station ID allocation unless firmware restart is in progress, in which case the previous ID is reused. `iwl_mvm_sta_init()` initializes the embedded `struct iwl_mvm_sta`, per-TID queue state, duplicate RX data, rate-scaling state, and legacy queue reservation. `iwl_mvm_sta_send_to_fw()` builds the firmware `ADD_STA` command from mac80211 capabilities: bandwidth, RX NSS, SMPS mode, aggregation density/size, AID, U-APSD ACs, station type, and legacy queue mask. After successful firmware addition, the station is published in `fw_id_to_mac_id[]` under RCU.

Removing a station drains firmware traffic, flushes the station queues, waits for queues to empty, clears drain state, disables per-TID TX queues, releases reserved queue state, runs common AP/TDLS cleanup in `iwl_mvm_sta_del()`, sends `REMOVE_STA`, and clears the RCU map. Internal stations follow the same firmware commands but use `iwl_mvm_int_sta` and fixed queues for aux/sniffer/broadcast/multicast roles.

Legacy DQA queue allocation first tries management queues for management TID, then reserved station queues, then free data queues, then inactive queue reclamation, and finally shared queues. Shared queues disable aggregation for active TIDs on that queue and may redirect the scheduler FIFO to the lowest-priority AC represented. Inactive cleanup scans all queue TIDs, skips queues with queued frames or active BA state, unshares single-TID queues, and changes queue ownership if the owner TID was removed.

TX aggregation starts by reserving or validating a queue, recording SSN, and returning whether mac80211 can send ADDBA immediately or must wait for the queue to empty. Operational start marks `IWL_AGG_ON`, configures SCD aggregation window where supported, enables firmware aggregation through `ADD_STA`, and updates rate-scaling aggregation limits. Stop/flush paths clear state, notify mac80211, drain/flush hardware queues when needed, and disable firmware aggregation.

RX aggregation allocates firmware BAID sessions. On new RX APIs it allocates per-RXQ reorder buffers, initializes timers, stores BAID data in `mvm->baid_map[]` under RCU, and synchronizes RX queues before removal. A session timer calls mac80211 BA timeout handling if firmware traffic has not refreshed `last_rx`.

Key setup selects station ID from a station, AP station, or AP multicast station, assigns or reuses firmware key offsets, formats cipher-specific flags and PN state, and sends `ADD_STA_KEY` or `MGMT_MCAST_KEY`. Removal clears the key table, updates LRU-like deletion counters, and sends invalidation commands. TKIP update can send an asynchronous updated phase-1 key.

## State and persistence

Persistent driver state includes `mvm->fw_id_to_mac_id[]`, `mvm->queue_info[]`, `mvm->tvqm_info[]`, `mvm->fw_key_table`, `mvm->fw_key_deleted[]`, `mvm->rx_ba_sessions`, `mvm->baid_map[]`, and status bits for restart/CSA. Per-station state lives in `struct iwl_mvm_sta`: firmware station ID, MAC context color, queue mask, reserved queue, per-TID sequence/reclaim/aggregation data, TID-to-BAID map, key PN storage, duplicate detection state, sleep state, TX-disable state, and rate-scaling data.

Queue and aggregation state persists across firmware restart by reusing station IDs and re-enabling queues with `iwl_mvm_realloc_queues_after_restart()`. New TX API queues are reallocated by transport, while legacy DQA queues are re-enabled with the saved TXQ IDs. Some counters, especially sequence tracking on gen2, are intentionally reset or masked to match firmware behavior.

## Dependencies and integration points

This file depends on mac80211 station/TXQ/key/BA APIs, firmware command structures from `fw-api.h`, transport TXQ primitives, rate scaling, RCU synchronization, the MVM mutex, per-station spinlocks, notification synchronization, and MLD equivalents for paths delegated when `mvm->mld_api_is_used` is true. It is called from station state transitions, TX path queue activation, TX reclaim/BA notifications, RX reorder handling, AP power-save hooks, TDLS/CSA handling, and key configuration callbacks.

## Risks

The highest risk is state skew between mac80211, driver maps, transport queues, and firmware station table entries. Queue reuse is especially delicate: stale `txq_id`, missing `synchronize_net()`, incorrect shared-queue ownership, or incomplete aggregation disabling can cause frames to be sent to freed or misconfigured queues. Firmware API version gates are also risk-heavy because the file supports old SCD/DQA, new TX API/TVQM, old and new RX BAID APIs, station API variants, and key-command versions.

Security-sensitive risks include incorrect PN conversion, key slot reuse, multicast/pairwise selection, TKIP MIC handling, and invalid station lookup during GTK/IGTK removal. RX reorder data is freed under RCU and synchronized RX queue notifications; bugs there can produce use-after-free or leaked buffered frames. Restart paths intentionally skip some firmware removals, so they must keep local state consistent enough for mac80211 reconfiguration.

## Test signals

Useful signals include KUnit or mock firmware command tests for ADD/REMOVE station command contents, queue allocation/reclaim/share cases, restart reallocation, BAID allocation/removal, key slot LRU behavior, and PN formatting. Runtime validation should exercise AP/client/TDLS/internal stations, firmware restart, queue exhaustion, aggregation start/stop/flush, RX BA timeout, U-APSD EOSP, CSA absent handling, WEP/TKIP/CCMP/GCMP/IGTK keys, and both legacy and new TX/RX firmware APIs.
