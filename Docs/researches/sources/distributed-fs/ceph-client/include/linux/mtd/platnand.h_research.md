# sources/distributed-fs/ceph-client/include/linux/mtd/platnand.h

## Purpose

Defines legacy platform data containers for raw NAND chips and controllers.

## Important APIs, Types, and Functions

Key types are `struct platform_nand_chip`, `struct platform_nand_ctrl`, and `struct platform_nand_data`, carrying chip scan limits, partition data, options/BBT options, parser names, and optional controller callbacks.

Source-visible symbols include structs: `struct platform_nand_chip`, `struct mtd_partition *partitions;`, `struct platform_nand_ctrl`, `struct platform_nand_data`, `struct platform_nand_chip chip;`, `struct platform_nand_ctrl ctrl;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_PLATNAND_H`.

## Control Flow

A platform NAND driver combines chip-level geometry/options with controller-level `probe`, `remove`, ready, select, command-control, and buffer callbacks, then scans/registers raw NAND through the raw NAND core.

## State and Persistence Behavior

The header stores static platform configuration and a private controller pointer. Runtime state is in `nand_chip` and controller driver objects.

## Dependencies and Integration Points

It depends on partition definitions, raw NAND APIs, and platform devices.

Direct includes observed in the source are: `#include <linux/mtd/partitions.h>`, `#include <linux/mtd/rawnand.h>`, `#include <linux/platform_device.h>`.

## Risks and Edge Cases

Legacy callbacks must match raw NAND command sequencing. Wrong chip count, options, or BBT flags can misdetect chips or lose bad-block metadata.

## Test Signals

Legacy command-control traces, ready polling, partition parser selection, multi-chip scan, and BBT option handling.

Source read signal: 74 lines, 2542 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
