<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/power.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/power.c

## Purpose
Builds and sends device and per-MAC power management commands, decides when power save and U-APSD are allowed, manages beacon filtering/beacon abort settings, responds to firmware U-APSD misbehaving AP notifications, and exposes debugfs-readable/overrideable power parameters.

## Important APIs, Types, And Functions
Public entry points are `iwl_mvm_power_update_device`, `iwl_mvm_power_update_mac`, `iwl_mvm_power_update_ps`, `iwl_mvm_power_vif_assoc`, `iwl_mvm_power_uapsd_misbehaving_ap_notif`, `iwl_mvm_power_mac_dbgfs_read`, `iwl_mvm_beacon_filter_debugfs_parameters`, `iwl_mvm_enable_beacon_filter`, and `iwl_mvm_disable_beacon_filter`. Key static helpers include `iwl_mvm_power_build_cmd`, `iwl_mvm_power_send_cmd`, `iwl_mvm_power_set_pm`, `iwl_mvm_power_set_ps`, `iwl_mvm_power_set_ba`, `iwl_mvm_power_configure_uapsd`, `iwl_mvm_power_allow_uapsd`, `iwl_mvm_power_config_skip_dtim`, and beacon-filter command helpers.

## Control Flow
Device power update sets global power-save flags from module power scheme, per-interface `ps_disabled`, debugfs overrides, external 32 kHz clock validity, and D3 no-sleep requirements. MAC power update gathers uploaded active vifs by role, disables PM on all, then selectively enables PM for standalone BSS/P2P, multi-channel client cases, or same-channel BSS+P2P without AP conflicts. It sends per-MAC power commands for BSS/P2P vifs, then updates beacon abort for BSS. Power command building always sets a keep-alive period at least 3 DTIMs and at least 25 seconds, then enables PS/PM only when global, mac80211, and MVM policy allow it. It selects default, short low-latency, or WoWLAN timeouts, optional low-power RX, DTIM skipping, U-APSD, snooze, and debugfs overrides.

Beacon filtering can only be enabled for the allowed non-P2P station vif with a DTIM period. CQM RSSI and debugfs parameters adjust the filter command. Misbehaving AP notifications find the vif whose link AP station ID matches firmware, store the AP address, and suppress U-APSD on reconnection.

## State And Persistence
Mutates `mvm->ps_disabled`, `mvmvif->pm_enabled`, `mvmvif->bf_enabled`, `mvmvif->ba_enabled`, `mvmvif->uapsd_misbehaving_ap_addr`, and debugfs `mac_pwr_cmd` snapshots. Firmware receives `POWER_TABLE_CMD`, `MAC_PM_POWER_TABLE`, and `REPLY_BEACON_FILTERING_CMD`; these settings persist in firmware until changed or reset. D3 status changes timeout/DTIM behavior for WoWLAN.

## Dependencies And Integration Points
Depends on mac80211 vif/link state, module parameter `iwlmvm_mod_params.power_scheme`, firmware power command definitions, beacon filter API versions, cfg80211 channel/radar flags, TDLS station counting, low-latency helpers, P2P NoA attributes, debugfs structures from `mvm.h`, and `iwl_mvm_send_cmd_pdu`. Called by association, interface state, WoWLAN, and low-latency/power recalculation paths.

## Risks And Edge Cases
Power policy is role-sensitive: enabling PM with AP/GO, TDLS, same-channel combinations, P2P opportunistic PS, or low latency can break traffic. DTIM skipping is disabled for long DTIM periods or radar channels. U-APSD must avoid APs firmware flagged as misbehaving and P2P cases firmware cannot support. Debugfs overrides can force unusual command combinations. Beacon filter enable silently no-ops unless the vif is eligible and allowed.

## Test Signals
Cover CAM/BPS/LP module schemes, `ps_disabled` vifs, BSS-only, P2P-only, BSS+P2P same and different channel, BSS+AP, TDLS present, D3/WoWLAN timeouts, radar channel DTIM skip suppression, low-latency P2P, U-APSD all ACs/snooze and partial ACs, misbehaving AP notification/reassociation, beacon filter enable/disable/CQM parameters, debugfs overrides, and firmware command failure rollback of `mvm->ps_disabled`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/power.c -->
