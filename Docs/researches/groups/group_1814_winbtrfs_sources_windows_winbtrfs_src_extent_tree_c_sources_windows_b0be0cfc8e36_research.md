# Group Research: group_1814_winbtrfs_sources_windows_winbtrfs_src_extent_tree_c_sources_windows_b0be0cfc8e36

Scope: subset A (`Docs/research_subset_a.md`), source tree `sources/windows/winbtrfs`.

Files researched:
- `sources/windows/winbtrfs/src/extent-tree.c`
- `sources/windows/winbtrfs/src/fastio.c`

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/extent-tree.c -->
# File Research: sources/windows/winbtrfs/src/extent-tree.c

## Scope

This file implements WinBtrfs extent-tree reference manipulation and changed-extent staging. It covers Btrfs extent item creation, conversion from old extent formats, inline and non-inline backreference insertion/removal, refcount and uniqueness queries, extent flag reads/writes, and in-memory tracking of changed data extents before transaction flush.

The file is in subset A through `sources/windows/winbtrfs`.

## High-Level Role

`extent-tree.c` is the driver-side extent accounting layer for WinBtrfs. Its main responsibility is to keep the on-disk extent tree consistent when file data or tree blocks gain or lose references. It knows the Btrfs extent item encodings (`EXTENT_ITEM`, `EXTENT_ITEM_V0`, skinny metadata items, inline refs, and separate ref items) and provides the helpers used by higher-level write, COW, truncation, deletion, and flush paths.

Core responsibilities:
- Compute Btrfs extent-data-reference hashes.
- Build sorted extent-reference lists and serialize them as inline refs or separate ref tree items.
- Upgrade old `EXTENT_ITEM_V0` plus `TYPE_EXTENT_REF_V0` records into current extent items.
- Increase and decrease extent refcounts for data, tree blocks, shared data, shared tree blocks, and legacy refs.
- Delete checksum ranges when data extents become unreferenced and are not superseded.
- Query total extent refcounts, uniqueness, flags, and shared-ref counts.
- Maintain per-chunk `changed_extent` records with current and old extent-data refs for later commit processing.

## Main APIs And Entry Points

- `get_extent_data_ref_hash2(root, objid, offset)`: computes the Btrfs hash key for an `EXTENT_DATA_REF` from root, inode/object id, and logical offset.
- `increase_extent_refcount(...)`: central insertion/increment path for extent refs. It creates missing extent items, converts old items, increments inline refcounts, inserts new inline refs when size allows, or creates separate non-inline ref items.
- `increase_extent_refcount_data(...)`: data-ref convenience wrapper around `increase_extent_refcount`.
- `decrease_extent_refcount(...)`: central deletion/decrement path. It locates skinny or normal extent items, converts old items as needed, decrements inline or non-inline refs, deletes the whole extent item when the total refcount reaches zero, and removes checksums for dropped data extents.
- `decrease_extent_refcount_data(...)`: data-ref convenience wrapper around `decrease_extent_refcount`.
- `decrease_extent_refcount_tree(...)`: tree-block-ref convenience wrapper around `decrease_extent_refcount`.
- `get_extent_refcount(...)`: returns the stored total refcount from skinny metadata, normal extent items, or old extent items.
- `is_extent_unique(...)`: determines whether all refs for a data extent point at the same root/object/offset, allowing multi-count refs to still count as unique to one logical owner.
- `get_extent_flags(...)` and `update_extent_flags(...)`: read and mutate the `EXTENT_ITEM.flags` field.
- `update_changed_extent_ref(...)`: transaction-time staging API that updates or creates a `changed_extent` entry under the chunk's `changed_extents_lock`, preserving old refs and applying ref deltas.
- `add_changed_extent_ref(...)`: simpler changed-extent append/merge path without old-ref lookup or locking in this function.
- `find_extent_shared_tree_refcount(...)`: returns whether a shared tree block ref exists for a parent.
- `find_extent_shared_data_refcount(...)`: returns the count for a shared data ref by parent.

