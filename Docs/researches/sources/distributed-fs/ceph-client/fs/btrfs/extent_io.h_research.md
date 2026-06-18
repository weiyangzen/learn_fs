# sources/distributed-fs/ceph-client/fs/btrfs/extent_io.h

## Purpose

`extent_io.h` declares the public interface and core data structures for Btrfs extent-buffer and extent I/O helpers. It exposes metadata tree-block memory abstraction, folio/delalloc helpers, data and metadata writeback/read entry points, extent-buffer allocation/read/release APIs, and small inline utilities used throughout Btrfs tree and file I/O code.

## Important APIs, Types, And Functions

- Extent-buffer flags enumerate runtime buffer state: uptodate, dirty, tree ref, stale, writeback, unmapped, write error, zoned zeroout, and reading.
- Page operation flags describe range operations for delalloc cleanup: unlock, start/end writeback, and set ordered.
- `EXTENT_FOLIO_PRIVATE` is the non-subpage folio-private sentinel for data extent-managed folios.
- Bitmap macros (`BIT_BYTE`, `BYTE_MASK`, first/last masks) support byte-granular little-endian bitmap manipulation inside extent buffers.
- `struct extent_buffer` is the central metadata block abstraction. It stores logical start, length, folio size/shift, runtime flags, fs_info, optional contiguous virtual address, refcount and ref lock, read mirror, writeback inhibitor count, log tree index, RCU head, tree lock, folio array, and debug-only leak/lock owner fields.
- `struct btrfs_eb_write_context` carries metadata writeback context, including writeback control, current buffer, and zoned block-group state.
- Inline helpers `offset_in_eb_folio()`, `get_eb_offset_in_folio()`, and `get_eb_folio_index()` hide differences between page-sized metadata, larger nodes spanning pages, high-order folios, and subpage nodes.
- `struct extent_changeset` plus helpers track changed byte counts and optionally changed ranges; `EXTENT_CHANGESET_BYTES_ONLY` is a sentinel for callers that only need byte totals.
- Declared exported operations cover read/writepages, readahead, extent buffer allocation/cloning/finding/freeing, metadata reads, memory copy/compare/zero/bitmap operations, delalloc range cleanup, invalidate/release, dirty/uptodate state, test allocation helpers, and writeback inhibition.

## Control Flow

This header is mostly declarative, but it shapes control flow by separating data page-cache operations (`btrfs_read_folio()`, `btrfs_writepages()`, `extent_write_locked_range()`, `btrfs_readahead()`) from metadata extent-buffer operations (`alloc_extent_buffer()`, `read_extent_buffer_pages()`, `btree_writepages()`, `btrfs_btree_wait_writeback_range()`). Callers allocate or find an `extent_buffer`, read it through the metadata BIO path, modify it through memory helpers, mark it dirty/uptodate, and let btree writeback submit it later.

The inline offset helpers are central to all extent-buffer memory access. Any caller that reads or writes tree block fields through accessors depends on them to translate an offset inside the logical tree block into the right folio and byte offset.

## State And Persistence Behavior

The header defines runtime state only; it does not persist data directly. However, the state bits it declares decide whether metadata is considered valid, dirty, writeback-active, stale, or failed. `struct extent_buffer` state gates tree-block persistence through metadata writeback, and its `log_index` allows writeback errors to be attributed to the main tree or one of the log trees. `extent_changeset` is transient operation accounting for extent-state changes.

## Dependencies And Integration Points

The header depends on Linux rbtree/refcount/fiemap/spinlock/atomic/rwsem/list/slab definitions and Btrfs headers for messages, ulist, and miscellaneous helpers. It is included by Btrfs files that need tree block memory access, metadata read/write, page-cache extent I/O, delalloc cleanup, and tests. It also forwards many Btrfs structures to avoid broad include coupling.

## Risks And Edge Cases

- `INLINE_EXTENT_BUFFER_PAGES` assumes maximum metadata block size over page size; all extent-buffer users depend on this array being large enough.
- Offset helpers must be correct for both sectorsize equal to page size and sectorsize smaller than page size; mistakes corrupt metadata field access.
- Runtime flags are bit indices, not persisted values. Adding or reordering flags can affect code expectations but not on-disk format.
- `EXTENT_CHANGESET_BYTES_ONLY` uses a sentinel pointer value; callers must honor `extent_changeset_tracks_ranges()` before touching range lists.
- `wait_on_extent_buffer_writeback()` waits on a bit in `bflags`; callers must ensure the buffer lifetime remains valid while waiting.

## Test Signals

Build coverage is important because this header is widely included. Runtime signals include Btrfs sanity tests, metadata read/write tests, subpage tests, lockdep for extent-buffer locks, and debug assertions around extent-buffer access and changeset handling.
