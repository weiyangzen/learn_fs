# Group Research: group_948_linux_stable_sources_os_linux_linux_stable_fs_btrfs_file_item_c_sour_ee8f129c3d97

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/os/linux/linux-stable`, which is included in subset A. Every listed source file was read completely. The four `linux-stable` files are byte-for-byte identical to the corresponding `sources/os/linux/linux/fs/btrfs/` files already present in this workspace, but this report is for the `linux-stable` paths below.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/file-item.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/file-item.c

Btrfs file extent item and checksum implementation. This file connects on-disk file extent items, in-memory extent maps, inode file-extent range tracking, ordered write checksums, read-bio checksum lookup, and checksum tree mutation.

Key responsibilities:
- Maintains `inode->disk_i_size` safely. With `NO_HOLES`, it can mirror `i_size`; without it, the safe disk size is limited to the contiguous file-extent-covered range starting at offset 0.
- Tracks logical file extent coverage in `inode->file_extent_tree` when extent items are inserted or removed.
- Inserts explicit hole extents with `btrfs_insert_hole_extent()`.
- Looks up file extent items through `btrfs_lookup_file_extent()`.
- Looks up read-bio checksums in `btrfs_lookup_bio_sums()`, including inline checksum storage, heap fallback, checksum-tree readahead, free-space-inode commit-root search, and commit-root semaphore protection for past-transaction reads.
- Provides list and bitmap checksum range lookup through `btrfs_lookup_csums_list()` and `btrfs_lookup_csums_bitmap()`.
- Computes write bio checksums in `btrfs_csum_one_bio()`, synchronously or with async work, and attaches `btrfs_ordered_sum` records to ordered extents.
- Allocates dummy ordered sums for zoned nodatasum writes so zone append completion can still record logical addresses.
- Deletes checksum ranges with whole-item deletion, batched deletion, leading/trailing truncation, or middle splitting.
- Inserts ordered checksum records into checksum/log trees, extending adjacent checksum items when possible while respecting item size, leaf space, and log-tree overlap constraints.
- Converts on-disk `btrfs_file_extent_item` records into `struct extent_map` entries for regular, prealloc, explicit hole, compressed, and inline extents.
- Computes the exclusive logical end of a file extent item with inline extents rounded to sector size.

Important data flows:
- `btrfs_lookup_bio_sums()` derives the disk range from `bio->bi_iter`, allocates `bbio->csum`, then repeatedly calls `search_csum_tree()` to fill sector checksums. Missing checksums warn for normal data, but for data relocation they mark the inode io tree with `EXTENT_NODATASUM`.
- `btrfs_lookup_csums_list()` searches at the requested start, backs up to a previous overlapping checksum item if needed, and emits bounded `btrfs_ordered_sum` chunks.
- `btrfs_lookup_csums_bitmap()` performs a similar walk but copies checksum bytes into a caller buffer and sets one bitmap bit per sector with a checksum.
- `btrfs_del_csums()` walks backward from the deletion range end so item deletion/truncation does not skip earlier overlapping checksum items.
- `btrfs_insert_data_csums()` starts at `sums->logical`, finds or extends an item when possible, otherwise inserts a new item sized by remaining checksum count and next checksum item position.
- `btrfs_extent_item_to_extent_map()` reads the current path key and item fields, then fills extent-map logical range, disk range, offset, generation, ram bytes, compression/prealloc flags, hole marker, or inline marker.

Concurrency and invariants:
- `btrfs_inode_safe_disk_i_size_write()` holds `inode->lock` while reading file extent tracking and updating `disk_i_size`.
- Commit-root checksum searches set `path->search_commit_root` and `path->skip_locking`, and hold `fs_info->commit_root_sem` across repeated searches to avoid mixing committed roots.
- Checksum and file extent coverage ranges are sector-size aligned; checksum byte counts are checksum-size aligned.
- `btrfs_lookup_csum()` returns `-EFBIG` when the requested checksum is exactly adjacent to the previous item, signaling an extension opportunity.
- Missing read checksums are exceptional for normal data roots but tolerated for data relocation of nodatasum extents.
- Log-tree checksum insertion must not extend a checksum item across a later checksum item already present in the log.
- Inline file extents are represented as `EXTENT_MAP_INLINE`, start at logical offset 0, and map to one sector in the extent map.

Notable risks:
- Checksum item deletion mutates packed item contents, keys, and item boundaries in several overlap cases; off-by-one or alignment mistakes can corrupt checksum coverage.
- Commit-root lookup correctness depends on holding `commit_root_sem` for the whole multi-search walk.
- File extent range tracking feeds safe `disk_i_size`; missed set/clear calls can produce unsafe persisted sizes on filesystems without `NO_HOLES`.
- `btrfs_extent_item_to_extent_map()` relies on tree-checker invariants for inline extents and only reports unknown extent types as filesystem errors.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/file-item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/file-item.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/file-item.h

Public Btrfs file item and checksum interface. This header exposes inline file extent layout helpers and declares the file extent, checksum, ordered-sum, extent-map conversion, and inode file-extent tracking APIs implemented by `file-item.c` or consumed by nearby Btrfs code.

Key responsibilities:
- Defines `BTRFS_FILE_EXTENT_INLINE_DATA_START`, the offset where inline file extent payload begins.
- Computes maximum inline payload size from `BTRFS_MAX_ITEM_SIZE()` minus the inline extent header.
- Computes inline payload length from a leaf item size.
- Provides pointer/size helpers for inline file extent payloads.
- Declares checksum deletion, read-bio checksum lookup, checksum insertion, write-bio checksum calculation, dummy ordered-sum allocation, list checksum lookup, and bitmap checksum lookup.
- Declares explicit hole extent insertion and file extent item lookup.
- Declares conversion from a file extent item and B-tree path into `struct extent_map`.
- Declares inode file extent range set/clear helpers and safe `disk_i_size` update.
- Declares `btrfs_file_extent_end()`.

Dependencies and invariants:
- Includes Linux block/list definitions, Btrfs tree UAPI, `ctree.h`, and `ordered-data.h`.
- Forward-declares extent map, path, bio, transaction, root, ordered sum, inode, and file extent structures.
- Inline layout helpers must match the on-disk `struct btrfs_file_extent_item` layout exactly.
- `btrfs_file_extent_inline_item_len()` reports stored payload bytes, which are compressed size for compressed inline extents.
- Public checksum APIs operate on filesystem-sector-aligned logical ranges.
- File extent range tracking callers must pass ranges matching file extent item boundaries.

Notable risks:
- This header exposes low-level mutation helpers whose correctness depends on external transaction, path, inode, mmap, and extent-lock contracts.
- It declares `btrfs_lookup_csums_range()`, but this group’s implementation file provides `btrfs_lookup_csums_list()` and `btrfs_lookup_csums_bitmap()` instead.
- Any on-disk file extent layout change must update these helpers and matching tree-checker assumptions together.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/file-item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/file.c

Btrfs regular-file VFS implementation and file extent mutation code. This file implements buffered writes, encoded/direct/buffered write dispatch, fsync/logging, mmap write faults, extent dropping and replacement, prealloc-to-written conversion, hole punching, fallocate, zero range, delalloc discovery, `SEEK_DATA`/`SEEK_HOLE`, open/read/splice/mmap hooks, and the exported `btrfs_file_operations` table.

Key responsibilities:
- Marks folios dirty through `btrfs_dirty_folio()`, setting delalloc state, uptodate/dirty bits, clearing checked state, handling `EXTENT_NORESERVE`, and extending in-memory `i_size`.
- Drops or rewrites file extent items in `btrfs_drop_extents()`, handling full deletion, front/back truncation, middle splits, inline extent rejection, delayed ref updates, extent-map cache invalidation, and optional replacement-item setup.
- Converts preallocated extents to written regular extents in `btrfs_mark_extent_written()`, including splitting, merging adjacent compatible extents, delayed ref updates, generation changes, and file extent range tracking.
- Prepares folios for buffered writes, reads partial blocks when required, locks ranges, waits ordered extents, and retries when folios are invalidated or ordered I/O overlaps.
- Checks NOCOW write eligibility with `btrfs_check_nocow_lock()`, using the root snapshot lock and ordered-range flushing/try-locking before calling `can_nocow_extent()`.
- Performs common write preflight in `btrfs_write_check()`, including NOWAIT COW rejection, privilege stripping, timestamp/version updates, and hole expansion before writes past EOF.
- Reserves and releases data/metadata space for buffered writes, including metadata-only reservations for NOCOW fallback.
- Dispatches encoded, direct, and buffered writes from `btrfs_do_write_iter()`, rejecting writes during shutdown or filesystem error states and running write sync when needed.
- Implements `btrfs_sync_file()` for files and directories using tree logging when possible and transaction commit fallback when required.
- Handles mmap write faults in `btrfs_page_mkwrite()`, reserving delalloc before folio lock, handling EOF/truncate races, waiting ordered extents, zeroing partial EOF, and marking delalloc/dirty state.
- Inserts or merges explicit hole extent items in `fill_holes()` for filesystems without `NO_HOLES`, and installs hole extent maps or forces full fsync when extent-map insertion fails.
- Replaces file extents with holes or supplied replacement metadata through `btrfs_replace_file_extents()`.
- Implements hole punching, fallocate preallocation, zero range, delalloc/ordered range discovery, and `SEEK_DATA`/`SEEK_HOLE`.

Important data flows:
- Buffered write path: `btrfs_file_write_iter()` calls `btrfs_do_write_iter()`, which selects `btrfs_buffered_write()` unless direct or encoded I/O is requested. `btrfs_buffered_write()` locks the inode, runs generic and Btrfs write checks, then loops through `copy_one_range()` to reserve space, fault user pages, prepare a folio, wait conflicting ordered extents, copy bytes, mark delalloc, and release reservations.
- NOCOW reservation path: `reserve_space()` first tries normal data reservation. On reservation failure, it may call `btrfs_check_nocow_lock()` and reserve metadata only, with cleanup through `release_space()` or `shrink_reserved_space()`.
- Extent drop path: `btrfs_drop_extents()` searches file extent items around the requested range, adjusts overlapping regular/prealloc extents, rejects partial inline changes, deletes covered items in batches, updates delayed refs and bytes-found accounting, and may pre-create space for a replacement item.
- Fsync path: `btrfs_sync_file()` widens every fsync to the full file range, starts writeback before locking, locks inode plus mmap state, starts writeback again for concurrent dirties, then either waits ordered extents for full sync/zoned filesystems or gathers ordered extents for fast logging. It logs the dentry, syncs the log if possible, or commits a transaction on fallback.
- Mmap fault path: `btrfs_page_mkwrite()` reserves before folio locking to avoid writeback deadlocks, locks `i_mmap_lock`, locks the folio and io_tree range, waits ordered extents, clips to EOF, marks delalloc, sets dirty/uptodate bits, and returns the folio locked.
- Hole punching path: `btrfs_fallocate()` routes `FALLOC_FL_PUNCH_HOLE` to `btrfs_punch_hole()`, which zeros unaligned boundaries, waits ordered extents, locks and evicts page cache for the aligned range, calls `btrfs_replace_file_extents()` without replacement metadata, and updates inode metadata.
- Fallocate/zero-range path: `btrfs_zero_range()` avoids work when the target is already preallocated, handles unaligned boundary blocks, reserves data/qgroup space, locks the clean aligned range, uses preallocation, and updates `i_size`. `btrfs_fallocate()` scans extent maps to build coalesced ranges needing allocation.
- Seek path: `btrfs_file_llseek()` calls `find_desired_extent()`, which locks the searched io_tree range, walks file extent items, treats prealloc and explicit holes as holes, detects implicit holes, and overlays delalloc/ordered ranges so dirty data is reported as data.

Concurrency and locking:
- Buffered writes take the Btrfs inode lock, using `BTRFS_ILOCK_TRY` for NOWAIT.
- Write preparation locks folios and io_tree ranges and drops them to wait ordered extents when conflicts are found.
- NOCOW checks hold `root->snapshot_lock` in write mode on success; callers must release it with `btrfs_check_nocow_unlock()`.
- Fsync starts writeback outside inode lock, then locks inode plus `i_mmap_lock` to stabilize logging state.
- Hole punching and fallocate take inode and mmap locks exclusively, wait ordered extents, lock aligned io_tree ranges, and assert the target range is clean before metadata mutation.
- `btrfs_punch_hole_lock_range()` repeatedly truncates page cache, locks the io_tree range, and rechecks for folios to avoid racing page faults/reads.
- Per-file llseek cached state is stored in `file->private_data`, guarded during installation by `inode->lock`, and reused only by the owning task.

Important invariants:
- File extent item ranges and file extent presence tracking are sector aligned.
- `btrfs_drop_extents()` reports allocated bytes removed through `args->bytes_found`; callers update inode byte counts atomically with replacement/removal.
- Partial inline extent replacement/drop is unsupported and returns `-EOPNOTSUPP`.
- `btrfs_replace_file_extents()` returns an open transaction through `trans_out` on success; callers must finish inode updates and end the transaction.
- Explicit hole items are inserted only when `NO_HOLES` is disabled or replacement logic requires an item; otherwise file extent tracking is cleared.
- Fallocate is rejected on zoned filesystems.
- Fast fsync correctness depends on full-file range consideration, ordered extent checksum handling, and hole extent maps; failures to install hole maps force full sync.
- `SEEK_HOLE` can return `i_size` quickly only when the inode has no prealloc extents and allocated bytes equal `i_size`.
- `btrfs_fdatawrite_range()` intentionally performs a second writeback pass when async compression has staged extents but not yet marked pages writeback.

Notable risks:
- `btrfs_drop_extents()` and `btrfs_mark_extent_written()` mutate B-tree items, delayed refs, extent-map cache, inode byte accounting, and file extent presence state in tightly coupled sequences.
- Buffered write cleanup has many branches for data reservations, metadata reservations, NOCOW metadata-only state, extent locks, folio references, and cached extent states.
- Mmap write faults reserve before folio locking, so all error paths must release the correct reservation type and possibly the NOCOW snapshot lock.
- Fsync deliberately widens the requested range; narrowing it would risk missing holes, checksums, or ordered extents.
- `btrfs_replace_file_extents()` restarts transactions inside a loop, so callers must tolerate partial progress and repeated inode timestamp/version updates.
- Large folio handling in hole punching avoids false positives from generic page-cache range checks; future page-cache changes must preserve the head/tail folio assumptions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/file.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/file.h

Public Btrfs regular-file interface. This header declares the VFS file operations table and the main regular-file helpers implemented by `file.c` and consumed by inode, direct I/O, encoded I/O, ioctl, reflink, logging, mmap, and writeback paths.

Key responsibilities:
- Exposes `btrfs_file_operations` for regular-file VFS registration.
- Declares `btrfs_sync_file()` for fsync and directory sync through tree logging or transaction commit.
- Declares file extent mutation APIs: `btrfs_drop_extents()`, `btrfs_replace_file_extents()`, and `btrfs_mark_extent_written()`.
- Declares common write dispatch through `btrfs_do_write_iter()`, with optional encoded I/O arguments.
- Declares file release cleanup through `btrfs_release_file()`.
- Declares `btrfs_dirty_folio()` for marking copied page-cache data as delalloc and dirty.
- Declares `btrfs_fdatawrite_range()` for writeback with Btrfs compression-specific retry behavior.
- Declares NOCOW check/lock and unlock helpers.
- Declares `btrfs_find_delalloc_in_range()` for discovering dirty or ordered ranges before file extent items exist.
- Declares `btrfs_write_check()` and `btrfs_buffered_write()` for shared write validation and buffered write entry.

Dependencies and invariants:
- Includes Linux basic type definitions and forward-declares VFS, iterator, folio/page, Btrfs inode/root/path/transaction, drop-extents, replace-extent, and encoded-I/O structures.
- A positive `btrfs_check_nocow_lock()` return means the caller owns the root snapshot write lock and must call `btrfs_check_nocow_unlock()`.
- `btrfs_replace_file_extents()` expects the target range and inode to already be locked and returns a transaction handle through `trans_out` on success.
- `btrfs_drop_extents()` behavior is controlled by caller-supplied `struct btrfs_drop_extents_args`, including path ownership, replacement mode, cache dropping, extent item size, and byte accounting.
- `btrfs_dirty_folio()` assumes the folio covers the written byte range and updates both Btrfs extent state and folio state.

Notable risks:
- This header exposes low-level file extent mutation functions whose correctness depends on external locking and transaction context.
- The write helpers mix VFS-facing and Btrfs-internal contracts; prototype changes must stay synchronized with direct I/O, encoded I/O, ioctl, and inode callers.
- Misuse of NOCOW lock helpers can leave the snapshot lock held or permit unsafe writes into shared/snapshotted extents.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/file.h -->