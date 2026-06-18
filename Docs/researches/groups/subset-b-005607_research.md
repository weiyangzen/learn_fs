# subset-b-005607 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/backref.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/backref.c

## Purpose
`backref.c` implements Btrfs back-reference discovery and resolution. It answers questions such as "which leaves/inodes/roots reference this logical extent?", "is this data extent shared?", "which paths name this inode?", and "what tree-parent graph should relocation use for this tree block?". The file converts extent-tree references, delayed references, and fs-tree searches into parent logical addresses, inode/file-offset tuples, root IDs, and relocation cache edges.

## Important APIs, types, and functions
- `struct extent_inode_elem` is the private linked-list payload attached to leaf `ulist` entries; each element records inode number, file offset, and referenced byte count for a file extent item.
- `struct preftree`/`struct preftrees` hold merged preliminary refs in cached rbtrees for direct refs, indirect refs with keys, and indirect refs that need keys read from tree blocks.
- `struct share_check` carries state for `btrfs_is_data_extent_shared()`, including target root/inode/bytenr/generation, direct-reference counts, self-reference counts, and whether delayed deletes prevent early exits.
- `btrfs_prelim_ref_init()` and `btrfs_prelim_ref_exit()` create and destroy the `btrfs_prelim_ref` slab cache.
- `btrfs_find_all_leafs()` fills `ctx->refs` with leaves that contain file extent items referencing `ctx->bytenr`.
- `btrfs_find_all_roots()` recursively walks parent refs until root IDs are found in `ctx->roots`.
- `btrfs_is_data_extent_shared()` is the fast sharedness query used by fiemap-like callers.
- `extent_from_logical()`, `iterate_extent_inodes()`, and `iterate_inodes_from_logical()` form the logical-address-to-inode reporting path.
- `btrfs_ref_to_path()`, `paths_from_inode()`, `init_data_container()`, and `init_ipath()` support inode-to-path reporting.
- `btrfs_find_one_extref()` scans `BTRFS_INODE_EXTREF_KEY` items.
- `tree_backref_for_extent()` and the private `get_extent_inline_ref()` iterate inline metadata backrefs in an extent item.
- `btrfs_backref_iter_start()` and `btrfs_backref_iter_next()` provide a metadata-backref iterator over inline and keyed tree refs.
- `btrfs_backref_init_cache()`, node/edge allocation/free helpers, `btrfs_backref_add_tree_node()`, `btrfs_backref_finish_upper_links()`, and `btrfs_backref_error_cleanup()` implement the relocation/general tree-backref cache.

## Control flow
The core walk starts in `find_parent_nodes()`. It chooses the extent root for `ctx->bytenr`, prepares a path against either the commit root or the current tree view, optionally reads delayed refs from an active transaction, then reads inline and keyed extent-tree references. Inline refs are parsed by `add_inline_refs()`, while external keyed refs are collected by `add_keyed_refs()`. Both paths classify direct shared refs, indirect tree refs, indirect data refs, counts, owners, roots, and parent bytenrs into preliminary reference trees.

Indirect refs are resolved in two phases. `add_missing_keys()` reads referenced tree blocks when an on-disk tree-block ref does not carry a search key, inserts a first key into the indirect tree, and releases the extent buffer. `resolve_indirect_refs()` repeatedly removes refs from the indirect tree, calls `resolve_indirect_ref()` to search the owning root, and converts found parents into direct refs. For data refs at level 0, `add_all_parents()` scans matching file extent items, filters by `extent_item_pos` unless ignored, and attaches inode-list data to the leaf parent. Duplicate refs are merged by `prelim_ref_insert()`, which also updates sharedness counters.

After indirect resolution, `find_parent_nodes()` walks the direct-prelim rbtree. Parent bytenrs are appended to `ctx->refs`, roots are appended to `ctx->roots` when a resolved ref has no parent, and missing inode lists for leaf parents are filled by reading the leaf and calling `find_extent_in_eb()`. `btrfs_find_all_leafs()` is a one-level wrapper for data extent to leaf discovery. `btrfs_find_all_roots_safe()` iterates this process, using the `refs` ulist as a frontier until it reaches roots; `btrfs_find_all_roots()` adds `commit_root_sem` protection when there is no transaction.

