# sources/distributed-fs/ceph-client/include/linux/mtd/onenand_regs.h

## Purpose

Defines the OneNAND memory-map translation, register offsets, command codes, status bits, ECC bits, device-ID fields, and OTP offsets.

## Important APIs, Types, and Functions

This header is macro-only. It includes `ONENAND_MEMORY_MAP()`, register offsets like `ONENAND_REG_COMMAND`, command values such as `ONENAND_CMD_READ/PROG/ERASE/RESET`, system configuration bits, interrupt/status bits, write-protect bits, ECC status masks, and Flex-OneNAND PI/OTP constants.

Source-visible symbols include structs: none visible in this header; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__ONENAND_REG_H`, `ONENAND_MEMORY_MAP`, `ONENAND_REG_MANUFACTURER_ID`, `ONENAND_REG_DEVICE_ID`, `ONENAND_REG_VERSION_ID`, `ONENAND_REG_DATA_BUFFER_SIZE`, `ONENAND_REG_BOOT_BUFFER_SIZE`, `ONENAND_REG_NUM_BUFFERS`, `ONENAND_REG_TECHNOLOGY`, `ONENAND_REG_START_ADDRESS1`, `ONENAND_REG_START_ADDRESS2`, `ONENAND_REG_START_ADDRESS3`, `ONENAND_REG_START_ADDRESS4`, `ONENAND_REG_START_ADDRESS5`, `ONENAND_REG_START_ADDRESS6`, `ONENAND_REG_START_ADDRESS7`.

## Control Flow

OneNAND code writes address/start-buffer registers, issues command values through `ONENAND_REG_COMMAND`, then polls or waits on controller status/interrupt bits and checks ECC/write-protect fields.

## State and Persistence Behavior

The defined state is hardware register state and persistent device OTP/PI fields. The header itself has no runtime storage.

## Dependencies and Integration Points

It is consumed by `onenand.h` and OneNAND controller implementations that perform MMIO word access.

Direct includes observed in the source are: none visible in this header.

## Risks and Edge Cases

Register offsets are word-address translated; treating them as byte offsets without `ONENAND_MEMORY_MAP()` would hit wrong registers. Status-bit handling differs across SLC/MLC/Flex devices.

## Test Signals

Hardware or register-model tests should verify command programming, interrupt clear/status detection, ECC classification, write-protect status, and Flex-OneNAND PI access.

Source read signal: 221 lines, 7217 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
