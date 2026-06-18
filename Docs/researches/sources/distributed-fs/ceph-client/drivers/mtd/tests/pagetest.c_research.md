# sources/distributed-fs/ceph-client/drivers/mtd/tests/pagetest.c

## Purpose
Destructively tests NAND page read/write correctness, page boundary behavior, read data-register isolation, erase effects, and eraseblock cross-interference.

## Important APIs, Types, and Functions
Module parameter `dev` selects the MTD. Helpers include `write_eraseblock()`, `verify_eraseblock()`, `crosstest()`, `erasecrosstest()`, and `erasetest()`. Buffers include one eraseblock of random data, two-page read buffers, a boundary expected buffer, and a BBT.

## Control Flow
Init opens a NAND MTD, computes page and eraseblock counts, allocates buffers, scans bad blocks, erases the device, writes deterministic random data to all good eraseblocks, verifies each block with two-page reads including eraseblock boundary checks, then performs crosstest, erasecrosstest when enough blocks exist, and erasetest.

## State and Persistence
The whole selected MTD is erased and rewritten. Runtime state is deterministic prandom seed, geometry values, `errcnt`, and bad-block table. The test leaves whatever final erase/write state the sequence produced.

## Dependencies and Integration Points
Depends on NAND MTD read/write/erase behavior, shared helpers, and bad-block handling. It uses two-page reads to catch controller data buffer problems.

## Risks
This test wipes data. It assumes enough good blocks for boundary and cross tests; some subtests are skipped or constrained when bad blocks occupy ends. Verification reads adjacent pages and eraseblock boundaries, so geometry misreporting can produce false failures or expose driver bugs.

## Test Signals
Progress logs for writing/verifying all eraseblocks, "crosstest ok", "erasecrosstest ok", "erasetest ok", and final zero `errcnt` indicate success.