`iterate_extent_inodes()` resolves a data extent into leaves, then for each leaf either uses caller-provided root cache callbacks or calls `btrfs_find_all_roots_safe()`. For every root/leaf combination, `iterate_leaf_refs()` invokes the supplied `iterate_extent_inodes_t` callback with inode, file offset, byte count, and root ID. `iterate_inodes_from_logical()` first maps an arbitrary logical address to a data extent with `extent_from_logical()`, computes the relative extent item position, and then uses `build_ino_list()` to write triples into a `btrfs_data_container`.

The sharedness query `btrfs_is_data_extent_shared()` first checks a small previous-extents cache, then joins or attaches to a transaction to see delayed refs consistently, or falls back to `commit_root_sem`. It can answer immediately from a path cache when the current leaf is already known shared. Otherwise it calls `find_parent_nodes()` with `share_check`, short-circuiting on direct sharing, different inodes/roots, or known not-shared generation conditions. If direct refs do not prove sharing, it walks up parent tree blocks and stores per-level path-cache answers; multiple parents disable the simple path cache and force conservative invalidation. Results for extents with multiple self refs are stored in the small ring cache.

The path-building path is separate. `paths_from_inode()` searches normal inode refs and extended inode refs, clones the leaf before releasing the shared search path, and calls `inode_to_path()`. `inode_to_path()` stores a pointer into a caller-provided `btrfs_data_container` after `btrfs_ref_to_path()` walks parent inode refs backward into the supplied buffer. Short buffers do not fail; missed paths and missing bytes are counted.

The relocation/general backref cache path uses `btrfs_backref_iter_start()` to locate a metadata extent item, skip data extents, and set cursor pointers for inline or keyed tree refs. `btrfs_backref_add_tree_node()` iterates refs for one tree block. Direct shared block refs call `handle_direct_tree_backref()` and produce an edge to a known parent bytenr or identify a reloc-root self-reference. Indirect tree refs call `handle_indirect_tree_backref()`, which opens the root, searches the commit tree for the child pointer, builds upper nodes/edges along the path, and queues unchecked parents. `btrfs_backref_finish_upper_links()` then inserts the newly checked node and breadth-first finalizes edge membership in upper/lower lists and the cache rb-tree.

## State and persistence behavior
All state is in memory. Walk state lives in caller-owned `struct btrfs_backref_walk_ctx`, temporary `btrfs_path`s, `ulist`s, preliminary ref rbtrees, and linked inode-element lists. There is no new on-disk persistence; the file reads extent-tree items, delayed refs, root tree nodes, file extent items, inode refs, and commit roots to build transient answers.

Consistency depends on the selected view. With a transaction and tree-mod sequence, searches can use old-tree helpers and delayed refs up to `ctx->time_seq`. With `BTRFS_SEQ_LAST`, delayed refs are skipped and commit-root searching is used for qgroup commit-style callers. Without a transaction, `commit_root_sem` protects commit-root views. The sharedness cache stores generation tags from root last-snapshot generation or last root-drop generation so cached not-shared/shared answers are invalidated when snapshots or root drops make them unsafe.

Memory ownership is subtle. `free_leaf_list()` must free inode lists attached to ulist node auxiliary pointers. When preliminary refs are merged or transferred into `ctx->refs`, inode-list ownership is explicitly nulled to avoid double frees. Relocation cache nodes own extent buffers only while cached and locked state requires them; cleanup functions drop locks, extent buffers, rb-tree membership, root refs, and edge lists.

## Dependencies and integration points
The implementation depends on Btrfs extent-tree layout, delayed-ref internals, tree-mod-log sequence handling, root lookup, commit roots, old-tree search helpers, ulist, rbtrees, extent buffers, tree locking, relocation root lookup, simple quota owner refs, and file-item accessors. External users include fiemap/sharedness checks, logical-inode/path ioctls, qgroup/root discovery, send/receive or users of extent inode iteration, and relocation tree-building code.

The file assumes tree-checker and lower Btrfs accessors validate impossible inline-ref types and extent item corruption where possible. It reports corruption with `-EUCLEAN`, missing extents/roots with `-ENOENT`, unsupported metadata iteration cases with `-ENOTSUPP`, and propagates allocation/search errors.

