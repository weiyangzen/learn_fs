# sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/onenand_bbt.c

## Purpose
`onenand_bbt.c` implements the memory-resident bad block table used by the generic OneNAND core. It scans factory bad-block markers in OOB, builds a two-bit-per-block RAM table, and provides the `isbad_bbt` callback used by `onenand_base.c`.

## Important APIs, Types, and Functions
The public function is `onenand_default_bbt(struct mtd_info *mtd)`, which allocates `struct bbm_info`, selects the default marker descriptor, and calls `onenand_scan_bbt()`. Internals include `check_short_pattern()`, `create_bbt()`, `onenand_memory_bbt()`, `onenand_isbad_bbt()`, and the static `largepage_memorybased` `struct nand_bbt_descr` with the `{ 0xff, 0xff }` good-block pattern at OOB offset 0.

## Control Flow
`onenand_default_bbt()` installs the default pattern and delegates to `onenand_scan_bbt()`. `onenand_scan_bbt()` allocates `bbm->bbt`, stores the erase shift, defaults `bbm->isbad_bbt`, then calls `onenand_memory_bbt()`. `create_bbt()` iterates all eraseblocks, reads the first two pages' OOB marker bytes with `onenand_bbt_read_oob()`, treats fatal read errors as scan failure, and marks a block bad if the read returns a non-fatal BBT error or if the expected `0xff` pattern is missing. Flex-OneNAND uses `flexonenand_region()` and `mtd->eraseregions[]` to advance by variable erase sizes.

## State and Persistence
The BBT is RAM-only and allocated under `this->bbm->bbt`; it is freed by `onenand_release()`. It mirrors persistent factory or software OOB bad-block markers but does not itself persist to flash. `mtd->ecc_stats.badblocks` is incremented for detected initial bad blocks.

## Dependencies and Integration Points
This file depends on `struct onenand_chip`, `struct bbm_info`, `struct nand_bbt_descr`, `onenand_bbt_read_oob()`, `onenand_block()`, and `flexonenand_region()` from the OneNAND core/header. `onenand_base.c` installs this scanner when platform drivers do not provide a custom `scan_bbt`.

## Risks
The table size uses `this->chipsize` and `this->erase_shift`, while Flex devices may expose variable `mtd->size` and erase regions; scan correctness depends on the Flex advancement logic. The descriptor expects a short OOB pattern at offset 0 and does not do a full empty-page check. Non-fatal read/ECC errors during marker reads cause the block to be marked bad, which is conservative but can reduce usable capacity if read paths are noisy.

## Test Signals
Boot logs should show bad-block scan progress and any initial bad block notices. Tests should verify `mtd->_block_isbad` results before and after `onenand_block_markbad()`, BBT behavior on Flex-OneNAND variable erase regions, scan failure on `ONENAND_BBT_READ_FATAL_ERROR`, and clean release of `bbm->bbt`.
