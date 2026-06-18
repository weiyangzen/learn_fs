# sources/distributed-fs/ceph-client/include/linux/mtd/physmap.h

## Purpose

Defines platform data for the generic physically mapped flash driver.

## Important APIs, Types, and Functions

The main type is `struct physmap_flash_data` with bus width, init/exit/VPP callbacks, PFOW base, probe type, partition list, and partition parser names.

Source-visible symbols include structs: `struct map_info;`, `struct platform_device;`, `struct physmap_flash_data`, `struct mtd_partition	*parts;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_PHYSMAP__`.

## Control Flow

Board/platform code supplies physical map configuration; the physmap driver maps memory, initializes `map_info`, toggles VPP through callbacks, probes the specified chip type, and registers fixed or parsed partitions.

## State and Persistence Behavior

This is static platform configuration. Runtime map and MTD state are created by the physmap driver.

## Dependencies and Integration Points

It depends on MTD core, partition descriptors, platform devices, and map/chip probe infrastructure.

Direct includes observed in the source are: `#include <linux/mtd/mtd.h>`, `#include <linux/mtd/partitions.h>`.

## Risks and Edge Cases

Wrong width, probe type, PFOW base, or VPP callback can prevent detection or make writes unsafe.

## Test Signals

Probe with each configured width, fixed and parser-based partitions, VPP enable/disable counts, and init/exit cleanup.

Source read signal: 31 lines, 808 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