## Risks and test signals
High-risk areas are delayed-ref merging with negative counts, early sharedness exits when delayed deletes exist, tree-mod-log/commit-root view selection, file extent offset underflow compatibility handling, inode-list ownership transfer, cache invalidation around snapshots/root drops, and parent resolution when direct and indirect refs coexist. The relocation cache adds risks around partially built edges, detached nodes, reloc-root self-refs, and cache hits that bypass pending checks.

Useful tests include reflink, snapshot, clone, hole-punch, prealloc, compressed and encoded extents, direct and shared data refs, mixed delayed add/drop refs, deleted roots, qgroup commit-root walks, logical-inode ioctl on exact and ignored offsets, inode path lookup with normal and extended refs, short data containers, skinny and non-skinny metadata, metadata extents with inline and keyed refs, relocation trees, root drop/snapshot generation cache invalidation, and error injection for extent-buffer reads and allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/backref.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/backref.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/backref.h

## Purpose
`backref.h` declares the public Btrfs back-reference walking interface. It defines the context passed into the backref engine, callback contracts for inode iteration and optional caching/filtering, sharedness-check cache state, inode path container helpers, and exported functions used by logical-inode queries, fiemap sharedness checks, qgroups, relocation, and extent-tree backref parsing.

## Important APIs, types, and functions
- `BTRFS_ITERATE_EXTENT_INODES_STOP` is a non-error stop code that iterator callbacks may return to end backref iteration early.
- `iterate_extent_inodes_t` is the callback signature for inode/file-offset/root results.
- `struct btrfs_backref_walk_ctx` is the central argument block. Callers set `bytenr`, `extent_item_pos`, `ignore_extent_item_pos`, `trans`, `fs_info`, `time_seq`, output `refs`/`roots`, optional cache callbacks, optional early indirect-ref iterator, optional extent-item checker, optional data-ref skip callback, and `user_ctx`.
- `struct inode_fs_paths` carries the path, root, and result container for inode-to-path lookup.
- `struct btrfs_backref_share_check_ctx` stores reusable fiemap-style state: a working `ulist`, current/previous leaf bytenrs, per-level path cache entries, and a small previous-extent result cache.
- `btrfs_alloc_backref_share_check_ctx()` and `btrfs_free_backref_share_ctx()` manage sharedness context lifetime.
- `extent_from_logical()`, `iterate_extent_inodes()`, and `iterate_inodes_from_logical()` expose logical address to inode/root enumeration.
- `paths_from_inode()`, `btrfs_ref_to_path()`, `init_data_container()`, and `init_ipath()` expose inode path construction helpers.
- `btrfs_find_all_leafs()` and `btrfs_find_all_roots()` expose lower-level parent/root discovery.
- `btrfs_find_one_extref()` scans extended inode refs.
- `tree_backref_for_extent()` exposes tree-backref extraction from extent items.
- `btrfs_is_data_extent_shared()` exposes the optimized sharedness query.
- `btrfs_prelim_ref_init()` and `btrfs_prelim_ref_exit()` are module init/exit hooks for the private prelim-ref cache.

## Control flow
Callers normally allocate and initialize a `btrfs_backref_walk_ctx`, set `fs_info`, `bytenr`, and data-offset options, and choose the required output path. Leaf discovery calls `btrfs_find_all_leafs()` and reads `ctx->refs`. Root discovery calls `btrfs_find_all_roots()` and reads `ctx->roots`. Inode enumeration calls `iterate_extent_inodes()` with a callback, and optional cache callbacks can avoid re-resolving roots for leaves that were seen before.

For user-facing logical lookup, callers can use `iterate_inodes_from_logical()`, which internally maps the logical address to an extent, rejects metadata extents, and invokes the generic inode iterator. For path lookup, callers create an `inode_fs_paths` with `init_ipath()`, then call `paths_from_inode()` and read paths stored in the embedded `btrfs_data_container`.

