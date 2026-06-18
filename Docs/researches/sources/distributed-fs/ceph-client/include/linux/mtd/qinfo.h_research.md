# sources/distributed-fs/ceph-client/include/linux/mtd/qinfo.h

## Purpose

Defines LPDDR flash query-info structures, private chip state, command helpers, fixup IDs, and the LPDDR command-set probe entry.

## Important APIs, Types, and Functions

Key types are `struct lpddr_private`, `struct qinfo_query_info`, and `struct qinfo_chip`; helpers include `lpddr_build_cmd()`, `CMD`, `CMDVAL`, and `lpddr_cmdset()`.

Source-visible symbols include structs: `struct lpddr_private`, `struct qinfo_chip *qinfo;`, `struct flchip chips[] __counted_by(numchips);`, `struct qinfo_query_info`, `struct qinfo_chip`, `struct mtd_info *lpddr_cmdset(struct map_info *);`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_QINFO_H`, `LPDDR_MFR_ANY`, `LPDDR_ID_ANY`, `NUMONYX_MFGR_ID`, `R18_DEVICE_ID_1G`, `CMD`, `CMDVAL`.

## Control Flow

LPDDR probe code reads qinfo records, builds `qinfo_chip` geometry/timing data, initializes `flchip` entries, and uses map-word commands for subsequent command-set operations.

## State and Persistence Behavior

Runtime state includes manufacturer/device IDs, qinfo pointer, chip count, chipshift, and an array of `flchip` state objects. Persistent qinfo data is read from the flash information query area.

## Dependencies and Integration Points

It depends on map, wait/spinlock/delay, MTD core, flashchip state, and partitions.

Direct includes observed in the source are: `#include <linux/mtd/map.h>`, `#include <linux/wait.h>`, `#include <linux/spinlock.h>`, `#include <linux/delay.h>`, `#include <linux/mtd/mtd.h>`, `#include <linux/mtd/flashchip.h>`, `#include <linux/mtd/partitions.h>`.

## Risks and Edge Cases

The flexible array is sized by `numchips`; allocation must match. Query record interpretation controls device size, block size, partitioning, and operation timing.

## Test Signals

Probe known LPDDR qinfo records, fixup manufacturer/device IDs, command-word construction for each bank width, and timing-derived wait behavior.

Source read signal: 92 lines, 2553 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
