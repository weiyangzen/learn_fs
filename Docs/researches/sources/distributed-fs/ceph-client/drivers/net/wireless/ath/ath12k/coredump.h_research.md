# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/coredump.h

## Purpose
Defines the ath12k firmware coredump file format, TLV payload format, dump type enum, and no-op fallbacks when coredump support is disabled.

## Important APIs, Types, And Functions
Defines `ATH12K_FW_CRASH_DUMP_V2`, `COREDUMP_TLV_HDR_SIZE`, `enum ath12k_fw_crash_dump_type`, `struct ath12k_tlv_dump_data`, and `struct ath12k_dump_file_data`. The enabled declarations are `ath12k_coredump_get_dump_type()`, `ath12k_coredump_upload()`, and `ath12k_coredump_collect()`; disabled builds return `FW_CRASH_DUMP_TYPE_MAX` and no-op.

## Control Flow
No runtime flow beyond compile-time selection by `CONFIG_ATH12K_COREDUMP`. The structures are filled by HIF/core coredump code and consumed by Linux devcoredump readers.

## State And Persistence
The dump file header persists magic, total length, version, chip/QRTR/bus IDs, GUID, timestamps, reserved bytes, and trailing TLV data. TLV records persist a little-endian type and length followed by aligned data.

## Dependencies And Integration Points
Depends on QMI memory type declarations and Linux GUID/little-endian types through included users. It is included by `core.h`, making coredump state part of `ath12k_base`.

## Risks
This is a binary format contract; changing packed layout breaks tooling. Comments still mention ath11k in one TLV field comment, which is harmless but confusing. Disabled-build stubs must preserve call-site behavior during recovery.

## Test Signals
Build with and without `CONFIG_ATH12K_COREDUMP`. Validate generated dump headers with external parsers and confirm TLV lengths align to the collected memory regions.