For sharedness, callers allocate one `btrfs_backref_share_check_ctx` and reuse it across adjacent file extent items, updating `curr_leaf_bytenr` before each `btrfs_is_data_extent_shared()` call. The context caches tree-path sharedness and repeated data-extent results, so repeated fiemap-style scans do not pay full recursive backref costs every time.

## State and persistence behavior
This header defines only in-memory contracts. `btrfs_backref_walk_ctx` is per-walk and mostly caller-owned. `refs` and `roots` are `ulist` outputs or temporaries depending on the called helper. `btrfs_backref_share_check_ctx` is reusable but still volatile; it must be freed with `btrfs_free_backref_share_ctx()`. No state is persisted outside normal Btrfs metadata read by the implementation.

The `time_seq` and `trans` fields encode consistency requirements. A tree-mod-log sequence lets the implementation use old-tree views plus delayed refs; `BTRFS_SEQ_LAST` selects commit-root behavior and deliberately skips delayed refs for commit-time qgroup usage.

## Dependencies and integration points
The header depends on Linux rbtrees/lists/slab types, Btrfs UAPI tree definitions, extent buffers, locking, disk I/O, and core `ctree` definitions. Its declarations are consumed by backref-heavy features outside `backref.c`, including fiemap, logical-inode ioctls, qgroups, relocation, and extent-tree metadata parsers.

## Risks and test signals
API misuse risks include failing to initialize mandatory fields, passing a `refs` pointer where the callee expects `NULL`, forgetting to free returned ulists or inode path containers, using `BTRFS_SEQ_LAST` when delayed refs matter, enabling `indirect_ref_iterator` without cache callbacks, or letting cache callbacks return stale root IDs. Tests should cover each exported helper with initialized and intentionally missing context fields, transaction and commit-root modes, callback early-stop behavior, sharedness context reuse across leaves, short path containers, and logical addresses that map to data, metadata, and no extent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/backref.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/bio.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/bio.c

## Purpose
`bio.c` is the Btrfs logical I/O submission and completion layer. It wraps Linux block `bio`s in `struct btrfs_bio`, maps logical ranges to physical devices and RAID profiles, splits I/O at mapping or zone-append boundaries, performs or schedules checksum generation and verification, handles mirrored/RAID56 write completion, performs data read repair, and owns the biosets/mempool used by normal, cloned, and repair bios.

## Important APIs, types, and functions
- `btrfs_bio_init()` and `btrfs_bio_alloc()` initialize/allocate high-level Btrfs bios.
- `btrfs_bio_end_io()` merges completion status from split/cloned bios, waits for async checksum work when needed, releases ordered extents, and invokes the caller end-io callback once all pending pieces finish.
- `btrfs_submit_bbio()` is the main submit entry point; it loops through `btrfs_submit_chunk()` until the whole logical bio is mapped/submitted.
- `btrfs_submit_chunk()` maps a logical range with `btrfs_map_block()`, performs splitting, preloads read checksums, attaches write checksum work, handles zone append constraints, and dispatches to the physical submit path.
- `btrfs_submit_bio()` selects single-device, RAID56, or mirrored-write submission.
- `btrfs_submit_dev_bio()` validates the target device, rewrites zone-append bios, tracks stats, and calls `submit_bio()` or `blkcg_punt_bio_submit()`.
- `btrfs_check_read_bio()`, `repair_one_sector()`, `btrfs_end_repair_bio()`, `btrfs_repair_io_failure()`, and `btrfs_submit_repair_write()` implement checksum/error-based read repair and targeted repair writes.
- `run_one_async_start()`, `run_one_async_done()`, `should_async_write()`, and `btrfs_wq_submit_bio()` offload expensive checksum generation before write submission.
- End-io handlers `btrfs_simple_end_io()`, `btrfs_raid56_end_io()`, `btrfs_orig_write_end_io()`, and `btrfs_clone_write_end_io()` normalize device/RAID completion into Btrfs completion semantics.
- `btrfs_bioset_init()` and `btrfs_bioset_exit()` manage normal, clone, repair, and failed-bio allocation pools.

