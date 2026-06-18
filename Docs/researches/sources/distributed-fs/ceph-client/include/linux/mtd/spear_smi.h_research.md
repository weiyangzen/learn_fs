# sources/distributed-fs/ceph-client/include/linux/mtd/spear_smi.h

## Purpose

Defines platform data for ST SPEAr SMI serial NOR controller instances.

## Important APIs, Types, and Functions

Key items are `MAX_NUM_FLASH_CHIP`, `DEFINE_PARTS`, `struct spear_smi_flash_info`, and `struct spear_smi_plat_data`.

Source-visible symbols include structs: `struct spear_smi_flash_info`, `struct mtd_partition *partitions;`, `struct spear_smi_plat_data`, `struct spear_smi_flash_info *board_flash_info;`, `struct device_node *np[MAX_NUM_FLASH_CHIP];`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__MTD_SPEAR_SMI_H`, `MAX_NUM_FLASH_CHIP`, `DEFINE_PARTS`.

## Control Flow

Platform code supplies controller clock rate, flash count, per-flash mapped base/size/fast-mode/partition data, and DT nodes; the SMI driver probes up to four serial NOR chips.

## State and Persistence Behavior

This is static platform/board configuration. Runtime MTD and controller state are allocated by the SMI driver.

## Dependencies and Integration Points

It depends on MTD core, partitions, platform devices, and device tree.

Direct includes observed in the source are: `#include <linux/types.h>`, `#include <linux/mtd/mtd.h>`, `#include <linux/mtd/partitions.h>`, `#include <linux/platform_device.h>`, `#include <linux/of.h>`.

## Risks and Edge Cases

Incorrect memory base/size or fast-mode capability can break reads, and partition macros must not create overlapping regions.

## Test Signals

Multi-flash probe, fast/slow mode selection, DT-node matching, and partition registration.

Source read signal: 66 lines, 1793 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
