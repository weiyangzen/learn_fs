# subset-b-005614 Research

Grouped source research for the Btrfs file item/checksum layer and the Btrfs regular file operation layer. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/file-item.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/file-item.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/file-item.c` implements Btrfs helpers for file extent items and data checksum items. It owns checksum tree lookup, checksum insertion/deletion, per-bio checksum buffer setup, checksum generation for write bios, dummy ordered sums for zoned nodatasum writes, conversion from on-disk file extent items into in-memory extent maps, and inode `disk_i_size` safety tracking for filesystems without `NO_HOLES`. The source was read as a complete 1407-line file for this report.

## Important APIs, Types, and Functions

`btrfs_inode_safe_disk_i_size_write()` updates `inode->disk_i_size`, either directly for `NO_HOLES` mode or by limiting it to the contiguous file-extent range recorded in `inode->file_extent_tree`. `btrfs_inode_set_file_extent_range()` and `btrfs_inode_clear_file_extent_range()` maintain that in-memory extent bitmap when file extent items are inserted or dropped.

`btrfs_insert_hole_extent()` creates an explicit regular file extent item with `disk_bytenr == 0`, zero disk bytes, and logical `num_bytes`/`ram_bytes` for filesystems that represent holes explicitly. `btrfs_lookup_file_extent()` wraps `btrfs_search_slot()` for `BTRFS_EXTENT_DATA_KEY` lookups and supports read, COW, and insertion-search modes through the `mod` argument.

Checksum read APIs include private `btrfs_lookup_csum()` and `search_csum_tree()`, plus exported `btrfs_lookup_bio_sums()`, `btrfs_lookup_csums_list()`, `btrfs_lookup_csums_range()`, and `btrfs_lookup_csums_bitmap()`. They search `BTRFS_EXTENT_CSUM_KEY` items by logical disk byte address and return checksums either into a bio-owned buffer, a list of `struct btrfs_ordered_sum`, or a caller-provided bitmap/buffer pair.

Checksum write/delete APIs include `btrfs_csum_one_bio()`, `btrfs_alloc_dummy_sum()`, `btrfs_del_csums()`, and `btrfs_insert_data_csums()`. These calculate checksums from bio pages, attach ordered sums to ordered extents, split or truncate existing checksum items when deleting overlapping ranges, and insert or extend checksum items while respecting leaf space and log-tree overlap rules.

`btrfs_extent_item_to_extent_map()` translates regular, preallocated, hole, compressed, and inline file extent items into `struct extent_map`. `btrfs_file_extent_end()` returns the non-inclusive logical end of a file extent item, rounding inline extents to sectorsize.

## Control Flow

The checksum read path starts when the bio layer submits a data read and calls `btrfs_lookup_bio_sums()`. The function skips work for `NODATASUM` inodes or global no-data-csum state, allocates either `bbio->csum_inline` or a larger `kvcalloc()` buffer, optionally searches the commit root under `commit_root_sem`, and iterates sector-aligned chunks through `search_csum_tree()`. Missing checksums are converted to zeroed checksum slots; data relocation reads mark `EXTENT_NODATASUM`, while normal roots emit a rate-limited warning about checksum holes.

The checksum range lookup paths first search for the requested start key, then step back to a previous checksum item if it overlaps the requested start. They iterate csum items in key order, trim each item to the requested range, and either allocate ordered-sum records (`btrfs_lookup_csums_list()`/`range`) or copy bytes into a dense checksum buffer while setting a sector bitmap (`btrfs_lookup_csums_bitmap()`).

The checksum write path begins in the bio submit/write path with `btrfs_csum_one_bio()`. It allocates a `struct btrfs_ordered_sum` sized to the bio, attaches it to the ordered extent, and either computes checksums synchronously or schedules `csum_one_bio_work()`. Ordered extent completion later calls `btrfs_insert_data_csums()`, which repeatedly looks for an existing csum item ending at the new range, extends it when safe, or inserts a new item. Log-tree insertion has additional next-item checks to avoid overlapping checksum items.

The delete path in `btrfs_del_csums()` searches backward from the end of the target range. Fully covered checksum items are batched and deleted; prefix/suffix overlaps are truncated by `truncate_one_csum()`; ranges in the middle of a checksum item are split in place, then the newly formed overlapping item is processed again. This allows tree-log code to replace overlapping logged checksum ranges before inserting new ones.

The extent-map conversion path is used after a file extent item has already been found in a B-tree leaf. It reads the item type and fields, fills an extent map with logical start/length, disk bytenr, disk length, generation, RAM bytes, offset, compression, and prealloc flags, and emits an error for unknown types.

## State and Persistence Behavior

Persistent state modified here is Btrfs metadata: file extent items for holes and checksum tree items for data checksums. All such changes happen under `struct btrfs_trans_handle` and target either the checksum tree, a tree-log root, or a file's subvolume root. Checksum item layout is compact: item payload length is a multiple of `fs_info->csum_size`, and logical byte coverage is derived from sectorsize.

Runtime state includes `bbio->csum`, `bbio->sums`, `bbio->csum_inline`, async checksum work/completion, `struct btrfs_path` cursor reuse, temporary ordered-sum list nodes, and `inode->file_extent_tree`. `disk_i_size` is protected by `inode->lock`; extent bitmap updates rely on sectorsize-aligned ranges and preserve crash-consistency decisions made by truncation, hole punching, and extent replacement callers.

The file also preserves consistency between ordered extents and later metadata insertion. `btrfs_csum_one_bio()` stores checksums with ordered extents, while `btrfs_insert_data_csums()` persists them after I/O completion. For zoned nodatasum writes, `btrfs_alloc_dummy_sum()` persists no checksum bytes but keeps ordered-sum state so zone append completion can record the updated logical address.

## Dependencies and Integration Points

Direct dependencies include Btrfs B-tree accessors, extent buffers, transaction handles, checksum roots, ordered extents, bio wrappers, compression helpers, volume mapping, and inode extent I/O trees. Public prototypes are exported through `file-item.h`.

Major callers are the bio layer (`btrfs_lookup_bio_sums()` on data reads and checksum generation on writes), inode ordered extent completion (`btrfs_insert_data_csums()`), tree-log code (`btrfs_insert_data_csums()` and `btrfs_del_csums()` for logged checksum ranges), file/inode extent replacement and truncation paths (`btrfs_inode_*_file_extent_range()` and `btrfs_insert_hole_extent()`), and extent map lookup code (`btrfs_extent_item_to_extent_map()` and `btrfs_file_extent_end()`).

## Risks and Edge Cases

Important risks are off-by-one errors in inclusive/exclusive byte ranges, checksum-item splitting with a locked path, search cursor reuse across leaves, missing checksum roots returning corruption errors, and incorrect treatment of checksum holes for data relocation versus normal reads. Alignment assertions are central: most checksum and file-extent bitmap APIs require sectorsize-aligned ranges, while checksum item sizes must be multiples of `csum_size`.

`btrfs_insert_data_csums()` has subtle log-tree behavior because logged checksum items can overlap after reflink and fast fsync sequences. Extending an existing csum item beyond the next csum item would corrupt later lookup semantics. `btrfs_del_csums()` must preserve non-overlapping prefix/suffix checksums while deleting the requested range. `btrfs_extent_item_to_extent_map()` must treat inline extents specially because the disk-bytenr field location is inline data.

## Test Signals

Useful signals include xfstests covering reads with missing/bad checksums, data relocation of nodatasum extents, checksum tree deletion during truncation and hole punching, log replay after reflink plus fsync, compressed and inline file reads, zoned zone-append nodatasum writes, sectorsize larger than page size, and commit-root checksum lookup under free-space-cache reads. Debug builds should exercise alignment assertions, checksum item split/extend paths, extent map conversion for regular/prealloc/hole/inline items, and `disk_i_size` updates with and without `NO_HOLES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/file-item.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/file-item.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/file-item.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/file-item.h` is the public interface for Btrfs file extent item and checksum item helpers implemented mostly by `file-item.c`. It exposes inline layout helpers for inline file extents and prototypes used by bio submission, ordered extent completion, tree logging, file extent replacement, inode truncation, and extent-map construction. The source was read as a complete 87-line file for this report.

## Important APIs, Types, and Functions

The layout macro `BTRFS_FILE_EXTENT_INLINE_DATA_START` defines where inline extent payload begins inside `struct btrfs_file_extent_item`. Inline helpers include `BTRFS_MAX_INLINE_DATA_SIZE()`, `btrfs_file_extent_inline_item_len()`, `btrfs_file_extent_inline_start()`, and `btrfs_file_extent_calc_inline_size()`. They abstract the relationship between B-tree item size, file extent header size, filesystem node size, and inline payload bytes.

Declared checksum APIs include `btrfs_del_csums()`, `btrfs_lookup_bio_sums()`, `btrfs_insert_data_csums()`, `btrfs_csum_one_bio()`, `btrfs_alloc_dummy_sum()`, `btrfs_lookup_csums_range()`, `btrfs_lookup_csums_list()`, and `btrfs_lookup_csums_bitmap()`. Declared file extent APIs include `btrfs_insert_hole_extent()`, `btrfs_lookup_file_extent()`, `btrfs_extent_item_to_extent_map()`, `btrfs_inode_clear_file_extent_range()`, `btrfs_inode_set_file_extent_range()`, `btrfs_inode_safe_disk_i_size_write()`, and `btrfs_file_extent_end()`.

The header forward-declares the involved Btrfs and block-layer structures rather than including their full definitions: `extent_map`, `btrfs_file_extent_item`, `btrfs_fs_info`, `btrfs_path`, `btrfs_bio`, `btrfs_trans_handle`, `btrfs_root`, `btrfs_ordered_sum`, and `btrfs_inode`.

## Control Flow

The header has no standalone runtime flow. It defines the callable surface for several flows: bio reads preload checksum buffers through `btrfs_lookup_bio_sums()`, write bios attach ordered sums through `btrfs_csum_one_bio()` or `btrfs_alloc_dummy_sum()`, ordered extent completion persists sums through `btrfs_insert_data_csums()`, tree-log code deletes and reinserts checksum ranges, and file extent mutation paths update file-extent maps and `disk_i_size` using the inode/file extent helpers.

The inline helpers are used wherever inline extents are created, copied, or interpreted. Their control role is to keep item-size calculations centralized so callers do not duplicate offset arithmetic against the on-disk `btrfs_file_extent_item` format.

## State and Persistence Behavior

This header owns no storage and performs no persistence directly. Its declared functions operate on persistent Btrfs metadata through transaction handles and B-tree paths, and on runtime structures such as `struct btrfs_bio`, ordered sums, extent maps, and inode extent-state trees. The inline-size helpers encode on-disk layout constraints, so changes to them affect how inline file data is packed in B-tree leaves.

## Dependencies and Integration Points

The header includes Linux block/list definitions, the UAPI Btrfs tree format, `ctree.h`, and `ordered-data.h`. It is included by Btrfs bio, inode, file, tree-log, reflink, extent-map, and writeback code that needs checksum or file-extent item helpers.

Integration points are transaction-safe B-tree mutation, ordered extent checksum lifetime, file extent map caching, inline extent creation, tree-log replay, reflink checksum logging, and `NO_HOLES` versus explicit-hole behavior.

## Risks and Edge Cases

The main risks are interface contract drift and layout drift. The inline data offset must match the UAPI on-disk structure; a wrong size calculation can corrupt inline file extent items or reject valid inline writes. The prototypes expose functions with strict alignment, locking, and transaction expectations that are not enforceable by the compiler. Callers must also respect checksum buffer sizing and list ownership conventions.

## Test Signals

Compile coverage across Btrfs is the first signal because this header is a shared ABI inside the filesystem. Runtime signals include inline extent write/read tests, compressed inline extents, checksum lookup and insertion tests, log replay with checksums, hole punching/truncation with explicit holes and `NO_HOLES`, and large sectorsize/subpage coverage that stresses the inline length and sectorsize alignment helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/file-item.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/file.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/file.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/file.c` implements regular-file operations and file extent mutation for Btrfs. It provides the VFS `file_operations` table, buffered/direct/encoded write dispatch, fsync and tree-log integration, mmap write-fault handling, fallocate/punch-hole/zero-range behavior, SEEK_DATA/SEEK_HOLE, NOCOW write eligibility, file extent dropping/replacement, prealloc-to-written conversion, and helper flows for dirty folio and delayed allocation accounting. The source was read as a complete 3896-line file for this report.