## Internal Helpers

- `extent_ref` is a local list node that stores one of `EXTENT_DATA_REF`, `SHARED_DATA_REF`, `TREE_BLOCK_REF`, or `SHARED_BLOCK_REF`, plus its type and sort hash.
- `get_extent_hash(type, data)` normalizes the key offset/hash for each supported ref type.
- `free_extent_refs`, `add_shared_data_extent_ref`, `add_shared_block_extent_ref`, and `add_tree_block_extent_ref` build temporary reference lists while converting old extents.
- `sort_extent_refs` insertion-sorts refs by type ascending and hash descending, matching the ordering expected by this implementation.
- `construct_extent_item(...)` serializes a newly constructed extent item, keeping as many refs inline as fit within one quarter of the node size and inserting the rest as separate ref items.
- `convert_old_extent(...)` deletes a legacy old-style extent item, scans following `TYPE_EXTENT_REF_V0` items, transforms them into current shared/tree refs, and reinserts a modern extent item.
- `find_extent_data_refcount(...)` searches inline refs first, then non-inline `TYPE_EXTENT_DATA_REF`, to discover the previous count for a specific data ref.
- `get_changed_extent_item(...)` finds or allocates a per-chunk `changed_extent`.

## Control Flow And Algorithms

Extent ref insertion starts by locating the expected extent-tree item. For missing items, `increase_extent_refcount` constructs a new `EXTENT_ITEM`, optionally appending `EXTENT_ITEM2` for non-skinny tree blocks, writes the first inline ref, and inserts either `TYPE_METADATA_ITEM` or `TYPE_EXTENT_ITEM`. Existing old-format items are first converted through `convert_old_extent`, after which the insertion retries against the modern format.

For existing modern extent items, insertion scans inline refs and handles matching refs in place by copying the extent item, increasing both the total `EXTENT_ITEM.refcount` and the matching section count where applicable, deleting the old tree item, and reinserting the updated copy. If no matching inline ref exists and all refs are still inline, the function inserts a new inline section when the item stays below the local max inline item size. Otherwise it searches or creates the appropriate non-inline ref item and updates the main extent item's total refcount.

Extent ref deletion mirrors that model. `decrease_extent_refcount` finds skinny metadata or normal extent items, validates size and refcount, scans inline sections, and either deletes the whole extent item when the requested removal consumes the total refcount or rewrites the item with a reduced or removed section. If inline refs do not account for the full total, it locates the non-inline ref item, reduces or deletes that item, then reduces or deletes the owning extent item. Data extent removal calls `add_checksum_entry(..., NULL, ...)` when the extent is no longer referenced and the removal is not superseded.

Old extent conversion reads a legacy `EXTENT_ITEM_V0`, deletes it, then walks following `TYPE_EXTENT_REF_V0` entries for the same address. Tree refs become top-level `TREE_BLOCK_REF` entries when the old ref's key offset equals the extent address, otherwise shared block refs. Data refs become shared data refs keyed by parent. The converted item is rebuilt by `construct_extent_item` with `EXTENT_ITEM_SHARED_BACKREFS`.

Uniqueness is stricter than a raw refcount test. `is_extent_unique` returns true immediately for refcount 1, but for higher counts it accepts only `TYPE_EXTENT_DATA_REF` refs and requires every inline and non-inline ref to share the same root, inode, and offset. Any shared refs, old-format items, malformed items, missing refs, or unaccounted refs make the function return false.

Changed-extent staging groups ref deltas by chunk, address, and size. `update_changed_extent_ref` initializes `ce->count` and `ce->old_count` from the current extent-tree item, records the old data ref count in `ce->old_refs` if one exists, records the new count in `ce->refs`, applies the signed delta, and marks the extent as superseded when requested. This gives later flush code enough state to reconcile data extent ref changes and checksum handling.

## Important State Mutated

