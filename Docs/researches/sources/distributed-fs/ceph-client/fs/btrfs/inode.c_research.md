# Research: sources/distributed-fs/ceph-client/fs/btrfs/inode.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005616`: lines 1-8840, `Docs/researches/chunks/subset-b-005616_research.md`
- `subset-b-005617`: lines 8841-10803, `Docs/researches/chunks/subset-b-005617_research.md`

## Chunk Research

### subset-b-005616: lines 1-8840

# sources/distributed-fs/ceph-client/fs/btrfs/inode.c lines 1-8840

## Scope

This chunk covers the first 8,840 lines of Btrfs' inode implementation. It includes the main data-writeback paths, inline/compressed/COW/NOCOW delayed allocation, ordered extent completion, checksum validation, delayed iput/orphan cleanup, inode read/write/update lifecycle, unlink/rmdir/subvolume deletion, truncate and page invalidation, inode allocation/freeing, directory lookup/readdir, new inode/link creation, extent-map lookup, direct NOCOW eligibility checks, stat reporting, and rename/exchange handling.

The range ends at the close of `btrfs_rename()`. Operation tables and later address-space/file operation wiring are outside this chunk and should be reconciled by later chunks.

## Purpose

`inode.c` is the core bridge between VFS inode operations and Btrfs' copy-on-write metadata model. In this range it:

- Converts dirty page-cache ranges into durable file extents through inline extents, compressed COW extents, regular COW extents, or safe NOCOW writes.
- Maintains the in-memory `struct btrfs_inode` accounting needed for delayed allocation, qgroups, outstanding extent reservations, inode byte counts, delayed items, and fsync correctness.
- Completes ordered extents by installing file extent items, inserting checksums, updating inode items, unpinning extent maps, and releasing reservations.
- Implements metadata-changing namespace operations such as create, link, unlink, rmdir, subvolume deletion, and rename with explicit transaction reservation sizing.
- Loads and caches inodes, extent maps, directory entries, ACL/property hints, and per-root inode xarray membership.
- Handles destructive lifecycle paths, especially truncation, eviction, orphan cleanup, and delayed iput processing.

The file is therefore a high-risk persistence component: it coordinates page cache state, extent IO state, B-tree metadata, transaction handles, delayed refs/items, log-tree/fsync state, and qgroup/space accounting.

## Important APIs, Types, and Functions

Important local helper types:

- `struct btrfs_iget_args` carries inode number and root identity for `iget5_locked_rcu()` lookup and initialization.
- `struct btrfs_rename_ctx` returns the removed directory index during rename so log updates can reference the old name correctly.
- `struct data_reloc_warn` carries context for relocation checksum diagnostics and backref path resolution.
- `struct async_extent`, `struct async_chunk`, and `struct async_cow` describe asynchronous compressed writeback work. Each async chunk compresses a range, records compressed or fallback-uncompressed extents, then submits in original order.
- `struct can_nocow_file_extent_args` is the shared input/output contract for deciding whether an existing file extent can be overwritten without COW.
- `struct btrfs_writepage_fixup` defers repair of dirty folios that were dirtied without going through Btrfs' normal delalloc reservation path.
- `struct dir_entry` is the temporary readdir buffer record copied out after B-tree locks are released.

Major writeback and extent APIs:

- `btrfs_run_delalloc_range()` is the top-level delayed allocation callback. It first tries inline extents for a small range at offset 0, then chooses NOCOW, compressed COW, zoned COW, or regular COW.
- `run_delalloc_inline()`, `__cow_file_range_inline()`, `can_cow_file_range_inline()`, and `insert_inline_extent()` create inline file extent items and update `disk_i_size`/inode bytes for small files.
- `compress_file_range()`, `run_delalloc_compressed()`, `submit_compressed_extents()`, and `submit_one_async_extent()` implement the two-stage compressed writeback pipeline.
- `cow_file_range()` and `cow_one_range()` reserve new disk extents, create pinned IO extent maps, allocate ordered extents, and unlock/mark page-cache ranges for writeback.
- `run_delalloc_nocow()`, `can_nocow_file_extent()`, `nocow_one_range()`, `fallback_to_cow()`, and exported `can_nocow_extent()` decide whether a write can target existing extents, handling snapshots, cross references, checksums, prealloc extents, read-only block groups, and data-relocation special cases.
- `btrfs_create_io_em()` creates pinned temporary extent maps for ordered IO.

Major ordered IO and checksum APIs:

- `btrfs_finish_one_ordered()` is the central ordered-extent completion path. It joins a transaction, inserts RAID stripe-tree extent data, handles NOCOW/PREALLOC/REGULAR/COMPRESSED/DIRECT/ENCODED/TRUNCATED ordered extents, inserts file extent items, adds pending data checksums, updates inode metadata, releases reservations, and removes the ordered extent.
- `btrfs_finish_ordered_io()` wraps zoned ordered completion and calls `btrfs_finish_one_ordered()`.
- `add_pending_csums()` inserts checksum sums accumulated on the ordered extent.
- `btrfs_calculate_block_csum_folio()`, `btrfs_calculate_block_csum_pages()`, `btrfs_check_block_csum()`, and `btrfs_data_csum_ok()` calculate and validate data checksums, zero corrupted sectors, and emit relocation-aware diagnostics.
- `print_data_reloc_error()`, `data_reloc_print_warning_inode()`, and `btrfs_print_data_csum_error()` turn checksum mismatches into useful root/inode/path warnings.

