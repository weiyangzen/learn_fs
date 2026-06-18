# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/fw.h

## Purpose
`fw.h` defines the on-disk/in-firmware record format consumed by the wil6210 firmware and board-file loader. It is the schema shared by parser code and reset-time firmware loading.

## Important APIs, Types, And Functions
The file defines `WIL_FW_SIGNATURE`, `WIL_FW_FMT_VERSION`, and `enum wil_fw_record_type`. Packed record types include `wil_fw_record_head`, `wil_fw_record_data`, `wil_fw_record_fill`, `wil_fw_record_comment`, `wil_fw_record_capabilities`, `wil_fw_record_concurrency`, `wil_fw_record_brd_file`, `wil_fw_record_action`, `wil_fw_record_direct_write`, `wil_fw_record_verify`, `wil_fw_record_file_header`, `wil_fw_record_gateway_data`, and `wil_fw_record_gateway_data4`. Magic constants identify capabilities, concurrency, and board metadata stored inside comment records.

## Control Flow
There is no executable control flow in the header. The parser in `fw_inc.c` reads a `wil_fw_record_head`, uses `type` and `size` to dispatch to a handler, and interprets the following packed structure according to the definitions here. The file header record must appear first, carries CRC and total data length, and may carry a version string using `WIL_FW_VERSION_PREFIX`.

## State And Persistence
The structures describe persistent firmware/board-file bytes. Runtime state derived from them includes firmware capability bitmaps, interface concurrency combinations, board-file target addresses and limits, firmware version text, and device memory contents written during firmware load.

## Dependencies And Integration Points
Types use Linux endian annotations and flexible array declarations. The records integrate with WMI capability enums, cfg80211 interface combinations, `wil6210_priv` firmware mapping, and board-file download logic.

## Risks
Every structure is `__packed` and endian-sensitive. Extending the format requires careful versioning because `fw_inc.c` rejects file-header versions greater than `WIL_FW_FMT_VERSION` and unknown record types. Variable-length records must be bounds-checked before dereference; this is especially important for concurrency and board metadata.

## Test Signals
Useful tests include malformed record sizes, unaligned lengths, unsupported header versions, bad signatures, bad CRCs, truncated variable arrays, unknown record types, and valid images containing each supported record type.
