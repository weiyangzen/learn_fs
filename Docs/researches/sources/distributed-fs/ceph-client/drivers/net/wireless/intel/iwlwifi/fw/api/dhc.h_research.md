# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/dhc.h

Purpose: Defines Debug Host Command table selection, command/response formats, TAS status response payload, and integration commands such as TWT operation triggering.

Important APIs and types: `enum iwl_dhc_table_id` selects tools or integration tables. `DHC_TARGET_UMAC` and `DHC_TABLE_MASK_POS` define descriptor bits. `struct iwl_dhc_cmd` wraps variable data with length and index/mask descriptor. `struct iwl_dhc_payload_hdr`, `iwl_dhc_tas_status_per_radio`, `iwl_dhc_tas_status_resp`, `iwl_dhc_cmd_resp_v1`, `iwl_dhc_cmd_resp`, and `iwl_dhc_twt_operation` define response and payload shapes. Enums define UMAC tools/integration entries and TWT operation types.

Control flow: No executable flow. Debug/integration code builds a descriptor identifying table, target, LMAC/UMAC, and entry, sends `DEBUG_HOST_COMMAND`, then parses status plus optional descriptor and payload.

State and persistence: Header owns no state. DHC operations query or alter firmware runtime debug/integration state, such as TAS reporting or TWT negotiation.

Dependencies and integration points: Uses BIOS/TAS types such as `bios_value_u32` and `IWL_WTAS_BLACK_LIST_MAX`, and TAS enums from debug APIs. TWT operation payloads integrate with MAC/TWT management.

Risks: Descriptor bit packing is dense; mixing table ID, target, LMAC selector, and entry index incorrectly sends the wrong DHC operation. v1 and v2/v3 responses differ by descriptor field. Variable `data[]` length is in DWORDs and must match payload sizes. TWT fields are protocol-sensitive and many one-byte booleans are not bitfields.

Test signals: UMAC tools TAS status query, response v1/v2 parsing, invalid descriptor/status handling, integration TLC debug config, all TWT operation enum values, UMAC vs LMAC target bits, and payload length validation.