## Important APIs, Types, and Functions

Public functions exported through `file.h` include `btrfs_sync_file()`, `btrfs_drop_extents()`, `btrfs_replace_file_extents()`, `btrfs_mark_extent_written()`, `btrfs_do_write_iter()`, `btrfs_release_file()`, `btrfs_dirty_folio()`, `btrfs_fdatawrite_range()`, `btrfs_check_nocow_lock()`, `btrfs_check_nocow_unlock()`, `btrfs_find_delalloc_in_range()`, `btrfs_write_check()`, and `btrfs_buffered_write()`.

`btrfs_drop_extents()` is the central low-level file extent deletion helper. It walks `BTRFS_EXTENT_DATA_KEY` items for an inode, truncates or splits partially overlapped extents, deletes fully covered items, updates delayed refs and `bytes_found`, optionally leaves an insertion slot for a replacement extent, and reports `drop_end`.

`btrfs_replace_file_extents()` builds on `btrfs_drop_extents()` for hole punching and extent replacement. It starts transactions, reserves metadata, drops existing file extents over a range, inserts explicit holes or replacement extents when needed, updates inode byte accounting, refreshes inode timestamps/version, and returns an open transaction through `trans_out` on success.

`btrfs_mark_extent_written()` converts preallocated extents to regular extents after writes. It may split a prealloc item into leading/written/trailing pieces, merge with adjacent regular extents that reference the same disk extent, and adjust delayed refs for shared extent-item references.

