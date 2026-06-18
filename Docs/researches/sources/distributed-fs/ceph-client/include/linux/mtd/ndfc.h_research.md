# sources/distributed-fs/ceph-client/include/linux/mtd/ndfc.h

## Purpose

Defines platform data for IBM/PowerPC NDFC NAND flash controller instances.

## Important APIs, Types, and Functions

The main type is `struct ndfc_controller_settings`, carrying bank settings and chip-select/platform details used by the NDFC driver.

Source-visible symbols include structs: `struct ndfc_controller_settings`, `struct ndfc_chip_settings`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_NDFC_H`, `NDFC_CMD`, `NDFC_ALE`, `NDFC_DATA`, `NDFC_ECC`, `NDFC_BCFG0`, `NDFC_BCFG1`, `NDFC_BCFG2`, `NDFC_BCFG3`, `NDFC_CCR`, `NDFC_STAT`, `NDFC_HWCTL`, `NDFC_REVID`, `NDFC_STAT_IS_READY`, `NDFC_MAX_BANKS`.

## Control Flow

Platform code passes NDFC timing/bank configuration to the controller driver, which then initializes raw NAND controller resources and partitions.

## State and Persistence Behavior

Only static platform/controller configuration is represented.

## Dependencies and Integration Points

It integrates with raw NAND, platform device setup, and board-specific NDFC resources.

Direct includes observed in the source are: none visible in this header.

## Risks and Edge Cases

Wrong bank or timing configuration causes failed probe or unreliable command/data cycles.

## Test Signals

Board probe validation, chip-select mapping, and read/write/erase smoke tests on NDFC-backed NAND.

Source read signal: 61 lines, 2084 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
