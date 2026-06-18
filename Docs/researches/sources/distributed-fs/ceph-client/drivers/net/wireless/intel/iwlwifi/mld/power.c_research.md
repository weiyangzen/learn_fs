# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/power.c

Purpose: builds and sends device-level power, beacon filtering, per-MAC power-management, AP/TPE power constraints, and link transmit-power commands for MLD operation.

Important APIs/functions: `iwl_mld_update_device_power()`, `iwl_mld_enable_beacon_filter()`, `iwl_mld_disable_beacon_filter()`, `iwl_mld_update_mac_power()`, `iwl_mld_send_ap_tx_power_constraint_cmd()`, and `iwl_mld_set_tx_power()`. Static helpers handle station PS iteration, radar/DTIM skip checks, U-APSD command flags, TPE table min selection, AP power type mapping, and command-version-specific TX power layouts.

Control flow: device power enables power save unless CAM mode or any station VIF disables PS, and adds D3 no-sleep flags when requested. Beacon filtering is station-only and considers debugfs disable and CQM RSSI thresholds. MAC power chooses a representative active link for MLD VIFs, sets keepalive, returns early when PS is disabled or TDLS exists, then configures SMPS, LPRX, D3/low-latency/default timeouts, DTIM skipping, and U-APSD. AP constraints are sent only for active 6 GHz links.

State and persistence: reads `mld_vif->ps_disabled`, `vif->cfg.ps`, `link->queue_params`, debugfs flags, TDLS station count, and link TPE/power-type state. It sends firmware commands; no persistent local storage is created.

Dependencies and integration: depends on mac80211 BSS/link config, local MLD VIF/link helpers, constants, firmware power APIs, regulatory 6 GHz power types, and command-version lookup.

Risks and test signals: MLD MAC power uses the lowest active link because firmware accepts one config per VIF; this can misrepresent heterogeneous links. DTIM math must avoid zero beacon/DTIM periods. U-APSD QNDP TID selection depends on AC ordering and ACM flags. Tests should cover CAM vs PS, D3, radar channels, debugfs overrides, 6 GHz AP type mapping, default max TX power, command v10/v11 lengths, and inactive link skips.
