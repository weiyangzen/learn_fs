# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/buffered.c

Purpose: Buffered VFS read, readahead, writeback, and buffered-write implementation for bcachefs.

Key APIs and behavior:
- Readahead collects folios, creates bcachefs folio state, extends bios across extents when profitable, and submits reads through bcachefs extent lookup.
- `bch2_read_single_folio()` performs synchronous single-folio reads for page faults/write preparation.
- Writeback builds `bch_writepage_io` bios from dirty folio-sector ranges, throttles against allocator/journal pressure, and accounts sectors on completion.
- `bch2_write_begin()` and `bch2_write_end()` implement buffered write reservation, partial-folio read/zero handling, dirty marking, i_size update, and reservation release.
- `bch2_buffered_write()` performs multi-folio atomic user copies with fault-in, fallback for short/no copies, dirty balancing, and pagecache cleanup after short post-EOF writes.
- `bch2_write_iter()` dispatches direct IO separately and serializes buffered writes against snapshot creation.

Integration:
- Uses bcachefs read/write paths, btree transactions, snapshot lookup/locks, pagecache helpers, folio reservations, allocator/journal waiters, and Linux writeback APIs.
- Declared in `buffered.h`; also calls direct-write API from `direct.h`.

Risks and invariants:
- `bchfs_read()` temporarily mutates `bio.bi_iter.bi_size`; comments warn transaction-restart behavior would be dangerous there.
- Writeback relies on per-sector folio state and write counts to end writeback exactly once.
- Buffered writes assume synchronous same-task lock/unlock around snapshot create lock.
