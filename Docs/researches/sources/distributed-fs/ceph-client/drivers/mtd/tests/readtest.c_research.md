# sources/distributed-fs/ceph-client/drivers/mtd/tests/readtest.c

## Purpose
Non-writing MTD test that reads every good eraseblock page-by-page and optionally reads OOB data, reporting and dumping failing eraseblocks.

## Important APIs, Types, and Functions
Module parameter `dev` selects the MTD. `read_eraseblock_by_page()` reads page data via `mtdtest_read()` and OOB via `mtd_read_oob()` in `MTD_OPS_PLACE_OOB`. `dump_eraseblock()` prints data and OOB hex dumps on failure. Init is `mtd_readtest_init()`.

## Control Flow
Init opens the selected MTD, chooses page size (`writesize` or 512 for non-NAND), computes eraseblock/page counts, allocates data/OOB buffers and a BBT, scans bad blocks, then reads each good eraseblock page-by-page. Any failed block is dumped while the scan continues unless interrupted by `mtdtest_relax()`.

## State and Persistence
No flash writes or erases occur. Runtime state consists of buffers and a bad-block table.

## Dependencies and Integration Points
Depends on MTD read and OOB APIs plus shared helper functions. It can run on NAND and non-NAND MTD, with non-NAND using assumed 512-byte pages.

## Risks
Large failures can produce extensive kernel logs due to hex dumps. OOB reads are attempted only when `mtd->oobsize` is nonzero. Corrected bitflips are treated as successful by `mtdtest_read()`.

## Test Signals
Success prints "finished"; failure prints read/OOB error addresses and dumps the affected eraseblock.
