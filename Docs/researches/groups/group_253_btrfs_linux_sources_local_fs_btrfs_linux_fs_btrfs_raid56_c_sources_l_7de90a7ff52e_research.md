# Group Research: group_253_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_raid56_c_sources_l_7de90a7ff52e

Scope: subset A from `Docs/research_subset_a.md`, covering the listed Btrfs RAID56, reference-verification, and reflink files under `sources/local-fs/btrfs-linux/fs/btrfs/`.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/raid56.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/raid56.c

This file implements Btrfs RAID5/RAID6 parity I/O: write read-modify-write, failed-read reconstruction, parity scrub/repair, device-replace duplication, stripe locking, stripe caching, and rbio lifecycle. Its main exported entry points are `raid56_parity_write()`, `raid56_parity_recover()`, `raid56_parity_alloc_scrub_rbio()`, `raid56_parity_submit_scrub_rbio()`, `raid56_parity_cache_data_folios()`, `btrfs_alloc_stripe_hash_table()`, and `btrfs_free_stripe_hash_table()`.

Core private state:
- `struct btrfs_stripe_hash_table` owns the stripe hash buckets, LRU cache list, cache lock, and cache size.
- `struct btrfs_stripe_hash` is one hash bucket with a stripe list and lock.
- `struct btrfs_raid_bio` comes from `raid56.h` and represents one full RAID56 stripe, including all data and P/Q stripes.
- Per-rbio arrays map logical sectors to physical addresses: `bio_paddrs` for caller bios and `stripe_paddrs`/`stripe_pages` for internally allocated read/parity/recovery pages.
- Bitmaps track partial-write data columns (`dbitmap`), sector errors (`error_bitmap`), valid internal stripe sectors (`stripe_uptodate_bitmap`), temporary parity scrub sectors (`finish_pbitmap`), and optional data checksum coverage (`csum_bitmap`).

Stripe locking and caching:
- `btrfs_alloc_stripe_hash_table()` allocates a hash table of `1 << BTRFS_STRIPE_HASH_TABLE_BITS` buckets and initializes the LRU cache.
- `lock_stripe_add()` serializes all rbios for the same full-stripe logical address. It either gives the caller ownership, merges compatible rbios, queues an rbio on the current owner’s plug list, or steals cached data pages from an idle cached rbio.
- `unlock_stripe()` releases ownership, optionally keeps a cache-only rbio in the hash, or hands the stripe to the next pending rbio and schedules its operation-specific worker.
- `cache_rbio_pages()`, `cache_rbio()`, `steal_rbio()`, `remove_rbio_from_cache()`, and `btrfs_clear_rbio_cache()` implement a small LRU cache of full-stripe data sectors. Cached rbios are used to avoid rereading data sectors for later partial writes.
- `RBIO_RMW_LOCKED_BIT` prevents late merge once final RMW assembly starts; `RBIO_CACHE_BIT` marks cache ownership; `RBIO_CACHE_READY_BIT` says cached `stripe_pages` can be trusted.

Rbio allocation and indexing:
- `alloc_rbio()` derives geometry from `btrfs_io_context`: real stripes exclude replace target stripes, `nr_data` excludes parity stripes, stripe length is fixed at `BTRFS_STRIPE_LEN`, and sectors can have multiple steps when filesystem block size exceeds page size.
- `alloc_rbio_pages()`, `alloc_rbio_data_pages()`, `alloc_rbio_parity_pages()`, `alloc_rbio_sector_pages()`, and `alloc_rbio_essential_pages()` allocate only the page ranges needed by each path.
- `index_rbio_pages()` indexes higher-layer bio segments into `bio_paddrs`; `index_stripe_sectors()` indexes internally allocated pages into `stripe_paddrs`.
- Helpers such as `rbio_sector_index()`, `rbio_paddr_index()`, `sector_paddrs_in_rbio()`, and `sector_paddr_in_rbio()` centralize stripe/sector/step address lookup.

