# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/binding.c

## Purpose

Maintains firmware binding contexts that associate one PHY context with the active MAC contexts using it, and selects LMAC IDs for CDB-capable firmware.

## Important APIs, Types, and Functions

`iwl_mvm_binding_cmd()` builds and sends `BINDING_CONTEXT_CMD`. `iwl_mvm_iface_iterator()` collects matching VIF MAC IDs/colors. `iwl_mvm_binding_update()` chooses add/modify/remove action. Public entry points are `iwl_mvm_binding_add_vif()`, `iwl_mvm_binding_remove_vif()`, and `iwl_mvm_get_lmac_id()`.

## Control Flow

Add/remove paths require `mvm->mutex` and an existing default-link PHY context. The update path iterates active interfaces on the same PHY context while ignoring the target VIF, chooses `ADD`/`REMOVE` when the binding becomes non-empty/empty, otherwise `MODIFY`, optionally appends the target MAC, and sends the firmware command. Add disables Smart FIFO first; remove re-enables it after successful binding removal when possible.

## State and Persistence Behavior

The file owns no long-lived data. It derives commands from VIF IDs/colors, PHY context ID/color, active interface state, and firmware capabilities. Firmware stores the resulting binding.

## Dependencies and Integration Points

Uses mac80211 active-interface iteration, MVM VIF/PHY context private data, Smart FIFO updates, firmware CDB/binding capabilities, and `iwl_mvm_send_cmd_pdu_status()`.

## Risks

Overflow beyond `MAX_MACS_IN_BINDING`, missing mutex serialization, SF update failure policy changes, or wrong CDB command size/LMAC selection can leave firmware binding state inconsistent.

## Test Signals

Test single and multiple VIF binding on one PHY, AP/STA concurrency, CDB and non-CDB devices, Smart FIFO transitions, and firmware status failure handling.
