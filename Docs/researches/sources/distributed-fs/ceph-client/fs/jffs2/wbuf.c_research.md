# sources/distributed-fs/ceph-client/fs/jffs2/wbuf.c

## Purpose

`wbuf.c` implements write-buffer support for flash media that cannot be programmed byte-by-byte, including NAND, DataFlash, non-bitwriteable NOR, and UBI volumes with writesize greater than one. It batches writes into page/programming-unit buffers, merges reads with pending buffer contents, manages delayed flushes, handles NAND OOB cleanmarkers and bad-block marking, and attempts recovery after page-write failures.

## Important APIs, Types, And Functions

Main exported functions include `jffs2_flash_writev()`, `jffs2_flash_write()`, `jffs2_flash_read()`, `jffs2_flush_wbuf_gc()`, `jffs2_flush_wbuf_pad()`, OOB helpers (`jffs2_check_oob_empty()`, `jffs2_check_nand_cleanmarker()`, `jffs2_write_nand_cleanmarker()`, `jffs2_write_nand_badblock()`), delayed flush trigger `jffs2_dirty_trigger()`, and media setup/cleanup functions for NAND, DataFlash, NOR write-buffer flash, and UBI.

Important internal routines are `jffs2_wbuf_pending_for_ino()`, `jffs2_wbuf_dirties_inode()`, `jffs2_refile_wbuf_blocks()`, `jffs2_block_refile()`, `jffs2_incore_replace_raw()`, optional `jffs2_verify_write()`, `jffs2_wbuf_recover()`, `__jffs2_flush_wbuf()`, and `jffs2_fill_wbuf()`.

## Control Flow

Buffered writes enter `jffs2_flash_writev()`. If buffering is disabled it delegates to direct writev. Otherwise it takes `wbuf_sem`, initializes `wbuf_ofs` on first use, flushes if writing into a new eraseblock, enforces contiguous writes, fills the buffer from input kvecs, writes full pages directly or through `__jffs2_flush_wbuf()`, records summary data, and marks the affected inode dirty for delayed flush if non-GC data remains buffered.

`__jffs2_flush_wbuf()` requires `alloc_sem`, optionally pads the current page with dirty or padding-node bytes, writes one page through MTD, verifies when configured, and on failure calls `jffs2_wbuf_recover()`. On success it accounts padding as wasted/obsolete, refiles eraseblocks pending on the write buffer, clears dirty inode tracking, advances `wbuf_ofs`, and empties the buffer.

`jffs2_wbuf_recover()` handles failed page writes by refiling the failed block as bad-used or erase-pending, identifying non-obsolete raw refs affected by the failed buffer range, reading any already-written prefix if possible, reserving space in a new block, disabling summary for the recovery block, rewriting recoverable data, and replacing raw refs in inode/xattr in-core structures.

Reads use `jffs2_flash_read()`, which performs MTD read and then overlays any overlapping pending write-buffer bytes before returning. ECC clean/uncorrectable codes with full retlen are treated as success so higher-level node CRC validation can decide whether data is usable.

## State And Persistence Behavior

The write buffer stores not-yet-programmed bytes in `c->wbuf`, offset `c->wbuf_ofs`, length `c->wbuf_len`, and page size `c->wbuf_pagesize`. `c->wbuf_inodes` tracks which inodes have pending non-GC writes; on allocation failure it uses `inodirty_nomem` to conservatively treat all inodes as dirty.

Flush and recovery directly affect flash persistence, raw-node refs, eraseblock accounting, and bad-block state. NAND cleanmarkers are persisted in OOB, not inline, so `cleanmarker_size` becomes zero for NAND. Bad blocks are marked through `mtd_block_markbad()` after `MAX_ERASE_FAILURES`.

## Dependencies And Integration Points

The file integrates MTD page writes/reads/OOB operations, raw NAND bad-block APIs, delayed work on `system_long_wq`, dirty writeback timing, summary collection, nodemgmt reservation/accounting, GC passes, inode fetch/release helpers, xattr internals, and Linux read/write semaphores.

## Risks And Edge Cases

This is a high-risk area because failed writes can leave a page partly programmed. Recovery has to preserve live nodes, mark old refs obsolete, update in-core pointers for present inodes, and not trust data that could not be reread. Non-contiguous writes are fatal `BUG()` conditions. Summary collection in `jffs2_flash_writev()` returns before releasing `wbuf_sem` if `jffs2_sum_add_kvec()` fails, which is a suspicious locking risk to inspect if reachable. OOB reads/writes must handle bitflip return codes correctly. Setup paths must free partially allocated buffers on failure.

## Test Signals

Tests should cover buffered writes crossing page and eraseblock boundaries, delayed writeback, fsync/sync flushes, read-after-write before flush, GC-triggered flush by inode, padding modes, direct large-page writes, write failure recovery with live and obsolete refs, secondary recovery failure, ECC `-EUCLEAN` and `-EBADMSG` reads, NAND OOB cleanmarkers, bad-block marking threshold, and setup/cleanup for all supported media types.
