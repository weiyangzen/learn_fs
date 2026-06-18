# sources/distributed-fs/ceph-client/include/linux/mtd/flashchip.h

## Purpose

Provides common NOR/OneNAND-style flash-chip state tracking used by map and chip drivers while erase, write, suspend, sync, lock, and XIP operations are in flight.

## Important APIs, Types, and Functions

Key types are `flstate_t`, `struct flchip`, and `struct flchip_shared`. The state enum unifies historical NOR, NAND, and OneNAND operation states such as `FL_READY`, `FL_ERASING`, `FL_WRITING`, `FL_PM_SUSPENDED`, `FL_READING`, and `FL_CACHEDPRG`.

Source-visible symbols include structs: `struct flchip`, `struct mutex mutex;`, `struct flchip_shared`, `struct mutex lock;`, `struct flchip *writing;`, `struct flchip *erasing;`; enums: none visible in this header; typedefs: `typedef enum {`; prototypes: none visible in this header; representative macros: `__MTD_FLASHCHIP_H__`.

## Control Flow

Chip drivers change `flchip.state` while holding `flchip.mutex`, sleep on `flchip.wq` while another operation owns the device, and use `flchip_shared` to prevent write/erase contention across partitions that address the same physical chip.

## State and Persistence Behavior

All state is volatile kernel state: current and old operation state, suspend bits, in-progress block address/mask, timing estimates, point-reference counts, and driver private data.

## Dependencies and Integration Points

It depends on scheduler, mutex, and waitqueue primitives. Integration points are CFI/JEDEC map drivers, LPDDR/PFOW code, and OneNAND code that share the same state vocabulary.

Direct includes observed in the source are: `#include <linux/sched.h>`, `#include <linux/mutex.h>`, `#include <linux/wait.h>`.

## Risks and Edge Cases

Incorrect state transitions can deadlock waiters, permit erase/write overlap across partitions, or resume the wrong suspended operation. Timing fields are policy inputs and must match actual device behavior closely enough for robust wait logic.

## Test Signals

Stress read/write/erase/suspend/resume paths, partition contention, point/unpoint reference accounting, and shutdown/unload transitions.

Source read signal: 100 lines, 2502 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