Write path:
- `raid56_parity_write()` wraps a higher-layer write bio in a `BTRFS_RBIO_WRITE` rbio, marks covered data columns in `dbitmap`, and either plugs partial writes or immediately schedules RMW work.
- `raid_unplug()` sorts plugged rbios by logical sector and merges compatible partial writes before dispatching them to `rmw_rbio_work()`.
- `rmw_rbio()` allocates parity pages, reads missing data sectors for sub-stripe writes when the cache is insufficient, verifies checksummed data during the read phase, reconstructs bad sectors when possible, marks the rbio RMW-locked, generates P/Q for every vertical stripe, assembles write bios, submits them, waits for completion, and completes original bios.
- Full-stripe writes skip reading data sectors and generally do not populate the stripe cache; partial writes can cache the resulting full data stripe.
- `rmw_assemble_write_bios()` writes updated caller data sectors plus generated parity sectors. During device replace it duplicates the source stripe to the replace target stripe.

Failed-read recovery:
- `raid56_parity_recover()` handles failed normal reads from `bio.c`. It wraps the failed bio as `BTRFS_RBIO_READ_REBUILD`, records the failed sector range, optionally marks an extra failed stripe for RAID6 mirror retries, and schedules `recover_rbio_work()`.
- `recover_rbio()` allocates the full stripe, rereads all nonfailed sectors without trusting cache contents, then calls `recover_sectors()`.
- `recover_vertical_step()` performs RAID5 XOR recovery, RAID6 single-failure recovery, or RAID6 two-data/data+parity recovery with `raid6_datap_recov()` / `raid6_2data_recov()`.
- `recover_vertical()` checks the vertical stripe’s error count against `bioc->max_errors`, reconstructs failed sectors, verifies recovered data checksums when available, and marks recovered sectors uptodate.
- `set_rbio_raid6_extra_error()` implements retry behavior for RAID6 mirror numbers greater than 2 by selecting another stripe to treat as failed.

Checksum handling:
- `fill_data_csums()` loads checksums for the data portion of a full stripe before RMW reads, except for metadata and mixed block groups to avoid recursive RAID56 recovery deadlocks while holding a full-stripe lock.
- `verify_bio_data_sectors()` verifies read sectors against `csum_buf` during RMW reads.
- `verify_one_sector()` verifies a reconstructed data sector before it is accepted.
- If checksum lookup allocation or search fails, the code warns that sub-stripe write safety is degraded and proceeds without checksum verification.

Parity scrub and replace:
- `raid56_parity_alloc_scrub_rbio()` builds a `BTRFS_RBIO_PARITY_SCRUB` rbio around scrub’s completion bio, records which parity stripe is being scrubbed, and copies the caller’s horizontal-sector bitmap.
- `raid56_parity_cache_data_folios()` lets scrub prefill data stripe pages from already verified folios so the parity path can avoid extra reads.
- `raid56_parity_submit_scrub_rbio()` serializes the scrub rbio through the same stripe lock as writes and recovery.
- `scrub_rbio()` allocates only needed sectors, reads missing inputs, recovers tolerable data failures, verifies or repairs parity sectors, writes repaired parity, and waits for write completion.
- `finish_parity_scrub()` compares generated P/Q against the scrubbed parity stripe, clears `dbitmap` bits that already matched, writes only repaired sectors, and duplicates the parity write to the replace target when appropriate.
- `recover_scrub_rbio()` is stricter than ordinary recovery because the parity stripe being scrubbed cannot always be used as a trusted recovery source.