## Control flow
Submitters allocate or initialize a `btrfs_bio`, fill the embedded Linux `bio`, and call `btrfs_submit_bbio()`. The entry point asserts alignment, then repeatedly calls `btrfs_submit_chunk()`. Each chunk maps the current logical sector and length to a `btrfs_io_context` or single stripe. If the returned mapping is shorter than the remaining bio, `btrfs_split_bio()` clones the front portion, increments the original `pending_ios`, advances file and checksum offsets, and submits the split first.

For data reads, `btrfs_submit_chunk()` saves the original iterator and preloads checksums with `btrfs_lookup_bio_sums()`. For writes, it records the original logical address for fscrypt checksum generation, tracks ordered-extents that use RAID stripe tree metadata, decides whether checksums are needed, and either queues async checksum work or computes checksums synchronously. NODATASUM, remap, data-relocation, zoned, and zone-append cases take alternate checksum/dummy-sum paths. Successful chunks are passed to `btrfs_submit_bio()`.

Physical submission has three branches. Single-stripe I/O sets `mirror_num`, physical sector, device private data, and `btrfs_simple_end_io()`. RAID56 routes through parity recovery/write helpers and `btrfs_raid56_end_io()`. Mirrored writes clone the bio for all but the last stripe; clones use `btrfs_clone_write_end_io()` to update shared error state and end the original, while the original uses `btrfs_orig_write_end_io()` to apply `max_errors` tolerance before completing the high-level bbio.

Completion always returns to task context before the caller callback. Simple completions queue `simple_end_io_work()` on metadata or data endio workers. Reads of data inodes call `btrfs_check_read_bio()`, which verifies checksums block by block and starts repair reads for failed sectors. Repair reads try alternate mirrors; on success, they call `btrfs_repair_io_failure()` to synchronously rewrite bad mirrors. If repair fails on all mirrors, the original bbio gets `BLK_STS_IOERR`. Non-read or metadata paths call `btrfs_bio_end_io()` directly after optional zoned physical recording.

`btrfs_bio_end_io()` is the convergence point for split bios. Clone bios that were never submitted or are completing drop their ordered extent refs and `bio_put()` themselves, then update the original status via `cmpxchg()` so the first error wins. The original callback runs only when `pending_ios` reaches zero, and ordered extents are released after the submitter's end-io callback runs.

## State and persistence behavior
Persistent on-disk changes are indirect: submitted writes eventually update device blocks, repair writes correct bad mirrors, and write checksum generation attaches checksum state to ordered extents for later metadata insertion. Runtime state includes static biosets, the repair failed-bio mempool, per-bbio pending counts, mirror number, first error status, read checksum buffers, ordered extent refs, RAID stripe context refs, async checksum work, and saved iterators.

Device error counters are updated for read, write, flush, and repair-write failures. Filesystem I/O counters block device replace/removal races while mapped I/O or repair I/O is active. Zone append writes may have their physical sector rewritten to the zone start for submission and recorded back to ordered state on success.

## Dependencies and integration points
The file integrates Linux block-layer bios, biosets, blkcg punt submission, Btrfs volume mapping, RAID56 parity helpers, device stats, ordered extents, checksum lookup/generation/verification, fscrypt checksum handling, zoned allocation, RAID stripe tree metadata, device replace, scrub, data relocation roots, and async-thread workers. It is the common lower I/O path for data and metadata callers that submit through `btrfs_submit_bbio()`.

## Risks and test signals
Important risks include incorrect split accounting, first-error propagation races, ordered extent reference leaks, checksum buffer lifetime, async checksum completion ordering, zone append boundary alignment, device-missing/writeability checks, mirrored write tolerance thresholds, RAID56 completion context, and repair reads that accidentally loop back to the failed mirror. Repair writes deliberately bypass normal mirrored submission, so mapping and mirror-number correctness are critical.

Test signals include aligned and deliberately misaligned debug builds, reads with valid and invalid checksums, single-copy read failure, mirrored read repair success/failure, repair write to a bad mirror, RAID1/RAID10 mirrored write partial failures under `max_errors`, RAID56 read/write paths, split bios at chunk boundaries, NODATASUM and remap writes, async checksum enabled/disabled by sync flags and fast checksum flags, fscrypt write checksums, zoned sequential zone append, scrub repair writes with and without device replace, missing/non-writeable devices, cgroup punt submission, and bioset init failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/bio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/bio.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/bio.h

