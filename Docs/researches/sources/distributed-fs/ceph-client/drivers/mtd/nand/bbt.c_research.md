# sources/distributed-fs/ceph-client/drivers/mtd/nand/bbt.c

Purpose: provides the generic in-memory NAND bad block table (BBT) cache used by the NAND core to track eraseblock status values.

Important APIs and types: exported functions are `nanddev_bbt_init()`, `nanddev_bbt_cleanup()`, `nanddev_bbt_update()`, `nanddev_bbt_get_block_status()`, and `nanddev_bbt_set_block_status()`. The cache is `nand->bbt.cache`, a packed bitmap where each eraseblock consumes `fls(NAND_BBT_BLOCK_NUM_STATUS)` bits.

Control flow: init allocates enough bitmap bits for all eraseblocks. Get validates the entry, computes the containing word and bit offset, stitches across a word boundary when necessary, and masks the status field. Set validates the entry, clears and writes the packed status bits, and handles cross-word writes. Update is currently a no-op because on-flash BBT persistence is not implemented in this generic layer.

State and persistence: the BBT is volatile memory only. It can cache unknown, good, worn, factory-bad, or reserved status values, but persistence to NAND is intentionally absent here; low-level bad-block markers and future on-flash BBT support are separate concerns.

Dependencies and integration points: used by `nanddev_isbad()`, `nanddev_markbad()`, and `nanddev_isreserved()` in `core.c`. Depends on NAND geometry helpers, bitmap allocation/free, and exported GPL symbols for NAND drivers.

Risks and test signals: packed-bit arithmetic is the main risk, especially statuses crossing `BITS_PER_LONG`. Tests should cover entry 0, last entry, out-of-range entries, all status enum values, cross-word offsets on 32-bit and 64-bit builds, cleanup after failed init callers, and the current no-op behavior of `nanddev_bbt_update()`.