Major inode lifecycle APIs:

- `btrfs_read_locked_inode()`, `btrfs_iget_path()`, and `btrfs_iget()` load inode items from the B-tree, initialize VFS operation pointers, inode flags, ACL/property cache hints, extent-tree state, and root inode xarray membership.
- `fill_inode_item()`, `btrfs_update_inode_item()`, `btrfs_update_inode()`, and `btrfs_update_inode_fallback()` persist in-memory inode state into delayed inode items or directly into the subvolume tree.
- `btrfs_alloc_inode()`, `btrfs_destroy_inode()`, `btrfs_free_inode()`, `btrfs_drop_inode()`, `btrfs_init_cachep()`, and `btrfs_destroy_cachep()` manage the Btrfs inode slab and per-inode state initialization/teardown.
- `btrfs_evict_inode()` truncates pages, drops inode items for unlinked inodes, removes orphan items when possible, and leaves cleanup to mount-time orphan handling on failure.
- `btrfs_add_delayed_iput()`, `btrfs_run_delayed_iputs()`, and `btrfs_wait_on_delayed_iputs()` defer final iputs out of contexts where reclaim/transaction recursion would be unsafe.

Major namespace and directory APIs:

- `btrfs_inode_by_name()`, `fixup_tree_root_location()`, `btrfs_lookup_dentry()`, and `btrfs_lookup()` perform encrypted-name lookup and subvolume-root crossing.
- `btrfs_real_readdir()`, `btrfs_opendir()`, and `btrfs_dir_llseek()` merge B-tree directory index items with delayed directory items using a temporary buffer to avoid user faults under tree locks.
- `btrfs_new_inode_prepare()`, `btrfs_create_new_inode()`, `btrfs_create_common()`, `btrfs_mknod()`, `btrfs_create()`, `btrfs_mkdir()`, and `btrfs_new_subvol_inode()` create inode items, inode refs, initial properties/ACLs/security xattrs, orphan entries, and directory links.
- `btrfs_add_link()` inserts root refs or inode refs plus directory items and updates parent directory metadata.
- `__btrfs_unlink_inode()`, `btrfs_unlink_inode()`, `btrfs_unlink()`, `btrfs_unlink_subvol()`, `btrfs_rmdir()`, and `btrfs_delete_subvolume()` remove names, refs, delayed dir indexes, orphan/subvolume records, uuid-tree records, and root state.
- `btrfs_rename_exchange()` and `btrfs_rename()` implement atomic rename variants, including subvolume link constraints, log pinning, fscrypt names, whiteout creation, replacement unlink/orphan handling, and new link insertion.

Major truncate/page-cache APIs:

- `btrfs_truncate_block()` zeroes partial sectors and marks the affected block delalloc, with NOCOW/noreserve handling when data reservation is unavailable.
- `btrfs_cont_expand()` expands files by zeroing the old tail block and inserting explicit hole extents when the filesystem uses explicit holes.
- `btrfs_setsize()`, `btrfs_setattr()`, and `btrfs_truncate()` implement VFS size changes, ordered-range waits, extent item truncation, disk_i_size updates, full-sync marking, and block-reservation cycling.
- `btrfs_invalidate_folio()`, `btrfs_release_folio()`, `btrfs_launder_folio()`, and `btrfs_migrate_folio()` coordinate folio invalidation/release with ordered extents, subpage state, qgroup reservations, and extent-map cleanup.

## Control Flow

Writeback begins when extent IO calls `btrfs_run_delalloc_range()` for a locked dirty folio range. For a tiny first-block file, `run_delalloc_inline()` may compress the sector, validate inline-size constraints, join a transaction, drop overlapping extents, insert an inline file extent item, update inode bytes, and clear delalloc state without normal IO. If inline insertion is not possible, control continues.

If inode flags indicate `NODATACOW` or `PREALLOC`, `run_delalloc_nocow()` walks file extent items across the write range. For each extent it calls `can_nocow_file_extent()`, which rejects inline extents, regular extents without NODATACOW, extents older than the last snapshot, explicit holes, compressed/encrypted/encoded extents, cross-referenced/shared extents, and ranges with checksums. Accepted ranges increment NOCOW writers on the block group and create ordered extents with `nocow_one_range()`. Gaps or rejected extents accumulate as COW ranges and are processed by `fallback_to_cow()`, which repairs `EXTENT_NORESERVE` accounting before calling `cow_file_range()`.

For compressed writeback, `run_delalloc_compressed()` allocates an `async_cow` context split into compression-size chunks and queues `compress_file_range()` on `delalloc_workers`. Compression clears dirty bits for IO, chooses compression type/level from defrag state, inode property, or mount options, and rejects output that does not save at least one sector. Each chunk records either a compressed `compressed_bio` or a NULL `cb` fallback range. `submit_compressed_extents()` then processes recorded extents in order. Compressed extents reserve disk space, create pinned IO extent maps and ordered extents, clear delalloc state, and submit bios; fallback extents re-enter `run_delalloc_cow()`.

