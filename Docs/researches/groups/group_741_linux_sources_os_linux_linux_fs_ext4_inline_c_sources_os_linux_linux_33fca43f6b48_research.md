# Group Research: group_741_linux_sources_os_linux_linux_fs_ext4_inline_c_sources_os_linux_linux_33fca43f6b48

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux`.  
Read coverage: fully read all three assigned files: `inline.c` lines 1-2000, `inode-test.c` lines 1-283, and `inode.c` lines 1-6826.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/inline.c -->
# File Research: sources/os/linux/linux/fs/ext4/inline.c

## Purpose

`fs/ext4/inline.c` implements ext4 inline data support. Inline data stores small regular-file contents, symlink bodies, and small directory entries inside the inode: first in `ext4_inode.i_block`, then in the in-inode xattr value named `system.data`.

The file owns inline-data sizing, creation, reads/writes, conversion to normal extent/block storage, inline-directory lookup/enumeration/mutation, inline symlink reads, truncate handling, and iomap reporting for inline contents.

## Core Data Model

Important constants:

- `EXT4_XATTR_SYSTEM_DATA`: xattr name `"data"` in the system namespace.
- `EXT4_MIN_INLINE_DATA_SIZE`: size of `i_block`, `sizeof(__le32) * EXT4_N_BLOCKS`, the base inline area.
- `EXT4_INLINE_DOTDOT_OFFSET`: offset of inline directory `..` inode data.
- `EXT4_INLINE_DOTDOT_SIZE`: inline directory stores only the `..` inode number in the first 4 bytes.

Important inode state:

- `EXT4_I(inode)->i_inline_off`: byte offset of the `system.data` xattr entry within the raw inode; zero means no xattr-backed inline payload.
- `EXT4_I(inode)->i_inline_size`: total inline payload capacity, including `i_block`.
- `EXT4_INODE_INLINE_DATA`: persistent inode flag for inline data.
- `EXT4_STATE_MAY_INLINE_DATA`: in-memory state used by write paths to try inline writes before falling back to normal mapping.

The inline payload layout is split:

- bytes `[0, EXT4_MIN_INLINE_DATA_SIZE)` are stored in raw inode `i_block`;
- remaining bytes are stored in the value area of the in-inode xattr `system.data`.

## Main Entry Points

Inline size and discovery:

- `ext4_get_max_inline_size()` computes the maximum inline capacity available in the current inode by inspecting in-inode xattr free space under `xattr_sem`.
- `ext4_find_inline_data_nolock()` locates `system.data`, rejects external xattr-inode references, and initializes `i_inline_off` and `i_inline_size`.
- `get_max_inline_xattr_value_size()` walks the inode xattr table, accounts for entry headers, name length, value offsets, and existing inline xattr value space.

Read/write helpers:

- `ext4_read_inline_data()` copies inline data from `i_block` and optional xattr value into a caller buffer.
- `ext4_write_inline_data()` writes into the same split storage, returning early in ext4 emergency state.
- `ext4_readpage_inline()` and `ext4_read_inline_folio()` fill folio 0 from inline data, zero the tail, and mark the folio uptodate.
- `ext4_read_inline_link()` reads an inline symlink into a newly allocated, terminated buffer.

Inline data creation/update/destruction:

- `ext4_create_inline_data()` creates the `system.data` xattr, zeros `i_block`, clears `EXT4_INODE_EXTENTS`, sets `EXT4_INODE_INLINE_DATA`, and marks the inode dirty.
- `ext4_update_inline_data()` expands the xattr value while preserving existing value contents.
- `ext4_prepare_inline_data()` verifies `EXT4_STATE_MAY_INLINE_DATA`, checks max capacity, locks xattrs, refreshes inline metadata, then creates or updates inline storage.
- `ext4_destroy_inline_data()` wraps `ext4_destroy_inline_data_nolock()` under xattr write locking.
- `ext4_destroy_inline_data_nolock()` removes `system.data`, zeros inline memory, restores extent format when appropriate, clears inline state, and marks the inode dirty.

Conversion to normal storage:

- `ext4_convert_inline_data_to_extent()` converts inline regular-file data during non-delalloc writes. It creates folio 0, reads inline data into it, destroys inline metadata, maps a normal block, journals buffers for data-journal mode, commits the folio, and handles orphan/truncate cleanup on failure.
- `ext4_da_convert_inline_data_to_extent()` handles delayed-allocation conversion by reading inline data into page cache, preparing delayed blocks, marking the folio dirty, and setting `fsdata = CONVERT_INLINE_DATA`.
- `ext4_convert_inline_data_nolock()` converts inline data or inline directories to a real block while holding the xattr lock. It validates inline directory entries before conversion, allocates block 0, initializes directory blocks through `ext4_init_dirblock()`, and restores inline data if conversion fails.
- `ext4_convert_inline_data()` is the exported conversion entry point. If conversion is already in delayed-allocation progress, it flushes the mapping first.

Buffered write integration:

- `ext4_generic_write_inline_data()` starts a small inode transaction, prepares inline storage for `pos + len`, or converts to extent storage if capacity is insufficient. It returns `1` when inline write setup succeeded and returns normal errors otherwise.
- `ext4_try_to_write_inline_data()` rejects writes larger than current maximum inline capacity and otherwise delegates to the generic inline path.
- `ext4_write_inline_data_end()` copies written bytes from the locked folio into inline storage, updates `i_size`, clears folio dirty state so writepages will not process it, stops the journal, and truncates failed over-EOF writes.

Inline directory handling:

- `ext4_try_create_inline_dir()` initializes a new inline directory by storing the parent inode number in the first four inline bytes and creating an empty directory entry over the remaining inline space.
- `ext4_try_add_inline_entry()` first attempts to add a dirent into `i_block` inline space, then xattr inline space, then converts to a real block if no inline room remains.
- `ext4_find_inline_entry()` searches both inline regions for a directory entry.
- `ext4_delete_inline_entry()` deletes an inline dirent using `ext4_generic_delete_entry()`.
- `empty_inline_dir()` validates and scans inline directory entries to determine whether only `.`/`..` remain.
- `ext4_read_inline_dir()` emits inline directory entries to VFS `dir_context`, synthesizing `.` and `..` offsets so directory cookies remain compatible with block-based directories.
- `ext4_inlinedir_to_tree()` feeds inline directory entries into htree readdir state, synthesizing `.` and `..` and hashing entries when needed.
- `ext4_update_inline_dir()` grows the xattr inline directory region when xattr free space permits.
- `ext4_update_final_de()` stretches the last directory entry to cover newly available inline directory space.

Iomap and truncate:

- `ext4_inline_data_iomap()` reports inline data as `IOMAP_INLINE` using the physical address of the raw inode `i_block` area.
- `ext4_inline_data_truncate()` shrinks inline payloads, updates `i_disksize`, truncates xattr value length, zeros the tail in `i_block`, removes stale extent-status entries when needed, and uses orphan handling for crash consistency.

## Dependencies and Integration

This file depends heavily on:

- inode location and raw inode access: `ext4_get_inode_loc()`, `ext4_raw_inode()`;
- xattr internals: `ext4_xattr_ibody_find()`, `ext4_xattr_ibody_set()`, `ext4_xattr_ibody_get()`, xattr header/entry layout helpers;
- journaling: `ext4_journal_start()`, `ext4_journal_get_write_access()`, `ext4_mark_iloc_dirty()`, `ext4_handle_dirty_metadata()`;
- block mapping and writeback: `ext4_block_write_begin()`, `ext4_get_block()`, `ext4_get_block_unwritten()`, `ext4_da_get_block_prep()`;
- directory logic: `ext4_find_dest_de()`, `ext4_insert_dentry()`, `ext4_search_dir()`, `ext4_check_dir_entry()`, `ext4_init_dirblock()`;
- crash consistency: orphan add/delete and failed-write truncation.

## Locking and Ordering

Key locking rules:

- xattr state is protected with `xattr_sem`; many public paths take read or write locks, while `_nolock` helpers require callers to hold the right lock or run during safe initialization.
- inline-data destruction also takes `i_data_sem` write lock because it mutates block mapping state.
- conversion paths coordinate folio locks, xattr locks, journal handles, and orphan-list cleanup.
- inline write end updates `i_size` while holding the folio lock to avoid writeout racing and zeroing past EOF.

## Error Handling and Corruption Checks

The file treats these as corruption or hard failures:

- `system.data` xattr pointing to an external xattr inode returns `-EFSCORRUPTED`.
- missing inline xattr where inline metadata says one should exist returns `-EFSCORRUPTED`.
- inline size larger than `PAGE_SIZE` in folio reads returns `-EFSCORRUPTED`.
- malformed xattr entry walking reports inode errors.
- inline directory conversion validates all dirents before moving them into a real block.
- failed conversion attempts restore inline data when possible; failure to restore logs an emergency data-loss warning.

## Notable Risk Areas

- Inline data shares storage machinery with in-inode xattrs, so xattr compaction and `i_inline_off` changes must be refreshed before writes.
- Conversion paths are crash-sensitive because inline metadata is destroyed before block-backed data is committed; the code uses journaling, orphan handling, and restoration paths to manage this.
- Inline directories have synthetic `.`/`..` layout and offset translation; cookie correctness depends on `i_version` checks and the `extra_offset` calculation in `ext4_read_inline_dir()`.
- `ext4_write_inline_data()` silently returns in emergency state, so callers rely on earlier emergency checks and journal error propagation.
- Inline data and extent flags are mutually exclusive; this file clears and restores flags as storage format changes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/inline.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/inode-test.c -->
# File Research: sources/os/linux/linux/fs/ext4/inode-test.c

## Purpose

`fs/ext4/inode-test.c` is a KUnit test module for ext4 inode timestamp decoding. It verifies that `ext4_decode_extra_time()` correctly decodes the seconds and nanoseconds portions of ext4 inode timestamps across documented boundary cases.

## Test Coverage

The file defines a table of `struct timestamp_expectation` entries covering:

- negative 32-bit timestamp lower and upper bounds;
- nonnegative 32-bit timestamp lower and upper bounds;
- extra seconds bit 0 set;
- extra seconds bit 1 set;
- both extra seconds bits set;
- nanosecond decoding, including `1 ns` and maximum supported nanoseconds;
- documented date ranges from 1901 through 2446, matching the ext4 inode timestamp documentation.

Important constants:

- `LOWER_MSB_0`, `UPPER_MSB_0`: nonnegative 32-bit timestamp boundaries.
- `LOWER_MSB_1`, `UPPER_MSB_1`: negative 32-bit timestamp boundaries.
- `MAX_NANOSECONDS`: `(1 << 30) - 1`, the 30-bit nanosecond field maximum.
- `CASE_NAME_FORMAT`: assertion diagnostic format for parameterized failures.

## Main Test Flow

- `timestamp_expectation_to_desc()` gives each KUnit parameter a descriptive case name.
- `KUNIT_ARRAY_PARAM(ext4_inode, test_data, timestamp_expectation_to_desc)` creates the parameter generator.
- `get_32bit_time()` builds the low 32-bit timestamp input according to whether the test wants the signed MSB set and lower/upper bound value.
- `inode_test_xtimestamp_decoding()` calls:

  `ext4_decode_extra_time(cpu_to_le32(get_32bit_time(test_param)), cpu_to_le32(test_param->extra_bits))`

  It then asserts both `tv_sec` and `tv_nsec` against expected values with `KUNIT_EXPECT_EQ_MSG()`.

- `ext4_inode_test_cases` registers the parameterized test.
- `ext4_inode_test_suite` names the suite `ext4_inode_test`.
- `kunit_test_suites()` registers the suite as a module-level KUnit test.

## Dependencies and Integration

The file includes:

- `<kunit/test.h>` for KUnit infrastructure;
- `<linux/time64.h>` for `struct timespec64` and `time64_t`;
- `ext4.h` for `ext4_decode_extra_time()` and ext4 timestamp encoding definitions.

It does not instantiate a filesystem, mount ext4, or allocate inodes. This is a pure decode-table unit test.

## Behavior Verified

The test validates that ext4 extra timestamp bits extend the signed 32-bit seconds field into the documented extended timestamp range and preserve nanosecond values from the high bits of the extra timestamp field.

## Notable Risk Areas

- The test is table-driven and focused only on `ext4_decode_extra_time()`. It does not test timestamp encoding, raw inode read/write integration, endianness beyond explicit `cpu_to_le32()` inputs, or filesystem mount behavior.
- It intentionally tests boundary values; regressions in bit placement or sign-extension behavior should produce clear parameterized KUnit failures.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/inode-test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/inode.c -->
# File Research: sources/os/linux/linux/fs/ext4/inode.c

## Purpose

`fs/ext4/inode.c` is the main ext4 inode implementation. It handles inode checksum calculation, inode eviction, block mapping, buffered write setup/completion, delayed allocation, writeback, DAX writeback, direct-I/O iomap mapping, page invalidation/release, truncate and punch-hole operations, raw inode read/write, inode flag translation, setattr/getattr, journal-mode switching, and mmap page-fault write preparation.

This file is central glue between VFS inode operations, page cache, buffer heads, iomap, JBD2 journaling, ext4 extent/indirect mapping, delayed allocation, inline data, fscrypt, fsverity, DAX, quota, and fast commits.

## Major Responsibilities

### Inode checksums and raw inode updates

- `ext4_inode_csum()` computes the metadata checksum over the raw inode, zeroing checksum fields during calculation.
- `ext4_inode_csum_verify()` validates stored checksum fields when metadata checksums are enabled and creator OS is Linux.
- `ext4_inode_csum_set()` writes low and optional high checksum words into the raw inode.
- `ext4_fill_raw_inode()` serializes VFS/ext4 in-memory inode state into `struct ext4_inode`, including uid/gid/projid, timestamps, flags, size, block pointers, device numbers, generation, version, file ACL, and checksum.
- `ext4_do_update_inode()` writes the serialized inode into the inode-table buffer, updates lazytime neighbors, handles large-file feature enablement, dirties metadata, clears `EXT4_STATE_NEW`, and updates fsync transaction tracking.
- `ext4_mark_iloc_dirty()`, `ext4_reserve_inode_write()`, and `__ext4_mark_inode_dirty()` are the main journal-aware inode dirtying paths.

### Inode lookup and initialization

- `__ext4_get_inode_loc()` maps an inode number to its inode-table block and offset, with inode-table readahead and an optimization that avoids disk I/O if the inode block contains only this in-memory inode.
- `ext4_get_inode_loc()` and `ext4_get_fc_inode_loc()` expose inode-location lookup for normal and fast-commit paths.
- `__ext4_iget()` reads a raw inode, verifies bounds and checksum, loads core fields, validates mode/size/flags/block references, initializes inline data and xattrs, sets file/dir/symlink/special inode operations, and handles stale file handles.
- `check_igot_inode()` validates expected EA-inode/bad-inode conditions.
- `ext4_iget_extra_inode()` checks in-inode xattr layout and discovers inline data.
- `ext4_set_inode_flags()` maps ext4 inode flags to VFS flags such as `S_SYNC`, `S_APPEND`, `S_IMMUTABLE`, `S_DAX`, `S_ENCRYPTED`, `S_CASEFOLD`, and `S_VERITY`.
- `ext4_set_inode_mapping_order()` configures folio order constraints, lowering journal-data inodes to the minimum order.

### Inode lifecycle and eviction

- `ext4_inode_is_fast_symlink()` detects symlinks stored directly in `i_data`.
- `ext4_evict_inode()` handles final inode cleanup. For linked inodes it truncates page cache and clears in-core state. For unlinked inodes it starts a truncate transaction, zeros size, truncates blocks, deletes xattrs, removes orphan records, sets deletion time, frees the inode, and handles error fallback.
- `ext4_begin_ordered_truncate()` coordinates ordered-data truncation with JBD2.
- `ext4_inode_attach_jinode()` lazily allocates and publishes a JBD2 inode wrapper for ordered/journaled data tracking.

### Block mapping

- `ext4_map_blocks()` is the central logical-to-physical mapping function. It consults the extent-status cache, queries extents or indirect blocks, optionally allocates or converts blocks, validates physical block ranges, updates ordered-data tracking, and tracks fast-commit ranges.
- `ext4_map_query_blocks()` and `ext4_map_create_blocks()` split lookup and creation work.
- `ext4_map_query_blocks_next_in_leaf()` extends a cached extent over the next leaf entry when querying last-in-leaf mappings.
- `_ext4_get_block()`, `ext4_get_block()`, and `ext4_get_block_unwritten()` adapt ext4 mapping into buffer-head `get_block_t` callbacks.
- `ext4_getblk()`, `ext4_bread()`, and `ext4_bread_batch()` provide metadata/data buffer access by logical block.
- `check_block_validity()` rejects mappings outside legal filesystem block ranges, except for the journal inode.
- `ext4_issue_zeroout()` zeroes physical ranges, delegating to fscrypt zeroout for encrypted regular files.

### Buffered write path

- `ext4_block_write_begin()` prepares buffer heads for a folio write, maps missing blocks, reads partial existing blocks, zeroes partial new blocks, decrypts read buffers for fs-layer encryption, and handles journal-data write access.
- `ext4_write_begin()` handles non-delalloc buffered writes: emergency-state checks, inline-data attempt, folio allocation before journal start, block mapping, data-journal access, retry on `-EAGAIN`/`-ENOSPC`, and failed-write truncation.
- `ext4_write_end()` completes non-journal buffered writes: commits written bytes, updates `i_size`, marks inode dirty, handles orphan cleanup for short writes beyond EOF, and stops the journal.
- `ext4_journalled_write_end()` completes data-journal writes by dirtying data buffers as metadata, updating `i_datasync_tid`, and handling short writes.
- `ext4_journalled_zero_new_buffers()` zeroes and journals new buffers without relying on generic dirtying.

### Delayed allocation and writeback

- `ext4_da_reserve_space()`, `ext4_da_release_space()`, and `ext4_da_update_reserve_space()` manage per-inode reserved delayed-allocation clusters and quota reservations.
- `ext4_clu_alloc_state()` and `ext4_insert_delayed_blocks()` handle bigalloc-aware delayed reservation accounting.
- `ext4_da_map_blocks()` finds existing mappings or inserts delayed extents into the extent-status tree.
- `ext4_da_get_block_prep()` prepares buffer heads for delayed allocation, marking delayed or unwritten buffers appropriately.
- `ext4_da_write_begin()` chooses delayed allocation unless free space is low or fsverity is writing Merkle data; it also supports inline-data setup.
- `ext4_da_write_end()` and `ext4_da_do_write_end()` finish delayed writes, update `i_size`, and update `i_disksize` only when the end block is already mapped.
- `ext4_alloc_da_blocks()` forces delayed blocks to be allocated by flushing the mapping.
- `ext4_do_writepages()` is the main writeback engine. It handles inline-data destruction before writeback, data-journal mode, dioread_nolock reserved handles, cyclic ranges, dirty-page scanning, block allocation for delayed/unwritten buffers, bio submission, transaction lifetime, error recovery, and writeback index updates.
- `mpage_*` helpers collect dirty folios, build extents to map, map delayed/unwritten buffers, submit bios, update `i_disksize`, release unused pages, and handle fatal writeback errors.
- `ext4_writepages()` wraps `ext4_do_writepages()` with ext4 writepages locking and reruns data-journal writeback if DMA-pinned pages were dirtied behind journaling.
- `ext4_normal_submit_inode_data_buffers()` submits ordered-data dirty ranges for JBD2.
- `ext4_dax_writepages()` delegates DAX writeback to `dax_writeback_mapping_range()`.

### Iomap, DAX, direct I/O, and atomic writes

- `ext4_set_iomap()` converts `ext4_map_blocks` results into iomap records, including mapped, unwritten, delayed, hole, dirty, new, DAX, and atomic-bio flags.
- `ext4_iomap_begin()` is the main iomap begin operation for direct I/O and DAX. It rejects inline data, allocates blocks for writes, limits fscrypt I/O block continuity, and validates atomic-write coverage.
- `ext4_iomap_alloc()` starts journal transactions for direct/DAX writes, chooses create/unwritten/zeroing flags, retries ENOSPC, and forces a commit for mixed atomic-write mappings.
- `ext4_map_blocks_atomic_write()` and `_slow()` ensure atomic-write ranges resolve to one contiguous mapped extent, using bigalloc-only slow-path zeroing for mixed mappings.
- `ext4_iomap_begin_report()` reports mappings for fiemap/swap-like queries and supports inline-data iomap reporting.
- `ext4_iomap_ops` and `ext4_iomap_report_ops` publish iomap operations.
- `ext4_dio_alignment()` reports DIO alignment capability, rejecting fsverity, journal-data, inline-data, and unsupported encrypted files.
- `ext4_iomap_swap_activate()` activates iomap-based swapfiles.

### Address-space operations

The file defines address-space operation tables:

- `ext4_aops`: regular non-delalloc buffered mode.
- `ext4_journalled_aops`: data=journal mode, with journalled write end, dirty folio, invalidate, and migration behavior.
- `ext4_da_aops`: delayed-allocation mode.
- `ext4_dax_aops`: DAX writeback/dirty/bmap/swap operations.

`ext4_set_aops()` chooses the correct table based on inode journal mode, DAX, and delalloc mount options.

### Truncate, zeroing, and hole punching

- `ext4_block_zero_range()`, `ext4_block_do_zero_range()`, and `ext4_block_journalled_zero_range()` zero partial block ranges for normal, DAX, and journal-data modes.
- `ext4_block_zero_eof()` zeroes from EOF to block end and orders zeroed written data before `i_disksize` updates in ordered mode.
- `ext4_zero_partial_blocks()` zeroes partial start/end blocks around a hole-punch or zero range.
- `ext4_can_truncate()` allows truncation for regular files, directories, and non-fast symlinks.
- `ext4_update_disksize_before_punch()` ensures `i_disksize` is updated before page-cache truncation can prevent writeback from doing so.
- `ext4_truncate_page_cache_block_range()` handles page-cache invalidation for punched ranges, including journal-data write-and-wait and partial-folio mmap cleanup.
- `ext4_break_layouts()` coordinates DAX layout breaking.
- `ext4_punch_hole()` zeros partial blocks, removes page cache, starts a truncate transaction, removes extent or indirect mappings, inserts hole status, tracks fast-commit ranges, and handles sync semantics.
- `ext4_truncate()` performs crash-consistent truncate with orphan-list protection, inline-data truncation, EOF zeroing, extent/indirect truncation, timestamp update, and inode dirtying.

### setattr/getattr

- `ext4_setattr()` handles VFS attribute changes. It enforces immutable/append restrictions, prepares fscrypt and quota changes, transfers quota ownership, handles file size changes, converts inline data when new size exceeds inline capacity, waits for DIO on shrink, breaks DAX layouts, zeroes EOF tails on extension, updates `i_size` and `i_disksize` under `i_data_sem`, tracks fast-commit ranges, truncates page cache, calls `ext4_truncate()`, increments inode version, and updates ACLs for mode changes.
- `ext4_getattr()` fills birth time, DIO alignment, atomic-write capability, and user-visible ext4 attribute flags.
- `ext4_file_getattr()` adjusts reported block count for inline data and delayed allocations.

### Journal mode and mmap write faults

- `ext4_change_inode_journal_flag()` safely switches per-inode data journaling. It waits for DIO, flushes and invalidates page cache, locks journal updates and writepages, flushes the journal when disabling data journaling, switches aops, marks fast commits ineligible, and dirties the inode.
- `ext4_page_mkwrite()` handles mmap write faults: starts pagefault protection, updates file time, converts inline data, uses delalloc where possible, verifies folio size/truncation races, avoids journal start when all buffers are already mapped, and otherwise allocates/makes buffers writable via `ext4_block_page_mkwrite()`.
- `ext4_block_page_mkwrite()` starts a write transaction, locks the folio, maps needed blocks, commits buffers, and handles data-journal mode.

## Important Structures and Constants

- `struct mpage_da_data`: state object for writeback scanning, delayed mapping, io submission, and range tracking.
- `DIO_MAX_BLOCKS`: maximum direct-I/O mapping length, 4096 blocks.
- `BH_FLAGS`: buffer state mask for delayed/unwritten writeback collection.
- `MAX_WRITEPAGES_EXTENT_LEN`: caps writeback mapping extent length at 2048 blocks.

## Dependencies and Integration

This file integrates with:

- JBD2 journaling: transaction starts/stops, ordered data lists, data journaling, journal inode tracking, fast commits.
- ext4 extent and indirect mapping: `ext4_ext_map_blocks()`, `ext4_ind_map_blocks()`, truncate/remove/check helpers.
- extent-status cache: lookup, insert, remove, delayed/hole/written/unwritten states.
- page cache and writeback: folios, buffer heads, `write_begin_get_folio()`, `block_write_end()`, `filemap_flush()`, `filemap_write_and_wait*()`.
- iomap and DAX: direct I/O, fiemap reporting, swap activation, DAX writeback and zeroing.
- inline data: calls into `inline.c` for inline write setup, conversion, truncation, and iomap reporting.
- fscrypt/fsverity: encrypted zeroout/decryption/DIO alignment and verity write-size behavior.
- quotas: delayed allocation reservations, ownership transfer, xattr-inode usage.
- VFS inode operations: iget, eviction, setattr/getattr, dirty inode, mmap page faults.

## Locking and Ordering

Key locking patterns:

- `i_data_sem` protects extent/indirect mapping mutations, extent-status updates tied to mapping, and coordinated `i_size`/`i_disksize` updates.
- folio locks protect write begin/end, writeback submission, partial zeroing, and page fault mapping.
- `filemap_invalidate_lock` protects truncate, DAX layout breakage, journal-mode switching, and mmap/page-cache invalidation interactions.
- JBD2 transaction handles wrap all metadata mutations and some data-buffer mutations in journal-data mode.
- orphan-list updates protect crash recovery during truncate and failed over-EOF writes.
- writepages locking (`ext4_writepages_down_read/write`) serializes writeback against mode changes and allocation-sensitive operations.
- raw inode writes use `i_raw_lock` while serializing in-memory fields into the on-disk inode.

## Error Handling and Corruption Checks

Important checks include:

- inode number bounds and special-inode access mode in `__ext4_iget()`;
- raw inode checksum verification, with `-EFSBADCRC` on mismatch;
- invalid `i_extra_isize`, size beyond maxbytes, bad xattr block, bad extent/indirect block references;
- invalid inline-data plus extents flag combination;
- invalid dir-index flag when filesystem lacks `dir_index` under metadata checksums;
- invalid symlink flags or malformed fast symlink length;
- physical block validity checks after mappings;
- delayed allocation fatal errors can force dirty-page invalidation to prevent infinite writeback loops;
- atomic write mapping failures return errors rather than risking torn or discontiguous writes;
- emergency filesystem state short-circuits writes and dirtying.

## Notable Risk Areas

- `ext4_map_blocks()` is a concurrency-sensitive choke point. Incorrect flags or missing locks can corrupt extent-status cache assumptions, especially around `EXT4_GET_BLOCKS_IO_SUBMIT`, `EXT4_EX_NOCACHE`, and writeback callers.
- `i_size` and `i_disksize` ordering is critical. The file repeatedly updates them under `i_data_sem` or folio lock to avoid stale exposure and crash-inconsistent allocation beyond EOF.
- Delayed allocation accounting spans quota reservations, per-inode counters, dirty cluster counters, bigalloc cluster sharing, and extent-status entries.
- Journal-data mode has special folio dirtying semantics. DMA-pinned folios are marked checked and journaled later by writepages.
- Truncate and punch-hole paths rely on orphan records, page-cache invalidation, EOF zeroing, and metadata transaction ordering for recovery correctness.
- Inline data conversion is interleaved with generic write, delayed allocation, truncate, setattr, and page fault paths.
- Atomic-write support adds strict contiguous mapping requirements and forced transaction commits for mixed mappings.
- Journal mode switching is intentionally heavyweight because stale journal records can corrupt data if mode changes are not serialized with writeback and journal flushes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/inode.c -->