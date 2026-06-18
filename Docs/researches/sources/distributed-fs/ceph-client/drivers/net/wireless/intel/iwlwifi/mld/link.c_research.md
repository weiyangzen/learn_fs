# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/link.c

Purpose: Manages firmware link contexts for each mac80211 BSS/link configuration. It adds/removes/activates/deactivates links, packs link configuration commands, handles missed beacon and beacon filter notifications, and computes link quality grades for MLO/EMLSR policy.

Important APIs/types/functions: `iwl_mld_add_link()`, `iwl_mld_remove_link()`, `iwl_mld_activate_link()`, `iwl_mld_deactivate_link()`, `iwl_mld_change_link_in_fw()`, `iwl_mld_handle_missed_beacon_notif()`, `iwl_mld_cancel_missed_beacon_notif()`, `iwl_mld_link_set_associated()`, `iwl_mld_get_link_grade()`, `iwl_mld_get_chan_load()`, `iwl_mld_get_chan_load_by_others()`, and `iwl_mld_handle_beacon_filter_notif()`.

Control flow: Link add allocates or reuses link state, allocates a firmware link ID, maps it with RCU, and sends `LINK_CONFIG_CMD` add. Change builds a modify command with MAC/PHY IDs, local addresses, active state, rates, protection, QoS, beacon/DTIM, HE/MU-EDCA/BSS color, RU blocking, and nontransmitted BSSID fields. Activation marks active, sends active modify, and records activation time; deactivation cancels session protection, frees probe response data, sends inactive modify, and cancels link-scoped notifications. Remove sends firmware remove and clears mappings. Missed beacon notifications can trigger connection loss, CQM beacon loss, MLO scan, or EMLSR exit depending on thresholds and second-link loss.

State/persistence: Owns `struct iwl_mld_link` firmware ID, active flag, queue parameters, channel context pointer, HE RU 2 MHz block, IGTK/BIGTK pointers, internal broadcast/multicast/monitor stations, average beacon energy, early AP keys, silent deactivation flag, and RCU probe response data. Link grade is derived, not persisted except beacon energy and channel-load inputs.

Dependencies/integration: Integrates with mac80211 BSS configs, MLD VIFs, PHY contexts, TLC/rate constants, MLO/EMLSR policy, session protection, AP beacon/NoA handling, firmware MAC configuration, and cfg80211 BSS load elements.

Risks: Link command packing depends on valid channel context for rates and PHY ID. Silent deactivation is subtle and only intended around CSA with quiet in EMLSR. Channel load from QBSS elements can be absent or invalid; defaults differ by band. Link grading assumes valid RSSI/band/width and adjusts 6 GHz RSSI. Missed beacon thresholds have several branches that can disconnect or merely warn when RX data continues.

Test signals: KUnit exports cover missed beacon handling and link grading. Tests should exercise add/remove rollback, active state failure rollback, QoS/rate/protection modify masks, EMLSR missed beacon exits, channel-load fallback, puncturing subchannel counts, and beacon filter average energy updates.