Regular COW flows through `cow_file_range()`. It computes allocation size and hints, reserves extents with `btrfs_reserve_extent()`, creates extent maps and ordered extents, handles data relocation checksum cloning, then clears delalloc and sets page ordered/writeback state. Zoned filesystems can return `-EAGAIN` when no active zones are available; the first allocation waits for a zone finish, while later partial progress can be returned through `done_offset`.

Bio completion decrements ordered pending bytes elsewhere; once an ordered extent is complete, `btrfs_finish_ordered_io()` calls `btrfs_finish_one_ordered()`. The function locks the affected extent range for COW-like writes before joining a transaction, inserts RAID stripe-tree data, handles NOCOW by only updating inode metadata, converts PREALLOC extents with `btrfs_mark_extent_written()`, or inserts a regular file extent with `insert_ordered_extent_file_extent()`. It then unpins the IO extent map, inserts checksums, clears `EXTENT_DELALLOC_NEW` with inode-byte accounting, writes safe `disk_i_size`, updates the inode item, frees or preserves reserved extents depending on how far completion got, drops stale extent maps for unwritten portions, and removes the ordered extent.

Lookup starts at `btrfs_lookup()`, which delegates to `btrfs_lookup_dentry()`. Normal inode items are loaded with `btrfs_iget()`. Root items are validated through `fixup_tree_root_location()` and either cross into the referenced subvolume root or synthesize a dummy empty-subvolume directory inode when the real root is unavailable. Successful subvolume lookup can trigger orphan cleanup under `cleanup_work_sem`.

Create paths allocate a VFS inode first, initialize mode-specific operations, call `btrfs_new_inode_prepare()` to resolve encrypted names and ACLs and count transaction items, then `btrfs_create_new_inode()` to reserve an objectid, insert inode and inode-ref items in one batch, inherit flags/properties, initialize ACL/security xattrs, add the inode to the root xarray, add orphan or directory link metadata, and instantiate the dentry.

Unlink and rmdir remove the directory item, inode/root refs, delayed dir index item, and log entries, update parent size/timestamps/iversion, then update inode link counts and orphan items when the target has no remaining links. Subvolume deletion additionally marks the root dead, prevents deletion during send or active swapfile use, checks default-subvolume and nested-ref constraints, removes uuid-tree records, inserts a tree-root orphan item for later root drop, invalidates dentries, and prunes aliases.

Rename first validates cross-root and subvolume constraints, resolves encrypted old/new names, sizes transaction reservations, optionally prepares a whiteout inode, inserts the new inode/root reference before removing the old name, pins log transactions for non-subvolume renames, unlinks any replaced target, adds the new dir item, updates `dir_index` hints for singly-linked inodes, logs the new name, and finally creates the whiteout if requested. `btrfs_rename_exchange()` performs the same pattern twice with two new directory indexes and two add-link calls.

## State and Persistence Behavior

Delayed allocation state is represented by bits in `inode->io_tree` and counters on the inode/root/fs:

- `EXTENT_DELALLOC` tracks dirty ranges needing extent allocation and participates in root/fs delalloc inode lists.
- `EXTENT_DELALLOC_NEW` marks ranges that will add to inode byte counts when cleared at ordered completion.
- `EXTENT_DEFRAG`, `EXTENT_NORESERVE`, `EXTENT_DO_ACCOUNTING`, and qgroup reservation bits drive metadata/data/qgroup release behavior.
- `inode->delalloc_bytes`, `new_delalloc_bytes`, `defrag_bytes`, and `outstanding_extents` must match io-tree state; `btrfs_set_delalloc_extent()`, `btrfs_clear_delalloc_extent()`, `btrfs_split_delalloc_extent()`, and `btrfs_merge_delalloc_extent()` keep those counters aligned.

Extent persistence is transaction based. COW writeback first creates in-memory ordered extents and pinned extent maps; the durable file extent item is installed only during ordered extent completion. Inline extents are directly inserted in the file tree during delalloc processing and then force a full inode sync. NOCOW writes do not create new file extent items, but still create ordered extents to enforce data=ordered semantics and update inode metadata safely.

`disk_i_size` is updated conservatively. Inline insertion may update it immediately while folios remain locked. Ordered completion calls `btrfs_inode_safe_disk_i_size_write()` before inode update. Truncate uses `control.last_size` from `btrfs_truncate_inode_items()` and may later zero the partial final block outside the transaction before safely writing disk size.

Inode metadata is usually persisted through delayed inode updates for normal inodes. Free-space inodes, data relocation roots, and log recovery paths bypass delayed inode updates and write inode items directly to avoid deadlocks or replay inconsistency. `btrfs_update_inode_fallback()` falls back to direct update on delayed-update `-ENOSPC`.

Orphan state is persistent B-tree metadata. Unlinked inodes get orphan items before their final iput can delete extents. Mount/open cleanup calls `btrfs_orphan_cleanup()` to find orphan items, iput unlinked inodes, remove stale orphan records, and preserve orphan root items for subvolume deletion. Eviction attempts to remove orphan items after truncation but tolerates failure because cleanup can retry on next mount.

