# Group Research: group_249_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_file_item_c_source_df964e47e89c

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/local-fs/btrfs-linux`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/file-item.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/file-item.c

## Purpose

Implements Btrfs file extent item helpers and checksum-tree operations. This file bridges on-disk file extent metadata, in-memory extent maps, ordered write checksums, read bio checksum lookup, checksum insertion/deletion, and inode disk-size safety tracking.

## Main Responsibilities

- Maintains `disk_i_size` safely relative to real file extents when hole extent items are required.
- Tracks file extent coverage in an inode-local extent state tree through `EXTENT_DIRTY`.
- Inserts explicit hole file extent items.
- Searches file extent items by inode/objectid and file offset.
- Looks up checksums for read bios, checksum ranges, and bitmap-based checksum requests.
- Calculates checksums for write bios, synchronously or via workqueue.
- Allocates dummy ordered sums for zoned nodatasum writes where Zone Append completion updates logical addresses.
- Deletes checksum items over byte ranges, including truncating or splitting partially overlapped checksum items.
- Inserts ordered checksums into the checksum tree, extending adjacent checksum items where possible.
- Converts on-disk `btrfs_file_extent_item` records into `struct extent_map`.
- Computes the logical end offset of a file extent item.

## Important APIs

- `btrfs_inode_safe_disk_i_size_write()` sets `disk_i_size` to the safe contiguous byte range from file offset 0, or directly to `i_size` when the inode has no file-extent tracking tree.
- `btrfs_inode_set_file_extent_range()` and `btrfs_inode_clear_file_extent_range()` update inode file-extent coverage bits after inserting or removing file extent items.
- `btrfs_insert_hole_extent()` creates a regular file extent item with `disk_bytenr == 0`, representing an explicit hole.
- `btrfs_lookup_file_extent()` wraps `btrfs_search_slot()` for `BTRFS_EXTENT_DATA_KEY` lookup.
- `btrfs_lookup_bio_sums()` allocates and fills `bbio->csum` for read verification.
- `btrfs_lookup_csums_list()` returns found checksums as `btrfs_ordered_sum` list entries.
- `btrfs_lookup_csums_bitmap()` fills a checksum buffer and sector bitmap for found checksums.
- `btrfs_csum_one_bio()` creates an ordered checksum record and calculates sector checksums for a write bio.
- `btrfs_alloc_dummy_sum()` attaches an empty ordered sum for zoned nodatasum IO.
- `btrfs_del_csums()` removes checksum records for a byte range.
- `btrfs_insert_data_csums()` writes ordered sums into the checksum or log tree.
- `btrfs_extent_item_to_extent_map()` initializes extent-map fields from regular, prealloc, hole, compressed, and inline file extent items.
- `btrfs_file_extent_end()` returns the non-inclusive logical end of the file extent item at a path slot.

## Control Flow

Checksum lookup centers on `search_csum_tree()`, which reuses the current path when possible and otherwise searches the appropriate checksum root for the target logical bytenr. `btrfs_lookup_bio_sums()` walks a read bio sector range, fills checksum slots, uses commit-root searches for free-space inodes and optionally for past-transaction reads, and handles checksum holes by warning or marking data-relocation sectors as nodatasum.

Checksum range lookups first search at `start`, then step back to the previous checksum item if it overlaps the range. They then iterate forward through checksum items, clipping to the requested range. The list variant allocates bounded `btrfs_ordered_sum` chunks; the bitmap variant copies into caller-owned storage and sets one bit per covered sector.

Checksum deletion scans backward from the end of the target range. Fully covered checksum items are batch-deleted. Leading or trailing overlaps are handled by `truncate_one_csum()`. Middle overlaps are split in place by zeroing the dropped checksum bytes and using `btrfs_split_item()` so the next loop can delete/truncate a cleanly bounded item.

Checksum insertion tries to locate an existing checksum item ending at the insertion point and extend it, subject to leaf space and `MAX_CSUM_ITEMS`. For log trees, it avoids extending across the next checksum item because the log can contain partial overlapping checksum history from repeated fsyncs. If extension is not suitable, it inserts a new checksum item sized to fit the remaining ordered sum and the next checksum item boundary.

Extent-map conversion distinguishes regular/prealloc extents, explicit holes (`disk_bytenr == 0`), compressed extents, and inline extents. For old non-compressed extents with `ram_bytes < disk_num_bytes`, it normalizes `ram_bytes` to `disk_num_bytes`.

## Dependencies

This file depends on Btrfs btree path/search/mutation helpers, checksum roots, ordered extents, bio wrappers, compression flags, extent maps, transaction handles, file extent item accessors, and filesystem geometry such as `sectorsize`, `sectorsize_bits`, `csum_size`, and `csums_per_leaf`.

## Invariants And Risks

- Checksum and file-extent operations assume sectorsize alignment; assertions enforce this in conversion helpers and range tracking.
- `btrfs_lookup_bio_sums()` must not mix checksum data from different commit roots when `csum_search_commit_root` is set, so it holds `commit_root_sem` across repeated searches.
- Checksum item splitting/truncation mutates btree items in place and must preserve key offsets exactly.
- Log-tree checksum insertion has stricter overlap constraints than the main checksum tree.
- Missing checksums for non-nodatasum reads are suspicious except in data relocation of nodatasum extents.
- `btrfs_extent_item_to_extent_map()` trusts tree-checker guarantees for inline extents starting at file offset 0.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/file-item.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/file-item.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/file-item.h

## Purpose

Declares the Btrfs file extent item and checksum helper interface implemented by `file-item.c`, plus inline helpers for inline file extent sizing and addressing.

## Key Definitions

- `BTRFS_FILE_EXTENT_INLINE_DATA_START` is the byte offset inside `struct btrfs_file_extent_item` where inline payload data begins.
- `BTRFS_MAX_INLINE_DATA_SIZE()` computes the maximum inline payload that fits in a leaf item.
- `btrfs_file_extent_inline_item_len()` returns the on-disk inline payload length, excluding the file extent header.
- `btrfs_file_extent_inline_start()` returns the address of inline payload data within a file extent item.
- `btrfs_file_extent_calc_inline_size()` returns total item size for a given inline data size.

## Public API Surface

The header exposes checksum deletion, checksum lookup for bios/ranges/bitmaps, checksum insertion, bio checksum generation, dummy ordered sum allocation, explicit hole extent insertion, file extent lookup, extent item to extent-map conversion, inode file-extent coverage tracking, safe disk i_size updates, and file extent end calculation.

## Integration Points

It includes Btrfs tree definitions, ordered-data declarations, and core ctree declarations, while forward-declaring most heavier structures. It is used by file IO, extent mapping, logging, checksumming, encoded IO, direct/buffered write paths, and metadata update paths that need file extent item semantics.

## Invariants And Risks

- Inline extent helpers encode on-disk layout assumptions; changes to `struct btrfs_file_extent_item` layout must keep these helpers consistent.
- `BTRFS_MAX_INLINE_DATA_SIZE()` depends on leaf item sizing and therefore filesystem node/leaf geometry.
- Callers of the declared mutation APIs must provide correct transaction/path locking and sectorsize-aligned ranges where required by `file-item.c`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/file-item.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/file.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/file.c

## Purpose

Implements the Btrfs regular-file VFS layer: buffered writes, direct/encoded write dispatch, file extent dropping/replacement, prealloc-to-written conversion, fsync/logging, mmap write faults, hole punching, fallocate/zero-range, SEEK_DATA/SEEK_HOLE, file open/read/splice/read/write operations, and writeback kickoff helpers.

## Main Responsibilities

- Marks page-cache folios dirty and updates inode delalloc state.
- Drops, truncates, splits, duplicates, and replaces file extent items.
- Converts preallocated extents to written regular extents, merging adjacent compatible extents when possible.
- Handles buffered write reservations, folio preparation, ordered-extent conflicts, NOCOW fallback, and i_size extension.
- Dispatches encoded, direct, and buffered writes through a shared write entry point.
- Implements fsync using the tree log when possible and full transaction commit when required.
- Handles `page_mkwrite` for writable mmap faults with delalloc/NOCOW accounting.
- Inserts or merges explicit hole extents when `NO_HOLES` is not active.
- Punches holes and replaces ranges with holes or cloned/new extent records.
- Implements fallocate preallocation and zero-range behavior.
- Finds delalloc and ordered extents for correctness of SEEK_DATA/SEEK_HOLE.
- Provides Btrfs regular-file `file_operations`.

## Important APIs And Entry Points

- `btrfs_dirty_folio()` clears stale delalloc accounting, sets delalloc bits, marks folio subranges uptodate/dirty, and extends in-memory `i_size` for writes past EOF.
- `btrfs_drop_extents()` removes or trims file extent items over a range and optionally prepares an insertion slot for replacement.
- `btrfs_mark_extent_written()` turns a prealloc extent range into regular written extents, splitting and merging items as needed.
- `btrfs_check_nocow_lock()` tests whether a buffered write range can use NOCOW and holds the root snapshot lock on success.
- `btrfs_write_check()` performs privilege/time/version updates and expands holes before writes past EOF.
- `btrfs_buffered_write()` is the buffered write loop around `copy_one_range()`.
- `btrfs_do_write_iter()` dispatches encoded, direct, or buffered writes and runs write-sync handling.
- `btrfs_sync_file()` implements file and directory fsync with tree-log fast path and transaction commit fallback.
- `btrfs_replace_file_extents()` drops file extents and inserts holes or replacement extents over a locked range.
- `btrfs_find_delalloc_in_range()` reports contiguous dirty or ordered delalloc subranges.
- `btrfs_fdatawrite_range()` starts writeback, with a second writeback pass when async compression extents are present.

## Extent Mutation Behavior

`btrfs_drop_extents()` is the core file extent removal primitive. It searches `BTRFS_EXTENT_DATA_KEY` items for an inode, handles overlap cases, deletes fully covered items in batches, truncates leading/trailing overlaps, duplicates items for middle-range splits, and updates delayed data refs for real disk extents. It tracks allocated bytes removed through `args->bytes_found` and can insert a replacement item into free leaf space.

`btrfs_mark_extent_written()` requires the target range to be inside a prealloc file extent. It splits the prealloc item into up to three parts, converts the target part to `BTRFS_FILE_EXTENT_REG`, merges with adjacent compatible regular extents using the same disk extent mapping, updates delayed refs, and marks the file extent range as present for safe disk i_size logic.

`fill_holes()` inserts or merges explicit hole file extents when the filesystem does not use `NO_HOLES`. It also installs a hole extent map when possible; if allocation or replacement fails, it drops the extent map range and forces a full inode sync.

`btrfs_replace_file_extents()` is used by hole punching and extent replacement. It starts bounded transactions with a temp block reserve, loops over the range, drops existing extents, fills explicit holes or clears file-extent tracking beyond EOF, inserts replacement extents when supplied, updates inode version/times, periodically ends transactions, and returns the final transaction handle on success.

## Write Path

Buffered writes run under the Btrfs inode lock. `copy_one_range()` faults user pages, reserves data and metadata space, optionally falls back to NOCOW metadata-only reservation, prepares a locked folio, waits out overlapping ordered extents, copies into the folio, shrinks unused reservations after short copies, calls `btrfs_dirty_folio()`, unlocks extents and folios, and releases reservation state.

`reserve_space()` first tries normal data reservation. If that fails and the range can be NOCOW, it reserves metadata only and leaves the snapshot lock held until release. NOWAIT writes return `-EAGAIN` when they would need blocking reservation or COW work.

`btrfs_do_write_iter()` rejects writes after shutdown or filesystem error, disallows NOWAIT encoded writes, dispatches encoded/direct/buffered paths, records the inode's last subtransaction, and applies `generic_write_sync()` for synchronous writes.

## Fsync And Logging

`btrfs_sync_file()` always expands the requested fsync range to the full file to avoid missing holes, file extent items, or checksums. It starts writeback before and after taking inode/mmap locks, decides whether a full sync is required, waits for ordered extents for full sync or zoned filesystems, otherwise captures ordered extents for fast logging and waits for writeback.

If logging can be skipped because the inode is already logged or committed, it clears stale full-sync state and checks writeback errors. Otherwise it starts a transaction, logs the dentry, syncs the log when possible, or falls back to committing the transaction. For fast fsync fallback it ends the transaction, waits for ordered extents, attaches to the transaction barrier, and commits only what is necessary.

## Mmap, Hole Punch, And Fallocate

`btrfs_page_mkwrite()` reserves delalloc space before locking the faulting folio to avoid dirty-page deadlocks, handles NOCOW metadata-only fallback, locks the mmap and extent ranges, waits for ordered extents, trims reservation at EOF, sets delalloc and folio dirty/uptodate state, zeroes bytes past EOF, and returns the folio locked to the VM.

`btrfs_punch_hole()` handles unaligned boundaries by zeroing partial sectors with `btrfs_truncate_block()`, skips already-hole ranges, flushes ordered extents, locks and truncates page cache over aligned ranges, calls `btrfs_replace_file_extents()` with no replacement extent, and updates inode metadata.

`btrfs_fallocate()` rejects unsupported modes and zoned filesystems, handles punch-hole and zero-range modes, expands preceding holes if needed, waits for ordered extents, reserves qgroup/data space for real holes, preallocates missing ranges, and updates i_size unless `FALLOC_FL_KEEP_SIZE` is set.

`btrfs_zero_range()` avoids work if the range is already preallocated, zeroes written unaligned boundaries, includes hole boundary sectors in allocation, reserves data/qgroup space, and uses preallocation to represent the zero range.

## SEEK_DATA/SEEK_HOLE

`find_desired_extent()` locks the target inode range and scans file extent items with forward readahead. It treats explicit holes, implicit `NO_HOLES` gaps, and prealloc extents as holes, but overlays delalloc and ordered extents so dirty data is reported as data before it has landed in the btree. It caches llseek extent-state lookup state per file/private owner task for repeated seeks.

## File Operations

`btrfs_file_operations` wires Btrfs regular files to llseek, read_iter, splice_read, write_iter, splice_write, mmap_prepare, open, release, fsync, fallocate, ioctls, remap_file_range, uring commands, NOWAIT/direct capability, buffered async flags, and generic leases.

## Dependencies

This file integrates with extent maps, ordered extents, delayed refs, transactions, tree logging, delalloc space accounting, qgroups, direct IO, encoded IO, compression writeback, reflink/remap, subpage folio state, inode runtime flags, mmap locks, VFS writeback/error handling, fsverity open checks, and Btrfs block reserves.

## Invariants And Risks

- Extent mutation requires strict inode, extent-range, path, and transaction locking; wrong ordering can corrupt file extent items or delayed refs.
- `btrfs_drop_extents()` must update extent refs for real disk extents but not for holes or log-tree-only operations.
- NOCOW success leaves the snapshot lock held and callers must release it through `btrfs_check_nocow_unlock()`.
- Fsync correctness depends on flushing the full file range and coordinating ordered extents with log-tree checksum/file extent logging.
- `page_mkwrite()` must reserve before folio locking and must recheck EOF/truncation after locks are acquired.
- Hole punching must remove page cache and wait for ordered extents before replacing file extent items.
- SEEK_DATA/HOLE must combine btree extents with delalloc and ordered extents to avoid reporting dirty data as a hole.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/file.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/file.h

## Purpose

Declares the public Btrfs regular-file interface implemented by `file.c` and consumed by inode, direct IO, encoded IO, ioctl, reflink, mmap, logging, and writeback paths.

## Public API Surface

- `btrfs_file_operations` exports the VFS regular-file operations table.
- `btrfs_sync_file()` is the fsync entry point for files and directories.
- `btrfs_drop_extents()` removes or trims file extent items over a range.
- `btrfs_replace_file_extents()` replaces a locked file range with holes or supplied extent metadata.
- `btrfs_mark_extent_written()` converts preallocated file extent ranges to written regular extents.
- `btrfs_do_write_iter()` dispatches encoded, direct, and buffered writes.
- `btrfs_release_file()` frees Btrfs per-file private state and handles flush-on-close.
- `btrfs_dirty_folio()` marks a folio range as dirty/delalloc.
- `btrfs_fdatawrite_range()` starts writeback with Btrfs compression-aware retry behavior.
- `btrfs_check_nocow_lock()` and `btrfs_check_nocow_unlock()` expose NOCOW write eligibility and snapshot lock release.
- `btrfs_find_delalloc_in_range()` finds dirty or ordered delalloc ranges.
- `btrfs_write_check()` performs common Btrfs write preflight.
- `btrfs_buffered_write()` exposes the buffered write implementation.

## Dependencies And Consumers

The header forward-declares VFS, iterator, folio, extent-state, transaction, root, inode, drop-extents, replace-extent, and encoded-IO structures to keep includes light. It is the boundary between Btrfs regular file operations and other subsystems that need to mutate file extents, write data, or query delalloc state.

## Invariants And Risks

- Callers of extent mutation APIs must satisfy the locking and transaction expectations documented in `file.c`.
- `btrfs_check_nocow_lock()` has paired unlock semantics only when it returns success.
- `btrfs_replace_file_extents()` may return an open transaction through `trans_out`, so ownership transfer must be handled carefully.
- Delalloc range queries combine io-tree and ordered-extent state; callers should pass cached extent state only when it matches the current task/use context.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/file.h -->