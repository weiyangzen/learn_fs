# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/pagecache.c

Purpose: implements bcachefs per-folio sector state, reservation handling, dirtying/undirtying, mmap fault support, invalidation/release hooks, and pagecache data/hole scanning.

Key behavior:
- `bch2_filemap_get_contig_folios_d()` gets contiguous folios, limiting creation after a 1 MiB window.
- `bch2_write_invalidate_inode_pages_range()` repeatedly writes and invalidates pagecache ranges until pages are gone or an error occurs.
- `bch2_folio_set()` initializes per-sector folio state from extent btree records and publishes cached sequential reservation state into `bch_inode_info`.
- Tracks sector states: unallocated, reserved, dirty, dirty_reserved, allocated.
- Manages disk and quota reservations before dirtying folios, including partial reservation support.
- `bch2_set_folio_dirty()` consumes reservations, updates per-sector state and `i_blocks`, and dirties the folio.
- `bch2_vfs_dirty_folio()` handles generic VFS dirty callbacks by obtaining nofail reservations.
- `bch2_page_fault()` coordinates page faults with pagecache blocking and fault-disabled mappings.
- `bch2_page_mkwrite()` reserves space, updates file time, marks folio dirty, waits for stable writes, and schedules delayed inode writeback.
- Invalidate/release hooks clear per-folio bcachefs state and return reservations.
- Seek helpers scan pagecache for dirty data or holes and are used by fiemap, fallocate, and `SEEK_DATA`/`SEEK_HOLE`.

Important interactions:
- This file is the in-memory contract between VFS pagecache and bcachefs COW allocation semantics.
- Callers must respect lock ordering: btree locks cannot be held while blocking on folio locks unless locks are dropped and reacquired.