Directory indexes are monotonically increasing through `index_cnt`. The value is lazily initialized from delayed dir items or highest `BTRFS_DIR_INDEX_KEY`. Readdir freezes `private->last_index` at open/seek time and deliberately advances `ctx->pos` to a large value after the last entry to avoid seeing entries created during a scan.

Fsync/log correctness depends on pessimistic transaction markers. Reloaded inodes set `last_unlink_trans` and `last_reflink_trans` to `last_trans`; truncation with extents found sets full sync; newly-created/reused inode numbers set full sync; rename pins log transactions around remove/add windows; subvolume rename/deletion forces full log commits.

## Dependencies and Integration Points

This chunk depends heavily on Btrfs internal subsystems:

- Extent map and extent IO: `extent_map_tree`, `btrfs_lookup_extent_mapping()`, `btrfs_replace_extent_map_range()`, `extent_clear_unlock_delalloc()`, folio private/subpage state, and ordered folio bits.
- Ordered extents: allocation, pending byte accounting, completion, truncation, `BTRFS_ORDERED_*` flags, and lockdep maps.
- Transactions and block reservations: `btrfs_start_transaction()`, `btrfs_join_transaction()`, delayed refs, inode block reserves, global reserves, truncate/evict temporary reserves, and abort paths.
- File-tree metadata helpers: file extent item conversion, extent dropping, inline/hole insertion, prealloc conversion, inode item lookup/update, inode/root refs, dir items, delayed dir indexes, and root refs.
- Compression: compression heuristics, inode properties, defrag overrides, mount options, `compressed_bio`, compressed bio cleanup/submission, and sector-aligned compressed size padding.
- Checksums and repair diagnostics: csum roots, ordered sums, data relocation roots, backref walking, path resolution, device corruption counters, and zeroing corrupted memory.
- Space and qgroups: `btrfs_check_data_free_space()`, delalloc metadata/data reservation, `bytes_may_use`, block-group delalloc bytes, qgroup reserved data/meta release, and quota cleanup on error.
- Snapshotting and relocation: `snapshot_force_cow`, root last snapshot generation, subvolume semaphores, data relocation checksum cloning, zoned relocation behavior, and read-only block group transitions.
- VFS/MM integration: inode locks, `i_mmap_lock`, page cache truncation, folio migration/release/invalidate/launder, `setattr`, ACLs, fscrypt, statx, dentry pruning, and dcache aliasing.
- Log tree/fsync: `btrfs_record_unlink_dir()`, `btrfs_log_new_name()`, log transaction pinning, log full commit forcing, and delayed log deletion helpers.

External VFS entry points represented here include inode locking helpers, lookup/create/link/unlink/mkdir/rmdir/rename/setattr/getattr/update_time behaviors, directory open/seek/readdir behavior, inode allocation/destruction, and address-space callbacks for folio lifecycle.

## Risks

- Delalloc accounting is fragile. Missing or extra `EXTENT_CLEAR_DATA_RESV`, `EXTENT_CLEAR_META_RESV`, `EXTENT_DELALLOC_NEW`, or `EXTENT_ADD_INODE_BYTES` handling can leak space, double-free reservations, corrupt qgroup accounting, or make `stat.blocks` inaccurate.
- Error cleanup paths in `cow_file_range()`, `run_delalloc_nocow()`, `nocow_one_range()`, `submit_one_async_extent()`, and `btrfs_finish_one_ordered()` split ranges into already-ordered, partially-handled, and untouched segments. Off-by-one mistakes can leave locked extents, dirty folios without ordered extents, or ordered extents without metadata cleanup.
- NOCOW eligibility must stay conservative. Allowing NOCOW on shared, checksummed, compressed, encoded, encrypted, read-only block-group, snapshot-visible, or cross-referenced extents can corrupt data or invalidate checksums.
- Inline extent handling updates B-tree metadata during writeback and unlocks/finishes the folio differently from normal ordered IO. Regressions can confuse generic writepage return handling or leave stale page-cache data.
- `disk_i_size` and inode byte accounting are updated in several places. A mismatch between in-memory size, persisted inode size, and file extent items can expose stale data after crash or break fsync replay.
- Rename and exchange depend on log pinning and full-log-commit decisions. Any new exit path must release pinned logs/subvol semaphores and preserve the invariant that replay never sees a directory after removal but before add-link.
- Subvolume deletion is interwoven with root refs, orphan root items, uuid-tree cleanup, `S_DEAD`, dentry invalidation, and dead-root queuing. Partial failures intentionally leave work for later cleanup; tests must distinguish acceptable deferred cleanup from lost root refs.
- Eviction runs in memory-reclaim-sensitive contexts and uses special reserve refill modes to avoid delayed-iput recursion. Calling flush paths that process delayed iputs from eviction can deadlock.
- `btrfs_invalidate_folio()` must coordinate with endio and ordered extent completion. Clearing ordered or extent-state bits too early can double-complete ordered extents or allow use-after-free of subpage state.
- Directory readdir deliberately buffers entries outside B-tree locks. Any change to `dir_entry` packing, delayed-item merge ordering, or `ctx->pos` behavior can regress telldir/seekdir semantics or expose entries created during a scan.
- Inode load initializes pessimistic fsync state after eviction. Removing those assignments can create replay inconsistencies after unlink/reflink followed by cache eviction and fsync.
- Several paths intentionally treat data-relocation and free-space inodes specially. Applying normal delayed inode, ordered lockdep, checksum, or extent-cache assumptions to those inodes can deadlock or trip assertions.