Bio submission and completion:
- `rbio_add_io_paddrs()` builds physical-device bios for one sector and merges adjacent sectors on the same block device when possible. Missing devices set error bits and can fail early if tolerance is exceeded.
- `submit_read_wait_bio_list()` and `submit_write_bios()` install RAID56-specific endio callbacks, emit trace events, submit bios, and synchronize using `stripes_pending` plus `io_wait`.
- `raid_wait_read_end_io()` records I/O errors or marks read pages uptodate and checksum-verifies data sectors.
- `raid_wait_write_end_io()` records write errors.
- `rbio_orig_end_io()` frees checksum state, clears the data bitmap before unlocking, releases stripe ownership/cache references, frees the rbio, and completes all original bios with the final status.

Cross-file relationships:
- `bio.c` calls `raid56_parity_write()` for RAID56 writes and `raid56_parity_recover()` when normal reads need parity reconstruction.
- `scrub.c` allocates, optionally preloads, and submits scrub rbios through the scrub entry points.
- `disk-io.c` initializes and frees the stripe hash table during filesystem mount/unmount lifecycle.
- `volumes.c`, `block-group.c`, and `scrub.c` use RAID56 geometry helpers declared in `raid56.h`, especially `nr_data_stripes()`.
- The implementation depends on `volumes.h` for `btrfs_io_context`, `file-item.h` for checksum lookup/calculation, `async-thread.h` for the RMW worker pool, and the kernel RAID6/XOR libraries for parity math.

Important invariants and risks:
- Only one active rbio may own a full stripe while RMW, read recovery, or scrub repair is in progress; merge and cache decisions depend on `RBIO_RMW_LOCKED_BIT`, `bio_list_lock`, and the stripe hash bucket lock.
- `bio_paddrs` and `stripe_paddrs` must be reindexed after page allocation or page stealing, especially for block-size-greater-than-page-size configurations.
- Partial writes are unsafe without correct pre-write data contents; the code mitigates this with checksum lookup, data-sector reads, cache validation, and recovery before parity generation.
- Missing devices and checksum mismatches share `error_bitmap`; per-vertical-stripe error counts must never exceed `bioc->max_errors`.
- Device replace makes `bioc->num_stripes` larger than `real_stripes`, so write assembly checks target stripe numbers against `bioc->num_stripes`, not only `real_stripes`.
- Metadata or mixed-block-group checksum lookup is deliberately skipped to avoid deadlocking on recursive RAID56 recovery while the stripe lock is held.
- Scrub repair has lower data-recovery capability when the scrubbed parity stripe is one of the failed inputs.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/raid56.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/raid56.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/raid56.h

This header defines the public RAID56 interface and the full in-memory rbio model used by `raid56.c`. It is included by RAID56 callers such as `bio.c`, `scrub.c`, `disk-io.c`, `volumes.c`, `block-group.c`, `extent-tree.c`, and `super.c`.

Public operation type:
- `enum btrfs_rbio_ops` distinguishes normal parity writes (`BTRFS_RBIO_WRITE`), read-time reconstruction (`BTRFS_RBIO_READ_REBUILD`), and parity scrub/repair (`BTRFS_RBIO_PARITY_SCRUB`).

`struct btrfs_raid_bio`:
- Represents one complete RAID5/RAID6 full stripe, including data and P/Q stripes.
- Owns a `btrfs_io_context` reference, hash/cache/plug/work list nodes, the original bio list, and the operation mode.
- Stores full-stripe geometry: number of pages, total sectors, data stripes, real stripes excluding replace targets, pages per stripe, sectors per stripe, and sector steps for block-size/page-size mismatches.
- Tracks original caller bio pages in `bio_paddrs` and internally allocated data/parity/recovery pages in `stripe_pages` plus `stripe_paddrs`.
- Uses `bio_list_bytes` and `dbitmap` to decide whether a write is a full-stripe write or a partial RMW.
- Uses `stripe_uptodate_bitmap` and `error_bitmap` for read/recovery/scrub state.
- Carries `finish_pointers` and `finish_pbitmap` as temporary parity-generation/scrub state.
- Optionally stores `csum_buf` and `csum_bitmap` for data-sector checksum verification during RMW/recovery.

