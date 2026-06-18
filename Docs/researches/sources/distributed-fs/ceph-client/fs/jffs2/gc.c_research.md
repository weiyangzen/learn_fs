# sources/distributed-fs/ceph-client/fs/jffs2/gc.c

## Purpose
`gc.c` implements one-pass JFFS2 garbage collection. It checks unchecked inodes, chooses victim eraseblocks, copies or rewrites live nodes, removes obsolete deletion dirents when safe, and schedules fully dirty blocks for erasure.

## Important APIs, Types, And Functions
The public API is `jffs2_garbage_collect_pass()`. Internal helpers include `jffs2_find_gc_block()`, `jffs2_garbage_collect_live()`, `jffs2_garbage_collect_pristine()`, `jffs2_garbage_collect_metadata()`, `jffs2_garbage_collect_dirent()`, `jffs2_garbage_collect_deletion_dirent()`, `jffs2_garbage_collect_hole()`, and `jffs2_garbage_collect_dnode()`.

## Control Flow
Each pass locks `alloc_sem`. If unchecked space remains, it walks inode-cache buckets, runs CRC checks on one unchecked inode, and returns. Otherwise it erases pending/completed blocks if possible, selects a GC block by weighted lists, skips obsolete refs, resolves the owning inode/xattr, and chooses a fast pristine copy or a slow rewrite path. Live dnodes may be merged to page boundaries, read through page cache, recompressed, and written as new raw inode nodes. When a GC block has no used bytes left, it moves to `erase_pending_list`.

## State And Persistence Behavior
GC persists replacement raw inode/dirent nodes or copied raw bytes, then marks old refs obsolete. It mutates `c->gcblock`, eraseblock list membership, node refs, inode-cache states, fragment trees, dirent lists, metadata pointers, compression statistics, and erase scheduling counters.

## Dependencies And Integration Points
It depends on inode-cache state from `nodelist.h`, MTD flash read/write helpers, CRC32, page cache, compression APIs, xattr GC hooks, reservation functions, erase scheduling, and VFS inode fetch/release from `fs.c`.

## Risks And Test Signals
GC is concurrency-sensitive: it drops locks when waiting for inode reads, must not race final `iput()` of unlinked inodes, and must avoid page-cache deadlocks with writes. Deletion dirents are only discardable on media that can mark obsolete nodes or after scanning older matching dirents. Tests should include unchecked CRC progress, GC under ENOSPC, corrupt pristine CRC fallback, hole-node rewrite, page merge behavior, deletion dirent retention on NAND, xattr nodes, unlinked open files, and repeated passes making measurable dirty-space progress.
