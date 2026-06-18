# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/power.h

Purpose: declares MLD power-management and transmit-power command helpers used by interface/link lifecycle code.

Important APIs/types: exported declarations cover device power update, beacon filter enable/disable, MAC power update, AP TX power constraint command, and per-link TX power setting.

Control flow: callers invoke these helpers when association, suspend/D3, link configuration, beacon filtering, 6 GHz TPE, or user/regulatory TX power state changes. The implementation translates mac80211 state into firmware commands.

State and persistence: no state is defined here. Functions operate on `struct iwl_mld`, `struct ieee80211_vif`, and `struct ieee80211_bss_conf` live state.

Dependencies and integration: includes mac80211 and local `mld.h`. Integrates with interface/link modules and regulatory information that populates link power type/TPE fields.

Risks and test signals: callers need correct serialization around link state and should avoid sending AP power constraints for inactive or non-6 GHz links. TX power units are driver-specific and are converted in implementation.