## Purpose
`bio.h` defines the high-level Btrfs bio wrapper and the public I/O submission/repair API implemented by `bio.c`. It extends the Linux `struct bio` with Btrfs inode/offset context, checksum and ordered-extent state, completion aggregation, mirror tracking, scrub/remap/async flags, and parent-check metadata for btree reads.

## Important APIs, types, and functions
- `BTRFS_BIO_INLINE_CSUM_SIZE` is the inline checksum buffer size used for small read checksum arrays.
- `btrfs_bio_end_io_t` is the high-level completion callback type.
- `struct btrfs_bio` embeds `struct bio` as its last member and stores `inode`, `file_offset`, unioned read/write/metadata state, `end_io_work`, caller `end_io` and `private`, `pending_ios`, `mirror_num`, first error `status`, and flags for commit-root checksum search, scrub, remap, async checksum, and zone append.
- The read union stores checksum pointer/inline storage and saved iterator.
- The write union stores an ordered extent, ordered sums, checksum work/completion state, checksum iterator, original physical address, and original logical address.
- The metadata union stores `struct btrfs_tree_parent_check`.
- `btrfs_bio()` converts a Linux `bio *` to its containing `struct btrfs_bio *`.
- `btrfs_bio_init()` and `btrfs_bio_alloc()` initialize or allocate high-level bios.
- `btrfs_bio_end_io()`, `btrfs_submit_bbio()`, `btrfs_submit_repair_write()`, and `btrfs_repair_io_failure()` are the exported completion/submission/repair functions.
- `REQ_BTRFS_CGROUP_PUNT` aliases `REQ_FS_PRIVATE` to mark bios that should be submitted through `blkcg_punt_bio_submit()`.
- `btrfs_bioset_init()` and `btrfs_bioset_exit()` manage module-level allocation pools.

## Control flow
Callers allocate a `struct btrfs_bio` with `btrfs_bio_alloc()` or provide an embedded one that has an already-initialized block `bio`, then call `btrfs_bio_init()` to set Btrfs-owned fields. They fill the embedded `bio` vectors and operation flags, optionally populate operation-specific fields such as `ordered`, `parent_check`, `csum_search_commit_root`, `is_scrub`, or `is_remap`, and submit with `btrfs_submit_bbio()`.

The implementation may split a high-level bio into clone bios. The original `pending_ios` tracks all outstanding pieces, `status` records the first error, and the caller's `end_io` callback fires only once through `btrfs_bio_end_io()`. Repair callers use `btrfs_repair_io_failure()` for synchronous targeted data repair writes or `btrfs_submit_repair_write()` for scrub/dev-replace style metadata repair writes to one mirror.

## State and persistence behavior
The structure is per-I/O runtime state. It does not persist independently, but it carries enough metadata for `bio.c` to update persistent device contents, checksum items via ordered extents, zoned physical addresses, and repair writes. The embedded `bio` must remain last because bioset allocation sizes depend on `offsetof(struct btrfs_bio, bio)`.

Unioned fields are operation-specific and must not be interpreted across paths: data reads use checksum fields, data writes use ordered/checksum fields, and metadata reads use parent-check fields. Flags further specialize behavior for commit-root checksum lookup, scrub, remapped data I/O, async checksum generation, and zone append.

## Dependencies and integration points
The header depends on Linux block I/O types, workqueues, Btrfs tree-checker parent verification, and forward declarations for Btrfs fs/inode types. It is included by Btrfs data, metadata, scrub, repair, checksum, and volume-mapping code that submits logical I/O through the central Btrfs bio path.

## Risks and test signals
Key risks are misuse of the union fields, failing to set `inode` for data I/O that needs checksum/repair, incorrect `file_offset` when splitting or repairing, forgetting to hold ordered extent references, callback assumptions before all split bios finish, and breaking the "embedded bio last" allocation contract. Tests should cover normal allocation/init, stack or embedded initialization, data reads with checksum lookup, metadata reads with parent checks, data writes with ordered extents and async checksums, split completion aggregation, repair submissions, scrub/remap flags, zone append state, and bioset init/exit under fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/bio.h -->