Trace support:
- `struct raid56_bio_trace_info` records device id, offset inside the stripe, and stripe number for RAID56 read/write tracepoints.

Geometry helpers and constants:
- `nr_data_stripes()` computes data stripes for a chunk map by subtracting parity stripes from `map->num_stripes`.
- `nr_bioc_data_stripes()` performs the same calculation for an active `btrfs_io_context`.
- `RAID5_P_STRIPE`, `RAID6_Q_STRIPE`, and `is_parity_stripe()` provide sentinel values used outside this file to identify parity stripes.

Exported functions:
- `raid56_parity_write()` submits a normal RAID56 write.
- `raid56_parity_recover()` reconstructs failed read bios.
- `raid56_parity_alloc_scrub_rbio()`, `raid56_parity_submit_scrub_rbio()`, and `raid56_parity_cache_data_folios()` support scrub and device replace parity repair.
- `btrfs_alloc_stripe_hash_table()` and `btrfs_free_stripe_hash_table()` manage the per-filesystem stripe lock/cache table.

Important invariants:
- The header documents the addressing model used throughout `raid56.c`: stripe number, sector number, step number, and whether the sector comes from higher-layer bios or internal pages.
- `INVALID_PADDR` is private to `raid56.c`, but the header’s comments establish that invalid physical-address entries mean no page is available for a given sector/step.
- The structure is tightly coupled to the fixed `BTRFS_STRIPE_LEN` full-stripe model and to page/sector alignment rules enforced in `alloc_rbio()`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/raid56.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ref-verify.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ref-verify.c

This debug file implements Btrfs reference verification for the `REF_VERIFY` mount option under `CONFIG_BTRFS_DEBUG`. It builds an in-memory model of extent-tree references at mount time, updates that model as delayed refs are modified, and disables reference verification if it detects inconsistency or cannot maintain the model.

Private data model:
- `struct block_entry` represents one referenced block by bytenr/length. It records total refs, metadata/data classification, whether it came from disk, per-root direct ref counts, detailed refs, and a list of historical actions.
- `struct root_entry` tracks how many direct refs one root has for a block.
- `struct ref_entry` describes one expected extent-tree reference by `root_objectid`, `parent`, `owner`, `offset`, and `num_refs`.
- `struct ref_action` records each delayed-ref action applied to a block, including the action, real root, a copy of the ref fields, list node, and optional stack trace.

Tree indexing:
- `fs_info->block_tree` is keyed by block bytenr and protected by `fs_info->ref_verify_lock`.
- Each `block_entry` has a `roots` red-black tree keyed by root objectid and a `refs` red-black tree keyed by the full ref tuple.
- `block_entry_bytenr_*`, `root_entry_root_objectid_*`, `comp_refs()`, and `ref_entry_cmp()` implement the ordering.
- `insert_block_entry()`, `lookup_block_entry()`, `insert_root_entry()`, `lookup_root_entry()`, and `insert_ref_entry()` are the local rb-tree primitives.

Mount-time model construction:
- `btrfs_build_ref_tree()` is called after the extent tree is available. It reads and locks the root node, walks the entire extent tree, and populates `fs_info->block_tree`.
- `walk_down_tree()` descends from the current internal node to leaves with read locks.
- `walk_up_tree()` releases nodes and advances to the next subtree.
- `process_leaf()` iterates leaf items and dispatches extent items, metadata items, tree block refs, shared block refs, extent data refs, and shared data refs.
- `process_extent_item()` parses inline refs inside extent or metadata items, including tree block refs, shared block refs, extent data refs, shared data refs, and simple-quota owner refs.
- `add_tree_block()`, `add_extent_data_ref()`, and `add_shared_data_ref()` add refs found on disk into the in-memory model.

