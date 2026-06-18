# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/coex.c

## Purpose

Implements Bluetooth/Wi-Fi coexistence policy for MVM: firmware BT configuration, BT profile notification handling, primary/secondary 2.4 GHz CI mask selection, SMPS constraints, reduced TX power, RSSI event handling, aggregation/MIMO/antenna/TPC decisions, and TX priority hints.

## Important APIs, Types, and Functions

`iwl_mvm_send_bt_init_conf()` sends `BT_CONFIG`. `iwl_mvm_rx_bt_coex_old_notif()` stores notifications and recalculates policy. `iwl_mvm_bt_coex_notif_handle()` iterates VIFs/links and sends changed `BT_COEX_CI` commands. `iwl_mvm_bt_notif_per_link()` applies per-link SMPS, primary/secondary selection, RSSI thresholds, and reduced TX power. Policy helpers include `iwl_mvm_coex_agg_time_limit()`, `iwl_mvm_bt_coex_is_mimo_allowed()`, `iwl_mvm_bt_coex_is_ant_avail()`, `iwl_mvm_bt_coex_is_tpc_allowed()`, `iwl_mvm_bt_coex_get_single_ant_msk()`, and `iwl_mvm_bt_coex_tx_prio()`.

## Control Flow

Initialization sends forced BT/Wi-Fi antenna mode if configured, otherwise enables normal coexistence modules. Notifications update `last_bt_notif`, iterate station/AP links, clear constraints off 2.4 GHz, derive SMPS from BT activity, prefer low-latency links as primary, choose AP/STA primary and secondary channel contexts, optionally swap by TCM load, compute CI masks from channel/width, and send `BT_COEX_CI` only when changed. RSSI events flip reduced TX power unless BT is off or coexistence is loose.

## State and Persistence Behavior

Updates `mvm->last_bt_notif`, `mvm->last_bt_ci_cmd`, `bt_coex_last_tcm_ts`, per-station `bt_reduced_txpower`, and per-link beacon-filter RSSI thresholds.

## Dependencies and Integration Points

Depends on firmware coexistence APIs, mac80211 channel contexts and SMPS, MVM VIF/link/STA/PHY/TCM state, beacon-filter RSSI events, rate-control policy, and antenna helpers.

## Risks

Rate-control lookups are intentionally racy and may briefly use stale LUT data. CI mask table indexing assumes valid 2.4 GHz channel values. Device-family gates skip reduced TX power on AX210+. Primary/secondary logic assumes at most two relevant 2.4 GHz contexts and has FIXME notes for MLD load granularity.

## Test Signals

Validate BT activity levels, 2.4 vs 5/6 GHz operation, AP+STA concurrency, low-latency preference, TCM load swaps, RSSI events, forced antenna modes, AX210 and older devices, LUT variants, and rate-control helper outcomes.