- Extent tree items in `Vcb->extent_root`, including `TYPE_EXTENT_ITEM`, `TYPE_METADATA_ITEM`, `TYPE_EXTENT_DATA_REF`, `TYPE_SHARED_DATA_REF`, `TYPE_TREE_BLOCK_REF`, `TYPE_SHARED_BLOCK_REF`, and legacy `TYPE_EXTENT_REF_V0`.
- `EXTENT_ITEM.refcount`, `EXTENT_ITEM.generation`, and `EXTENT_ITEM.flags`.
- Inline ref records embedded after `EXTENT_ITEM` and optional `EXTENT_ITEM2`.
- Checksum tree ranges through `add_checksum_entry` when data extents are fully removed.
- Per-chunk `changed_extents`, each `changed_extent`'s `count`, `old_count`, `no_csum`, `superseded`, `refs`, and `old_refs`.

## Dependencies

This file depends heavily on project-local Btrfs tree helpers and definitions from `btrfs_drv.h`, including:
- `find_item`, `find_next_item`, `insert_tree_item`, `delete_tree_item`, and `keycmp`.
- `get_extent_data_len`, `get_extent_data_refcount`, `add_checksum_entry`.
- Btrfs structures and constants such as `EXTENT_ITEM`, `EXTENT_ITEM2`, `EXTENT_ITEM_V0`, `EXTENT_DATA_REF`, `SHARED_DATA_REF`, `TREE_BLOCK_REF`, `SHARED_BLOCK_REF`, `EXTENT_REF_V0`, `TYPE_EXTENT_ITEM`, `TYPE_METADATA_ITEM`, and `BTRFS_INCOMPAT_FLAGS_SKINNY_METADATA`.
- Runtime state structures such as `device_extension`, `chunk`, `changed_extent`, `changed_extent_ref`, `KEY`, and `traverse_ptr`.

Windows kernel dependencies include pool allocation/freeing (`ExAllocatePoolWithTag`, `ExFreePool`), list primitives (`LIST_ENTRY`, `InsertTailList`, `RemoveEntryList`, `IsListEmpty`), resource locking (`ExAcquireResourceExclusiveLite`, `ExReleaseResourceLite`), and memory copying (`RtlCopyMemory`).

## Notable Behaviors

- Inline refs are preferred while the extent item remains below a fraction of the Btrfs node size; larger ref sets spill into separate keyed ref items.
- The code supports skinny metadata for tree blocks by using `TYPE_METADATA_ITEM` keyed by level and omitting `EXTENT_ITEM2`.
- Some ref types are idempotent for increases: attempts to increase non-shared tree refs or shared block refs that already exist return success rather than increasing an embedded count.
- Shared data refs store a full `SHARED_DATA_REF` inline, but non-inline `TYPE_SHARED_DATA_REF` items store only a `uint32_t` count keyed by parent.
- `update_extent_flags` mutates the item data in place after locating the tree item, unlike most refcount paths that delete and reinsert copied items.
- Query helpers generally return `0` or `false` on malformed or missing items after logging, so callers must treat those values as failure-prone rather than authoritative absence in all contexts.

## Risks And Edge Cases