Delayed-ref update verification:
- `btrfs_ref_tree_mod()` is the main update hook. `extent-tree.c` calls it when delayed refs are added or dropped.
- It ignores work unless the `REF_VERIFY` mount option is active.
- It normalizes a `struct btrfs_ref` into a `ref_entry`: metadata refs use tree level as owner, data refs use objectid/offset, and shared refs use `parent`.
- For `BTRFS_ADD_DELAYED_EXTENT`, it creates or finds a block entry, increments total refs, marks metadata when appropriate, and verifies that a newly allocated block does not already have live refs.
- For ordinary add/drop delayed refs, it looks up the existing block, inserts root tracking for direct refs, inserts or updates the detailed ref, rejects dropping nonexistent refs, rejects over-dropping, and rejects adding duplicate tree-block refs.
- It adjusts `block_entry::num_refs` and root-entry counts for `BTRFS_ADD_DELAYED_REF` / `BTRFS_DROP_DELAYED_REF`.
- It appends a `ref_action` history entry on success; on failure it dumps diagnostic state, frees the ref cache, and clears `REF_VERIFY`.

Diagnostics:
- `__save_stack_trace()` and `__print_stack_trace()` capture and print action stack traces when `CONFIG_STACKTRACE` is available.
- `dump_ref_action()` logs one action’s operation, real root, ref root, parent, owner, offset, and ref count.
- `dump_block_entry()` logs all refs, roots, and action history for a block.
- Error messages target conditions such as reallocating a referenced block, dropping a nonexistent ref, finding duplicate on-disk refs, missing root entries, and block entries overlapping a freed range.

Cache cleanup:
- `free_block_entry()` releases roots, refs, actions, and the block entry itself.
- `btrfs_free_ref_cache()` frees the whole model at unmount or after verification failure.
- `btrfs_free_ref_tree_range()` removes all block entries contained in a freed block-group range and logs entries that overlap the range boundaries.

Cross-file relationships:
- `disk-io.c` initializes the verifier lock/tree with `btrfs_init_ref_verify()`, builds the ref tree during mount, and frees it during cleanup.
- `extent-tree.c` calls `btrfs_ref_tree_mod()` from delayed-ref and extent-allocation/freeing paths.
- `block-group.c` calls `btrfs_free_ref_tree_range()` when a block group range is removed.
- `super.c` parses and reports the `REF_VERIFY` mount option.
- `ref-verify.h` compiles these hooks to no-ops outside `CONFIG_BTRFS_DEBUG`.

Important invariants and risks:
- `add_block_entry()` returns with `fs_info->ref_verify_lock` held on success or existing-entry return; callers are responsible for unlocking in those flows.
- The model intentionally persists block action history until unmount, except when a block is successfully reallocated with zero live refs and old actions are discarded.
- Direct refs update both detailed refs and root-entry counts; shared refs do not have a root entry.
- `metadata = owner < BTRFS_FIRST_FREE_OBJECTID` drives duplicate-ref rules, so correct owner normalization is essential.
- The extent-tree walker carries the last `bytenr`, `num_bytes`, and `tree_block_level` across items because separate ref-key items can follow an extent item on later leaves.
- Any verification error disables `REF_VERIFY` rather than continuing with a suspect model.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ref-verify.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ref-verify.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/ref-verify.h

This header declares the Btrfs reference-verification hooks and hides them behind `CONFIG_BTRFS_DEBUG`.

Debug build interface:
- Includes `spinlock.h` because `btrfs_init_ref_verify()` initializes `fs_info->ref_verify_lock`.
- Declares `btrfs_build_ref_tree()` for mount-time extent-tree scanning.
- Declares `btrfs_free_ref_cache()` for unmount/failure cleanup.
- Declares `btrfs_ref_tree_mod()` for delayed-ref add/drop verification.
- Declares `btrfs_free_ref_tree_range()` for removing verifier state over a block-group range.
- `btrfs_init_ref_verify()` initializes the verifier spinlock and sets `fs_info->block_tree = RB_ROOT`.

