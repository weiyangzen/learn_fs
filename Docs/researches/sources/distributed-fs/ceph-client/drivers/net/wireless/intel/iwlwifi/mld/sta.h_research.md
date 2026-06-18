# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/sta.h

Purpose: Defines driver-private MLD station data structures and declares peer/internal station lifecycle helpers used across TX, RX, key, aggregation, TLC, and MLO code.

Important APIs and types: Defines duplicate-detection data (`iwl_mld_rxq_dup_data`), per-link station state (`iwl_mld_link_sta`), PTK PN storage, per-link/per-queue MPDU counters, main `iwl_mld_sta`, and internal firmware-only station state (`iwl_mld_int_sta`). Provides dereference/iteration helpers, cleanup helpers, mac80211 private-data casts, and declarations for station add/remove/update, TXQ flush/wait, MPDU counting, internal station add/remove, and link-station updates.

Control flow and integration: `iwl_mld_cleanup_sta()` is an inline cleanup path that removes TXQ private state, validates active-link cleanup, clears FW ID maps, and frees non-default link STAs. The header’s helpers are used by RX duplicate/reorder code, stats/TLC notification handling, key management, aggregation, and interface cleanup.

State and persistence: The zeroed-on-restart groups in station structs separate firmware-runtime fields from state that survives restart. `fw_id` and pointer topology survive so reconfiguration can preserve firmware station identity.

Dependencies: Includes mac80211, MLD core, and TX private helpers. It relies on RCU and the wiphy mutex for safe link station lookup.

Risks: `iwl_mld_cleanup_sta()` assumes failed link removal should be exceptional; if active link state is wrong it warns and force-clears maps. `IWL_NUM_DEFAULT_KEYS` and PN queue sizing must match key code expectations. Callers must not dereference link STAs without the documented lock/RCU protection.

Test signals: Compile and runtime coverage from station lifecycle, RX duplicate detection, stats/TLC notification lookup, MLO link update, and KUnit cleanup scenarios.
