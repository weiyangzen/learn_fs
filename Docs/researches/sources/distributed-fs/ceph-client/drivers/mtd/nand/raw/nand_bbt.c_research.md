# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_bbt.c

## Purpose
`nand_bbt.c` implements bad-block table support for the raw NAND core. It scans factory bad-block markers, creates the in-memory two-bit-per-block BBT, finds or writes flash-resident BBTs and mirrors, marks BBT storage blocks as reserved, and exposes query/update APIs used by `nand_base.c`.

## Important APIs, types, and functions
- The in-memory table uses two bits per eraseblock with internal values `BBT_BLOCK_GOOD`, `BBT_BLOCK_WORN`, `BBT_BLOCK_RESERVED`, and `BBT_BLOCK_FACTORY_BAD`.
- Public APIs are `nand_create_bbt()`, `nand_isreserved_bbt()`, `nand_isbad_bbt()`, and `nand_markbad_bbt()`.
- Scanning helpers include `scan_block_fast()`, `create_bbt()`, `search_bbt()`, `search_read_bbts()`, and `nand_memory_bbt()`.
- Flash BBT helpers include `read_bbt()`, `read_abs_bbt()`, `read_abs_bbts()`, `get_bbt_block()`, `write_bbt()`, `check_create()`, `nand_update_bbt()`, and `mark_bbt_region()`.
- Descriptor setup is handled by `nand_create_badblock_pattern()` plus the default main/mirror descriptors for OOB and no-OOB BBT markers.

## Control flow
`nand_create_bbt()` selects default flash BBT descriptors when `NAND_BBT_USE_FLASH` is set, otherwise forces a RAM-only table. It ensures a bad-block marker descriptor exists and then calls `nand_scan_bbt()`. `nand_scan_bbt()` allocates the RAM BBT, either scans the device directly when no flash descriptor exists, or searches/reads flash BBT descriptors, reconciles missing or stale mirrors through `check_create()`, and reserves BBT regions.

When creating a RAM table, `create_bbt()` walks eraseblocks, reads configured BBM pages through `scan_block_fast()`, and records factory-bad entries. When using flash BBTs, `search_bbt()` searches candidate blocks from the start or end, skips blocks that are bad or conflict with marker areas, validates marker patterns, and records pages and versions. `check_create()` compares primary and mirror versions, decides whether to create, read, rewrite, or scrub tables, reads valid tables into RAM, and writes missing/stale copies.

`write_bbt()` serializes the RAM BBT to flash using the descriptor bit width and reserved-block code. It can preserve block contents, store the marker in the data area for `NAND_BBT_NO_OOB`, write marker/version in OOB otherwise, erase the destination with BBT access allowed, write data plus OOB, and mark failed BBT blocks as worn before retrying another reserved block.

## State and persistence behavior
The primary runtime state is `this->bbt`, a compact RAM bitmap of eraseblock states. Persistent state can be OOB bad-block markers and optional flash BBT blocks, including mirrored versions. Descriptor arrays store selected pages and per-chip versions. `nand_markbad_bbt()` updates the RAM entry and then updates on-flash BBTs when `NAND_BBT_USE_FLASH` is enabled. `mark_bbt_region()` marks BBT storage blocks as reserved in RAM and may write that reservation back to flash when the descriptor carries a reserved-block code.

## Dependencies and integration points
The file depends on MTD read/write/OOB/erase APIs, raw NAND geometry from `struct nand_chip`, marker-page iteration from `nand_bbm_get_next_page()`, bad-block marker writes from `nand_markbad_bbm()`, erase from `nand_erase_nand()`, and expert-analysis behavior from the MTD layer. `nand_base.c` uses these APIs for `block_isbad`, `block_isreserved`, bad-block marking, and scan-tail BBT creation.

## Risks and edge cases
- Flash BBT version comparison uses signed byte subtraction semantics, so wraparound behavior must remain intentional.
- `NAND_BBT_NO_OOB` descriptors have strict constraints; invalid descriptor combinations trigger `BUG_ON()`.
- A failed erase/write of a BBT block marks that block bad and retries, which is correct for flash health but destructive if geometry or descriptor placement is wrong.
- Scanning ignores ECC failures when checking BBM OOB patterns, but ECC errors while reading flash BBTs can invalidate tables and force fallback paths.
- RAM table entries use OR-style marking, so state transitions only add bits; callers must not expect a simple overwrite from bad/reserved back to good.
- The expert analysis mode can report bad/reserved blocks as usable, which is useful diagnostically but risky in normal deployments.

## Test signals
Validation should cover RAM-only BBT creation, flash BBT with and without mirrors, per-chip BBTs, absolute-page descriptors, OOB and no-OOB marker placement, version mismatch and missing mirror repair, bitflip-triggered BBT scrubbing, BBT storage block failures, reserved-block handling, 8-bit and 16-bit BBM descriptors, expert-analysis mode, and `nand_markbad_bbt()` persistence.