Non-debug build behavior:
- All hooks are static inline no-ops or return 0.
- This lets common mount, unmount, block-group, and extent-tree code call verifier functions unconditionally without scattering `#ifdef CONFIG_BTRFS_DEBUG`.

Cross-file relationships:
- `disk-io.c` calls init/build/free lifecycle hooks.
- `extent-tree.c` calls `btrfs_ref_tree_mod()`.
- `block-group.c` calls `btrfs_free_ref_tree_range()`.
- `super.c` manages the runtime `REF_VERIFY` option, but the header determines whether the implementation exists.

Important invariants:
- `struct btrfs_fs_info` and `struct btrfs_ref` are forward-declared so this header does not pull in the full extent-tree internals.
- The runtime `REF_VERIFY` mount option only has operational effect when `CONFIG_BTRFS_DEBUG` is enabled.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/ref-verify.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/reflink.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/reflink.c

This file implements Btrfs `remap_file_range`, covering clone/reflink and dedupe operations. It validates VFS remap requests, locks source and destination inodes/ranges, flushes ordered extents so file extent items are stable, clones regular/prealloc extents by reference, handles inline extents, replaces holes, updates inode metadata, and performs sync handling for synchronous files.

Public entry point:
- `btrfs_remap_file_range()` is exported through `reflink.h` and installed in `file.c` as `.remap_file_range`.
- It supports `REMAP_FILE_DEDUP` and `REMAP_FILE_ADVISORY`; any other remap flags return `-EINVAL`.
- It rejects shutdown filesystems, locks one inode for same-file remaps or both non-directory inodes for cross-file remaps, and takes the involved Btrfs mmap locks in a stable order.

Request preparation:
- `btrfs_remap_file_range_prep()` enforces Btrfs-specific constraints before delegating to `generic_remap_file_range_prep()`.
- Non-dedupe clone checks the destination root is writable.
- Source and destination must either both be encrypted or both unencrypted.
- Source and destination must match `BTRFS_INODE_NODATASUM`; the destination must not become partly checksummed.
- The function explicitly flushes source mapping writeback and waits for ordered extents in source and destination ranges, because Btrfs needs compression writeback and ordered extent completion, not just bio completion.
- It flushes the whole source inode mapping first so buffered NOCOW writes reach disk as NOCOW before extent refs are increased.

Clone implementation:
- `btrfs_clone_files()` adjusts EOF-block length to sector alignment, expands the destination with `btrfs_cont_expand()` when cloning beyond EOF, waits for writeback over the old EOF area, locks the destination extent range, calls `btrfs_clone()`, waits for any inline-data delalloc completion, invalidates destination page cache, and balances dirty btrees.
- `btrfs_clone()` walks source file extent items from `off` through the aligned clone length. It handles previous extents that overlap the start, implicit holes with `NO_HOLES`, regular/prealloc extents, inline extents, and trailing implicit holes.
- Regular and prealloc extents are cloned via `btrfs_replace_file_extents()` with `struct btrfs_replace_extent_info`, after trimming leading/trailing portions outside the requested source range.
- Holes are cloned by calling `btrfs_replace_file_extents()` with a `NULL` clone info over the destination hole range.
- After each cloned extent or hole, `clone_finish_inode_update()` updates i_version, times unless suppressed, i_size, safe disk i_size, inode item, and ends the transaction.

Inline extent handling:
- `clone_copy_inline_extent()` tries to clone an inline extent item directly only when the destination offset is 0 and the destination file shape allows replacing/inserting an inline item.
- If inline direct insertion is unsafe or impossible, it falls back to `copy_inline_to_page()`.
- `copy_inline_to_page()` reserves delalloc space, gets/creates the destination folio, sets extent mapping and delalloc state, sets `BTRFS_INODE_NO_DELALLOC_FLUSH` to avoid transaction/delalloc deadlocks, copies or decompresses inline data, zero-fills the rest of the sector when the inline data is short, marks the folio uptodate/dirty, and releases reservations on error.
- The code may increase destination `i_size` before starting a transaction after copying inline data beyond EOF to avoid a flush-on-commit deadlock involving folio invalidation and extent locks.

