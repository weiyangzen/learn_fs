# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/iface.c

Purpose: Manages mac80211 virtual interfaces as firmware MAC contexts. It allocates/free firmware MAC IDs, builds `MAC_CONFIG_CMD` payloads by interface type, handles restart cleanup, tracks association side effects, and processes firmware notifications tied to VIF or link-level behavior.

Important APIs/types/functions: `iwl_mld_add_vif()`, `iwl_mld_rm_vif()`, `iwl_mld_mac_fw_action()`, `iwl_mld_cleanup_vif()`, `iwl_mld_set_vif_associated()`, `iwl_mld_get_fw_bss_vifs_ids()`, `iwl_mld_handle_probe_resp_data_notif()`, `iwl_mld_handle_datapath_monitor_notif()`, `iwl_mld_reset_cca_40mhz_workaround()`, and `iwl_mld_get_bss_vif()`.

Control flow: VIF add initializes `struct iwl_mld_vif`, allocates a firmware MAC ID except for NAN, and sends `MAC_CONFIG_CMD` add. MAC command construction fills common address/type/action fields, WiFi generation support, NIC ACK policy, and type-specific filters for STA, AP, monitor, P2P device, and IBSS. Remove sends a firmware remove action, clears the `fw_id_to_vif` RCU mapping, and cancels pending VIF-scoped notifications. Association updates all active links and recalculates multicast filtering.

State/persistence: `iwl_mld_vif` holds restart-cleaned fields such as firmware ID, AP STA, authorization, AP/IBSS active state, low latency causes, power-save state, CCA workaround state, and session protection. It also holds persistent pointers and workers for EMLSR, ROC, aux station, MLO scan deferral, and debugfs. Restart cleanup clears ROC, frees aux/internal link resources, invalidates inactive links, resets EMLSR active flags, and clears keys' hardware indices.

Dependencies/integration: Integrates mac80211 VIFs, firmware MAC context API, MLO link data, key cleanup, session protection, P2P NoA/probe response data, datapath monitor notifications, and multicast filter recalculation.

Risks: NAN is special-cased as unknown to firmware, so callers must not assume every VIF has a firmware ID. Probe-response data notification is explicitly not MLD-ready and rejects MLD VIFs. The 2.4 GHz 40 MHz CCA workaround mutates advertised HT/HE band capabilities and disconnects, so failure to reset on real disconnect would leave stale reduced capabilities. Cleanup warns if inactive links remain allocated unexpectedly.

Test signals: Add/remove VIF tests should validate `fw_id_to_vif` mappings and NAN bypass. Notification tests should cover invalid MAC IDs, P2P NoA length validation, CSA countdown updates, UAPSD misbehaving AP warnings, datapath monitor CCA reconnect flow, and CCA capability restoration.
