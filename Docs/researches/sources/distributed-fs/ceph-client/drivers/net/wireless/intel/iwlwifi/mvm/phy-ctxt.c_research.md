<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/phy-ctxt.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/phy-ctxt.c

## Purpose
Manages firmware PHY context commands for channel definitions, channel width/control-position encoding, RX/TX chain selection, RLC configuration, PHY context add/modify/remove, reference counts, and active PHY context counting.

## Important APIs, Types, And Functions
Public functions are `iwl_mvm_get_channel_width`, `iwl_mvm_get_ctrl_pos`, `iwl_mvm_phy_send_rlc`, `iwl_mvm_phy_ctxt_add`, `iwl_mvm_phy_ctxt_ref`, `iwl_mvm_phy_ctxt_changed`, `iwl_mvm_phy_ctxt_unref`, and `iwl_mvm_phy_ctx_count`. Static helpers build firmware command headers/data and RX chain fields: `iwl_mvm_phy_ctxt_cmd_hdr`, `iwl_mvm_phy_ctxt_set_rxchain`, `iwl_mvm_phy_ctxt_cmd_data_v1`, `iwl_mvm_phy_ctxt_cmd_data`, and `iwl_mvm_phy_ctxt_apply`.

## Control Flow
Channel width and control position translate cfg80211 channel definitions into firmware constants. PHY context add records channel/width/center frequency, sends `PHY_CONTEXT_CMD` with ADD, then increments refcount. Change validates an existing ref, sends only RLC if the channel definition did not change and RLC version supports that split, otherwise removes/adds when CDB binding changes bands, or sends MODIFY. Unref decrements and sends REMOVE when the last reference drops. RLC send is skipped when firmware offloads RLC or the context disables it; otherwise it sends `RLC_CONFIG_CMD` v2 with RX chain info.

## State And Persistence
Mutates `struct iwl_mvm_phy_ctxt` fields: `channel`, `width`, `center_freq1`, `ref`, and uses `rlc_disabled`. Firmware state persists until remove or reset. RX chain selection depends on valid antenna masks from NVM/firmware/debugfs and may promote one active chain to two for diversity when allowed.

## Dependencies And Integration Points
Depends on mac80211/cfg80211 channel definitions, firmware command versions, `iwl_mvm_set_chan_info_chandef` and channel info helpers from `mvm.h`, antenna helpers, RLC offload feature gating, and `iwl_mvm_send_cmd_pdu`. Channel context and binding code call these APIs under `mvm->mutex`.

## Risks And Edge Cases
Invalid channel widths warn and fall back to 20 MHz. Control-position encoding is bit-sensitive for wide channels. Command version handling changes struct size and padding; ultra-high-band channel info changes tail placement. Refcount misuse can remove an active PHY context or modify a non-added one. Band changes with CDB binding support require remove/add rather than modify. RLC offload version boundaries must be correct.

## Test Signals
Cover 20/40/80/160/320 MHz widths, all primary-channel offsets, add/change/unref lifecycles, refcount warnings, same-channel RLC-only update, band-switch remove/add path, RLC offload skip, debugfs RX chain override, static/dynamic chain diversity behavior, and active context count across STA/AP interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/phy-ctxt.c -->
