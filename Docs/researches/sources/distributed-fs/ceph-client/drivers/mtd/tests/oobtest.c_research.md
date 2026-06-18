# sources/distributed-fs/ceph-client/drivers/mtd/tests/oobtest.c

## Purpose
Destructively tests NAND OOB read/write behavior across whole-device writes, block-wide OOB transfers, varying offsets/lengths, bounds checks, and cross-eraseblock OOB reads/writes.

## Important APIs, Types, and Functions
Module parameters are `dev` and `bitflip_limit`. Core helpers are `write_eraseblock()`, `write_whole_device()`, `verify_eraseblock()`, `verify_eraseblock_in_one_go()`, `verify_all_eraseblocks()`, `memcmpshowoffset()`, and `memffshow()`. The module uses `struct mtd_oob_ops` in `MTD_OPS_AUTO_OOB` mode with data length zero.

## Control Flow
Init validates `dev`, requires NAND, allocates buffers/BBT, scans bad blocks, then runs five tests. It erases good blocks before major write phases, writes deterministic pseudo-random OOB bytes, verifies them page-by-page or in one transfer, tests variable OOB offset/length, confirms reads/writes past OOB/device ends fail, and verifies OOB access spanning the boundary between neighboring good eraseblocks.

## State and Persistence
The module erases and writes OOB data across the selected whole MTD device, skipping bad blocks. `errcnt` accumulates verification failures; pseudo-random seeds make expected data deterministic.

## Dependencies and Integration Points
Depends on NAND OOB availability, MTD OOB API, bad-block handling, prandom state, and shared MTD test helpers.

## Risks
This test wipes the specified MTD device. It assumes `mtd->oobavail` and page/eraseblock geometry are stable. Bitflip tolerance can hide small OOB differences if `bitflip_limit` is set. Some controllers may restrict OOB operations differently, producing expected failures.

## Test Signals
Successful logs progress through "test 1 of 5" to "test 5 of 5" and finish with zero errors. Boundary and out-of-range tests should explicitly log expected errors.
