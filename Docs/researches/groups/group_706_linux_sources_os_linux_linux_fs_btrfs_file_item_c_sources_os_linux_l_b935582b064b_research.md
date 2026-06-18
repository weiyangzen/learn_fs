# Group Research: group_706_linux_sources_os_linux_linux_fs_btrfs_file_item_c_sources_os_linux_l_b935582b064b

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/os/linux/linux`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/file-item.c -->
# File Research: sources/os/linux/linux/fs/btrfs/file-item.c

Btrfs file extent item and checksum implementation. This file provides the low-level helpers that connect file extent B-tree items, in-memory extent maps, inode file-extent presence tracking, and data checksum tree operations used by read, write, logging, truncation, relocation, and extent replacement paths.

Key responsibilities:
- Maintains `inode->disk_i_size` safely with respect to the `NO_HOLES` feature and the in-memory `file_extent_tree`; without `NO_HOLES`, persisted size is limited to the contiguous file-extent-covered range from offset 0.
- Marks or clears inode logical ranges in `inode->file_extent_tree` when file extent items are inserted or removed, enforcing sector alignment except for clear-to-end truncation cases.
- Converts between logical byte counts and packed checksum item byte counts using filesystem sector size and checksum size.
- Inserts explicit regular file extent items representing holes via `btrfs_insert_hole_extent()`.
- Looks up file extent items with `btrfs_lookup_file_extent()`, forwarding caller intent for insertion length and COW/modification.
- Looks up checksums for read bios in `btrfs_lookup_bio_sums()`, including inline checksum storage, heap fallback, csum-tree readahead, free-space-inode commit-root search, and commit-root semaphore protection for past-transaction reads.
- Searches checksum items for arbitrary ranges as either ordered-sum list records (`btrfs_lookup_csums_list()`) or caller-provided checksum buffer plus sector bitmap (`btrfs_lookup_csums_bitmap()`).
- Computes write bio checksums in `btrfs_csum_one_bio()`, either synchronously or through `csum_one_bio_work()`, and attaches `struct btrfs_ordered_sum` to the ordered extent.
- Allocates dummy ordered sums for zoned nodatasum writes so zone append completion can record logical addresses even without checksum bytes.
- Deletes checksum ranges from the checksum tree or log tree through whole-item deletion, batched adjacent-item deletion, middle split, and leading/trailing truncation.
- Inserts ordered-sum checksums into existing or new checksum items, extending adjacent checksum items when possible while respecting max item size, leaf free space, and log-tree next-item boundaries.
- Converts on-disk file extent items into in-memory extent maps for regular, prealloc, explicit hole, compressed, and inline extents.
- Computes the exclusive logical end of a file extent item, rounding inline extents to one sector.

Important data flows:
- `btrfs_lookup_bio_sums()` derives the bio disk range from `bi_iter`, allocates `bbio->csum`, optionally switches to commit-root search, then walks the requested disk range with `search_csum_tree()`. Missing checksums become warnings for normal data but are tolerated for data relocation by marking the inode io tree with `EXTENT_NODATASUM`.
- `btrfs_lookup_csums_list()` searches from the requested start, backs up to a previous overlapping checksum item if needed, then emits one or more `btrfs_ordered_sum` chunks capped by `max_ordered_sum_bytes()`.
- `btrfs_lookup_csums_bitmap()` performs the same checksum-tree walk but copies checksum bytes into a range-relative buffer and sets one bitmap bit per sector covered by a checksum.
- `btrfs_csum_one_bio()` allocates an ordered sum sized for the bio, records the original logical offset and length, attaches it to the ordered extent, and either computes checksum bytes immediately or schedules work that signals `bbio->csum_done`.
- `btrfs_insert_data_csums()` starts at `sums->logical`, repeatedly tries to find or extend an existing checksum item, otherwise inserts a new item sized according to remaining checksums and next checksum item position, then copies checksum bytes until `sums->len` is covered.
- `btrfs_del_csums()` walks backward from the end of the deletion range, which lets it batch-delete covered checksum items and safely handle earlier overlapping items without skipping ranges after mutation.
- `btrfs_extent_item_to_extent_map()` reads the current B-tree path key and item fields, then fills extent-map logical start, length, disk address, disk length, offset, generation, ram bytes, compression flag, prealloc flag, hole marker, or inline marker.

Concurrency and locking:
- `btrfs_inode_safe_disk_i_size_write()` holds `inode->lock` while consulting `file_extent_tree` and updating `disk_i_size`.
- Checksum lookups use B-tree path locking, but commit-root checksum searches set `path->search_commit_root` and `path->skip_locking` while holding `fs_info->commit_root_sem` across multiple searches to avoid mixing checksums from different committed roots.
- Async checksum generation stores the bio iterator in `bbio->csum_saved_iter`, schedules `csum_work`, and completes `bbio->csum_done`.
- Checksum insertion/deletion are transaction-bound B-tree mutations; unrecoverable metadata update failures abort the transaction.
- The bitmap checksum lookup can reuse a caller-supplied B-tree path and leaves path lifecycle to the caller unless it allocated the path internally.

Important invariants:
- Checksum ranges, checksum sizes, and file extent presence ranges are sector/checksum-size aligned.
- A checksum item key offset plus its packed item size defines the logical range covered by the item.
- `btrfs_lookup_csum()` returns `-EFBIG` when the target checksum is exactly at the end of the previous item, signaling an adjacent extension opportunity.
- Missing read checksums are exceptional for normal data roots, but data relocation may copy nodatasum extents whose owning inode flags are not visible on the relocation inode.
- Log-tree checksum insertion must not extend an item across the start offset of a later checksum item already present in the log.
- Inline file extents are represented as `EXTENT_MAP_INLINE`, start at logical offset 0, and get an extent-map length of one sector.
- For old uncompressed regular extents with `ram_bytes < disk_num_bytes`, the extent-map ram bytes are normalized to `disk_num_bytes`.

Notable risks:
- Checksum deletion mutates packed item contents, keys, and item boundaries in several overlap cases; alignment or off-by-one errors can corrupt checksum coverage.
- Commit-root checksum search correctness depends on holding `commit_root_sem` for the whole multi-search walk.
- Checksum insertion optimizes by extending items, but log trees need extra next-offset checks because partial fsyncs can already have overlapping checksum subsets.
- File extent range tracking is used to decide safe persisted i_size without `NO_HOLES`; missed set/clear calls can produce incorrect on-disk size updates.
- `btrfs_extent_item_to_extent_map()` relies on tree-checker invariants for inline extents and only reports unknown extent types as filesystem errors.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/file-item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/file-item.h -->
# File Research: sources/os/linux/linux/fs/btrfs/file-item.h

Public Btrfs file item and checksum interface. This header exposes inline file extent layout helpers and declares the file extent, checksum, ordered-sum, extent-map conversion, and inode file-extent tracking APIs implemented by `file-item.c` or expected by nearby Btrfs code.

Key responsibilities:
- Defines `BTRFS_FILE_EXTENT_INLINE_DATA_START`, the offset in `struct btrfs_file_extent_item` where inline payload begins.
- Computes the maximum inline data payload for a filesystem from `BTRFS_MAX_ITEM_SIZE()` minus the inline extent header.
- Computes inline payload length from a leaf item size by subtracting `BTRFS_FILE_EXTENT_INLINE_DATA_START`.
- Provides pointer arithmetic helpers for inline payload start and inline item size calculation.
- Declares checksum deletion, read-bio checksum lookup, checksum insertion, write-bio checksum calculation, dummy ordered-sum allocation, list-style checksum lookup, and bitmap-style checksum lookup.
- Declares hole extent insertion and file extent item lookup.
- Declares conversion from a file extent item and B-tree path into a `struct extent_map`.
- Declares inode file extent range set/clear helpers and safe `disk_i_size` update.
- Declares `btrfs_file_extent_end()` for deriving the exclusive logical end of a file extent item.

Dependencies:
- Includes Linux block and list definitions, the Btrfs tree UAPI, `ctree.h`, and `ordered-data.h`.
- Forward-declares `extent_map`, Btrfs path, bio, transaction, root, ordered sum, inode, and file extent structures.

Important invariants:
- Inline layout helpers must match the on-disk `struct btrfs_file_extent_item` layout exactly.
- `btrfs_file_extent_inline_item_len()` reports compressed size for compressed inline extents because it measures stored item payload bytes.
- Public checksum APIs operate on logical disk byte ranges aligned to the filesystem sector size.
- `btrfs_inode_set_file_extent_range()` and `btrfs_inode_clear_file_extent_range()` callers are responsible for passing ranges that match file extent item boundaries.

Notable risks:
- This header exposes low-level mutation helpers; callers must already satisfy the required transaction, path, inode lock, mmap lock, and extent lock contracts established by higher-level code.
- The header declares `btrfs_lookup_csums_range()`, but this file group contains no implementation in `file-item.c`; within the checked tree only the declaration was found, while `btrfs_lookup_csums_list()` and `btrfs_lookup_csums_bitmap()` are implemented here.
- Any future on-disk file extent layout change must update these helpers and all tree-checker assumptions together.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/file-item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/file.c -->
# File Research: sources/os/linux/linux/fs/btrfs/file.c

Btrfs regular-file VFS implementation and file extent mutation code. This file implements buffered writes, write validation and dispatch, fsync/logging, mmap write faults, extent dropping and replacement, hole punching, fallocate and zero range, delalloc discovery, SEEK_DATA/SEEK_HOLE, open/read/splice/mmap hooks, and the exported `btrfs_file_operations` table.

Key responsibilities:
- Marks folios dirty for buffered writes through `btrfs_dirty_folio()`, including delalloc state, folio uptodate/dirty bits, checked-bit clearing, `EXTENT_NORESERVE`, and in-memory i_size extension.
- Drops or rewrites file extent items with `btrfs_drop_extents()`, handling full deletion, front/back truncation, middle split, inline extent rejection, reference updates, extent-map cache dropping, and optional replacement item setup.
- Converts preallocated extents to written regular extents with `btrfs_mark_extent_written()`, including splitting into multiple file extent items, merging adjacent compatible written extents, delayed ref updates, generation updates, and file extent range tracking.
- Prepares folios for buffered writes, reads partial blocks when required, sets extent mapping private data, locks ranges, waits for ordered extents, and retries when folios are invalidated or ordered I/O overlaps.
- Probes NOCOW write eligibility with `btrfs_check_nocow_lock()`, using the root snapshot lock, ordered-range flushing or try-locking, and `can_nocow_extent()` over the candidate range.
- Performs common write validation in `btrfs_write_check()`, including NOWAIT COW rejection, privilege stripping, time/version updates, and hole expansion before writes past EOF.
- Reserves and releases data/metadata space for buffered writes, including metadata-only reservations for NOCOW fallback and careful shrinking after short copies or folio-boundary clipping.
- Implements the buffered write loop through `btrfs_buffered_write()` and `copy_one_range()`, copying at most one folio-sized chunk per iteration and updating `ki_pos` only after successful bytes are copied.
- Dispatches encoded, direct, and buffered writes from `btrfs_do_write_iter()`, rejects writes during shutdown or filesystem error state, and performs generic write sync after successful data writes.
- Cleans per-file private state and flush-on-close state in `btrfs_release_file()`.
- Implements `btrfs_sync_file()` for file and directory fsync, using tree logging when possible and transaction commit fallback when required.
- Implements mmap write faults through `btrfs_page_mkwrite()`, reserving delalloc space before taking the folio lock to avoid writeback deadlocks, handling EOF/truncate races, waiting ordered extents, zeroing partial EOF, and setting delalloc/dirty state.
- Inserts or merges explicit hole extent items in `fill_holes()` for filesystems without `NO_HOLES`, and installs hole extent maps or forces full fsync when extent-map insertion fails.
- Replaces file extents through `btrfs_replace_file_extents()`, used by hole punching and clone/dedupe-style replacement, with transaction restart handling and optional replacement extent insertion.
- Implements `btrfs_punch_hole()`, including unaligned head/tail zeroing, ordered extent waits, range locking with page-cache eviction, file extent replacement, inode timestamp/version updates, and transaction completion.
- Implements `btrfs_fallocate()` and `btrfs_zero_range()`, including qgroup/data reservations, preallocation range coalescing, keep-size behavior, i_size updates, zoned rejection, and optimized handling of already preallocated ranges.
- Finds delalloc and ordered subranges with `btrfs_find_delalloc_in_range()` and uses this to implement correct `SEEK_DATA`/`SEEK_HOLE` over explicit extents, implicit holes, prealloc extents, and dirty ranges.
- Defines regular-file read, splice, open, mmap, llseek, fsync, fallocate, ioctl, remap, io_uring command, and lease operations in `btrfs_file_operations`.
- Provides `btrfs_fdatawrite_range()`, including a second writeback pass when async compression has staged extents but not yet marked pages writeback.

Important data flows:
- Buffered write path: `btrfs_file_write_iter()` calls `btrfs_do_write_iter()`, which selects `btrfs_buffered_write()` unless direct or encoded I/O is requested. `btrfs_buffered_write()` locks the inode, runs generic checks and `btrfs_write_check()`, then repeatedly calls `copy_one_range()` to reserve space, fault user pages, prepare a folio, wait conflicting ordered extents, copy data, mark delalloc, and release reservations.
- NOCOW reservation path: `reserve_space()` first tries normal data reservation. On reservation failure, it may call `btrfs_check_nocow_lock()` and reserve metadata only, with cleanup routed through `release_space()` or `shrink_reserved_space()`.
- Extent drop path: `btrfs_drop_extents()` searches file extent items around the requested range, adjusts overlapping regular/prealloc extents, rejects partial inline changes, deletes covered items in batches, updates delayed refs and bytes-found accounting, and may pre-create space for a replacement extent item.
- Fsync path: `btrfs_sync_file()` widens every fsync to the full file range, starts writeback before locking, locks inode plus mmap state, starts writeback again for concurrent dirties, then either waits ordered extents for full sync/zoned filesystems or gathers ordered extents for fast logging. It logs the dentry, syncs the log if possible, or commits the transaction if logging is impossible or fails.
- Mmap write-fault path: `btrfs_page_mkwrite()` reserves data and metadata before folio lock, falls back to metadata-only NOCOW when possible, locks `i_mmap_lock`, locks the folio and io_tree range, waits ordered extents, clips to EOF, marks delalloc, sets dirty/uptodate bits, and returns `VM_FAULT_LOCKED`.
- Hole punching path: `btrfs_fallocate()` routes `FALLOC_FL_PUNCH_HOLE` to `btrfs_punch_hole()`. The punch helper waits ordered extents, zeros unaligned boundary blocks, locks a clean aligned range with `btrfs_punch_hole_lock_range()`, calls `btrfs_replace_file_extents()` with no replacement extent, and updates inode metadata.
- Replacement path: `btrfs_replace_file_extents()` loops over the target range, drops extents, fills holes or clears file-extent tracking, inserts replacement extent items if requested, updates inode time/version at transaction boundaries, restarts transactions, and returns the final open transaction through `trans_out` on success.
- Zero range/fallocate path: `btrfs_zero_range()` avoids work when the target is already preallocated, partially zeros written boundary blocks when needed, reserves data/qgroup space, locks the clean aligned range, then uses `btrfs_prealloc_file_range()` and updates i_size. `btrfs_fallocate()` scans extent maps to build coalesced ranges needing allocation before calling preallocation helpers.
- Seek path: `btrfs_file_llseek()` locks the inode shared and calls `find_desired_extent()`, which locks the searched io_tree range, walks file extent items, treats prealloc and explicit holes as holes, detects implicit holes between extent items, and overlays delalloc/ordered ranges so dirty data is reported as data.

Concurrency and locking:
- Buffered writes take the Btrfs inode lock, using `BTRFS_ILOCK_TRY` for NOWAIT.
- Write preparation locks folios and io_tree ranges and drops those locks to wait ordered extents when conflicts are found.
- NOCOW checks hold `root->snapshot_lock` in write mode while proving and preserving NOCOW eligibility; callers release it with `btrfs_check_nocow_unlock()`.
- Fsync starts writeback outside the inode lock for concurrency, then locks inode plus `i_mmap_lock` to stabilize logging state and starts writeback again to close races.
- `btrfs_page_mkwrite()` uses pagefault accounting, pre-folio-lock reservation, `i_mmap_lock`, folio lock, io_tree extent lock, and ordered-extent waits.
- Hole punching and fallocate take inode and mmap locks exclusively, wait ordered extents, lock aligned io_tree ranges, and assert the target range is clean before metadata mutation.
- `btrfs_punch_hole_lock_range()` repeatedly truncates page cache, locks the io_tree range, and rechecks for folios to avoid racing readers that refault pages.
- Per-file `llseek` cached state is stored in `file->private_data`, guarded by `inode->lock` during installation, and only reused by the owning task.

Important invariants:
- File extent item ranges and file extent presence tracking are sector aligned.
- `btrfs_drop_extents()` does not update VFS inode byte counts itself; it reports `args->bytes_found` so callers can update accounting atomically with extent replacement or removal.
- Partial inline extent replacement/drop is unsupported and returns `-EOPNOTSUPP` in the relevant paths.
- `btrfs_replace_file_extents()` returns an open transaction through `trans_out` on success; callers must update inode metadata as needed and end the transaction.
- Explicit hole items are inserted only when `NO_HOLES` is disabled or replacement logic requires an item; otherwise the file extent presence tree is cleared.
- Fallocate is rejected on zoned filesystems in this path.
- Fast fsync correctness depends on full-file range consideration, ordered extent checksum handling, and hole extent maps; failures to install hole extent maps force full sync.
- `SEEK_HOLE` can return `i_size` quickly only when the inode has no prealloc extents and allocated bytes equal i_size.
- `btrfs_fdatawrite_range()` intentionally performs a second writeback pass for compressed async extents.

Notable risks:
- `btrfs_drop_extents()` and `btrfs_mark_extent_written()` mutate B-tree items, delayed refs, extent-map cache, inode byte accounting, and file extent presence state in tightly coupled sequences; errors often require transaction aborts to avoid corruption.
- Buffered write cleanup has many branches for data reservations, metadata reservations, NOCOW metadata-only state, extent locks, folio references, and cached extent states.
- Mmap write faults reserve before folio locking to avoid deadlocks, so all failure paths must release the correct reservation type and possibly the NOCOW snapshot lock.
- Fsync deliberately widens the requested range; narrowing it would risk missing holes, checksums, or ordered extents documented in the code comments.
- `btrfs_replace_file_extents()` restarts transactions inside a loop, so callers must tolerate partial progress and repeated inode timestamp/version updates.
- Large folio handling in hole punching avoids false positives from generic page-cache range checks; future page-cache changes must preserve the head/tail folio assumptions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/file.h -->
# File Research: sources/os/linux/linux/fs/btrfs/file.h

Public Btrfs regular-file operation interface. This header declares the VFS file operations table and the main regular-file helpers implemented by `file.c` and used by inode, direct I/O, encoded I/O, ioctl, reflink, logging, and writeback paths.

Key responsibilities:
- Exposes `btrfs_file_operations` for regular-file VFS registration.
- Declares `btrfs_sync_file()` for fsync and directory sync through tree logging or transaction commit.
- Declares file extent mutation APIs: `btrfs_drop_extents()`, `btrfs_replace_file_extents()`, and `btrfs_mark_extent_written()`.
- Declares common write dispatch through `btrfs_do_write_iter()`, with optional encoded I/O arguments.
- Declares file release cleanup through `btrfs_release_file()`.
- Declares `btrfs_dirty_folio()` for marking copied page-cache data as delalloc and dirty.
- Declares `btrfs_fdatawrite_range()` for writeback with Btrfs compression-specific handling.
- Declares NOCOW check/lock and unlock helpers.
- Declares `btrfs_find_delalloc_in_range()` for discovering dirty or ordered ranges before file extent items exist.
- Declares `btrfs_write_check()` and `btrfs_buffered_write()` for shared write validation and buffered write entry.

Dependencies:
- Includes Linux basic type definitions.
- Forward-declares VFS file/inode/kiocb/iov_iter/folio/page structures and Btrfs inode, root, path, transaction, drop-extents, replace-extent, and encoded I/O structures.

Important invariants:
- A positive `btrfs_check_nocow_lock()` result means the caller owns the root snapshot write lock and must call `btrfs_check_nocow_unlock()`.
- `btrfs_replace_file_extents()` expects the target range and inode to already be locked by the caller and returns a transaction handle through `trans_out` on success.
- `btrfs_drop_extents()` behavior is controlled by caller-supplied `struct btrfs_drop_extents_args`, including path ownership, replacement mode, cache dropping, extent item size, and byte accounting.
- `btrfs_dirty_folio()` assumes the folio covers the written byte range and updates both Btrfs extent state and folio state.

Notable risks:
- This header exposes low-level file extent mutation functions whose correctness depends on external locking and transaction context.
- The write helpers mix VFS-facing and Btrfs-internal contracts; prototype changes must stay synchronized with direct I/O, encoded I/O, ioctl, and inode callers.
- Misuse of the NOCOW lock helpers can leave the snapshot lock held or permit unsafe writes into shared or snapshotted extents.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/file.h -->