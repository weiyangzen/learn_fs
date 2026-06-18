# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/fw.h

## Purpose
`fw.h` is the mwifiex firmware ABI contract. It defines packed download headers, transmit/receive packet descriptors, command IDs, TLV IDs, event IDs, capability bit helpers, host command payloads, and the top-level `struct host_cmd_ds_command` union used by command preparation and response handling across the driver.

## Important APIs, Types, and Functions
The file is type and macro heavy rather than function based. Core framing types are `struct mwifiex_fw_header`, `struct mwifiex_fw_data`, `struct txpd`, `struct rxpd`, `struct uap_txpd`, `struct uap_rxpd`, `struct mwifiex_ie_types_header`, and `struct host_cmd_ds_gen`. Command payloads include hardware spec, scan, association, ad-hoc start/join, key material v1/v2/WEP, power save, host sleep, WMM status, UAP system config, TDLS, coalesce, GTK rekey, channel report, station configure, packet aggregation, and config-data structures. Important constants include `HostCmd_CMD_*`, `EVENT_*`, `TLV_TYPE_*`, `S_DS_GEN`, `MWIFIEX_AUTO_IDX_MASK`, `MWIFIEX_DELETE_MASK`, `MGMT_MASK_*`, `ISSUPP_*`, `IS_SUPPORT_MULTI_BANDS()`, `HostCmd_SET_SEQ_NO_BSS_INFO()`, and event/BSS extraction macros.

## Control Flow
Runtime control flow in other files is built around these layouts. Firmware download code sends `mwifiex_fw_data` chunks headed by `mwifiex_fw_header`; TX/RX paths prepend or parse `txpd`/`rxpd`; command builders fill `host_cmd_ds_command.command`, `.size`, `.seq_num`, and the relevant `params` union member; response handlers reinterpret the same union with `HostCmd_RET_BIT` response IDs. Scan, join, UAP, power, and key paths append variable TLVs by writing `mwifiex_ie_types_header` followed by packed payload data.

## State and Persistence
The header defines volatile wire state, not persistent storage. State survives only when copied into `mwifiex_adapter` or `mwifiex_private` fields in `main.h`, or when firmware retains configured state. Packed little-endian fields are the source of truth at the firmware boundary, so callers must use `cpu_to_le*()` and `le*_to_cpu()` consistently.

## Dependencies and Integration Points
`fw.h` depends on Linux Ethernet, WLAN, cfg80211, and 802.11 structures pulled through surrounding mwifiex headers. It integrates with `init.c` for firmware download and hardware-spec parsing, `main.c` for sleep-confirm setup and packet paths, `join.c` for association/ad-hoc command construction, `ie.c` for custom management IE TLVs, and command/event handlers throughout the mwifiex directory.

## Risks and Edge Cases
The main risk is binary ABI drift. Many structures are `__packed`, include flexible arrays, or carry explicit comments that fields must not be added, especially `struct adhoc_bss_desc`. Wrong endian conversion, size accounting, or TLV length calculation can corrupt firmware commands. Command union growth must stay within allocated command buffers. Capability macros encode firmware bit positions; changing them without firmware coordination breaks feature gating. Management IE indexes and masks are shared with firmware and must match `ie.c` semantics.

## Test Signals
Useful signals include successful firmware download and `GET_HW_SPEC`, correct command sizes in association, scan, UAP, and power-save commands, event dispatch for all expected `EVENT_*` values, stable key install/remove across key API versions, successful custom IE add/delete, valid sleep-confirm handling, and no firmware rejects caused by malformed TLV lengths or command IDs.
