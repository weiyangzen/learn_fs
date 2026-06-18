# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mld-mac.c

## Purpose
Builds and sends MLD firmware MAC context commands. It is the MLD replacement for legacy MAC context command construction: given a mac80211 vif, it fills `MAC_CONFIG_CMD` for station, AP/GO, monitor, P2P device, and IBSS contexts, including MLD address, MAC type, filter flags, association state, HE/EHT support, P2P CT window, TWT policy, and NIC ACK policy.

## Important APIs, Types, And Functions
The main public helpers are `iwl_mvm_mld_mac_ctxt_add()`, `iwl_mvm_mld_mac_ctxt_changed()`, and `iwl_mvm_mld_mac_ctxt_remove()`. Internally, `iwl_mvm_mld_mac_ctxt_cmd_common()` fills shared `struct iwl_mac_config_cmd_v3` fields and scans all active `vif->link_conf[]` entries to set HE/EHT support. Type-specific builders are `iwl_mvm_mld_mac_ctxt_cmd_sta()`, `iwl_mvm_mld_mac_ctxt_cmd_listener()`, `iwl_mvm_mld_mac_ctxt_cmd_ibss()`, `iwl_mvm_mld_mac_ctxt_cmd_p2p_device()`, and `iwl_mvm_mld_mac_ctxt_cmd_ap_go()`. `iwl_mvm_mld_mac_ctx_send()` dispatches by interface type, and `iwl_mvm_mld_mac_ctxt_send_cmd()` wraps command submission and error logging.

## Control Flow
Add validates that the MAC is not already uploaded, sends an ADD command with association forced off, restores last non-QoS sequence state for D3 resume cases, and marks `mvmvif->uploaded`. Change validates the context is uploaded and sends MODIFY with optional `force_assoc_off`, which is used by common station/channel-switch flows to temporarily suppress association state. Remove sends a minimal REMOVE command with id/color and clears `uploaded` only after firmware accepts it.

For station contexts, the builder accepts group frames, sets P2P CT window when needed, marks association and AID unless forced off, applies high-priority coexistence policy before authorization, accepts beacons while unassociated, accepts P2P probe requests when requested, and adds TWT policy when HE is enabled. Monitor contexts use promiscuous/control/management/beacon/probe/group filters. P2P device contexts use extended discovery capability and accept control/management frames. AP/GO contexts delegate filter flag construction to common AP helper logic.

## State And Persistence
The file mutates only the per-vif `uploaded` flag directly, but commands serialize persistent firmware MAC context state keyed by `mvmvif->id`. It reads vif association, AID, P2P, HE/EHT, probe request registration, and authorization state. HE/EHT flags are aggregated from current link configurations, so MLD link state in mac80211 drives firmware MAC-level capabilities.

## Dependencies And Integration Points
Depends on `mvm.h`, mac80211 vif/link structures, firmware `MAC_CONFIG_CMD` versions, common helper functions from the legacy MAC context implementation, module parameters disabling 11ax/11be, and MVM command submission. It is called by `mld-mac80211.c` for MLD mac80211 callbacks and by common station-state code through a callback table.

## Risks
Firmware command version handling is strict: versions above 3 warn and return without filling the command, so future API changes require updates here. MAC type support is limited to known interface types; unsupported types return `-EOPNOTSUPP`. HE/EHT capability aggregation runs under RCU and assumes link configuration is coherent with vif lifetime. Incorrect `force_assoc_off` use can leave firmware accepting or rejecting frames with the wrong association state. The `uploaded` flag must match firmware state; failed add/remove paths need callers to unwind link and vif state correctly.

## Test Signals
Create and remove station, AP/GO, P2P device, monitor, and IBSS interfaces under MLD firmware. Validate association transitions update MAC_CONFIG_CMD fields, P2P probe request filtering works, AP/GO filter flags accept the expected management frames, and HE/EHT capability exposure follows active links and module disables. Restart and D3 resume should verify `uploaded` state and sequence restoration.
