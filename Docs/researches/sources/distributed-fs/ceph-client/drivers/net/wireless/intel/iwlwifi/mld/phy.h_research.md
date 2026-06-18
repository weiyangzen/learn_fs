# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/phy.h

Purpose: defines the private PHY context state attached to mac80211 channel contexts and declares PHY command helpers.

Important APIs/types: `struct iwl_mld_phy` stores firmware id, cached chandef, channel load by device, averaged channel load by others, and back pointer to `struct iwl_mld`. `iwl_mld_phy_from_mac80211()` casts channel context private storage. `iwl_mld_cleanup_phy()` wraps `CLEANUP_STRUCT()`. Declarations expose fw id allocation, PHY action, chandef choice, control position conversion, global PHY config command, and chandef update.

Control flow: channel context setup code allocates/initializes this private structure, uses command helpers from `phy.c`, and later cleanup/restart paths zero the restart-sensitive group.

State and persistence: `zeroed_on_hw_restart` includes `fw_id` and `chandef`; channel-load statistics survive hardware restart. This is live kernel state only.

Dependencies and integration: includes `mld.h` and uses mac80211 `struct ieee80211_chanctx_conf` private storage. It integrates with MLO channel-load decisions in `mlo.c` and PHY context firmware programming in `phy.c`.

Risks and test signals: callers must not use stale `fw_id` after restart cleanup. Channel-load fields are used by EMLSR policy and need tests around clearing/updating across active-link transitions.
