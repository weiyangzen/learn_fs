# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mld-mac80211.c

## Purpose
Provides the MLD-specific mac80211 operation table `iwl_mvm_mld_hw_ops`. It reuses many common callbacks from `mac80211.c` but replaces interface, link, station, channel-context, AP/IBSS, remain-on-channel, per-link BSS change, and QoS handling with link-aware firmware flows using MLD MAC/link/station commands.

## Important APIs, Types, And Functions
`iwl_mvm_mld_hw_ops` is the exported ops table. MLD-specific callbacks include `iwl_mvm_mld_mac_add_interface()`, `iwl_mvm_mld_mac_remove_interface()`, `iwl_mvm_mld_assign_vif_chanctx()`, `iwl_mvm_mld_unassign_vif_chanctx()`, `iwl_mvm_mld_switch_vif_chanctx()`, `iwl_mvm_mld_start_ap()`/`stop_ap()`, `iwl_mvm_mld_start_ibss()`/`stop_ibss()`, `iwl_mvm_mld_mac_sta_state()`, `iwl_mvm_mld_link_info_changed()`, `iwl_mvm_mld_vif_cfg_changed()`, `iwl_mvm_mld_mac_conf_tx()`, and `iwl_mvm_mld_roc()`. It also implements `iwl_mvm_send_ap_tx_power_constraint_cmd()` for 6 GHz AP/client TPE constraints and uses common operation callback structs for station-state, channel switching, and ROC.

## Control Flow
Interface add initializes `mvmvif`, allocates a MAC context id, publishes `vif_id_to_mac`, sends MLD MAC context ADD, disables beacon filtering, chooses beacon-filter ownership for a station vif, attaches deflink as link 0, adds the initial firmware link, updates power, adds TCM/debugfs/MEI state, and enables monitor FCS handling when relevant. Removal flushes P2P ROC state, removes TCM/debugfs/MEI state, updates power, removes or disables the firmware link, removes the MAC context, clears RCU mappings/probe response data, and clears monitor FCS state.

Channel assignment maps mac80211 chanctx private id to an MVM PHY context, sets the per-link `phy_ctxt`, sends a link update first with PHY context id, then activates the link if mac80211 marks it active. Station links also send 6 GHz AP TX power constraints, while monitor links add a sniffer station. Unassignment deactivates the firmware link, removes sniffer stations, optionally blocks AP TX during channel switch, and cleans the PHY pointer unless the switch flow intentionally keeps firmware state for CSA. The switch callback reuses the common swap/reassign code from `mac80211.c` with MLD assign/unassign functions.

AP/IBSS start sends TPE constraints for AP, beacon template, non-active link parameters, multicast station, broadcast station, common AP/IBSS state, P2P device MAC updates, coex updates, TDLS teardown for DCM, and FTM responder restart. Stop removes common AP/IBSS state, P2P updates, responder state, bcast/mcast stations, and power state. Station state transitions delegate to common `iwl_mvm_mac_sta_state_common()` but use MLD add/update/remove station and MAC context callbacks.

MLD separates per-link changes from per-vif changes. `link_info_changed` updates link active state during link switch, QoS, ERP slot/rates, HE/EHT/puncturing, MAC context, BSSID, common station BSS behavior, AP beacon templates, and TX power. `vif_cfg_changed` handles association-level state, statistics, periodic system stats for link selection, power, session protection, disassociation cleanup, multicast, SMPS workaround, and idle scan stop.

## State And Persistence
Persistent state spans per-vif `link[]` entries with firmware link ids, active flags, PHY contexts, queue parameters, bcast/mcast/sniffer stations, AP station ids, BSSID, and beacon stats. It updates `mvm->vif_id_to_mac`, `bf_allowed_vif`, `p2p_device_vif`, `monitor_on`, hardware FCS flag, CSME/MEI netdev state, and periodic statistics requests. Firmware state includes MAC contexts, link contexts, station contexts, TPE constraints, beacon templates, and internal stations. Restart flows rely on common counters and status bits from `mac80211.c` plus MLD station/link reallocation.

## Dependencies And Integration Points
Depends on the common mac80211 callbacks and helper APIs in `mac80211.c`, MLD MAC command helpers from `mld-mac.c`, station helpers from `mld-sta.c`, link helpers declared in `mvm.h`, firmware MAC/link/PHY/data-path commands, cfg80211/mac80211 MLO link APIs, FTM, scan, power, BT coexistence, MEI, debugfs, and time-event/ROC code.

## Risks
MLD correctness depends on keeping mac80211 active-link state, MVM per-link state, and firmware link context state synchronized. Error unwinds in interface add and AP start must remove MAC/link/beacon-filter state in the right order. Link switching deliberately keeps or clears PHY/link state depending on CSA mode, making regressions easy. Some code has FIXME notes for per-link FTM responder and misbehaving AP handling. Periodic statistics are enabled for associated MLD station operation and must be disabled on disassociation. Monitor mode toggles the shared RX_INCLUDES_FCS hardware flag and must be paired with removal.

## Test Signals
Test MLD station association with multiple links, link activation/deactivation, link switch/CSA, 6 GHz TPE constraints, HE/EHT QoS and puncturing updates, AP/GO start/stop, P2P device ROC, monitor mode, and firmware restart. Signals include correct `MAC_CONFIG_CMD`, link update, station config, bcast/mcast station add/remove, periodic statistics toggling, preserved beacon counters, and absence of stale `vif_id_to_mac` or link pointers under RCU diagnostics.
