# sources/distributed-fs/ceph-client/drivers/mtd/tests/nandbiterrs.c

## Purpose
Tests NAND ECC recovery by using one selected page and either injecting increasing bit errors or repeatedly overwriting the same pattern until physical bit errors appear.

## Important APIs, Types, and Functions
Module parameters are `dev`, `page_offset`, `seed`, and `mode`. Helpers include `hash()` for deterministic page data, `write_page()`, `rewrite_page()` using raw `mtd_write_oob()` without ECC/OOB writes, `read_page()` which measures corrected ECC count via `mtd->ecc_stats`, `verify_page()`, `insert_biterror()`, `incremental_errors_test()`, and `overwrite_test()`.

## Control Flow
Init opens the selected MTD, requires NAND, calculates target offset/eraseblock/subpage layout, allocates one-page buffers, erases the block, runs the selected mode, then erases the block again on success. Incremental mode writes known data, raw-rewrites progressively corrupted data with one additional cleared bit per subpage, reads through ECC, and stops when read fails. Overwrite mode repeatedly writes the same data and records a corrected-bit histogram until failure or `max_overwrite`.

## State and Persistence
The test erases and rewrites the target eraseblock. It intentionally leaves the block unerased on failure for inspection. Runtime state includes page buffers, selected offset, subpage counts, and ECC stat deltas.

## Dependencies and Integration Points
Depends on NAND MTD semantics, raw OOB write support, ECC stats, and shared `mtd_test` helpers.

## Risks
This is destructive for the selected eraseblock. Raw writes bypass ECC and may depend on controller support. The init path sets `err = -EIO` after success before printing success, so module load behavior should be checked carefully against expected test-module conventions.

## Test Signals
Logs show corrected bit counts, ECC failure thresholds, histograms, and final success/failure. Run on expendable NAND pages only.