## Test and Validation Signals

Useful validation for this chunk includes:

- Build coverage for Btrfs with compression, fscrypt, ACLs, qgroups, zoned mode, migration, and sanity-test options enabled where possible.
- Generic xfstests coverage for buffered writeback, delalloc ENOSPC, compression, inline extents, NODATACOW, prealloc, reflink/snapshot interactions, truncate, hole punching, fallocate, fsync replay, and mmap writeback.
- Targeted writeback tests that force transitions among inline, compressed, uncompressed COW, NOCOW, and fallback-to-COW paths, including block groups becoming read-only during scrub/relocation.
- ENOSPC/EDQUOT fault injection around `btrfs_reserve_extent()`, delayed inode update, extent map allocation, ordered extent allocation, csum insertion, `btrfs_drop_extents()`, and transaction start/join paths; check for no locked extents, no leaked reservations, and correct mapping errors.
- Qgroup tests that dirty, truncate, invalidate, and evict ranges before and after IO submission, verifying reserved data/meta accounting and no leak warnings from `btrfs_qgroup_check_reserved_leak()`.
- Crash-recovery/fsync tests for unlink, rename, rename exchange, truncate, O_TMPFILE link, hard links, reflinks, and eviction before fsync; verify log replay preserves link counts, parent entries, and file extents.
- Subvolume namespace tests for lookup crossing, dummy empty-subvolume dirs, deleting default subvolume refusal, deleting nested subvolume refusal, send/swapfile deletion refusal, uuid-tree cleanup, dentry pruning, and orphan root cleanup on remount.
- Directory tests with fscrypt names, hash collisions, delayed dir items, large directories, `telldir`/`seekdir`, and concurrent create/unlink during readdir.
- Folio lifecycle tests for invalidate/release/migrate/launder under subpage sectorsize, writeback races, truncation, and eviction while readahead/endio is active.
- Checksum tests that inject data checksum mismatches on normal and data-relocation roots, verifying warnings include root/inode/path when resolvable, corrupted memory is zeroed, and device corruption stats increment.
- Zoned filesystem tests for COW retry on `-EAGAIN`, ordered zoned completion, data relocation fixed-size allocation, and waiting ordered ranges before truncate.
- Static assertions or runtime debug checks that no inode is destroyed with nonzero delalloc/new_delalloc/csum/defrag bytes, nonempty ordered tree, outstanding extents, block reservations, or remaining page cache.

### subset-b-005617: lines 8841-10803

# sources/distributed-fs/ceph-client/fs/btrfs/inode.c lines 8841-10803

## Scope

This chunk covers the tail of Btrfs inode operation implementation. It starts at the VFS `rename2` dispatcher and runs through delalloc flushing helpers, symlink and tmpfile creation, file preallocation, permission checks, encoded read/write support, swapfile activation/deactivation, inode byte accounting helpers, inode lookup by minimum object id, and the final VFS operation tables for directories, files, special inodes, symlinks, address spaces, and dentries.

The range is functionally dense and provides several exported integration points used outside this file: `btrfs_start_delalloc_snapshot()`, `btrfs_start_delalloc_roots()`, `btrfs_prealloc_file_range()`, `btrfs_prealloc_file_range_trans()`, encoded I/O helpers declared in `btrfs_inode.h`, `btrfs_update_inode_bytes()`, `btrfs_assert_inode_range_clean()`, and `btrfs_find_first_inode()`.

## Purpose

This section connects Btrfs inode state to Linux VFS operations and low-level extent machinery. It turns high-level file-system requests into Btrfs transactions, extent items, ordered extents, qgroup reservations, extent-map updates, and delayed writeback. It also exposes specialized entry points for send/receive and ioctl encoded I/O, and enforces the restrictions required to let a Btrfs file be used safely as swap.

The chunk is also where final operation tables bind previously defined functions from the full file to VFS callbacks. The merge lane should treat this as the end-of-file integration point: many callbacks named here are implemented in earlier chunks, while helpers implemented here are called from `file.c`, `ioctl.c`, `send.c`, and other Btrfs modules.

## Important APIs, Types, and Functions