Buffered write helpers include `btrfs_write_check()`, `reserve_space()`, `copy_one_range()`, `btrfs_dirty_folio()`, and `btrfs_buffered_write()`. They perform generic write checks, privilege/time updates, hole expansion, data and metadata reservation, NOCOW fallback, folio preparation, extent locking, ordered-extent waiting, atomic copy from the iterator, delayed allocation marking, and inode size updates.

File operation entry points include `btrfs_file_write_iter()`, `btrfs_file_read_iter()`, `btrfs_file_splice_read()`, `btrfs_file_open()`, `btrfs_file_llseek()`, `btrfs_file_mmap_prepare()`, `btrfs_fallocate()`, and `btrfs_release_file()`. `btrfs_file_operations` wires these into VFS along with ioctl, remap, uring command, lease, and splice helpers.

## Control Flow

The write path enters through `btrfs_do_write_iter()`. It rejects writes after shutdown or filesystem error, disallows NOWAIT encoded writes, and dispatches to encoded, direct, or buffered write handling. Buffered writes take the inode lock, run generic and Btrfs write checks, then loop over `copy_one_range()`. Each iteration faults user pages before locking folios, reserves data/metadata or obtains a NOCOW lock, balances dirty pages, prepares an uptodate mapped folio if partial-block preservation is needed, waits for overlapping ordered extents, copies bytes, marks the range delalloc and folio dirty, releases reservations/locks, and advances `ki_pos`. Direct writes are delegated to `btrfs_direct_write()`, while encoded writes use ioctl encoded I/O arguments and reject partial encoded writes.

