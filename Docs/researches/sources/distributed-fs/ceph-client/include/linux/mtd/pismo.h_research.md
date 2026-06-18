# sources/distributed-fs/ceph-client/include/linux/mtd/pismo.h

## Purpose

Defines board data for the PISMO memory driver.

## Important APIs, Types, and Functions

The exported type is `struct pismo_pdata`, containing a VPP callback/data pointer and up to five chip-select physical addresses.

Source-visible symbols include structs: `struct pismo_pdata`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_PISMO_H`.

## Control Flow

The PISMO driver consumes this board data to locate chip-select windows and control write/program voltage.

## State and Persistence Behavior

Only platform configuration is represented.

## Dependencies and Integration Points

It integrates with PISMO memory platform code and mapped flash drivers.

Direct includes observed in the source are: none visible in this header.

## Risks and Edge Cases

Incorrect chip-select addresses or VPP callback data can target the wrong memory window or fail writes.

## Test Signals

Probe with populated/empty chip-select entries and verify VPP callback invocation.

Source read signal: 14 lines, 271 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
