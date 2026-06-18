# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/firmware.h

## Purpose
`firmware.h` defines the S3FWRN5 firmware-update wire protocol structures, return codes, parsed firmware-image representation, firmware runtime state, and exported firmware helper prototypes.

## Important APIs, types, and constants
- Message types are `S3FWRN5_FW_MSG_CMD`, `S3FWRN5_FW_MSG_RSP`, and `S3FWRN5_FW_MSG_DATA`.
- Return codes enumerate bootloader failures such as invalid command, authentication failure, flash failure, address out of range, and invalid parameter.
- `struct s3fwrn5_fw_header` is the packed 4-byte firmware frame header with type, code, and length.
- Command payload structs describe GET_BOOTINFO response, ENTER_UPDATE_MODE sizes, and UPDATE_SECTOR base address.
- `struct s3fwrn5_fw_image` stores parsed firmware-blob metadata and pointers.
- `struct s3fwrn5_fw_info` stores firmware runtime state, selected signature, base/sector metadata, completion, pending response, and parity.

## Control flow and integration
The header is consumed by `firmware.c`, `core.c`, and physical readers that need `S3FWRN5_FW_HDR_SIZE` to distinguish firmware frames from NCI frames. Its prototypes are the only interface the shared core needs for optional update handling.

## State and persistence
The types model in-memory state only. Firmware persistence is external to the driver through Linux firmware files; pointers in `s3fwrn5_fw_image` are valid only while the requested firmware object is held.

## Dependencies and risks
The header relies on kernel integer types, `struct firmware`, `struct completion`, `struct sk_buff`, and `struct nci_dev` through included/including files. Protocol structs use native-endian integer fields as written by the C code; portability depends on the chip and firmware format matching the driver's endianness assumptions.

## Test signals
Compile coverage should verify all consumers agree on header size and struct layout. Runtime tests should validate command/response parsing against real bootloader frames and check return-code mapping to driver errors.
