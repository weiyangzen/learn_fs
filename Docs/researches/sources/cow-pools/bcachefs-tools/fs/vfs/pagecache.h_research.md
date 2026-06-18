# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/pagecache.h

Purpose: declares per-folio bcachefs pagecache structures, state helpers, reservation APIs, and pagecache scanning interfaces.

Key contents:
- `folios` dynamic array typedef for `struct folio *`.
- Safe `folio_end_pos()`, `folio_sectors()`, `folio_sector()`, and `folio_end_sector()` helpers using `u64` where needed to avoid overflow near maximum file offsets.
- Sector state enum generated from `BCH_FOLIO_SECTOR_STATE()`.
- `struct bch_folio_sector` stores fully allocated replica count, reserved replica count, and sector state.
- `struct bch_folio` stores a lock, write count, state-uptodate flag, and flexible sector-state array.
- `BCH_WRITEPAGE_BUF_BYTES` computes worst-case per-folio state snapshot size for writepage buffer pool sizing.
- Declares folio initialization, pagecache mark/unmark, reservation get/put, dirty/undirty, fault, invalidate/release, and seek helpers.

Important interactions:
- Included by `pagecache.c`, `fiemap.c`, `io.c`, and address-space operations.
- The `inode_nr_replicas()` helper derives required replicas from inode options or filesystem default.
