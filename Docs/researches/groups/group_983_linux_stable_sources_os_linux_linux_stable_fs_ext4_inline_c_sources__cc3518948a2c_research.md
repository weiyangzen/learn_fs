# Group Research: group_983_linux_stable_sources_os_linux_linux_stable_fs_ext4_inline_c_sources__cc3518948a2c

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux-stable`. All three requested files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/inline.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/inline.c

## Purpose

Implements ext4 inline data support: storing small regular-file data, symlink data, and small directory contents directly inside the inode body. Inline data occupies `i_block` first, then an in-inode extended attribute named `system.data` when extra inode xattr space is available.

## Storage Model

- `EXT4_MIN_INLINE_DATA_SIZE` is the fixed inline payload held in `struct ext4_inode.i_block`.
- Additional inline payload is stored as the value of the in-inode xattr `EXT4_XATTR_INDEX_SYSTEM:"data"`.
- `EXT4_I(inode)->i_inline_off` points to the xattr entry inside the raw inode.
- `EXT4_I(inode)->i_inline_size` is total inline capacity currently available.
- Inline directories store only the parent inode number for `..` in the first 4 bytes; `.` and `..` entries are synthesized during lookup/readdir/tree conversion.

## Main Responsibilities

- Discover inline data at inode load through `ext4_find_inline_data_nolock()`.
- Compute available inline capacity with `ext4_get_max_inline_size()` and `get_max_inline_xattr_value_size()`.
- Create, grow, shrink, destroy, and convert inline data under journaling.
- Serve buffered reads and writes for inline files.
- Support inline directory insert, search, delete, emptiness check, and readdir.
- Convert inline data to normal extent/indirect block storage when inline capacity is exceeded.
- Expose inline extents through iomap reporting.

## Key Functions and Flows

- `ext4_read_inline_data()` copies from raw inode `i_block` and then from the xattr value area.
- `ext4_write_inline_data()` writes to the same two-part layout, assuming inline metadata has already been prepared and journal access acquired.
- `ext4_create_inline_data()` inserts the `system.data` xattr, zeroes `i_block`, clears `EXT4_INODE_EXTENTS`, sets `EXT4_INODE_INLINE_DATA`, and marks the inode dirty.
- `ext4_update_inline_data()` expands the xattr value while preserving previous xattr content.
- `ext4_prepare_inline_data()` checks `EXT4_STATE_MAY_INLINE_DATA`, recomputes inline metadata, and either creates or updates inline storage.
- `ext4_destroy_inline_data_nolock()` removes the inline xattr, clears inline state, zeroes inode data fields, and reinitializes extent state where appropriate.
- `ext4_readpage_inline()` loads inline file data into folio 0 and zero-fills other pages.
- `ext4_generic_write_inline_data()` prepares folio 0 plus a journal handle for inline write_begin paths.
- `ext4_write_inline_data_end()` copies user data from the folio back into the inode/xattr inline area, updates size, handles partial-copy orphan cleanup, and stops the journal handle.
- `ext4_convert_inline_data_to_extent()` and `ext4_da_convert_inline_data_to_extent()` migrate inline data into page cache and normal block mapping paths for non-delalloc and delalloc writes.
- `ext4_convert_inline_data_nolock()` performs immediate conversion to a real block for directories or non-delalloc conversion, with restore-on-error logic.
- `ext4_inline_data_truncate()` shrinks the inline xattr value and clears truncated bytes from `i_block`.
- `ext4_inline_data_iomap()` reports an `IOMAP_INLINE` mapping pointing into the inode table buffer.

## Inline Directory Handling

- `ext4_try_create_inline_dir()` initializes a new inline directory with parent inode metadata and an empty fake dirent spanning remaining inline space.
- `ext4_try_add_inline_entry()` first inserts into the `i_block` region, then grows into xattr inline space, and finally converts to block-based directory storage if full.
- `ext4_find_inline_entry()` searches both inline regions.
- `ext4_delete_inline_entry()` removes an inline dirent via generic dirent deletion after journal write access.
- `ext4_read_inline_dir()` synthesizes stable offsets for `.` and `..` so userspace cookies resemble a normal block directory.
- `ext4_inlinedir_to_tree()` feeds inline entries into htree readdir state, synthesizing `.` and `..`.
- `empty_inline_dir()` validates inline dirents and returns whether any real child entries remain.

## Locking and Journaling

- Uses `xattr_sem` for inline xattr metadata stability.
- Uses `i_data_sem` while destroying or converting inline layout.
- Acquires journal write access before mutating raw inode/xattr storage.
- Uses orphan list cleanup on failed extending writes or conversion paths that allocated blocks beyond `i_size`.

## Important Edge Cases

- Inline xattr entries referring to external xattr inodes are treated as corruption.
- Inline size larger than `PAGE_SIZE` during read is reported as corruption.
- Conversion validates inline directory entries before writing them into a real directory block.
- Restore path attempts to recreate inline data after failed conversion to avoid data loss.
- `EXT4_STATE_MAY_INLINE_DATA` distinguishes files still eligible for inline storage from files already being converted through delayed allocation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/inline.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/inode-test.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/inode-test.c

## Purpose

KUnit tests for ext4 inode timestamp decoding. The file verifies that `ext4_decode_extra_time()` correctly reconstructs seconds and nanoseconds from the legacy 32-bit timestamp field plus ext4 extra timestamp bits.

## Test Data

The `timestamp_expectation` table covers timestamp boundary cases described by ext4 inode timestamp documentation:

- Negative 32-bit timestamp range without extra seconds bits: 1901 through 1969.
- Nonnegative 32-bit timestamp range without extra seconds bits: 1970 through 2038.
- Extra seconds bit combinations extending representable timestamps beyond 2038.
- High/low extra-bit combinations through dates around 2446.
- Nanosecond decoding, including `1 ns` and maximum 30-bit nanosecond value.

## Main Helpers

- `get_32bit_time()` constructs either the lower or upper bound of a signed 32-bit timestamp, based on whether the most significant bit is set.
- `timestamp_expectation_to_desc()` gives each KUnit parameter a readable case name.
- `KUNIT_ARRAY_PARAM(ext4_inode, ...)` turns the static table into KUnit parameters.

## Main Test

`inode_test_xtimestamp_decoding()`:

- Reads one `timestamp_expectation` from `test->param_value`.
- Calls `ext4_decode_extra_time(cpu_to_le32(base_time), cpu_to_le32(extra_bits))`.
- Asserts both `tv_sec` and `tv_nsec` match the expected values.
- Emits descriptive case information on failure.

## Test Registration

- Defines `ext4_inode_test_cases` with `KUNIT_CASE_PARAM`.
- Registers `ext4_inode_test_suite` named `ext4_inode_test`.
- Module metadata declares GPL v2 licensing.

## Coverage Notes

This test is narrowly focused on timestamp decode arithmetic. It does not exercise inode I/O, checksum validation, timestamp encoding, or mount/runtime integration.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/inode-test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/ext4/inode.c

## Purpose

Core ext4 inode implementation. This file owns inode lifetime, block mapping, buffered write paths, delayed allocation, writeback, direct/DAX iomap mapping, truncate and punch-hole behavior, inode load/store, setattr/getattr, dirtying, journal-mode switching, and mmap page-fault write preparation.

## Major Areas

### Inode Integrity and Lifetime

- `ext4_inode_csum()`, `ext4_inode_csum_verify()`, and `ext4_inode_csum_set()` compute and verify inode metadata checksums.
- `ext4_inode_is_fast_symlink()` identifies symlinks stored directly in inode block fields.
- `ext4_evict_inode()` handles final inode deletion: truncates pages, starts a truncate transaction, removes xattrs, removes orphan records, records deletion time, and frees the inode.
- Quota and reserved-delalloc accounting are updated through `ext4_da_update_reserve_space()`, `ext4_da_reserve_space()`, and `ext4_da_release_space()`.

### Block Mapping

- `ext4_map_blocks()` is the central logical-to-physical mapping entry point.
- It checks the extent status tree first, then queries extents or indirect blocks under `i_data_sem`.
- With `EXT4_GET_BLOCKS_CREATE`, it allocates or converts mappings under `i_data_sem` write lock via `ext4_map_create_blocks()`.
- New mapped blocks are validated with `ext4_inode_block_valid()`.
- Ordered-data mode registers freshly allocated written ranges with JBD2 so data reaches disk before metadata commit.
- `ext4_map_query_blocks()` caches queried written or unwritten extents in the extent status tree.
- `ext4_issue_zeroout()` zeroes newly allocated ranges, using fscrypt-aware zeroout for encrypted regular files.
- `_ext4_get_block()`, `ext4_get_block()`, and `ext4_get_block_unwritten()` adapt mapping results to buffer-head callbacks.

### Buffer and Metadata Access

- `ext4_getblk()` maps and fetches a metadata/data buffer, creating and journaling a new buffer when needed.
- `ext4_bread()` and `ext4_bread_batch()` provide read helpers for mapped blocks.
- `ext4_walk_page_buffers()` applies callbacks over buffer-head ranges inside a folio.
- `do_journal_get_write_access()` and `ext4_dirty_journalled_data()` provide common journal-data helpers.

### Buffered Write Paths

- `ext4_block_write_begin()` prepares buffers inside a folio, allocating blocks through a supplied `get_block` callback and reading partial buffers when required.
- `ext4_write_begin()` handles non-delalloc buffered writes, including inline-data attempt, journal start, folio locking, block allocation, data journaling, retry, and orphan cleanup.
- `ext4_write_end()` commits non-journalled buffered writes, updates `i_size`, marks inode dirty, trims failed extending writes, and stops the journal handle.
- `ext4_journalled_write_end()` handles `data=journal`, dirties data buffers as journal metadata, updates datasync transaction state, and performs similar failed-write cleanup.

### Delayed Allocation and Writeback

- `ext4_da_map_blocks()` resolves or inserts delayed extents, reserving clusters and quota as needed.
- `ext4_da_get_block_prep()` marks buffers as delayed or unwritten during delalloc write_begin.
- `ext4_da_write_begin()` chooses delalloc unless low-space or fsverity forces fallback to non-delalloc.
- `ext4_da_write_end()` updates pagecache and, where safe, advances `i_disksize`.
- `mpage_prepare_extent_to_map()` scans dirty folios and builds extents of delayed/unwritten buffers needing mapping.
- `mpage_map_one_extent()` allocates delayed blocks or converts unwritten extents during writeback.
- `mpage_map_and_submit_buffers()` updates buffer-head physical mappings and submits fully mapped folios.
- `mpage_map_and_submit_extent()` coordinates allocation, submission, partial-progress handling, `i_disksize` updates, and fatal writeback error behavior.
- `ext4_do_writepages()` is the central writeback engine for normal, delalloc, and journalled data modes.
- `ext4_writepages()` wraps writeback with ext4 writepage locking and repeats once for journalled pages dirtied through pinned mappings.
- `ext4_normal_submit_inode_data_buffers()` submits ordered-data ranges for JBD2.

### Iomap, Direct I/O, DAX, and Atomic Writes

- `ext4_set_iomap()` translates `ext4_map_blocks` results into `IOMAP_HOLE`, `IOMAP_DELALLOC`, `IOMAP_MAPPED`, or `IOMAP_UNWRITTEN`.
- `ext4_iomap_begin()` handles read/write mapping for direct I/O and DAX, allocating blocks where needed.
- `ext4_iomap_alloc()` starts a journal transaction and chooses create, unwritten, or zeroing flags based on DAX/direct-I/O state and EOF.
- Atomic write support enforces one contiguous mapping through `ext4_map_blocks_atomic_write()` and the bigalloc-only slow path.
- `ext4_iomap_begin_report()` powers fiemap/swap reporting and delegates inline data reporting to `ext4_inline_data_iomap()`.
- `ext4_dax_writepages()` delegates DAX writeback to `dax_writeback_mapping_range()`.

### Address Space Operations

Defines four aops tables:

- `ext4_aops` for regular buffered non-delalloc mode.
- `ext4_journalled_aops` for `data=journal`.
- `ext4_da_aops` for delayed allocation.
- `ext4_dax_aops` for DAX mappings.

`ext4_set_aops()` selects the table based on inode journal mode, DAX state, and `DELALLOC`.

### Zeroing, Truncate, and Hole Punch

- `ext4_load_tail_bh()` locks and reads the buffer containing a partial EOF or partial hole boundary.
- `ext4_block_zero_range()` zeroes a block subrange using DAX, journalled, or normal buffer paths.
- `ext4_block_zero_eof()` zeroes the tail of the block containing EOF and orders written zeroes in ordered-data mode.
- `ext4_zero_partial_blocks()` handles start/end partial blocks around hole-punch ranges.
- `ext4_update_disksize_before_punch()` persists `i_disksize` before removing pagecache or blocks.
- `ext4_truncate_page_cache_block_range()` invalidates pagecache safely, with special journalled-data and sub-page block handling.
- `ext4_punch_hole()` zeroes partial blocks, removes full-block extents or indirect blocks, updates extent status cache, tracks fast-commit range, and marks the inode dirty.
- `ext4_truncate()` handles inline truncation, EOF tail zeroing, orphan-list safety, extent or indirect truncation, and inode time/dirty updates.

### Inode Load and Store

- `__ext4_get_inode_loc()` maps an inode number to an inode table block and offset, with readahead and an optimization to avoid reading blocks containing only the in-memory inode.
- `ext4_get_inode_loc()` and variants wrap inode table access and report I/O errors.
- `ext4_fill_raw_inode()` serializes VFS/ext4 inode state into the on-disk inode, including uid/gid/projid, timestamps, block count, size, flags, device numbers, block array, i_version, and checksum.
- `__ext4_iget()` loads and validates an inode, including checksum, extra inode size, inline data, extent/indirect validity, xattr block validity, mode-specific operation tables, fast symlink validation, DAX selection, casefold feature consistency, and stale-handle behavior.
- `ext4_do_update_inode()` writes the in-memory inode into the raw inode buffer, updates lazytime peers in the same inode table block, marks metadata dirty, and enables `large_file` if needed.
- `ext4_write_inode()` commits inode state during writeback, delegating to fast commit/JBD2 when journalled or syncing the inode table buffer in nojournal mode.

### Attribute and Stat Handling

- `ext4_setattr()` validates immutable/append restrictions, handles quota transfer, converts oversized inline data before truncate/grow, coordinates ordered truncation and DIO waits, updates `i_size` and `i_disksize` under `i_data_sem`, manages orphan state, truncates pagecache, calls `ext4_truncate()`, updates i_version, and handles ACL chmod.
- `ext4_dio_alignment()` reports direct-I/O support/alignment constraints, disabling DIO for fsverity, journalled data, inline data, or unsupported encryption.
- `ext4_getattr()` fills birth time, direct-I/O alignment, atomic-write limits, and visible ext4 flags.
- `ext4_file_getattr()` adjusts `stat.blocks` for inline files and delayed allocation reservations.

### Dirtying, Extra Inode Size, and Journal Mode Changes

- `ext4_mark_iloc_dirty()` and `ext4_reserve_inode_write()` are the raw inode update primitives.
- `ext4_expand_extra_isize()` and helpers grow extra inode space, including xattr-aware expansion.
- `__ext4_mark_inode_dirty()` reserves inode write access, opportunistically expands extra inode size, writes the raw inode, and reports errors.
- `ext4_dirty_inode()` starts a small inode transaction for generic dirtying callbacks.
- `ext4_change_inode_journal_flag()` safely toggles per-inode data journaling by waiting for DIO, flushing pagecache, locking journal updates, flushing the journal when disabling, switching aops, and marking the inode dirty.

### mmap Write Faults

- `ext4_page_mkwrite()` prepares a mmap write fault:
  - rejects immutable files,
  - converts inline data first,
  - uses delalloc preparation when possible,
  - avoids a transaction if all buffers are already mapped,
  - otherwise allocates blocks through `ext4_block_page_mkwrite()`,
  - uses unwritten extents for dioread-nolock,
  - returns VM fault codes through `vmf_fs_error()`.

## Concurrency and Ordering Themes

- `i_data_sem` protects extent/indirect mapping changes and `i_disksize` races with writeback.
- `invalidate_lock` is used around truncate, DAX layout breaks, and page fault interactions.
- Journal handles are carefully stopped only after folios are unlocked and I/O has been submitted when synchronous handles might wait for commits.
- Orphan-list insertion protects crash recovery for failed extending writes and truncates.
- Ordered-data mode records data ranges before metadata commits to avoid stale exposure.
- Inline data is converted before paths that require normal block mappings.

## External Dependencies

This file depends heavily on ext4 subsystems implemented elsewhere:

- `extents.c` and `indirect.c` for physical mapping and truncation.
- `extents_status.c` for extent status cache.
- `page-io.c` for bio submission and unwritten extent completion.
- `xattr.c` and inline helpers for in-inode xattr and inline data state.
- `ext4_jbd2.c`/JBD2 for journaling, ordered data, fast commit, and orphan safety.
- fscrypt, fsverity, DAX, iomap, quota, and VFS pagecache APIs.

## Important Edge Cases

- Inline data and extent flags together are rejected as corruption.
- Bad inode checksums, invalid sizes, invalid xattr blocks, bad extent trees, and illegal inode numbers are rejected during iget.
- Direct I/O falls back for indirect holes to avoid stale-data exposure.
- Bigalloc atomic writes require contiguous mapping and force commits for mixed mappings.
- Journalled data has special invalidation and tail-page commit waiting to avoid dirty folios without buffers.
- Low free-space conditions can switch writes away from delayed allocation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ext4/inode.c -->