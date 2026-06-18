# sources/distributed-fs/ceph-client/drivers/mtd/nand/ecc-sw-bch.c

Purpose: implements the generic software BCH NAND ECC engine using the kernel BCH library, supporting multi-bit correction for large-page NAND.

Important APIs and types: exported helpers are `nand_ecc_sw_bch_calculate()`, `nand_ecc_sw_bch_correct()`, `nand_ecc_sw_bch_init_ctx()`, `nand_ecc_sw_bch_cleanup_ctx()`, and `nand_ecc_sw_bch_get_engine()`. The private `nand_ecc_sw_bch_conf` holds the BCH control object, code size, ECC mask, error-location array, request tweak context, and OOB calculation/code buffers.

Control flow: context init requires large-page OOB, installs a large-page OOB layout if none exists, derives step size/strength from user config or defaults, optionally maximizes strength from available OOB space, computes code size, allocates buffers, initializes BCH parameters, builds an erased-page ECC mask, and validates OOB layout capacity. Prepare ignores raw and data-less OOB-only operations, expands partial requests, and on writes calculates BCH ECC for each step and stores it through `mtd_ooblayout_set_eccbytes()`. Finish ignores raw operations, restores write requests, and on reads extracts stored ECC bytes, recalculates ECC, corrects each step through `bch_decode()`, updates `mtd->ecc_stats`, restores the request, and returns max corrected bitflips.

State and persistence: runtime state is per-NAND BCH context and temporary buffers. Persistent state is the ECC bytes written into the NAND OOB layout.

Dependencies and integration points: depends on `lib/bch`, generic NAND ECC request tweaking, MTD OOB layout helpers, and `ecc.c` software engine selection for `NAND_ECC_ALGO_BCH`.

Risks and test signals: risks include invalid BCH parameter derivation, OOB capacity mismatch, erased-page mask correctness, partial request bounce behavior, and stat handling for uncorrectable errors. Tests should cover default config, user config, maximize mode, impossible OOB layouts, raw operations, write ECC placement, one or more corrected bitflips, ECC-area-only errors, uncorrectable pages, and cleanup after allocation failures.
