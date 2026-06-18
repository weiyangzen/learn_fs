# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/pagecache.c

Implements bcachefs pagecache/folio-private state: per-sector allocation/dirty/reservation tracking, disk/quota reservation acquisition, page-fault and mmap write handling, invalidation/release hooks, and pagecache-aware data/hole seeking.

Key entry points:
- `bch2_filemap_get_contig_folios_d()` gathers contiguous folios over a byte range, creating at most the first 1 MiB before switching off creation.
- `bch2_write_invalidate_inode_pages_range()` writes back and invalidates a mapping range, retrying on `-EBUSY`.
- `bch2_folio_set()` initializes folio sector state from extent btree slots.
- `bch2_bio_page_state_set()` stamps folio state from extents represented by completed bios.
- `bch2_mark_pagecache_unallocated()` and `bch2_mark_pagecache_reserved()` adjust cached folio allocation state after remap/fallocate/truncate-style operations.
- `bch2_get_folio_disk_reservation()`, `bch2_folio_reservation_get()`, and `bch2_folio_reservation_get_partial()` reserve disk/quota space for dirtying folio ranges.
- `bch2_set_folio_dirty()`, `bch2_set_folio_undirty()`, and `bch2_vfs_dirty_folio()` transition folio sectors through dirty/reserved states and update accounting.
- `bch2_page_fault()` and `bch2_page_mkwrite()` implement mmap fault/write fault coordination with pagecache locks and reservations.
- `bch2_invalidate_folio()` and `bch2_release_folio()` release bcachefs folio-private state.
- `bch2_seek_pagecache_data()`, `bch2_seek_pagecache_hole()`, and `bch2_clamp_data_hole()` expose pagecache data/hole state to seek and fallocate code.

Core mechanics:
- `struct bch_folio` is allocated as folio private data and contains a spinlock, write count, uptodate flag, and per-sector `struct bch_folio_sector` entries.
- Sector states form a small state machine: unallocated, reserved, dirty, dirty-reserved, and allocated. Helpers dirty, undirty, or reserve states without losing allocation information.
- `bch2_folio_set()` walks extent slots in the inode subvolume and fills each sector with replica count and allocation/reservation/unallocated state.
- Disk reservation needs are computed as desired replicas minus existing replicas minus already-reserved replicas.
- Dirtying a range moves disk reservation sectors into per-sector `replicas_reserved`, consumes quota reservation for newly unallocated sectors, updates `i_blocks`, and dirties the folio through `filemap_dirty_folio()`.
- `bch2_vfs_dirty_folio()` handles generic mm dirtying by nofail-reserving enough space for the in-size part of the folio.
- `bch2_page_fault()` coordinates with the faults-disabled mapping table to avoid pagecache lock-order inversions; on dropped locks it signals SIGBUS so the higher path can retry safely.
- `bch2_page_mkwrite()` starts a page fault, updates file time, locks the folio, validates mapping and size, initializes folio state, reserves space, marks the folio dirty, waits for stable writeback, queues delayed inode writeback, and returns `VM_FAULT_LOCKED`.
- Data/hole helpers inspect dirty/reserved per-sector state in pagecache so cached not-yet-written data participates in `SEEK_DATA`, `SEEK_HOLE`, and fallocate hole clamping.

Important invariants:
- Folio-private state creation requires the folio lock.
- Reservation and dirty transitions require `bch_folio->uptodate`.
- Full-folio invalidation/release clears dirty accounting, releases reservations, and detaches private state; partial invalidation leaves state intact.
- `bch2_release_folio()` refuses to release dirty or writeback folios.
- Pagecache hole/data searches can run nonblocking and return `-EAGAIN` if folio locks cannot be acquired.

Filesystem relevance:
- This file is the bridge between Linux folios and bcachefs extent allocation. It lets buffered writes, mmap writes, fallocate, remap, truncate, and seek reason about sub-folio allocation and dirty state at filesystem-sector granularity.

Notable risks:
- Comments acknowledge that generic mm dirtying may dirty more of a large folio than the exact modified byte range.
- Folios above `i_size` can legitimately be dirtied by mm/GUP/truncate races; writeback must clean up sector dirty bits later.
- `bch2_mark_pagecache_reserved()` updates `*start` before deriving the folio offset, a subtle area to inspect if reservation marking appears off by range.
