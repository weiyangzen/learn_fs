# Group Research: group_645_kdave_linux_sources_local_fs_kdave_linux_fs_btrfs_file_item_c_source_85866d9c80e1

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/local-fs/kdave-linux`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/file-item.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/file-item.c

Btrfs file item and checksum implementation. This file owns the low-level helpers for file extent item lookup/conversion, hole extent insertion, inode file-extent presence tracking, checksum lookup for reads, checksum generation for writes, checksum range lookup, checksum insertion, and checksum deletion/truncation in the checksum tree or log tree.

Key responsibilities:
- Maintains `inode->disk_i_size` safely relative to the in-memory file extent presence tree, especially for filesystems without `NO_HOLES`.
- Marks inode logical ranges as having or lacking backing file extent items through `btrfs_inode_set_file_extent_range()` and `btrfs_inode_clear_file_extent_range()`.
- Provides checksum byte-count conversion helpers based on filesystem sector size and checksum size.
- Inserts explicit hole file extents for filesystems that need hole items.
- Looks up file extent items with `btrfs_lookup_file_extent()`, preserving caller control over COW/search modification behavior.
- Looks up read bio checksums with `btrfs_lookup_bio_sums()`, including commit-root searches, free-space inode special handling, missing checksum warnings, and data relocation `NODATASUM` exceptions.
- Searches checksum items for arbitrary ranges and returns either ordered-sum list chunks or a sector bitmap plus checksum buffer.
- Computes write bio checksums synchronously or through workqueue completion, attaching `struct btrfs_ordered_sum` records to ordered extents.
- Allocates dummy ordered sums for zoned nodatasum writes where zone append completion still needs logical address tracking.
- Deletes checksum ranges, including whole-item deletion, item splitting for middle deletions, and edge truncation.
- Inserts checksum data into existing or new checksum items while respecting maximum item sizes, adjacent-item layout, and log-tree overlap constraints.
- Converts on-disk file extent items into in-memory extent maps, including regular, prealloc, hole, compressed, and inline extents.
- Computes the exclusive logical end of a file extent item, rounding inline extents up to sector size.

Important data flows:
- Read checksum lookup starts at `btrfs_lookup_bio_sums()`, allocates inline or heap checksum storage for the bio, optionally pins `commit_root_sem`, then repeatedly calls `search_csum_tree()` until the bio range is covered or a fatal error occurs.
- Write checksum creation starts in `btrfs_csum_one_bio()`, allocates a `btrfs_ordered_sum` sized for the bio, attaches it to the ordered extent, and either calls `csum_one_bio()` immediately or schedules `csum_one_bio_work()`.
- Checksum insertion starts in `btrfs_insert_data_csums()`, tries to locate or extend an adjacent checksum item with `btrfs_lookup_csum()`, otherwise inserts a new item, then copies checksum bytes in chunks until all ordered-sum bytes are persisted.
- Checksum deletion starts from the end of the target range in `btrfs_del_csums()`, walking backward through overlapping items so it can batch-delete covered items and handle partial overlaps without missing earlier checksums.
- File extent conversion uses the current B-tree path key and item body in `btrfs_extent_item_to_extent_map()` to produce the extent-map fields consumed by read, write, fiemap, and seek paths.

Concurrency and locking:
- `btrfs_inode_safe_disk_i_size_write()` takes `inode->lock` while reading the file extent presence tree and updating `disk_i_size`.
- Checksum tree lookups use normal B-tree path locking, but read bio lookup can switch to commit-root searches with `path->skip_locking` while holding `fs_info->commit_root_sem` across repeated searches.
- Checksum generation for async bios stores the bio iterator in `bbio->csum_saved_iter`, schedules work, and signals `bbio->csum_done`.
- Checksum insertion/deletion are transaction-bound and rely on B-tree path write locks, item mutation helpers, and transaction aborts on unrecoverable metadata update failures.

Important invariants:
- Logical checksum ranges and checksum item sizes are sector/checksum-size aligned.
- File extent presence ranges are sector aligned except for the special clear-to-end length `(u64)-1`.
- A checksum item key offset plus item size defines the logical range covered by the packed checksums.
- Missing read checksums are exceptional for normal data roots but can be tolerated for data relocation of nodatasum extents.
- Log-tree checksum insertion must not extend one checksum item across the start of a following checksum item already present in the log tree.
- Inline file extents are represented as `EXTENT_MAP_INLINE`, start at logical offset 0, and have extent-map length equal to one sector.

Notable risks:
- The checksum deletion path mutates packed B-tree item payloads and keys in several overlap cases; off-by-one or alignment mistakes would corrupt checksum coverage.
- Commit-root checksum searches rely on holding `commit_root_sem` across multiple searches to avoid mixing checksums from different transactions.
- `btrfs_insert_data_csums()` optimizes by extending existing items; callers and future changes must preserve the max item and log-tree next-offset rules.
- `btrfs_extent_item_to_extent_map()` trusts tree-checker invariants for inline extents and emits an error only for unknown extent types.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/file-item.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/file-item.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/file-item.h

Public Btrfs file item and checksum interface. This header exposes inline file extent layout helpers and declares the checksum, file extent, and inode extent-range functions implemented by `file-item.c`.

Key responsibilities:
- Defines `BTRFS_FILE_EXTENT_INLINE_DATA_START`, the byte offset in `struct btrfs_file_extent_item` where inline data begins.
- Computes maximum inline data size for a filesystem from `BTRFS_MAX_ITEM_SIZE()` minus the inline data header.
- Computes inline data length from a leaf item size, excluding the file extent header bytes.
- Provides pointer arithmetic helpers for inline data start and inline item size calculation.
- Declares checksum deletion, lookup, insertion, bio checksum calculation, dummy checksum allocation, and range checksum lookup APIs.
- Declares conversion from a file extent item plus B-tree path into an extent map.
- Declares inode file extent range tracking helpers and safe disk i_size update.
- Declares `btrfs_file_extent_end()` for determining the logical end of a file extent item.

Dependencies:
- Includes Linux block type and list definitions, Btrfs UAPI tree structures, `ctree.h`, and ordered-data definitions.
- Forward-declares Btrfs path, bio, root, transaction, ordered-sum, inode, extent map, and file extent structures.

Important invariants:
- Inline helper calculations must match the on-disk `struct btrfs_file_extent_item` layout.
- Inline item length is the item payload size minus `BTRFS_FILE_EXTENT_INLINE_DATA_START`; compressed inline data reports compressed size by this calculation.
- The public checksum APIs operate on logical disk bytenr ranges aligned to filesystem sectors.

Notable risks:
- Any on-disk file extent layout change must update the inline data offset helpers here and all tree-checker assumptions.
- The header exposes low-level mutation helpers used by several higher-level file operations, so callers must already satisfy transaction, path, and range-locking requirements.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/file-item.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/file.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/file.c

Btrfs VFS regular-file operations and file extent mutation implementation. This file handles buffered writes, direct/encoded write dispatch, page-cache dirtying, fsync, mmap write faults, extent dropping/replacement, hole punching, fallocate, zero range, SEEK_DATA/SEEK_HOLE, open/read/splice dispatch, and the exported file operations table.

Key responsibilities:
- Implements page-cache dirtying for buffered writes through `btrfs_dirty_folio()`, including delalloc state, uptodate/dirty folio bits, and in-memory i_size extension.
- Drops and rewrites file extent items with `btrfs_drop_extents()`, handling full deletion, truncation, splitting, inline extent rejection, reference count updates, extent-map cache drops, and optional replacement item setup.
- Converts preallocated extents to written extents through `btrfs_mark_extent_written()`, including splitting, merging with adjacent compatible extents, delayed ref updates, and file extent range tracking.
- Prepares folios for writes, reads partial blocks when needed, locks ranges, waits for ordered extents, and retries when folios are invalidated.
- Checks NOCOW write eligibility with snapshot serialization, ordered-range flushing, and `can_nocow_extent()` probing.
- Performs generic write validation, privilege stripping, ctime/mtime/i_version updates, and pre-write hole expansion in `btrfs_write_check()`.
- Reserves and releases data/metadata space for buffered writes, including NOCOW metadata-only reservations and NOWAIT behavior.
- Implements the buffered write loop by copying one folio-sized range at a time, shrinking reservations on short copies, marking delalloc, and updating `ki_pos`.
- Dispatches encoded, direct, and buffered writes from `btrfs_do_write_iter()` and performs post-write sync handling.
- Releases per-file private state and flush-on-close state in `btrfs_release_file()`.
- Implements `btrfs_sync_file()` with ordered writeback, inode/mmap locking, fast vs full fsync decisions, log-tree logging, log sync, and transaction commit fallback.
- Implements mmap `page_mkwrite`, including delalloc reservation before folio lock, EOF/truncate races, ordered extent waits, partial EOF zeroing, and subpage/folio dirty state.
- Creates or merges explicit hole extents for non-`NO_HOLES` filesystems and updates extent maps for fsync correctness.
- Replaces file extents for hole punching, clone/dedupe-style replacement, and preallocation workflows with transaction restart handling.
- Implements `btrfs_punch_hole()`, including unaligned head/tail zeroing, ordered extent waits, range locking, file extent replacement, inode timestamp/version updates, and transaction completion.
- Implements fallocate and zero-range behavior, including qgroup/data reservations, preallocation range coalescing, zoned rejection, keep-size handling, and i_size updates.
- Finds delalloc/ordered subranges and uses them to implement correct `SEEK_DATA` and `SEEK_HOLE` behavior over explicit extents, implicit holes, prealloc extents, and dirty ranges.
- Defines `btrfs_file_operations` and read/open/splice/mmap/llseek dispatch.
- Provides `btrfs_fdatawrite_range()`, with a second writeback pass for compressed async extents.

Important data flows:
- Buffered write path: `btrfs_file_write_iter()` calls `btrfs_do_write_iter()`, which selects `btrfs_buffered_write()` unless direct or encoded I/O is requested. The buffered loop validates via `generic_write_checks()` and `btrfs_write_check()`, then repeatedly calls `copy_one_range()` to reserve space, prepare a folio, lock/wait extents, copy user data, dirty delalloc state, and release reservations.
- Fsync path: `btrfs_sync_file()` writes dirty ranges, locks inode and mmap state, starts more writeback for races, waits for ordered extents or writeback depending on full/fast sync, logs the dentry into the tree log, syncs the log when possible, otherwise falls back to transaction commit.
- Hole punching path: `btrfs_fallocate()` routes `FALLOC_FL_PUNCH_HOLE` to `btrfs_punch_hole()`, which handles unaligned zeroing, locks a clean aligned range with `btrfs_punch_hole_lock_range()`, then calls `btrfs_replace_file_extents()` without replacement extent info to drop extents and insert hole representation where required.
- Replacement path: `btrfs_replace_file_extents()` starts a transaction with temporary metadata reserve, repeatedly calls `btrfs_drop_extents()`, fills holes or clears file extent presence state, optionally inserts replacement extent items with `btrfs_insert_replace_extent()`, updates inode metadata, ends/restarts transactions, and returns the final open transaction through `trans_out`.
- SEEK_DATA/SEEK_HOLE path: `btrfs_file_llseek()` locks the inode shared, then `find_desired_extent()` locks the searched io_tree range, walks file extent items, and consults `btrfs_find_delalloc_in_range()` so dirty delalloc and ordered extents are reported as data even before file extent items exist.

Concurrency and locking:
- Buffered writes take the Btrfs inode lock, optionally with `BTRFS_ILOCK_TRY` for NOWAIT.
- File extent replacement and hole punching require inode and mmap locks plus aligned io_tree range locks after ordered extents are flushed.
- `btrfs_check_nocow_lock()` takes the root snapshot lock as a write lock while determining and preserving a NOCOW-writeable range; callers must release it with `btrfs_check_nocow_unlock()`.
- `btrfs_page_mkwrite()` uses `sb_start_pagefault()`, `i_mmap_lock`, folio lock, and io_tree extent locks while avoiding delalloc reservation under the folio lock.
- `btrfs_sync_file()` deliberately starts writeback before taking the inode lock, then repeats after locking to close races with concurrent dirtying.
- Per-file llseek cached state is stored in `file->private_data` and guarded by `inode->lock`; cached delalloc state is only reused by its owner task.

Important invariants:
- Extent item ranges and file extent presence tracking are sector aligned.
- `btrfs_drop_extents()` does not update VFS inode byte counts itself; callers use `args->bytes_found` to update accounting atomically with replacement/drop operations.
- Inline extents cannot be partially split for drop/replace operations and return `-EOPNOTSUPP` in those cases.
- `btrfs_replace_file_extents()` returns an open transaction through `trans_out` on success; callers are responsible for final inode updates and ending the transaction.
- Hole extent items are inserted only when `NO_HOLES` is not enabled or when replacement requires an explicit item; otherwise file extent presence tracking is cleared.
- Fallocate is rejected on zoned filesystems in this path.
- Fast fsync correctness depends on extent maps for holes and on ordered extent checksum availability, so extent-map update failures force full sync.
- `SEEK_HOLE` can return i_size quickly only when there are no prealloc extents and inode bytes equal i_size.

Notable risks:
- `btrfs_drop_extents()` and `btrfs_mark_extent_written()` mutate B-tree items, references, and extent-map/file-extent range state in tightly coupled steps; transaction aborts are used when invariants fail.
- Buffered write reservation has multiple cleanup branches for data reservation, metadata reservation, NOCOW metadata-only reservation, extent locks, folio references, and cached states; future changes must preserve balanced release paths.
- mmap write faults reserve space before folio locking to avoid deadlock with writeback, so error handling must carefully release either data+metadata or metadata-only NOCOW reservations.
- Fsync intentionally widens all ranges to the whole file to avoid missing holes, checksums, or ordered extents; narrowing it would require revalidating several documented corruption races.
- `btrfs_replace_file_extents()` restarts transactions inside a loop, so callers must tolerate partial progress and updated inode timestamps/version between transaction boundaries.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/file.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/file.h

Public Btrfs regular-file operation interface. This header declares the exported file operation table and the file write, fsync, extent mutation, dirtying, NOCOW, delalloc search, and writeback helpers implemented by `file.c`.

Key responsibilities:
- Exposes `btrfs_file_operations` for regular-file VFS registration.
- Declares fsync via `btrfs_sync_file()`.
- Declares extent dropping and replacement APIs: `btrfs_drop_extents()` and `btrfs_replace_file_extents()`.
- Declares `btrfs_mark_extent_written()` for converting prealloc ranges to regular written file extents.
- Declares `btrfs_do_write_iter()` for common write dispatch, including optional encoded writes.
- Declares file release cleanup through `btrfs_release_file()`.
- Declares `btrfs_dirty_folio()` for marking copied page-cache data as delalloc and dirty.
- Declares range writeback helper `btrfs_fdatawrite_range()`.
- Declares NOCOW range probe/lock and unlock helpers.
- Declares delalloc range discovery used by seek/logging-style callers.
- Declares write validation and buffered write entry points.

Dependencies:
- Includes Linux basic type definitions.
- Forward-declares VFS structures, folios/pages, iov_iter/kiocb, Btrfs inode/root/path/transaction, encoded I/O args, drop-extents args, and replace-extent info.

Important invariants:
- `btrfs_check_nocow_lock()` callers must call `btrfs_check_nocow_unlock()` when the function returns a positive result.
- `btrfs_replace_file_extents()` expects a previously locked range and returns a transaction handle through `trans_out` on success.
- `btrfs_drop_extents()` behavior is controlled by the caller-supplied `struct btrfs_drop_extents_args`, including path ownership, replacement mode, cache dropping, and accounting output.

Notable risks:
- This header exposes low-level extent mutation entry points; misuse outside the expected inode lock, mmap lock, extent lock, and transaction contexts can corrupt file extent state.
- The write helpers mix VFS-facing and Btrfs-internal contracts, so changes in direct/encoded/buffered write dispatch must keep prototypes synchronized across the file, ioctl, and direct I/O code.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/file.h -->