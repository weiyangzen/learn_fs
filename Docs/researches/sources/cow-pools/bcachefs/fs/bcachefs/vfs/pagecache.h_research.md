# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/pagecache.h

Defines the bcachefs folio-private data structures, sector state enum, reservation wrapper, folio geometry helpers, and pagecache operation declarations.

Key declarations:
- `typedef DARRAY(struct folio *) folios` is used for dynamic batches of folio pointers.
- `folio_end_pos()`, `folio_sectors()`, `folio_sector()`, and `folio_end_sector()` convert folio geometry to byte and sector ranges.
- `enum bch_folio_sector_state` defines unallocated, reserved, dirty, dirty-reserved, and allocated states.
- `struct bch_folio_sector` stores fully allocated replica count, reserved replica count, and sector state.
- `struct bch_folio` stores the folio-private spinlock, write count, uptodate flag, and variable-length per-sector array.
- `struct bch2_folio_reservation` combines a disk reservation and quota reservation.
- Public declarations cover folio creation/release, state initialization, bio state stamping, pagecache marking, reservation get/put, dirty/undirty transitions, mmap faults, invalidation/release, and pagecache data/hole seeking.

Core mechanics:
- `BCH_WRITEPAGE_BUF_BYTES` computes the worst-case temporary per-folio sector-state snapshot size for `MAX_PAGECACHE_ORDER`.
- `folio_pos_to_s()` converts a file offset inside a folio to a bcachefs sector-state index and asserts the offset lies inside the folio.
- `bch2_folio_release()` requires a locked folio before detaching and freeing private state.
- `inode_nr_replicas()` derives desired data replicas from inode options or filesystem defaults.
- `bch2_folio_reservation_init()` zeroes a reservation wrapper and seeds desired disk replica count.

Important invariants:
- The per-sector state array has one entry per 512-byte sector in the folio.
- `bch2_folio(folio)` returns folio private data and callers generally require it to exist and be uptodate before accounting transitions.
- The comment explains use of `u64` end positions to avoid overflow at maximum supported mapping ranges.

Filesystem relevance:
- This header defines the state model that lets bcachefs track dirty and reserved file data independently of coarse Linux folio dirty bits.