`btrfs_rename2()` is the VFS rename callback wrapper. It accepts only `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, and `RENAME_WHITEOUT`; dispatches exchange renames to `btrfs_rename_exchange()` and all other accepted cases to `btrfs_rename()`; then calls `btrfs_btree_balance_dirty()` on the destination root's filesystem.

`struct btrfs_delalloc_work`, `btrfs_run_delalloc_work()`, `btrfs_alloc_delalloc_work()`, `start_delalloc_inodes()`, `btrfs_start_delalloc_snapshot()`, and `btrfs_start_delalloc_roots()` implement root-wide or filesystem-wide flushing of inodes that have delayed allocation. The code walks `root->delalloc_inodes` and `fs_info->delalloc_roots`, grabs inode/root references, optionally queues async work on `fs_info->flush_workers`, and honors `BTRFS_INODE_NO_DELALLOC_FLUSH` when called from reclaim context.

`btrfs_symlink()` creates symlinks as uncompressed inline extent data. It validates that the target length fits Btrfs inline limits and the filesystem sector size, initializes the VFS inode, prepares and creates the Btrfs inode item, inserts a `BTRFS_EXTENT_DATA_KEY` item at offset zero, writes the symlink bytes into the inline extent, and instantiates the dentry.

`insert_prealloc_file_extent()`, `__btrfs_prealloc_file_range()`, `btrfs_prealloc_file_range()`, and `btrfs_prealloc_file_range_trans()` implement fallocate-style preallocation. They reserve extents, insert `BTRFS_FILE_EXTENT_PREALLOC` file extent items, release qgroup data reservations into the transaction, update extent maps with `EXTENT_FLAG_PREALLOC`, advance `i_size` when `FALLOC_FL_KEEP_SIZE` is not set, maintain `disk_i_size` safety with `btrfs_inode_set_file_extent_range()`, update ctime and inode version, and commit per-extent transactions when the caller did not provide one.

`btrfs_permission()` denies writes to regular files, directories, and symlinks when the root is readonly or the inode has `BTRFS_INODE_READONLY`, then defers ordinary checks to `generic_permission()`.

`btrfs_tmpfile()` creates unnamed temporary regular files. It uses `btrfs_new_inode_args` with `.orphan = true`, creates the inode in a transaction, temporarily sets nlink to one to satisfy `d_tmpfile()` expectations, attaches the file dentry, unlocks the new inode, marks it dirty, balances dirty B-tree state, and returns through `finish_open_simple()`.

`btrfs_encoded_io_compression_from_extent()` maps on-disk Btrfs compression identifiers to the encoded I/O ABI. It supports none, zlib, zstd, and LZO variants keyed by sector size; unsupported or corrupt compression values fail with `-EINVAL` or `-EUCLEAN`.

`btrfs_encoded_read_inline()`, `struct btrfs_encoded_read_private`, `btrfs_encoded_read_endio()`, `btrfs_encoded_read_regular_fill_pages()`, `btrfs_encoded_read_regular()`, and `btrfs_encoded_read()` implement the read side of the encoded I/O ioctl and io_uring paths. They return either inline extent data, zeroes for holes/prealloc extents, raw compressed extent bytes with compression metadata, or raw uncompressed bytes from disk-backed extents. The regular read helper can submit one or more bios and uses a refcounted private completion object for synchronous and io_uring completion.

`btrfs_do_encoded_write()` writes pre-compressed data supplied through the encoded write path. It validates the encoded ABI, compression type, encryption absence, inode checksum compatibility, sizes, sector alignment, and encoded offsets; copies compressed input into compressed-bio folios; waits for and invalidates conflicting page cache and ordered extents; reserves data, qgroup, and metadata; optionally writes an inline compressed extent; otherwise reserves a physical extent, creates an extent map and encoded compressed ordered extent, updates `i_size`, unlocks the range, and submits the compressed write.

Under `CONFIG_SWAP`, `btrfs_add_swapfile_pin()`, `btrfs_free_swapfile_pins()`, `struct btrfs_swap_info`, `btrfs_add_swap_extent()`, `btrfs_swap_activate()`, and `btrfs_swap_deactivate()` implement Btrfs swapfile support. They validate that the file is nocow, nodatasum, uncompressed, hole-free, non-inline, unshared, single-device, and backed by a single data profile; pin the backing device and block groups in `fs_info->swapfile_pins`; prevent snapshots and exclusive operations that could move extents; and register contiguous physical ranges with the kernel swap subsystem. Without `CONFIG_SWAP`, activation returns `-EOPNOTSUPP`.

`btrfs_update_inode_bytes()` atomically updates VFS inode byte counters under `btrfs_inode::lock`, for clone/dedupe/zero-range style extent replacement paths.

`btrfs_assert_inode_range_clean()` is an assertion helper that checks, when Btrfs assertions are enabled, that no ordered extent overlaps a range that callers believe is fully flushed, waited, and locked.

`btrfs_find_first_inode()` walks `root->inodes` with the XArray API and returns an `igrab()`'d Btrfs inode whose object id is at least a caller-supplied minimum.

The operation tables at the end bind Btrfs implementations into VFS dispatch: `btrfs_dir_inode_operations`, `btrfs_dir_file_operations`, `btrfs_aops`, `btrfs_file_inode_operations`, `btrfs_special_inode_operations`, `btrfs_symlink_inode_operations`, and `btrfs_dentry_operations`.

## Control Flow

Delalloc flushing uses two nested list-walk patterns. `btrfs_start_delalloc_roots()` splices the global `fs_info->delalloc_roots` list while holding `delalloc_root_mutex` and `delalloc_root_lock`, grabs each root, moves it back to the tail for fairness, drops the spinlock while flushing that root, and restores unfinished spliced roots on exit. `start_delalloc_inodes()` does the same at per-root inode granularity. Full snapshot flushing passes `nr_to_write == NULL`, queues a `btrfs_delalloc_work` for each grabbed inode, then waits for all queued completions before returning. Bounded flushing calls `filemap_flush_nr()` directly and stops when the write budget is exhausted or an error appears.

Symlink and tmpfile creation follow the standard Btrfs new-inode transaction pattern: allocate and initialize a VFS inode, run `btrfs_new_inode_prepare()` to reserve ids and delayed metadata, start a transaction sized by the preparation step, create the inode item, add extra records when needed, instantiate or attach the dentry, end the transaction, destroy the new-inode argument state, and drop the inode on error.

Preallocation loops until the requested range is covered. Each iteration caps the allocation request at 256 MiB, honors the minimum extent size, adapts to the previous allocation size under fragmentation, reserves a data extent, inserts a prealloc extent item, decrements block-group reservations only after the file extent item exists, updates the in-memory extent map if possible, updates inode metadata, and either ends its own transaction or reuses the caller transaction. Error paths free only the still-uncovered reserved data range and release qgroup reservations that were moved out of data reservation but never attached to a transaction.

Encoded read first locks the inode in shared mode, normalizes the starting offset to sector alignment, locks enough extent state to cover the maximum compressed extent size, and waits or returns `-EAGAIN` for ordered extents depending on `IOCB_NOWAIT`. It then resolves the extent map. Inline extents are read from the leaf and copied after dropping path and locks. Holes and prealloc extents return zeroes. Disk-backed extents leave locks held and return `-EIOCBQUEUED` so the ioctl/uring layer can call `btrfs_encoded_read_regular()` or complete the async flow with the resolved disk address and size.

Encoded write validates before modifying filesystem state, then serializes against existing ordered extents and page cache by waiting, invalidating, locking the range, and rechecking. After resource reservation it tries an inline compressed extent when the encoded range exactly matches the unencoded range and inline COW is allowed. Otherwise it reserves disk space, creates a compressed extent map, allocates an ordered extent marked `BTRFS_ORDERED_ENCODED` and `BTRFS_ORDERED_COMPRESSED`, updates `i_size` if the logical write extends EOF, releases delalloc accounting, and submits the compressed bio. The cleanup ladder unwinds in reverse order: reserved extent, delalloc extents and metadata, qgroup data, data-space reservation, extent lock, and compressed bio.

Swap activation serializes aggressively. It takes `i_mmap_lock` after the VFS inode lock, waits all ordered extents, validates immutable inode flags, starts an exclusive operation, takes the root snapshot write lock, increments `root->nr_swapfiles` only after checking that the root is not being deleted, locks the whole sector-aligned file range, then walks file extent items from offset zero to EOF. Each extent is checked for hole/inline/compression/share violations, mapped to a physical stripe, constrained to single profile and one device, pinned through the global swapfile pin tree, coalesced into contiguous physical swap extents, and periodically rescheduled. On any failure after `nr_swapfiles` is incremented, `btrfs_swap_deactivate()` frees pins and decrements the counter before locks are dropped.

## State and Persistence Behavior

The functions in this chunk persist Btrfs metadata through transactions and B-tree item updates. Symlinks persist their target as an inline `BTRFS_FILE_EXTENT_INLINE` extent. Preallocation persists `BTRFS_FILE_EXTENT_PREALLOC` items with disk bytenr, disk length, logical length, ram bytes, generation, and no compression; it also updates inode flags, ctime, i_version, `i_size`, and disk size when appropriate. Encoded writes persist compressed file extent metadata through ordered extent completion and update in-memory extent maps before I/O submission.

Delayed allocation state is maintained in per-root and per-fs lists guarded by mutexes and spinlocks. Work items hold temporary inode references until flushing completes, and direct flushing uses delayed iput to avoid dropping references in unsafe contexts. Snapshot flushes set `BTRFS_INODE_SNAPSHOT_FLUSH` on inodes being flushed.

Qgroup accounting is explicit in preallocation and encoded write. Prealloc insertion calls `btrfs_qgroup_release_data()` and transfers released data reservation into extent replacement or reserved extent insertion; early failures free the released refroot reservation. Encoded write reserves qgroup data for the logical range and frees it on failure before the write becomes ordered.

Swapfile state is partly persistent and partly runtime-only. The file extents already exist on disk, but activation builds runtime pins in `fs_info->swapfile_pins`, increments per-root `nr_swapfiles`, increments per-block-group swap extent counts, and assigns `sis->bdev`, `sis->max`, `sis->pages`, and span values for the swap subsystem. These pins are intentionally transient and are removed by swap deactivation.

Inode byte accounting is protected by `inode->lock` so concurrent `stat(2)` sees consistent `i_blocks`-style values while extent replacement adds and removes bytes. The final operation tables are static dispatch state compiled into the filesystem module.

## Dependencies and Integration Points

This chunk depends heavily on Btrfs core subsystems: transaction handles, path and extent-buffer manipulation, extent maps, ordered extents, delayed allocation accounting, qgroups, block-group reservations, compressed bio submission, chunk mapping, snapshot locks, exclusive-operation state, root/inode XArrays, and B-tree balancing. It also depends on VFS/MM primitives such as inodes, dentries, kiocbs, iov iters, folios/pages, bios, address-space operations, swap activation callbacks, inode locks, mmap locks, and generic permission helpers.

External users inside Btrfs include:

- `file.c`, which routes encoded write requests to `btrfs_do_encoded_write()`.
- `ioctl.c`, which drives encoded read/write ioctls and io_uring encoded reads using `btrfs_encoded_read()` and `btrfs_encoded_read_regular()`.
- `send.c`, which uses encoded read helpers to copy compressed extents without decompressing them.
- fallocate and extent-replacement paths that call the preallocation helpers and `btrfs_update_inode_bytes()`.
- snapshot, reclaim, transaction commit, and sync paths that call the delalloc flushing entry points.
- VFS dispatch through the inode/file/address-space/dentry operation tables.

The final callback tables connect this chunk to many earlier functions in the same file: lookup/create/unlink/link/mkdir/rmdir/mknod/getattr/setattr/listxattr/ACL/update-time/fileattr/readdir/open/release/fsync/read/writepage/readahead/invalidate/launder/release/migrate callbacks are all assembled here even when their implementations live outside this range.

## Risks

- Delalloc list walking is lock-sensitive. Incorrect splice restoration, root/inode reference handling, or spinlock dropping can lose inodes from flush lists, deadlock flush paths, or use freed roots/inodes.
- Full snapshot flushing queues async work and waits for all completions. Missing waits or failed work allocation paths can leave snapshot-sensitive delalloc unflushed.
- Preallocation has subtle qgroup and block-group reservation sequencing. Decrementing block-group reservations before inserting the file extent can race relocation; failing to free released qgroup reservation on early error leaks quota reservation.
- The `disk_i_size` update in preallocation relies on marking the file extent range before increasing size. Regressions here can persist a smaller disk size than VFS `i_size` after remounts when old keep-size prealloc extents left gaps in the extent-state tree.
- Encoded read/write bypass normal buffered data transformation. Misreported compression type, unencoded offset, disk I/O size, or extent length can expose corrupt data, overrun user buffers, or break send/receive and encoded ioctl ABI compatibility.
- Encoded write must reject NODATASUM/NOCOW-incompatible compressed writes and enforce sector alignment. Relaxing these checks can create compressed extents without expected checksums or extents that later read paths cannot decode safely.
- The encoded read endio path relies on refcount memory ordering around `priv->status`. Changes to completion/refcount handling can produce lost I/O errors or premature io_uring completion.
- Swap activation is correctness-critical. Allowing holes, shared/COW extents, compression, checksums, multi-device profiles, device changes, snapshots, or moving block groups while active can lead to swap I/O hitting stale or relocated physical blocks.
- Swap activation locks the entire aligned file range. Empty or sub-sector-sized files need careful treatment by callers because this code computes `isize - 1` after sector alignment.
- Operation table wiring is a broad integration point. A wrong callback assignment can silently change VFS behavior for all Btrfs files or directories.

## Test and Validation Signals

Useful validation should include xfstests and targeted Btrfs scenarios:

- Rename coverage for `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, `RENAME_WHITEOUT`, unsupported flags, and post-rename fsync/sync behavior.
- Snapshot and sync tests that create dirty delalloc across many roots/inodes, then verify `btrfs_start_delalloc_snapshot()` and bounded `btrfs_start_delalloc_roots()` write the expected amount without deadlock under memory reclaim.
- Symlink tests for inline-size boundaries, sector-size boundaries, mount/remount persistence, and failed transaction cleanup.
- Tmpfile tests covering open, linkat of an `O_TMPFILE`, orphan cleanup after crash/recovery, and nlink handling.
- Fallocate/preallocation tests for keep-size and non-keep-size ranges, fragmented allocations, qgroup limits, ENOSPC injection, remount persistence of `i_size`/`disk_i_size`, and relocation races around newly reserved extents.
- Permission tests for readonly roots and `BTRFS_INODE_READONLY` files, directories, and symlinks, with ordinary DAC/ACL checks still delegated to `generic_permission()`.
- Encoded read/write ioctl tests for zlib/lzo/zstd, inline compressed extents, holes, prealloc extents, uncompressed extents, short user buffers returning `-ENOBUFS`, NOWAIT returning `-EAGAIN`, io_uring completion, NODATASUM rejection, alignment rejection, EOF handling, and checksum verification after write completion.
- Send/receive tests that preserve compressed extents through encoded reads and writes.
- Swapfile tests for accepted nocow/nodatasum/single-device files and rejection of compressed, checksummed, holey, inline, shared, reflinked, multi-device, readonly block-group, snapshot-racing, and deleting-subvolume cases.
- Fault-injection tests for allocation failures in path allocation, delalloc work allocation, extent-map creation, compressed folio allocation, qgroup reservation, bio submission, and swap pin allocation.
- Assertion-enabled tests that exercise `btrfs_assert_inode_range_clean()` after flushing and locking ranges.

## Cross-Chunk Notes

This chunk begins immediately after the main rename implementations and only includes the `rename2` dispatcher. The full rename semantics, transaction item counts, inode link updates, and whiteout handling are in earlier chunks.

The final operation tables reference many functions implemented before line 8841 and should be reconciled with those chunks for a complete per-file callback map. Conversely, the encoded I/O helpers and preallocation helpers implemented here are referenced by headers and other Btrfs files, so the merged file report should connect this chunk to `btrfs_inode.h`, `file.c`, `ioctl.c`, and `send.c`.