- Several allocation results are not consistently checked before use. In the inline insertion path, `newei = ExAllocatePoolWithTag(...)` is followed immediately by `RtlCopyMemory(newei, ...)` without a null check, unlike most neighboring allocations.
- Delete-then-reinsert update patterns can leave the extent tree partially changed if reinsertion fails after a successful deletion. The broader transaction/rollback layer has to recover from these intermediate states.
- Some allocated buffers are not freed on later failure paths because ownership is transferred only on successful `insert_tree_item`; if insertion fails, the local buffer can leak unless the callee takes ownership on failure.
- `decrease_extent_refcount_tree` passes `NULL` for `firstitem` with a FIXME. If an old tree extent must be converted in that path, conversion may lack accurate first-item metadata.
- `find_extent_shared_tree_refcount` and `find_extent_shared_data_refcount` contain FIXME comments for old-format extent handling; old extent items may yield incomplete shared-ref answers.
- `is_extent_unique` searches only normal `TYPE_EXTENT_ITEM` at `(address, size)` after `get_extent_refcount`; skinny metadata is not part of its positive path and old-format items are treated as non-unique.
- Hash collision handling for non-inline `TYPE_EXTENT_DATA_REF` and `TYPE_SHARED_DATA_REF` logs an internal error. The code detects collisions but does not have a collision-resolution scheme beyond failing.
- `add_changed_extent_ref` manipulates `changed_extents` without acquiring `changed_extents_lock` in this function, unlike `update_changed_extent_ref`; callers must provide synchronization if used concurrently.
- `update_extent_flags` returns `void` and only logs failures, so callers cannot tell whether a flag update actually landed.

## Cross-File Relationships

- `flushthread.c` calls the extent refcount and changed-extent helpers while committing dirty trees, data extents, chunks, and checksums.
- File write/truncate/delete paths depend on `increase_extent_refcount_data`, `decrease_extent_refcount_data`, and changed-extent staging to maintain data extent ownership.
- Metadata COW paths depend on `increase_extent_refcount` and `decrease_extent_refcount_tree` for tree block lifetime.
- Checksum maintenance is delegated to `add_checksum_entry`, which is implemented outside this file and is triggered here only when data extent references are fully dropped.

## Summary

`extent-tree.c` is the WinBtrfs extent-reference authority. It translates higher-level ownership changes into precise Btrfs extent-tree mutations, including old-format migration, skinny metadata support, inline/non-inline backref management, checksum invalidation for freed data extents, and per-chunk changed-extent bookkeeping. Its correctness is central to avoiding leaked extents, premature frees, corrupted backrefs, and incorrect copy-on-write decisions.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/extent-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/fastio.c -->
# File Research: sources/windows/winbtrfs/src/fastio.c

## Scope

This file initializes and implements the Windows `FAST_IO_DISPATCH` callbacks for WinBtrfs. It covers fast metadata queries, fast read/write dispatch integration, byte-range locking callbacks, cache manager section/flush callbacks, and resource acquisition ordering around copy-on-write filesystem state.

The file is in subset A through `sources/windows/winbtrfs`.

## High-Level Role

`fastio.c` is the fast-path bridge between the Windows I/O manager/cache manager and WinBtrfs FCB/CCB state. It answers simple file information queries without building full IRPs when safe, delegates cached reads and writes to FsRtl helpers, implements fast byte-range lock and unlock operations, and supplies the resource callbacks the cache manager needs for modified writes, cache flushes, and memory-mapped section creation.

## Main APIs And Entry Points

- `init_fast_io_dispatch(FAST_IO_DISPATCH** fiod)`: zeroes the global dispatch table, fills supported Fast I/O callbacks, and returns the table pointer to driver initialization code.
- `fast_query_basic_info(...)`: implements `FastIoQueryBasicInfo`, returning timestamps and attributes.
- `fast_query_standard_info(...)`: implements `FastIoQueryStandardInfo`, returning allocation size, EOF, link count, directory status, and delete-pending status.
- `fast_io_check_if_possible(...)`: checks byte-range locks and readonly/subvolume constraints for fast read/write eligibility.
- `fast_io_query_network_open_info(...)`: returns network-open information, including timestamps, allocation size, EOF, and attributes.
- `fast_io_acquire_for_mod_write(...)` / `fast_io_release_for_mod_write(...)`: acquire and release resources for cache manager modified-page writes.
- `fast_io_acquire_for_ccflush(...)` / `fast_io_release_for_ccflush(...)`: mark and unmark `FSRTL_CACHE_TOP_LEVEL_IRP` during cache flush callbacks.
- `fast_io_write(...)`: wraps `FsRtlCopyWrite` under the tree lock and updates inode size when the fast write succeeds.
- `fast_io_lock(...)`, `fast_io_unlock_single(...)`, `fast_io_unlock_all(...)`, `fast_io_unlock_all_by_key(...)`: route byte-range lock operations through FsRtl and refresh `Header.IsFastIoPossible`.
- `fast_io_acquire_for_create_section(...)` / `fast_io_release_for_create_section(...)`: acquire and release tree and FCB resources around section creation.

