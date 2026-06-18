# sources/distributed-fs/ceph-client/drivers/mtd/tests/speedtest.c

## Purpose
Measures erase, write, and read throughput for an MTD device using eraseblock, page, two-page, and multi-block erase access patterns.

## Important APIs, Types, and Functions
Module parameters are `dev` and optional `count`. Helpers include `multiblock_erase()`, write/read functions by eraseblock/page/two-pages, timing helpers `start_timing()`, `stop_timing()`, and `calc_speed()`. Init is `mtd_speedtest_init()`.

## Control Flow
Init opens the selected MTD, computes geometry, optionally limits eraseblock count, fills an eraseblock buffer with random data, scans bad blocks, counts good eraseblocks, and runs timed phases: eraseblock write/read, page write/read, two-page write/read, single erase, and multi-block erase sizes from 2 to 64 blocks.

## State and Persistence
The test erases and writes all selected good eraseblocks, so it destroys data. Timing state is held in `ktime_t` globals. Speed is calculated in KiB/s over good eraseblocks.

## Dependencies and Integration Points
Depends on MTD erase/read/write APIs, shared helper functions, bad-block handling, and kernel timing APIs.

## Risks
Destructive to selected range. The speed denominator uses all good eraseblocks for every phase, including multi-block erase loops that may skip around bad blocks, so results are approximate. Non-NAND devices use a 512-byte assumed page size.

## Test Signals
Logs report KiB/s for each phase and any operation errors. Repeating with different `count` values can isolate device regions.