The fsync path in `btrfs_sync_file()` always expands the requested range to the whole file. It starts writeback, locks the inode and mmap lock, starts writeback again to close the race with dirty pages created before locking, decides fast versus full sync, waits for ordered extents or writeback as required, and either skips logging if already committed, logs the dentry into the tree log, synchronizes the log, or falls back to a full transaction commit. It carefully drops the inode lock before log sync/commit and, on fast-sync fallback, ends the transaction before waiting for ordered extents to avoid deadlocks with fallocate and transaction commit.

The mmap write-fault path in `btrfs_page_mkwrite()` reserves delalloc space before locking the folio to avoid dirty-page writeback deadlocks. It locks the mmap range, validates EOF/truncation races, waits for ordered extents, marks the page range delalloc, zeroes bytes beyond EOF inside the folio, marks Btrfs folio state dirty/uptodate, updates last-subtransaction state, and returns `VM_FAULT_LOCKED` with the folio locked for the VM.

Hole punching in `btrfs_punch_hole()` locks the inode/mmap state, waits for ordered extents, skips existing holes, zeroes unaligned boundary blocks through `btrfs_truncate_block()`, locks and truncates page cache for the aligned interior through `btrfs_punch_hole_lock_range()`, calls `btrfs_replace_file_extents()` with no replacement info, updates inode metadata, and unlocks the extent range. `btrfs_zero_range()` and `btrfs_fallocate()` share the same primitives but allocate preallocated extents for holes or zero ranges, reserve qgroup/data space, and update i_size when `KEEP_SIZE` is not set.