## Dispatch Table Contents

`init_fast_io_dispatch` installs:
- Custom callbacks for check-if-possible, write, basic info, standard info, locks/unlocks, network-open info, modified-write acquire/release, cache-flush acquire/release, and create-section acquire/release.
- FsRtl-provided helpers for cached fast reads and MDL reads/writes: `FsRtlCopyRead`, `FsRtlMdlReadDev`, `FsRtlMdlReadCompleteDev`, `FsRtlPrepareMdlWriteDev`, and `FsRtlMdlWriteCompleteDev`.

Unsupported Fast I/O entries remain zero because the table is cleared before assignment.

## Control Flow And Locking

Fast query paths enter the filesystem with `FsRtlEnterFileSystem`, validate `FileObject`, `FsContext`, and usually `FsContext2`, then acquire the relevant FCB resource shared if the caller permits waiting. Alternate data streams are mapped back to the parent file where Windows-visible timestamps, attributes, link counts, or delete-pending state must reflect the owning file rather than the ADS pseudo-FCB.

Fast write takes `Vcb->tree_lock` shared before calling `FsRtlCopyWrite`. On success it copies the cache manager file size back into `fcb->inode_item.st_size`, keeping in-memory inode metadata aligned with the cached write path.

Modified-page write acquisition deliberately takes `Vcb->tree_lock` shared before acquiring the FCB resource exclusive. The comment explains that this avoids interruption by the flush thread and uses the main FCB resource rather than `PagingIoResource` because Btrfs copy-on-write can require reallocations during writeback.

Section creation acquisition uses the same broad ordering: tree lock shared, then FCB resource exclusive. The release callback releases those resources in reverse order.

Byte-range lock and unlock callbacks only operate on regular files (`BTRFS_TYPE_FILE`). Locking acquires the FCB resource shared, calls the corresponding FsRtl fast lock/unlock helper, then recalculates `fcb->Header.IsFastIoPossible` through `fast_io_possible(fcb)`.

Cache flush callbacks use `IoSetTopLevelIrp((PIRP)FSRTL_CACHE_TOP_LEVEL_IRP)` and clear it only if the current top-level IRP is still that sentinel.

## Important State Read Or Mutated

- `FileObject->FsContext` as `fcb` and `FileObject->FsContext2` as `ccb`.
- `fcb->Header.Resource`, `fcb->Header.FileSize`, `fcb->Header.IsFastIoPossible`.
- `fcb->Vcb->tree_lock`, `fcb->Vcb->readonly`, `fcb->Vcb->dummy_fcb`, and `fcb->Vcb->volume_fcb`.
- `fcb->inode_item` timestamps, mode, size, link count, and object time.
- `fcb->atts`, `fcb->ads`, and `fcb->adsdata.Length`.
- `ccb->access` and `ccb->fileref`, including parent FCB and `delete_on_close`.
- `fcb->lock`, the FsRtl file-lock structure.
- Global `FastIoDispatch`.

## Dependencies

Windows kernel and FsRtl APIs used here include:
- `FAST_IO_DISPATCH` callback contracts and `_Function_class_` annotations.
- `FsRtlEnterFileSystem`, `FsRtlExitFileSystem`, `FsRtlCopyRead`, `FsRtlCopyWrite`, `FsRtlFastCheckLockForRead`, `FsRtlFastCheckLockForWrite`, `FsRtlFastLock`, `FsRtlFastUnlockSingle`, `FsRtlFastUnlockAll`, `FsRtlFastUnlockAllByKey`, and MDL helpers.
- `ExAcquireResourceSharedLite`, `ExAcquireResourceExclusiveLite`, and `ExReleaseResourceLite`.
- `IoSetTopLevelIrp`, `IoGetTopLevelIrp`, `KeQuerySystemTime`, and `PsGetCurrentProcess`.

