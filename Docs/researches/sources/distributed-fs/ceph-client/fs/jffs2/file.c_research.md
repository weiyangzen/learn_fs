# sources/distributed-fs/ceph-client/fs/jffs2/file.c

## Purpose
`file.c` implements regular file operations and address-space operations for JFFS2. It connects generic VFS buffered I/O to JFFS2's fragment tree and append-only raw inode node writes.

## Important APIs, Types, And Functions
Exported tables are `jffs2_file_operations`, `jffs2_file_inode_operations`, and `jffs2_file_address_operations`. Important functions are `jffs2_fsync()`, `jffs2_do_readpage_nolock()`, `__jffs2_read_folio()`, `jffs2_read_folio()`, `jffs2_write_begin()`, and `jffs2_write_end()`.

## Control Flow
Reads lock `f->sem`, map the folio, call `jffs2_read_inode_range()` for a page-sized range, mark the folio uptodate, flush dcache, and unlock. `write_begin()` handles sparse writes beyond EOF by writing a zero-compressed hole node, then locks `alloc_sem` while obtaining/reading the target folio to avoid GC read deadlocks. `write_end()` writes the modified page range, expanding to a whole page when the write reaches page end, via `jffs2_write_inode_range()`, updates size/timestamps/blocks, and marks the folio not uptodate if fewer bytes reached flash.

## State And Persistence Behavior
Persistent writes create new raw inode data or hole nodes. In-core updates include folio uptodate state, inode size/block/timestamps, `f->fragtree`, `f->metadata`, and raw-node obsolete marking. `jffs2_fsync()` waits on writeback and flushes the write buffer for the inode via GC-flush helpers.

## Dependencies And Integration Points
The file depends on generic file helpers, page/folio APIs, CRC32, `jffs2_read_inode_range()`, `jffs2_write_inode_range()`, reservation/write helpers, compression indirectly through write code, and write-buffer flush helpers.

## Risks And Test Signals
The lock ordering between folio locks, `f->sem`, and `c->alloc_sem` is critical for avoiding GC/write deadlocks. Short writes must correctly invalidate cache state. Tests should cover sparse writes, partial writes under ENOSPC, writes at page boundaries, fsync with write-buffered media, concurrent GC and writes to the same page, mmap-read behavior, and data integrity after remount.
