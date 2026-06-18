# sources/distributed-fs/ceph-client/include/linux/mtd/mtdram.h

## Purpose

Declares the helper for creating a RAM-backed MTD device.

## Important APIs, Types, and Functions

The exported API is `mtdram_init_device(struct mtd_info *mtd, void *mapped_address, unsigned long size, const char *name)`.

Source-visible symbols include structs: none visible in this header; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__MTD_MTDRAM_H__`.

## Control Flow

A caller provides an `mtd_info`, backing memory, size, and name; the implementation initializes MTD callbacks that emulate flash operations over RAM.

## State and Persistence Behavior

Runtime state is the caller-provided mapped memory and initialized `mtd_info`; contents persist only as long as RAM is retained.

## Dependencies and Integration Points

It depends on the MTD core and the mtdram implementation.

Direct includes observed in the source are: `#include <linux/mtd/mtd.h>`.

## Risks and Edge Cases

The backing address and size must remain valid for the MTD lifetime. RAM-backed semantics may not reproduce erase/program constraints of real flash.

## Test Signals

Initialize small devices, exercise read/write/erase boundaries, and verify unregister/lifetime cleanup.

Source read signal: 9 lines, 257 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
