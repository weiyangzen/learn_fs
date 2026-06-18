# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_adminq_cmd.h

## Purpose

`i40e_adminq_cmd.h` is the firmware-facing Admin Queue ABI for Intel i40e devices in this tree. It defines Admin Queue opcodes, descriptor payload overlays, indirect buffer layouts, bit masks, and compile-time structure-size checks used by `i40e_common.c`, `i40e_adminq.c`, NVM/DCB/link code, cloud filter code, and the iWARP client path. The header is intentionally low-level: command structs must match firmware-defined byte layouts, with most direct command payloads constrained to the 16-byte `libie_aq_desc.params.raw` area and larger data passed as indirect buffers.

## Important APIs, Types, And Constants

- `enum i40e_admin_queue_opc` is the central opcode registry. It covers core AQ commands, resource ownership, device/function capabilities, switch/VSI/VEB/MAC-VLAN/filter management, DCB and scheduler commands, PHY/link/NVM commands, LLDP, RSS/tunnel commands, virtualization mailbox commands, DDP, OEM, async events, and debug operations.
- Firmware API version constants such as `I40E_FW_API_VERSION_MAJOR`, `I40E_FW_API_VERSION_MINOR_X722`, `I40E_MINOR_VER_GET_LINK_INFO_XL710`, and `I40E_MINOR_VER_FW_LLDP_STOPPABLE_X722` gate behavior in common code.
- `I40E_CHECK_STRUCT_LEN` and `I40E_CHECK_CMD_LENGTH` enforce ABI sizes at compile time. These are test-like guards for the firmware contract.
- Descriptor overlays include `i40e_aqc_get_version`, `i40e_aqc_queue_shutdown`, `i40e_aqc_mac_address_read/write`, `i40e_aqc_add_get_update_vsi`, `i40e_aqc_set_vsi_promiscuous_modes`, `i40e_aqc_add_veb`, `i40e_aqc_macvlan`, `i40e_aqc_pf_vf_message`, `i40e_aqc_nvm_update`, `i40e_aqc_lldp_*`, `i40e_aqc_get_set_rss_*`, and `i40e_aqc_phy_register_access`.
- Larger indirect buffer contracts include `i40e_aqc_vsi_properties_data`, `i40e_aq_get_phy_abilities_resp`, scheduler bandwidth response/config buffers, DCB/CEE responses, WoL data, cloud filter entries, DDP profile responses, and RSS key data.

## Control Flow And Usage

This header has no executable control flow, but it shapes control flow throughout the driver. Callers allocate and fill `libie_aq_desc`, call `i40e_fill_default_direct_cmd_desc()` with an opcode from this file, cast `desc.params.raw` through `libie_aq_raw()`, set little-endian fields and AQ flags, and pass optional indirect buffers to `i40e_asq_send_command*()`.

Typical flows include initialization/version/capability discovery, link management, filtering, SR-IOV and RDMA virtual channel messages, DCB/scheduler configuration, NVM operations, and DDP profile handling.

## State And Persistence Behavior

The header describes state that lives in firmware, hardware tables, NVM, and driver-owned mirror structs. NVM update/erase/config commands, persistent LLDP start/stop, MAC write flags, DDP loading, and switch/VSI/filter/scheduler commands can change durable or reset-scoped device state. All multi-byte firmware fields are little-endian; command-specific byte arrays require careful interpretation.

## Dependencies And Integration Points

- Includes `<linux/net/intel/libie/adminq.h>` for common Admin Queue descriptor and shared command definitions.
- Includes Linux bit/type helpers.
- Used heavily by `i40e_common.c`, `i40e_adminq.c`, `i40e_dcb.c`, `i40e_nvm.c`, `i40e_main.c`, and client/iWARP integration.
- Command structs must remain synchronized with firmware and with common-code wrappers that assume exact field offsets.

## Risks

- ABI drift is the largest risk: changing field order, size, endian type, or flags can silently break firmware communication.
- Some layouts intentionally include padding for compiler/FW alignment differences, especially the legacy CEE DCB response.
- Command flags such as `LIBIE_AQ_FLAG_BUF`, `LIBIE_AQ_FLAG_RD`, `LIBIE_AQ_FLAG_LB`, and `LIBIE_AQ_FLAG_SI` must match firmware expectations.
- Firmware API-version gates mean fields can be ignored or interpreted differently on XL710 versus X722 and older firmware.

## Test Signals

- Compilation is a meaningful first-order test because `I40E_CHECK_*` catches many ABI-size regressions.
- Runtime coverage should exercise firmware-version discovery, link status, PHY abilities, VSI add/update/get, MAC-VLAN add/remove, RSS key/LUT get/set, LLDP/DCB commands, NVM read/update error paths, and virtual channel PF-to-VF messaging.
- Useful negative tests include zero/invalid buffer sizes, unsupported firmware capability bits, large-buffer AQ paths, and endian-sensitive fields.
