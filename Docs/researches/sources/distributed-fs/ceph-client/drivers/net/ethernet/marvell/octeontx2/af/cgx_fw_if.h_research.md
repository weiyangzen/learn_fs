# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cgx_fw_if.h

Purpose: Defines the firmware command/event ABI used for communication between non-secure software and CGX firmware/ATF through scratch registers. It enumerates firmware versions, command IDs, event IDs, status/error encodings, link speeds, physical modes, and bitfield layouts for command and response registers.

Important APIs/types/functions: Key enums are `cgx_error_type`, `cgx_link_speed`, `CGX_MODE_`, `cgx_cmd_id`, `cgx_evt_id`, `cgx_evt_type`, `cgx_stat`, and `cgx_cmd_own`. `FIELD_SET()` wraps bitfield update logic. Response masks define ACK, event type, status, ID, error type, firmware version, MAC address, MKEX profile, firmware data base, and link status fields. `struct cgx_lnk_sts` documents the packed link-status response. Command masks define ownership, command ID, enable flag, MTU, link change, FEC, mode-change speed/duplex/autoneg/base index/flags, and link bring-up timeout.

Control flow and integration: `cgx.c` builds command words with `FIELD_SET(CMDREG_ID, ...)`, writes them to `CGX_COMMAND_REG`, and decodes responses/events with `FIELD_GET()` using masks from this header. Link-mode setting, FEC setting, firmware data base queries, link bring-up/down, and asynchronous link events all depend on these definitions.

State and persistence: The header represents transient command/response state in scratch CSRs. Ownership bits coordinate whether firmware or non-secure software owns a command or advertised-link-mode shared field.

Dependencies: Requires Linux bit and bitfield helpers. It must remain synchronized with firmware and ATF implementations, not just kernel code.

Risks: ABI drift is the central risk. A changed command ID, bitfield width, or firmware major version can break link management. The mode enum includes sparse values and grouped mode ranges; callers must correctly set `CMDMODECHANGE_MODE_BASEIDX` for values above the first range. Incorrect ownership handling can lead to `CGX_ERR_PREV_ACK_NOT_CLEAR` or busy responses.

Test signals: Firmware version checks, every CGX command path, link change event decoding, FEC and advertised mode changes, and negative tests for invalid/unsupported modes validate this ABI.