SEEK_DATA/SEEK_HOLE enters through `btrfs_file_llseek()` and `find_desired_extent()`. It locks the inode shared, searches file extent items, treats prealloc and disk_bytenr-zero regular extents as holes, detects implicit holes between extent items, overlays delalloc and ordered extents through `btrfs_find_delalloc_in_range()`, and returns either the next data offset, hole offset, i_size, or `-ENXIO`.

## State and Persistence Behavior

Persistent state includes file extent items, extent reference counts, explicit hole items, preallocated and written extent types, inode item timestamps/version/size, and tree-log entries. Mutating paths run inside Btrfs transactions and often abort the transaction if an operation would leave dropped extents without the required replacement or hole item. `btrfs_replace_file_extents()` deliberately reopens transactions over long ranges to balance dirty B-tree pages and preserve crash consistency across partial progress.

Runtime state includes folio dirty/uptodate/checked bits, inode `io_tree` flags (`EXTENT_DELALLOC`, `EXTENT_NORESERVE`, `EXTENT_DEFRAG`, and ordered extent ranges), delayed allocation reservation state, qgroup reservation changesets, extent maps, `file->private_data` llseek cache state, log context ordered-extents lists, and `BTRFS_INODE_*` runtime flags such as `NEEDS_FULL_SYNC`, `COW_WRITE_ERROR`, `FLUSH_ON_CLOSE`, and `NO_DELALLOC_FLUSH`.

`disk_i_size` and file extent range tracking are coordinated with helpers from `file-item.c`. For filesystems without `NO_HOLES`, explicit hole items and the in-memory `file_extent_tree` keep the durable size from advancing across gaps. For fast fsync correctness, replacement/cloning paths may force full sync if extent maps were dropped or holes are only implicit.

## Dependencies and Integration Points

This file integrates Linux VFS file operations, page cache/folios, mmap fault handling, writeback, direct I/O, splice, fallocate modes, fsverity open checks, and generic write/llseek helpers. Btrfs dependencies include transactions, tree-log logging/sync, ordered extents, delalloc reservation, qgroups, compression writeback behavior, NOCOW/prealloc extent checks, extent-tree reference helpers, reflink/remap operations, ioctl encoded writes, subpage folio state, root snapshot locks, inode locks, and extent maps.

Important external callers include inode writeback/inline extent creation via `btrfs_drop_extents()`, reflink cloning through `btrfs_replace_file_extents()`, encoded write ioctls through `btrfs_do_write_iter()`, and tree-log code that relies on fsync ordering and checksum/extent consistency. The exported `btrfs_file_operations` is the VFS integration point for normal file descriptors.

## Risks and Edge Cases

The highest-risk areas are transaction error handling after partial extent deletion, delayed-ref accounting while splitting or merging extents, lock ordering between inode locks, mmap locks, extent locks, ordered extents, and transactions, and reservation unwinding on short copies or NOWAIT failures. Inline extents often return `-EOPNOTSUPP` for operations that require splitting; callers must distinguish clone limitations from corruption-worthy failures.

Fsync has many subtle races: dirty pages created before inode locking, ordered extent completion that updates file extent items and checksums, COW write errors that require waiting and dropping bad extent maps, zoned writes whose logical address stabilizes only after I/O, and fast-sync log checksum overlap after reflink. SEEK_DATA/SEEK_HOLE must combine on-disk extents, implicit holes, explicit hole items, prealloc extents, delalloc, and ordered extents without returning stale cached state from another task.

Fallocate and punch-hole edge cases include unaligned boundaries, large folios that partially overlap the lock range, subpage sectors, holes beyond EOF, `NO_HOLES` filesystems, qgroup limits, zoned filesystem rejection, and crash consistency when a long range requires multiple transactions.

## Test Signals

