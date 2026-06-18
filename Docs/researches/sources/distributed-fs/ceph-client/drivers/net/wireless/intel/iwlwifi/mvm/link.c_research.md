# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/link.c

## Purpose

`link.c` manages firmware link contexts for MVM's MAC configuration API, especially MLO-capable per-link state. It adds, modifies, deactivates, removes, and initializes per-vif link information, translating mac80211 `ieee80211_bss_conf` fields into `LINK_CONFIG_CMD` payloads.

## Important APIs, Types, And Functions

- `iwl_mvm_link_cmd_send()` is the local sender for `LINK_CONFIG_CMD` with add/modify/remove actions and standardized error logging.
- `iwl_mvm_set_link_fw_id()` assigns a firmware link ID; currently invalid links inherit the vif MAC ID.
- `iwl_mvm_add_link()` creates a firmware link context with MAC ID, link ID, local address, optional IBSS BSSID, invalid PHY ID, and listen LMAC for older command versions.
- `iwl_mvm_link_changed()` updates active state, PHY binding, local address, rates, protection, QoS, beacon/DTIM timing, HE/EHT parameters, BSS color, puncturing, nontransmitted-BSSID data, and link flags.
- `iwl_mvm_remove_link()` removes the firmware link context, invalidates the local firmware link ID, and updates Smart FIFO state.
- `iwl_mvm_disable_link()` deactivates then removes a link.
- `iwl_mvm_init_link()` initializes station IDs and SMPS request defaults for a link info object.

## Control Flow

Adding a link first ensures link info exists, assigns a firmware link ID, disables Smart FIFO if necessary, fills `LINK_CONFIG_CMD`, and sends `FW_CTXT_ACTION_ADD`. Modifying checks that the link exists and has a valid firmware ID, handles activation/deactivation bookkeeping, stops session protection on station deactivation, fills PHY/MAC/rate/protection/QoS/timing fields, conditionally encodes HE and EHT data, sends `FW_CTXT_ACTION_MODIFY`, and updates `link_info->active` only after a successful active-state change.

EHT puncturing is gated on command/PHY command version, module 11be disable flag, link EHT support, and available channel context. HE fields are skipped when HE is unsupported, disabled, or station mode is not associated. Removal sends `FW_CTXT_ACTION_REMOVE` and then attempts to restore Smart FIFO state.

## State And Persistence

The file mutates `struct iwl_mvm_vif_link_info`: `fw_link_id`, `active`, `phy_ctxt`, `csa_block_tx`, `listen_lmac`, queue parameters, `he_ru_2mhz_block`, station IDs, and SMPS request array. Firmware maintains the actual link context after commands are sent. Nothing is persisted beyond runtime driver state.

## Dependencies And Integration Points

It depends on MVM vif/link structures, mac80211 link/bss configuration, `MAC_CONF_GROUP` firmware commands, PHY context state, Smart FIFO updates, session protection, rate/protection/QoS helpers from `mac-ctxt.c`, module disable flags for 11ax/11be, and RCU channel-context access. It is a key integration point between mac80211 MLO link callbacks and firmware link contexts.

## Risks And Edge Cases

- Activating a link without a PHY context is treated as a no-op, which handles early removal but can hide sequencing bugs if callers expected activation.
- Link ID assignment currently aliases the vif ID for invalid links; future firmware with independent link ID allocation may need different handling.
- Smart FIFO update failure during add aborts binding because multiple bound MACs with SF enabled are forbidden.
- EHT puncturing behavior changes depending on PHY command version; wrong gates can send unsupported fields or omit required puncture masks.
- Deactivation must stop session protection and unblock CSA-blocked TX correctly to avoid stuck station traffic.

## Test Signals

Useful tests cover MLO and non-MLO link add/modify/remove, station link activation/deactivation, AP/IBSS BSSID handling, HE and EHT link changes, punctured-channel operation, Smart FIFO transitions with multiple links, CSA blocked-TX cleanup, and firmware logs for failed `LINK_CONFIG_CMD` actions.
