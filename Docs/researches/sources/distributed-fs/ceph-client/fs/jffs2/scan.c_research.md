# sources/distributed-fs/ceph-client/fs/jffs2/scan.c

## Purpose

`scan.c` scans the flash medium at mount time, discovers raw JFFS2 nodes, builds initial inode/xattr caches and eraseblock accounting, classifies eraseblocks, seeds GC lists, and optionally uses summary nodes to avoid a full scan of summarized blocks.

## Important APIs, Types, And Functions

The exported functions are `jffs2_scan_medium()`, `jffs2_scan_classify_jeb()`, `jffs2_scan_make_ino_cache()`, and `jffs2_rotate_lists()`. Internal scan helpers include `jffs2_scan_eraseblock()`, `jffs2_scan_inode_node()`, `jffs2_scan_dirent_node()`, xattr scanners under `CONFIG_JFFS2_FS_XATTR`, `jffs2_fill_scan_buf()`, `file_dirty()`, and list rotation helpers.

Block states come from `summary.h`: `BLK_STATE_ALLFF`, `CLEAN`, `PARTDIRTY`, `CLEANMARKER`, `ALLDIRTY`, and `BADBLOCK`. The scanner manipulates `struct jffs2_eraseblock` lists in `struct jffs2_sb_info`: free, clean, dirty, very-dirty, erase-pending, erasable, bad, and the special `nextblock`.

## Control Flow

`jffs2_scan_medium()` first tries `mtd_point()` over the whole device; if direct mapping is unavailable, it allocates a scan buffer sized for a page or whole eraseblock on NAND. It optionally allocates temporary summary collection state. For each eraseblock it resets collected summary state, calls `jffs2_scan_eraseblock()`, checks accounting, and places the block on the appropriate list based on the returned block state.

`jffs2_scan_eraseblock()` handles NAND OOB cleanmarkers and bad-block detection, then checks for a summary marker at the end of the eraseblock. If a valid summary node is found and `jffs2_sum_scan_sumnode()` returns a block classification, full scanning is skipped. Otherwise the scanner reads the block incrementally, skips erased `0xff` regions, detects wrong-endian/old/dirty magic patterns, validates node header CRCs, rejects nodes extending past the eraseblock, treats non-accurate nodes as dirty, and dispatches supported node types.

Inode nodes are scanned lightly: node CRC is checked, an inode cache is created, and the node is linked as `REF_UNCHECKED` for later inode read/CRC verification. Dirent nodes are more fully checked at scan time, including name CRC, parent inode cache creation, full-dirent allocation, and insertion into `ic->scan_dents`. Xattr and xref nodes create xattr datum/ref structures when configured.

## State And Persistence Behavior

The scanner is mostly reconstructive. It builds the in-memory view of persisted flash state and records unresolved inode data as unchecked until `readinode.c` validates it. It also converts invalid or unknown regions to dirty accounting by calling `jffs2_scan_dirty_space()`. Blocks that appear empty are queued for erase unless cleanmarkers make them usable. A partially dirty block with enough free space can become `c->nextblock`; otherwise it is filed dirty.

At the end of scanning, nextblock dirty bytes are treated as wasted because they cannot be recycled immediately, and write-buffered nextblocks may be aligned to the write-buffer page size by marking a small skip region dirty.

## Dependencies And Integration Points

This file integrates MTD mapping/reads, NAND OOB helpers from `wbuf.c`, summary parsing from `summary.c`, node-ref and inode-cache allocators, xattr subsystem setup, and garbage-collection triggering. `readinode.c` depends on the raw-ref chains and unchecked accounting produced here.

## Risks And Edge Cases

Mount safety is the dominant risk. The code refuses to erase pending blocks if the filesystem contains no valid JFFS2 nodes, preventing accidental erasure of non-JFFS2 data. Summary trust is bounded by CRC checks and can fall back to full scan. Name strings with embedded zeroes are truncated for historical media, and zero at start in a summary dirent aborts mount. Misdetected erase size, wrong endian media, old JFFS2 magic, or nodes over block boundaries are treated as dirty/error conditions.

## Test Signals

Tests should cover empty media, cleanmarker-only blocks, summarized blocks, corrupt summary CRCs, unknown compatible/incompatible nodes, corrupt header/node/name CRCs, NAND OOB cleanmarkers, bad blocks, partially dirty candidate nextblocks, all-dirty blocks, no-valid-node media refusal, and list rotation. Mount-time accounting totals and block list counts are the primary assertions.
