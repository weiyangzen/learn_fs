# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/phy.c

Purpose: manages firmware PHY context identifiers, channel-definition selection, control-channel encoding, PHY context commands, global PHY configuration, and cached channel definitions.

Important APIs/functions: `iwl_mld_allocate_fw_phy_id()`, `iwl_mld_get_chandef_from_chanctx()`, `iwl_mld_get_fw_ctrl_pos()`, `iwl_mld_phy_fw_action()`, `iwl_mld_send_phy_cfg_cmd()`, and `iwl_mld_update_phy_chandef()`. Static helpers detect FILS/FTM cases requiring full `ctx->def`, convert nl80211 bandwidths to firmware values, and derive valid antenna chain masks.

Control flow: allocation scans `mld->used_phy_ids` for a clear bit. Channel-definition selection iterates active interfaces and chooses full `ctx->def` for AP FTM responder or 6 GHz PSC/FILS-style cases, otherwise `ctx->min_def`. Firmware action builds `PHY_CONTEXT_CMD` from cached `phy->chandef`, optional puncturing and SBB/AP chandef, sends it, and logs failures. Global PHY config masks firmware config with valid TX/RX antennas and default calibration triggers.

State and persistence: updates in-memory `mld->used_phy_ids` and `struct iwl_mld_phy::chandef`. No disk persistence. `struct_group(zeroed_on_hw_restart)` in the header indicates `fw_id` and chandef are reset on hardware restart.

Dependencies and integration: depends on mac80211 channel contexts, cfg80211 channel definitions, firmware PHY context APIs, local host-command wrappers, antenna helpers from MLD core, and AP link settings.

Risks and test signals: control-position encoding is bit-sensitive for 80/160/320 MHz layouts; invalid bandwidth falls back to 20 MHz after warning; allocation has no locking internally and assumes caller serialization. Tests should cover fw id exhaustion, FILS/FTM chandef choice, puncturing propagation, SBB fields, and each control-channel offset class.