Useful signals include xfstests for buffered writes, direct writes, NOWAIT writes, NOCOW and prealloc writes, encoded writes, mmap write faults, fsync after buffered/direct/reflink writes, log replay after fast fsync, fallocate preallocation, zero range, punch hole with unaligned boundaries, `NO_HOLES` versus explicit holes, SEEK_DATA/SEEK_HOLE with delalloc and ordered extents, truncate/clone interactions, qgroup ENOSPC, zoned fallocate rejection, compression writeback fsync behavior, subpage and large-folio page-cache cases, and fault injection for ENOMEM/ENOSPC/EIO in extent mutation and reservation unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/file.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/file.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/file.h` is the public header for Btrfs regular-file operations and file extent mutation helpers implemented in `file.c`. It exposes the VFS file operations table and the cross-subsystem APIs used by inode writeback, reflink, ioctl encoded I/O, tree logging, truncation, hole punching, NOCOW checks, and delalloc discovery. The source was read as a complete 51-line file for this report.

## Important APIs, Types, and Functions

The header declares `extern const struct file_operations btrfs_file_operations`, which binds Btrfs regular inodes to VFS read, write, mmap, fsync, fallocate, ioctl, remap, splice, and llseek handlers.

Extent mutation APIs are `btrfs_drop_extents()`, `btrfs_replace_file_extents()`, and `btrfs_mark_extent_written()`. They operate on `struct btrfs_trans_handle`, `struct btrfs_root`, `struct btrfs_inode`, `struct btrfs_path`, `struct btrfs_drop_extents_args`, and `struct btrfs_replace_extent_info` contracts defined elsewhere.

Write and file lifecycle APIs are `btrfs_sync_file()`, `btrfs_do_write_iter()`, `btrfs_release_file()`, `btrfs_dirty_folio()`, `btrfs_fdatawrite_range()`, `btrfs_write_check()`, and `btrfs_buffered_write()`. NOCOW/delalloc helpers are `btrfs_check_nocow_lock()`, `btrfs_check_nocow_unlock()`, and `btrfs_find_delalloc_in_range()`.

The header forward-declares Linux and Btrfs types including `file`, `extent_state`, `kiocb`, `iov_iter`, `inode`, `folio`, encoded I/O args, drop/replace extent args, roots, paths, inodes, and transaction handles.

## Control Flow

This file has no executable control flow. It describes the callable edges into `file.c`: VFS enters through `btrfs_file_operations`, ioctl encoded write code enters `btrfs_do_write_iter()`, inode and reflink code enter extent dropping/replacement helpers, writeback and page-cache paths use dirty-folio and fdatawrite helpers, and NOCOW callers pair `btrfs_check_nocow_lock()` with `btrfs_check_nocow_unlock()` when the lock check succeeds.

## State and Persistence Behavior

No state is stored in the header itself. The declared functions mutate durable Btrfs metadata such as file extent items, inode items, delayed refs, and tree-log records, and they manipulate runtime state such as folio flags, extent-state bits, ordered extents, qgroup reservations, and file-private llseek caches. The header is therefore a transaction- and locking-sensitive interface even though it contains only declarations.

## Dependencies and Integration Points

The header includes only `<linux/types.h>` and relies on forward declarations to reduce include coupling. It is consumed by Btrfs inode, reflink, ioctl, tree-log, direct-I/O, and other file-related code that needs regular-file operations without including the full `file.c` implementation.

Integration points include VFS file operations, Btrfs transactions, ordered extents, file extent B-tree items, reflink extent replacement, encoded I/O, buffered write delayed allocation, fsync/tree-log, and SEEK_DATA/SEEK_HOLE delalloc detection.

## Risks and Edge Cases

The risk in this header is contract visibility. Several declarations require strict caller discipline: `btrfs_replace_file_extents()` expects locked ranges and returns an open transaction on success; `btrfs_check_nocow_lock()` must be balanced by unlock only on positive return; `btrfs_dirty_folio()` receives cached extent state ownership; and `btrfs_drop_extents()` depends on correctly initialized argument structures. Type forward declarations hide details, so compile-time checking cannot enforce most lifetime and locking rules.

## Test Signals

Compile coverage across Btrfs users is essential. Behavioral signals should come from the implementation users: reflink clone/dedupe tests, inline extent writeback, prealloc-to-written conversion, buffered and encoded writes, fsync/log replay, mmap dirtying, NOCOW NOWAIT paths, fallocate/punch-hole/zero-range, and SEEK_DATA/SEEK_HOLE with delalloc. Static analysis and lockdep are useful for checking that callers honor transaction, inode-lock, mmap-lock, and NOCOW lock pairing contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/file.h -->