Dedupe implementation:
- `btrfs_extent_same()` wraps dedupe with `root_dst->dedupe_in_progress` and rejects dedupe into a root with send in progress.
- It chunks dedupe work into `BTRFS_MAX_DEDUPE_LEN` (16 MiB) segments.
- `btrfs_extent_same_range()` locks the destination extent range, calls `btrfs_clone()` with `no_time_update = true`, unlocks, and balances dirty btrees.
- Data equality checking and generic dedupe range validation are delegated to VFS `generic_remap_file_range_prep()` after Btrfs-specific flushing and constraints.

Locking and synchronization:
- `btrfs_double_mmap_lock()` and `btrfs_double_mmap_unlock()` acquire two Btrfs mmap locks in pointer order with nested locking annotations.
- Destination extent locks serialize with readahead and protect the range while file extent items are replaced.
- Source mmap locks protect against relocation interactions described in comments.
- `BTRFS_INODE_NO_DELALLOC_FLUSH` is set only around inline-to-page clone work and cleared on every `btrfs_clone()` exit.
- Synchronous source or destination files trigger `btrfs_sync_file()` on both source and destination ranges after successful remap so reflinked data is durable after power loss.

Fsync and metadata correctness:
- `btrfs_clone()` updates `last_reflink_trans` on the destination for every cloned extent/hole/inline operation.
- It updates the source inode’s `last_reflink_trans` when a newly generated, non-hole, non-inline extent is shared, preventing fsync checksum logging overlap problems.
- Replacing inline extents and some hole cases set full-sync state with `btrfs_set_inode_full_sync()`.
- `clone_finish_inode_update()` rounds the final inode size to the user-requested clone length rather than the internally aligned clone length.

Cross-file relationships:
- `file.c` exposes this implementation through `btrfs_file_operations.remap_file_range`.
- `inode.c` provides `btrfs_cont_expand()`, inode update helpers, inode locking helpers, ordered extent waiting, file extent range tracking, and inode byte accounting used here.
- `file-item.c` / `accessors.h` provide file extent item accessors and checksum-sensitive metadata helpers.
- `delalloc-space.c`, `extent-io-tree.c`, `subpage.h`, and compression code support inline-to-page fallback.
- `transaction.c` and extent replacement/drop helpers provide the transactional file extent changes.

Important invariants and risks:
- All clone/dedupe ranges are sector-aligned except permitted EOF behavior handled by VFS prep and internal alignment.
- Reflink must not mix encryption state or checksum policy between source and destination.
- Ordered extent completion must finish before cloning refs, otherwise the file extent items and checksums being shared may not exist or may still change.
- Inline extents have special constraints: they start at offset 0, fit within the sectorsize, and cannot be partially cloned.
- Destination page cache is invalidated after clone so reads see the new shared extents rather than stale cached data.
- Send and dedupe are coordinated with `dedupe_in_progress` / `send_in_progress` to avoid changing a root while send is using it.
- The code intentionally releases btree paths before starting transactions or reserving delalloc space to avoid lockdep problems and real deadlocks.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/reflink.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/reflink.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/reflink.h

This small header declares the Btrfs remap/reflink VFS entry point.

Interface:
- Forward-declares `struct file`.
- Declares `loff_t btrfs_remap_file_range(struct file *file_in, loff_t pos_in, struct file *file_out, loff_t pos_out, loff_t len, unsigned int remap_flags);`.

Cross-file relationships:
- `reflink.c` implements the function.
- `file.c` includes this header and assigns the function to `btrfs_file_operations.remap_file_range`.

Important invariants:
- The header keeps reflink internals private; callers only see the VFS-compatible remap signature.
- All validation, locking, clone/dedupe behavior, and sync semantics live in `reflink.c`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/reflink.h -->