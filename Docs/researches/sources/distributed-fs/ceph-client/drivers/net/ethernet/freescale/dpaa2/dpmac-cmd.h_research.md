# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpmac-cmd.h

Purpose: Defines MC command IDs, bitfield helpers, and packed command/response payload layouts for the DPAA2 Data Path MAC API.

Important APIs, types, and functions: Version macros are `DPMAC_VER_MAJOR`, `DPMAC_VER_MINOR`, command versions, `DPMAC_CMD_ID_OFFSET`, `DPMAC_CMD()`, and `DPMAC_CMD_V2()`. Command IDs cover open/close, API version, attributes, link state, counters, protocol, and bulk statistics. Bitfield helpers are `DPMAC_MASK()`, `dpmac_set_field()`, and `dpmac_get_field()`. Payload structs include `dpmac_cmd_open`, `dpmac_rsp_get_attributes`, `dpmac_cmd_set_link_state`, `dpmac_cmd_get_counter`, `dpmac_rsp_get_counter`, `dpmac_rsp_get_api_version`, `dpmac_cmd_set_protocol`, and `dpmac_cmd_get_statistics`.

Control flow: No direct execution occurs. `dpmac.c` casts `fsl_mc_command.params` to these structs, fills little-endian fields and compact bitfields, sends the command through `mc_send_command()`, then interprets response layouts from the same buffer.

State and persistence behavior: The header encodes transient MC command payloads. Link state, protocol, counters, and statistics live in MC firmware/hardware; this file stores no driver state.

Dependencies and integration points: Depends on Linux endian/fixed-width types through including context and the FSL MC command ABI. It is private to the DPMAC wrapper implementation and must match MC firmware command layouts exactly.

Risks: Struct layout, padding, command version, and bit shifts are firmware ABI. `DPMAC_CMDID_SET_LINK_STATE` uses command version 2 while most commands use base version; changing that would break newer link-state fields such as supported/advertising. `dpmac_set_field()` ORs into the existing variable, so callers must start from zeroed command buffers or clear target bits first.

Test signals: Compile and runtime smoke tests for every `dpmac.c` wrapper, firmware API version query, link-state set with `up` and `state_valid`, counter reads across all IDs, protocol changes, and bulk statistics DMA commands. Static layout checks are useful if MC ABI headers evolve.
