# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/nan.c

Purpose: implements NAN support for MLD devices: capability detection, start/modify/stop configuration, aux-station lifecycle, EMLSR blocking while NAN is active, and NAN firmware notification delivery to cfg80211.

Important APIs/functions: `iwl_mld_nan_supported()` checks firmware capability. `iwl_mld_start_nan()`, `iwl_mld_nan_change_config()`, and `iwl_mld_stop_nan()` are mac80211/cfg80211 operation callbacks. `iwl_mld_handle_nan_cluster_notif()` and `iwl_mld_handle_nan_dw_end_notif()` translate firmware events to cfg80211. Cancellation callbacks always return true because NAN notifications are keyed by object type rather than a unique id.

Control flow: start blocks EMLSR globally for NAN, adds the VIF aux station, builds a full `NAN_CFG_CMD`, and rolls back aux station plus EMLSR blocker on failure. Change ignores the `changes` mask because firmware expects a complete configuration. Stop sends remove, flushes aux-station TX queues, removes the aux station, cancels queued NAN async notifications, and unblocks EMLSR. Cluster notifications validate that a NAN wdev exists and is started before reporting cluster join. DW-end notifications validate state, flush aux queues, choose a placeholder next channel from band, and notify cfg80211.

State and persistence: uses `mld->nan_device_vif`, `mld_vif->aux_sta.sta_id`, firmware NAN config, and queued async notification state. It persists only in live driver/mac80211 structures.

Dependencies and integration: depends on `fw/api/mac-cfg.h` NAN command structures, `iwl_mld_add_aux_sta()`, `iwl_mld_remove_aux_sta()`, `iwl_mld_flush_link_sta_txqs()`, `iwl_mld_update_emlsr_block()`, notification cancellation from `notif.c`, and cfg80211 NAN reporting APIs.

Risks and test signals: extra NAN/vendor attributes are concatenated into one duplicated host-command buffer, so length handling and allocation failures matter. The DW-end channel selection is marked TODO and currently maps band to fixed example channels. Tests should cover start rollback, stop cancellation, missing `nan_device_vif`, invalid DW band, optional 5 GHz config, saturated scan/dwell values, and EMLSR blocker symmetry.
