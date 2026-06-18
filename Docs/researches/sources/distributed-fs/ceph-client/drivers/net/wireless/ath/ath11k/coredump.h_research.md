# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/coredump.h

## Purpose
`coredump.h` defines ath11k firmware crash dump types and binary file/TLV layouts, plus enabled or stubbed coredump APIs depending on `CONFIG_DEV_COREDUMP`.

## Important APIs, Types, And Functions
`ATH11K_FW_CRASH_DUMP_V2` is the dump file version. `enum ath11k_fw_crash_dump_type` classifies paging, RDDM, remote memory, pageable, M3, and ignored dump data. `struct ath11k_tlv_dump_data` is a packed TLV payload with type and length. `struct ath11k_dump_file_data` is the packed top-level dump header containing magic, length, version, chip/QRTR/bus IDs, GUID, timestamp, reserved bytes, and flexible data. Prototypes cover dump type mapping, upload, and collect; stubs are emitted when devcoredump is off.

## Control Flow
HIF coredump code is expected to assemble `ath11k_dump_file_data` containing `ath11k_tlv_dump_data` records. Core reset code calls collect, then upload work eventually exposes that file to devcoredump. Disabled builds compile out collection/upload.

## State And Persistence
The structs define the serialized dump format consumed after a crash. Runtime storage is owned by `ath11k_base` until devcoredump takes it.

## Dependencies And Integration Points
This header is included from `core.h` and `coredump.c`, and indirectly used by bus/HIF-specific dump download implementations. Its packed layouts form an external diagnostic artifact, so compatibility matters beyond the kernel module.

## Risks And Test Signals
Changing packed fields or enum semantics can break dump parsers. Build tests must cover `CONFIG_DEV_COREDUMP=y/n`. Runtime tests should validate dump magic/version/length, TLV alignment, timestamps, GUID presence, and that ignored BDF/CALDB regions are not uploaded.
