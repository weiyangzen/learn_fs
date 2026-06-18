# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/debug.h

Purpose: Defines firmware debug command IDs and payloads for memory access, shared-memory configuration, MFUART notifications, trace markers, DBGC suspend/resume and buffer allocation, DRAM fragment info, host event config, dump completion, TAS status, and debug token configuration.

Important APIs and types: `enum iwl_debug_cmds` names debug group commands. `struct iwl_error_resp` reports firmware command errors. Shared-memory layouts v2/current expose TX/RX FIFO and buffer addresses. `iwl_mfuart_load_notif`, `iwl_mfu_assert_dump_notif`, marker command/response structs, `iwl_dbg_mem_access_cmd/rsp`, `iwl_buf_alloc_cmd`, `iwl_dram_info`, `iwl_dbg_host_event_cfg_cmd`, `iwl_dbg_dump_complete_cmd`, `iwl_tas_status_resp`, and `iwl_fw_dbg_config_cmd` are the key payloads.

Control flow: No local execution. Debug/runtime code sends memory access, marker, buffer allocation, host event, dump-complete, TAS, and debug-config commands and parses firmware notifications/responses.

State and persistence: Header owns no state. Firmware and driver maintain debug buffer allocations, shared memory addresses, host event settings, TAS status, and firmware debug token configuration at runtime.

Dependencies and integration points: Includes `dbg-tlv.h`; command IDs are referenced from `commands.h` debug group and legacy IDs. Integrates with debugfs, firmware dump collection, transport memory reads/writes, TAS ACPI/DHC policy, and firmware assert handling.

Risks: Memory access commands can be locked/hidden/length-rejected and must not expose unsafe memory. Shared-memory struct versions depend on firmware capability bits. Buffer allocation has a fixed fragment maximum. MFUART dump notifications are chunked and length-sensitive. TAS status fields are compact and versioned. Debug token command can alter firmware assert behavior.

Test signals: LMAC/UMAC read/write success and failure statuses, shared memory cfg v2/current parsing, MFUART load and assert chunk assembly, marker timestamp response, DBGC suspend/resume, buffer allocation at max fragment count, dump-complete command, TAS status across bands/LMACs, and debug token enable/disable.
