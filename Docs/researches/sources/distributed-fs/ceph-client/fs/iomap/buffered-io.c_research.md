<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/buffered-io.c -->
# sources/distributed-fs/ceph-client/fs/iomap/buffered-io.c

## Purpose

`sources/distributed-fs/ceph-client/fs/iomap/buffered-io.c` implements the generic iomap buffered page-cache path: folio read and readahead, per-block uptodate/dirty tracking for large folios, buffered writes, inline-data handling, delalloc reservation cleanup after short writes, unshare, zero/truncate-page helpers, page-mkwrite, and writeback over iomap mappings. It is a central library used by filesystems such as XFS and others that describe file layout through iomap iterators.

## Important APIs, Types, and Functions

The local `struct iomap_folio_state` tracks per-folio block uptodate bits, dirty bits, pending read bytes, and pending writeback bytes. Exported read helpers include `iomap_finish_folio_read()`, `iomap_read_folio()`, `iomap_readahead()`, and `iomap_is_partially_uptodate()`. Folio lifecycle helpers include `iomap_get_folio()`, `iomap_release_folio()`, `iomap_invalidate_folio()`, and `iomap_dirty_folio()`.

Exported write and maintenance helpers include `iomap_file_buffered_write()`, `iomap_write_delalloc_release()`, `iomap_file_unshare()`, `iomap_fill_dirty_folios()`, `iomap_zero_range()`, `iomap_truncate_page()`, `iomap_page_mkwrite()`, `iomap_finish_folio_write()`, `iomap_writeback_folio()`, and `iomap_writepages()`.

Important internal flows are `ifs_alloc()/ifs_free()`, `iomap_adjust_read_range()`, `iomap_read_inline_data()`, `iomap_read_folio_iter()`, `iomap_write_begin()`, `__iomap_write_begin()`, `iomap_write_end()`, `iomap_write_iter()`, `iomap_zero_iter()`, and the writeback range helpers.

## Control Flow

Read flow starts in `iomap_read_folio()` or `iomap_readahead()`, which initialize an `iomap_iter` and loop through filesystem-provided mappings. `iomap_read_folio_iter()` handles inline data directly, allocates per-block folio state when needed, trims already-uptodate ranges, zeroes holes/new/post-EOF ranges, and delegates mapped ranges to `ctx->ops->read_folio_range()`. Completion returns through `iomap_finish_folio_read()`, which updates per-block uptodate bits, reports errors, decrements pending bytes, and ends the folio read when all submitted ranges complete.

Buffered write flow starts in `iomap_file_buffered_write()`, which sets `IOMAP_WRITE` plus NOWAIT/DONTCACHE flags and iterates mappings. `iomap_write_iter()` rate-limits dirty pages, faults source iov pages before locking the destination folio, prepares a folio with `iomap_write_begin()`, copies data atomically, marks written ranges uptodate and dirty through `iomap_write_end()`, updates in-memory `i_size` when extending, and advances the iterator. Short writes can shrink the folio size target and retry; failed writes truncate newly allocated pagecache beyond EOF.

`iomap_write_begin()` obtains or batches a folio, validates stale mappings through optional filesystem callbacks, handles inline or buffer-head mappings, or calls `__iomap_write_begin()` to read/zero needed blocks before partial writes. `IOMAP_UNSHARE` forces existing data to be read rather than overwritten.

Delalloc release scans page cache under `invalidate_lock`, finds cached dirty data ranges, and punches only clean/non-dirty portions of a delayed-allocation extent through a filesystem callback so dirty cached data keeps its reservation. Zeroing uses `iomap_zero_range()` and can skip holes/unwritten extents unless dirty pagecache over unwritten mappings requires a flush and stale retry. `iomap_page_mkwrite()` handles mmap write faults by preparing the folio over the current mapping and marking it dirty.

Writeback flow starts in `iomap_writepages()` and processes dirty folios with `iomap_writeback_folio()`. It handles EOF, initializes pending write byte accounting, starts writeback before submission, walks per-block dirty ranges, calls filesystem `writeback_range()`, clears dirty bits, records mapping errors, and then submits pending IO through filesystem `writeback_submit()` if necessary. Completion calls `iomap_finish_folio_write()` to decrement pending byte accounting and end writeback.

## State and Persistence Behavior

The file persists no metadata by itself, but it is responsible for the page-cache state that filesystems eventually write to disk. `iomap_folio_state` stores transient per-block uptodate and dirty state for folios that contain multiple filesystem blocks. Folio flags, mapping errors, dirty/writeback state, and inode `i_size` are updated directly.

Persistence occurs through filesystem callbacks: `iomap_ops` supplies extents, `iomap_write_ops` can customize folio read/get/put/validity, delalloc punch callbacks remove reservations, and writeback callbacks submit disk I/O. Inline data writes copy back into `iomap->inline_data` and mark the inode dirty.

## Dependencies and Integration Points

The file depends on the iomap iterator framework, page cache/folio APIs, writeback control, buffer-head compatibility for `IOMAP_F_BUFFER_HEAD`, block-backed synchronous reads from `bio.c`, filesystem error reporting, swap/migrate-aware folio handling, readahead, mmap fault handling, dirty throttling, and tracepoints from `trace.h`.

Filesystem integration is callback-heavy: callers provide `iomap_ops`, optional `iomap_write_ops`, read ops, writeback ops, and delalloc punch functions. Correctness depends on filesystems returning stable iomaps or implementing `iomap_valid()` and on holding locks documented by the delalloc release path.

## Risks and Edge Cases

Large folios with smaller filesystem blocks are the main subtlety. Per-block uptodate and dirty bitmaps must stay synchronized with folio flags, read completion, invalidation, release, and writeback. Incorrect pending byte accounting can leave folios locked or under writeback forever.

Stale iomaps are a corruption risk: concurrent extent conversion or reclaim can make cached mappings invalid before write-begin, so filesystems that need validation must provide `iomap_valid()`. Short writes, poisoned user pages, post-EOF dirty mmap data, and delalloc reservations all require precise rollback or punch behavior to avoid stale data exposure or leaked reservations.

EOF handling is repeated in read, write, zero, page-mkwrite, and writeback paths. Off-by-one errors around block boundaries, folio boundaries, and `[start,end)` delalloc intervals would affect data integrity. Writeback from reclaim context is rejected because iomap writeback can recurse into filesystem allocation paths.

## Test Signals

Coverage should include full and partial folio reads, mixed uptodate/non-uptodate blocks, inline-data reads/writes, holes/new extents zeroing, reads crossing EOF, read errors and fserror reporting, buffered writes extending `i_size`, NOWAIT failures, DONTCACHE folio selection, short-copy retries, stale iomap retry, buffer-head compatibility, delalloc release with dirty and clean sub-folio blocks, zero range over holes/unwritten/mapped extents, truncate-page partial block zeroing, mmap page faults, writeback of dirty sub-folio ranges, EOF-straddling writeback, mapping error propagation, and reclaim-context writeback rejection.

Tracepoints such as `trace_iomap_readpage`, `trace_iomap_readahead`, `trace_iomap_zero_iter`, `trace_iomap_writeback_folio`, release/invalidate traces, and filesystem writeback callbacks provide useful runtime diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/iomap/buffered-io.c -->
