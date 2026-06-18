# sources/distributed-fs/ceph-client/drivers/mtd/tests/subpagetest.c

## Purpose
Destructively validates NAND subpage write/read behavior for single subpages and variable multiples of the subpage size, including erased-state verification.

## Important APIs, Types, and Functions
Module parameter `dev` selects the MTD. Helpers include `write_eraseblock()`, `write_eraseblock2()`, `verify_eraseblock()`, `verify_eraseblock2()`, `verify_eraseblock_ff()`, and `verify_all_eraseblocks_ff()`. `subpgsize` is derived from `mtd->writesize >> mtd->subpage_sft`.

## Control Flow
Init requires NAND, computes subpage and eraseblock geometry, allocates buffers sized for up to 32 subpages, scans bad blocks, erases the device, writes two subpages per good eraseblock and verifies them, erases and verifies all-`0xff`, then writes variable-size subpage multiples across each eraseblock and verifies again before a final erased-state check.

## State and Persistence
The selected MTD is erased and rewritten. Expected data is regenerated from deterministic prandom seeds. `errcnt` counts compare failures.

## Dependencies and Integration Points
Depends on NAND subpage support exposed through MTD geometry, raw MTD read/write calls, shared erase/BBT helpers, and prandom.

## Risks
Destructive. Some NAND/controllers restrict partial-page writes or require specific alignment; this test will expose those limitations. The buffer size limits variable writes to 32 subpages per operation.

## Test Signals
Success logs write/verify progress, all-`0xff` verification, and final zero errors. Failures print addresses and, for the first two subpage checks, written/read subpage dumps.
