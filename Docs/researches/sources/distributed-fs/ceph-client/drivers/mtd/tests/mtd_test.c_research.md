# sources/distributed-fs/ceph-client/drivers/mtd/tests/mtd_test.c

## Purpose
Provides shared helper functions for MTD test modules: erase an eraseblock, scan bad blocks, erase only good blocks, and perform full-length checked reads/writes.

## Important APIs, Types, and Functions
Exported GPL symbols are `mtdtest_erase_eraseblock()`, `mtdtest_scan_for_bad_eraseblocks()`, `mtdtest_erase_good_eraseblocks()`, `mtdtest_read()`, and `mtdtest_write()`. `is_block_bad()` wraps `mtd_block_isbad()` and logs bad eraseblocks.

## Control Flow
Erase helpers build `struct erase_info` and call `mtd_erase()`. Bad-block scanning skips devices that cannot have bad blocks and otherwise fills a caller-provided bad-block table. Read/write helpers call MTD core APIs, treat corrected bitflips as successful reads, enforce full transfer length, and log failing addresses.

## State and Persistence
The helper can erase and write flash through callers. It does not maintain its own persistent state; caller-owned BBT arrays hold scan results.

## Dependencies and Integration Points
All destructive test modules include `mtd_test.h` and link to these exported helpers through the test Makefile. It depends on MTD core APIs and kernel scheduling/printk support.

## Risks
Helpers perform real erase/write operations and rely on callers to restrict device and range. `mtdtest_read()` masks corrected bitflip returns, which is appropriate for tests that care about data correctness but hides ECC correction counts.

## Test Signals
Build/link tests should resolve exported symbols. Runtime signals are logs for erase/read/write failures and correct BBT population on NAND devices.
