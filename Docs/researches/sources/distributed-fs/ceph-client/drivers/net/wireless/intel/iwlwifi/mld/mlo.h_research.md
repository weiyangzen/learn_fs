# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mlo.h

Purpose: declares the MLO/EMLSR interface used by the rest of the MLD driver and provides inline helpers for common MLO state queries. It is the contract between link management, scan, NAN/ROC blocking, notification handling, and mac80211 callbacks.

Important APIs/types: inline `iwl_mld_emlsr_active()`, `iwl_mld_vif_has_emlsr_cap()`, `iwl_mld_max_active_links()`, `iwl_mld_count_active_links()`, `iwl_mld_get_primary_link()`, and `iwl_mld_get_other_link()` are the main call-site helpers. The exported declarations cover EMLSR delayed work callbacks, block/unblock/exit, firmware notification handlers, link selection, Bluetooth/channel-load/TPT retries, NAN blocking, and TPT ignore mode. `struct iwl_mld_link_sel_data` carries link id, chandef, signal, and grade into link-pair scoring.

Control flow: callers first use capability and active-link helpers to decide whether EMLSR logic is applicable. Blocking and retry APIs then route into `mlo.c` to change active links or schedule an internal MLO scan. Firmware notification handlers are declared here for table-driven dispatch in `notif.c`.

State and persistence: no storage is defined here, but helper semantics rely on `struct iwl_mld_vif` private state, `vif->active_links`, `IEEE80211_VIF_EML_ACTIVE`, firmware capability counts, and `mld->trans->info.hw_rf_id`. State survives only in kernel objects, not on disk.

Dependencies and integration: includes Linux/mac80211 headers plus local `iwl-config.h`, `iwl-trans.h`, `iface.h`, and `phy.h`. The capability helper rejects unauthorized VIFs, non-station/P2P station types, non-MLD VIFs, missing EMLSR capability, and CDB dual-radio hardware.

Risks and test signals: primary-link helper warns on empty active-link masks and AP-mode semantics differ from station mode. `iwl_mld_get_other_link()` is only well-defined for zero, one, or two active links and warns on larger counts. KUnit can access `iwl_mld_emlsr_pair_state()` when enabled.
