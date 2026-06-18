# sources/distributed-fs/ceph-client/include/linux/mtd/plat-ram.h

## Purpose

Defines platform data for generic RAM-backed MTD map devices.

## Important APIs, Types, and Functions

Key items are `PLATRAM_RO`, `PLATRAM_RW`, and `struct platdata_mtd_ram` with map/probe names, partition data, bank width, and optional `set_rw()` control callback.

Source-visible symbols include structs: `struct platdata_mtd_ram`, `struct mtd_partition	*partitions;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_PLATRAM_H`, `PLATRAM_RO`, `PLATRAM_RW`.

## Control Flow

The platform RAM driver uses this data to initialize a map, choose probes/partition parsers, and optionally switch hardware between read-only and writable modes.

## State and Persistence Behavior

Configuration is static platform data; actual contents are in the mapped RAM region.

## Dependencies and Integration Points

It integrates with map probes, partition descriptors, and platform devices.

Direct includes observed in the source are: none visible in this header.

## Risks and Edge Cases

Bank width and read/write control must match the hardware window. The `set_rw()` callback must not race with active MTD writes.

## Test Signals

Probe RO/RW modes, partition registration, bank-width access, and `set_rw()` transitions around writes.

Source read signal: 30 lines, 668 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