Project-local dependencies include `btrfs_drv.h` types and helpers such as `fcb`, `ccb`, `file_ref`, `INODE_ITEM`, `unix_time_to_win`, `fcb_alloc_size`, `is_subvol_readonly`, `fast_io_possible`, `S_ISDIR`, and Btrfs file type constants.

## Notable Behaviors

- `fast_query_basic_info` enforces `FILE_READ_ATTRIBUTES` or `FILE_WRITE_ATTRIBUTES` access before answering.
- Dummy FCBs synthesize all timestamps from the current system time.
- Alternate data streams use their own stream length for allocation/EOF but derive attributes, link counts, and timestamps from the parent file where appropriate.
- `fast_io_query_network_open_info` zeroes the output structure first and does not acquire the FCB resource, so it is a very lightweight information path compared with the basic and standard query callbacks.
- Fast writes are blocked by inability to acquire the shared tree lock with the requested wait behavior.
- Fast write eligibility rejects writes on readonly volumes and readonly subvolumes before calling `FsRtlFastCheckLockForWrite`.
- Non-file lock requests are completed in the fast path with `STATUS_INVALID_PARAMETER` instead of falling back to IRP processing.

## Risks And Edge Cases

- `fast_query_standard_info` dereferences `ccb` for `ccb->fileref` near the end without first validating `ccb` in the non-ADS path. If a file object has an FCB but no CCB, this can fault.
- `fast_io_check_if_possible` assumes `FileObject` and `FileObject->FsContext` are valid and does not enter the filesystem or acquire resources. That matches a lightweight Fast I/O check style but relies on caller invariants and stable FCB lifetime.
- `fast_io_query_network_open_info` ignores `Wait` and does not lock the FCB resource while reading inode fields, ADS state, parent attributes, and sizes. Results can be stale or racing with metadata updates.
- In `fast_io_query_network_open_info`, `IoStatus` is marked unused with a FIXME asking whether `IoStatus->Information` should be set; successful fast query completion does not populate it here.
- `fast_io_write` does not validate file type, readonly state, or subvolume readonly state itself. It relies on Fast I/O eligibility and cache manager/FsRtl behavior to route only valid writes.
- The modified-write acquire path returns only the FCB resource in `ResourceToRelease`, but it also holds `tree_lock`; the paired release callback depends on recovering the FCB from `FileObject` to release both locks.
- Create-section acquisition takes the FCB resource exclusive, which is conservative and COW-friendly but can reduce concurrency for memory-mapped operations.
- Several callbacks return `false` on validation or lock acquisition failure, correctly forcing fallback to the normal IRP path, but any caller that expects `IoStatus` to be meaningful on those false returns will not get a populated status from most paths.

## Cross-File Relationships

- The dispatch pointer returned by `init_fast_io_dispatch` is used by the driver/device initialization path.
- The FCB, CCB, file-reference, and VCB fields used here are defined in `btrfs_drv.h` and maintained by create, cleanup, write, flush, and metadata paths elsewhere in WinBtrfs.
- `fast_io_write` interacts with later flush/extent code by updating `inode_item.st_size`; dirtying and extent allocation are handled by the broader write/cache-manager pipeline.
- The tree-lock ordering is coordinated with the flush thread and transaction code in `flushthread.c`.

## Summary

`fastio.c` provides WinBtrfs' Windows Fast I/O surface. It accelerates common metadata queries, cached reads/writes, byte-range locks, MDL operations, and cache manager resource callbacks while respecting the driver's tree lock and FCB resources. The file is intentionally thin, but its locking order and assumptions are important because these callbacks run in high-frequency kernel fast paths and interact with copy-on-write transaction flushing.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/fastio.c -->