# subset-b-005620 Research

Grouped source research for Btrfs RAID5/6 parity handling, debug-only reference verification, and reflink/dedupe remap support. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/raid56.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/raid56.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/raid56.c` implements the Btrfs RAID5/RAID6 full-stripe engine. It is responsible for sub-stripe read/modify/write, full-stripe write parity generation, degraded read reconstruction, parity scrub/replace repair, stripe locking, stripe-cache reuse, bio assembly, data checksum-assisted validation, and asynchronous dispatch through the filesystem RMW workqueue. The source was read as a complete 3044-line file.

## Important APIs, Types, and Functions

Public entry points exported through `raid56.h` are `btrfs_alloc_stripe_hash_table()`, `btrfs_free_stripe_hash_table()`, `raid56_parity_write()`, `raid56_parity_recover()`, `raid56_parity_alloc_scrub_rbio()`, `raid56_parity_submit_scrub_rbio()`, and `raid56_parity_cache_data_folios()`. The core internal object is `struct btrfs_raid_bio`, allocated by `alloc_rbio()` from a `btrfs_io_context`; it owns the higher-layer `bio_list`, stripe/parity page arrays, physical-address indexes, uptodate and error bitmaps, checksums, and per-stripe operation metadata.

Important helpers include the stripe hash/cache routines `lock_stripe_add()`, `unlock_stripe()`, `cache_rbio()`, `steal_rbio()`, and `merge_rbio()`; page/index helpers `index_rbio_pages()`, `index_stripe_sectors()`, `sector_paddrs_in_rbio()`, and `rbio_add_io_paddrs()`; parity generation helpers `generate_pq_vertical_step()` and `generate_pq_vertical()`; recovery helpers `set_rbio_range_error()`, `recover_vertical_step()`, `recover_vertical()`, `recover_sectors()`, and `recover_rbio()`; RMW helpers `fill_data_csums()`, `rmw_read_wait_recover()`, `rmw_assemble_write_bios()`, and `rmw_rbio()`; scrub helpers `recover_scrub_rbio()`, `verify_one_parity_sector()`, and `finish_parity_scrub()`.

## Control Flow

The write path starts at `raid56_parity_write()`, which allocates an rbio, tags it as `BTRFS_RBIO_WRITE`, adds the incoming bio to the rbio, and either plugs it for later merging or queues `rmw_rbio_work()`. `rmw_rbio_work()` tries to acquire the per-full-stripe hash lock with `lock_stripe_add()`. The lock owner enters `rmw_rbio()`, allocates parity pages, optionally reads all data/parity sectors for a sub-stripe RMW, verifies/reconstructs sectors using checksums, locks out further merges by setting `RBIO_RMW_LOCKED_BIT`, generates P/Q for every vertical sector, assembles device bios for changed data and parity sectors, waits for write completion, checks tolerance, and completes original bios through `rbio_orig_end_io()`.

The degraded read path starts at `raid56_parity_recover()`. It allocates a `BTRFS_RBIO_READ_REBUILD` rbio, marks the failed range in `error_bitmap`, optionally marks an extra RAID6 failure for retry mirrors above 2, and queues recovery work. `recover_rbio()` reads every non-failed stripe sector into internal pages, then `recover_sectors()` reconstructs each vertical stripe with XOR or RAID6 syndrome recovery and verifies reconstructed data sectors when checksum information exists.

The scrub path creates an rbio with `raid56_parity_alloc_scrub_rbio()`, identifies the parity stripe being scrubbed, copies the caller's data-sector bitmap, and later `raid56_parity_submit_scrub_rbio()` serializes it through the same full-stripe lock. `scrub_rbio()` allocates only essential pages, reads missing sectors, recovers failed data if possible, verifies generated parity against the scrubbed parity stripe, repairs mismatches in memory, and writes back only parity sectors still marked in `dbitmap`.

The stripe-lock control flow is central. `lock_stripe_add()` serializes all operations for a full stripe, merges compatible writes into the active owner or pending plug list, steals cached data pages from idle cached rbios, and hands off incompatible operations through `plug_list`. `unlock_stripe()` caches idle rbios where useful and starts the next pending rbio with the operation-specific locked worker.

## State and Persistence Behavior

Most state is transient kernel memory attached to `struct btrfs_raid_bio`. Higher-layer bios remain in `bio_list`; caller data pages are indexed in `bio_paddrs`; internally allocated data/parity pages are indexed in `stripe_pages` and `stripe_paddrs`; `stripe_uptodate_bitmap` records which sectors are valid; `error_bitmap` records failed or checksum-bad sectors; `dbitmap` records horizontal sectors touched by writes or scrub; `csum_buf` and `csum_bitmap` are temporary checksum lookup results for data stripes.

Longer-lived state is the per-filesystem stripe hash table at `fs_info->stripe_hash_table`. It stores hash buckets for full-stripe serialization and an LRU cache of rbios whose data pages can seed later sub-stripe writes. The on-disk persistence effect is indirect but critical: data and parity writes are submitted to device bios, scrub can repair parity stripes, and degraded writes may duplicate to replace targets through `bioc->replace_nr_stripes`.

Reference counts on rbios cover workqueue ownership, hash ownership, and cache ownership. Completion drains the original bios, releases checksums, unlocks the stripe, may leave a cache reference, and frees the rbio when references reach zero.

## Dependencies and Integration Points

This file depends on Linux block I/O (`bio`, `submit_bio`, `blk_plug_cb`), memory/page helpers, RAID library routines (`raid6_call.gen_syndrome`, `raid6_datap_recov`, `raid6_2data_recov`, `xor_gen`), Btrfs mapping state (`struct btrfs_io_context`, device replace fields, `btrfs_nr_parity_stripes()`), filesystem geometry (`sectorsize`, checksum size), workqueues (`fs_info->rmw_workers`), tracing (`trace_raid56_read/write`), checksum lookup (`btrfs_lookup_csums_bitmap()`), and scrub callers that provide parity scrub rbios and data folios.

It integrates with the normal Btrfs bio mapping layer after the logical range has been mapped to a RAID56 `bioc`. It also integrates with device replacement by emitting additional writes to the replace target stripe, and with the scrub layer by accepting prevalidated data folios to avoid rereading data stripes.

## Risks and Edge Cases

This code is concurrency-sensitive: incorrect hash, plug-list, cache-list, or refcount handling can produce use-after-free, missed completion, or simultaneous RMW on the same stripe. The paddr indexing supports both block-size <= page-size and block-size > page-size cases; off-by-one errors in sector/step math would corrupt parity or recover the wrong data. Recovery correctness depends on accurate `error_bitmap` population from I/O failures, missing devices, checksum mismatches, and RAID6 retry mirror selection.

Sub-stripe RMW is only checksum-safe when data checksums can be loaded; mixed data/metadata block groups are deliberately skipped to avoid deadlock, which means stale data risk is surfaced only as a warning path. Scrub has reduced repair capability because the parity stripe being scrubbed cannot always be trusted to repair data. Device replace paths use stripe indexes beyond `real_stripes`, so helper assertions distinguish `bioc->num_stripes` from `rbio->real_stripes`. Missing block devices are modeled as stripe errors and can trigger early `-EIO` once tolerance is exceeded.

## Test Signals

Useful signals include RAID5 and RAID6 fstests that exercise full-stripe writes, partial writes, degraded reads, missing devices, checksum mismatch recovery, scrub repair, device replace, and block-size/page-size combinations. Runtime signals are `trace_raid56_read`, `trace_raid56_write`, warnings from `fill_data_csums()`, and assertion dumps from `ASSERT_RBIO*`. Fault injection for bio completion status, ENOMEM during rbio/page allocation, checksum lookup failure, and missing `bdev` paths would cover high-risk branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/raid56.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/raid56.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/raid56.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/raid56.h` declares the Btrfs RAID5/6 parity interface and the shared `struct btrfs_raid_bio` layout used by `raid56.c` and scrub callers. It documents how a full stripe is represented across higher-layer bios, internally allocated pages, sector indexes, parity stripes, and page-size/block-size steps. The source was read as a complete 291-line file.

## Important APIs, Types, and Functions

The file defines `enum btrfs_rbio_ops` with `BTRFS_RBIO_WRITE`, `BTRFS_RBIO_READ_REBUILD`, and `BTRFS_RBIO_PARITY_SCRUB`. `struct btrfs_raid_bio` is the main state container: it holds the `btrfs_io_context`, hash/cache/workqueue links, bio list and lock, plug list, operation flags, stripe geometry (`nr_data`, `real_stripes`, `stripe_nsectors`, `sector_nsteps`), scrub parity index, refcount, pending I/O counter, data/error/uptodate/checksum bitmaps, and page/paddr arrays. `struct raid56_bio_trace_info` carries devid, offset, and stripe number for tracepoints.

Inline helpers `nr_data_stripes()` and `nr_bioc_data_stripes()` subtract parity stripes from a chunk map or IO context. `RAID5_P_STRIPE`, `RAID6_Q_STRIPE`, and `is_parity_stripe()` encode special parity markers. Public prototypes expose parity write, read recovery, scrub allocation/submission, scrub data caching, and stripe hash table allocation/free.

## Control Flow

This header has no executable control flow beyond trivial inline helpers. Its declarations define the entry points used by Btrfs bio mapping, scrub, mount initialization, and unmount cleanup to enter the implementation in `raid56.c`.

## State and Persistence Behavior

The header defines transient in-memory state rather than persistent on-disk structures. `struct btrfs_raid_bio` instances exist for one full-stripe operation and may be cached in memory after completion for future RMW optimization. No on-disk format fields are declared here, but the structure controls writes that update persistent data/parity sectors.

## Dependencies and Integration Points

Direct dependencies are Linux list/spinlock/bio/refcount/workqueue types and Btrfs `volumes.h` for chunk map and IO context definitions. Public functions integrate with the Btrfs volume mapping layer, async RMW workqueue setup, device scrub/replace code, and tracepoints that consume `raid56_bio_trace_info`.

## Risks and Edge Cases

The layout is shared with implementation code and scrub users, so field semantics are tightly coupled to locking and lifetime rules. The paddr model must distinguish invalid sectors from real physical addresses; geometry fields are small integer types and rely on RAID56 stripe limits. Public scrub helpers assume callers provide a mapped `bioc`, correct `dbitmap`, and stable data folios when using the cache-data optimization.

## Test Signals

Compile coverage should catch include-order and prototype drift. Functional signals come from the same RAID56 tests as `raid56.c`, especially scrub callers that allocate rbios and cache data folios. Tracepoint tests or build checks should verify `struct raid56_bio_trace_info` consumers remain compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/raid56.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/ref-verify.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/ref-verify.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/ref-verify.c` implements the debug-only Btrfs reference verification cache behind the `REF_VERIFY` mount option. It builds an in-memory shadow model of extent-tree references at mount time, then updates that model on delayed reference modifications to detect incorrect reference accounting, invalid drops/adds, stale reallocations, overlapping freed ranges, and extent-tree inconsistencies. The source was read as a complete 1025-line file.

## Important APIs, Types, and Functions

The public functions are `btrfs_build_ref_tree()`, `btrfs_ref_tree_mod()`, `btrfs_free_ref_cache()`, and `btrfs_free_ref_tree_range()`. Internal state is modeled with `struct block_entry` for each referenced bytenr, `struct ref_entry` for individual tree/data/shared refs, `struct root_entry` for per-root direct ref counts, and `struct ref_action` for historical modifications plus optional stack traces.

Core helpers include rb-tree comparators and insert/lookups for block, root, and ref entries; `add_tree_block()`, `add_shared_data_ref()`, and `add_extent_data_ref()` for loading on-disk refs; `process_extent_item()`, `process_leaf()`, `walk_down_tree()`, and `walk_up_tree()` for extent-tree traversal; `dump_ref_action()` and `dump_block_entry()` for diagnostic logging; and `free_block_entry()` for full cache teardown.

## Control Flow

At mount or enable time, `btrfs_build_ref_tree()` checks `REF_VERIFY`, obtains the extent root, read-locks the root node, and walks the extent tree manually. Leaf processing reads extent items, metadata items, inline refs, and separate ref key items, then inserts equivalent shadow records into `fs_info->block_tree`. The walker tracks the last extent bytenr/length/tree-block level so separate ref items can be associated with the correct extent item.

During normal delayed-ref processing, `btrfs_ref_tree_mod()` receives a `struct btrfs_ref`, converts it into a normalized `ref_entry`, records a `ref_action` with stack trace and action metadata, and updates the matching `block_entry` under `fs_info->ref_verify_lock`. Add-extent actions preallocate or reset the block entry and verify that reallocation is not happening while references remain. Add/drop ref actions update `ref_entry`, `root_entry`, and total block ref counts, with metadata refs restricted from duplicate adds. On any verification failure it dumps diagnostics, frees the ref cache, and clears `REF_VERIFY`.

Freeing paths include `btrfs_free_ref_cache()`, which drains the whole rb-tree, and `btrfs_free_ref_tree_range()`, which removes cached entries for a block group range while warning about overlapping cached extents.

## State and Persistence Behavior

All verifier state is in memory under `fs_info->block_tree` and protected by `fs_info->ref_verify_lock`. It mirrors persistent extent-tree reference records but does not write disk state. `block_entry` objects are intentionally retained with historical actions until unmount or range removal so reallocations can be checked against prior history. Stack traces are stored only when `CONFIG_STACKTRACE` is enabled.

If the verifier detects an inconsistency or cannot continue safely, it tears down the in-memory cache and disables the mount option. This makes the verifier fail closed with respect to debug checking while leaving the live filesystem path to continue without ref verification.

## Dependencies and Integration Points

The file depends on Btrfs extent-tree accessors, delayed-ref structures, root locking and extent buffer APIs, rb-tree helpers, spinlocks, mount options, stacktrace support, and logging. It is compiled only through the debug interface declared in `ref-verify.h`; non-debug builds use inline no-op stubs. Runtime integration occurs wherever delayed refs call `btrfs_ref_tree_mod()`, mount setup calls `btrfs_build_ref_tree()`, block-group cleanup calls `btrfs_free_ref_tree_range()`, and unmount/disable calls `btrfs_free_ref_cache()`.

## Risks and Edge Cases

The shadow model must exactly match the extent-tree representation. Inline refs and separate ref key items are easy to misassociate if `bytenr`, `num_bytes`, or tree-block level tracking is stale. Metadata and data refs have different uniqueness rules, and shared refs use parent-based identity rather than direct root identity. The code performs memory allocation before or around spinlock-protected updates; error paths must free partially built objects and unlock correctly.

Because failures disable `REF_VERIFY`, a false positive can remove useful debug coverage for the rest of the mount. Range freeing has special overlap diagnostics and must tolerate empty block groups. Manual tree walking must balance read locks and extent-buffer refs while allowing rescheduling during large cache frees.

## Test Signals

Test signals include debug-kernel mounts with `ref_verify`, fstests that stress snapshot create/delete, reflink, extent sharing, relocation, block-group removal, and delayed-ref churn, plus injected duplicate refs, invalid drops, and reallocation-with-live-ref scenarios. Logging from `dump_block_entry()` and `dump_ref_action()` is the main diagnostic output; stack traces are an additional signal when `CONFIG_STACKTRACE` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/ref-verify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/ref-verify.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/ref-verify.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/ref-verify.h` exposes the Btrfs reference verifier interface and compiles it away outside `CONFIG_BTRFS_DEBUG`. The source was read as a complete 58-line file.

## Important APIs, Types, and Functions

When `CONFIG_BTRFS_DEBUG` is enabled, the header declares `btrfs_build_ref_tree()`, `btrfs_free_ref_cache()`, `btrfs_ref_tree_mod()`, and `btrfs_free_ref_tree_range()`. It also defines `btrfs_init_ref_verify()`, which initializes `fs_info->ref_verify_lock` and `fs_info->block_tree`. When debug support is disabled, all functions are static inline no-ops or zero-return stubs.

## Control Flow

The header controls build-time dispatch. Debug builds call the real verifier in `ref-verify.c`; non-debug builds preserve call sites without runtime cost or state changes.

## State and Persistence Behavior

In debug builds, initialization prepares in-memory verifier state inside `struct btrfs_fs_info`. In non-debug builds, no verifier state is initialized. No persistent filesystem data is defined or modified by this header.

## Dependencies and Integration Points

The header depends on Linux integer and rb-tree type declarations, and on spinlock declarations only for debug builds. It is included by Btrfs mount/setup and delayed-ref code that should remain source-compatible whether the verifier is compiled in or not.

## Risks and Edge Cases

The main risk is semantic drift between real debug functions and no-op stubs. Callers must not rely on side effects from verifier functions in production builds. Debug initialization must run before any verifier mutation path uses `fs_info->ref_verify_lock` or `fs_info->block_tree`.

## Test Signals

Compile both `CONFIG_BTRFS_DEBUG=y` and non-debug configurations. Debug boot/mount smoke tests should confirm `btrfs_init_ref_verify()` precedes `btrfs_build_ref_tree()` and delayed-ref modification calls; non-debug builds should verify call sites compile and optimize to stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/ref-verify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/reflink.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/reflink.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/reflink.c` implements Btrfs support for VFS `remap_file_range`: clone/reflink and dedupe. It validates remap requests, locks inodes and mmap/range state, flushes ordered extents, clones file extent items or inline data, handles holes and EOF extension, updates inode metadata and fsync state, invalidates stale page cache, and performs synchronous writes when requested. The source was read as a complete 975-line file.

## Important APIs, Types, and Functions

The public API is `btrfs_remap_file_range()`. Internal helpers include `btrfs_remap_file_range_prep()` for Btrfs-specific validation and writeback ordering; `btrfs_clone_files()` for non-dedupe reflink; `btrfs_extent_same()` and `btrfs_extent_same_range()` for dedupe; `btrfs_clone()` for walking source file extents and replacing destination extents; `clone_copy_inline_extent()` and `copy_inline_to_page()` for inline extent handling; `clone_finish_inode_update()` for i_version, timestamps, size, and inode item update; `btrfs_double_mmap_lock()` and unlock counterpart for ordered mmap locking; and `file_sync_write()` for sync semantics.

## Control Flow

`btrfs_remap_file_range()` rejects shutdown and unsupported flags, locks one or both inodes plus mmap locks, calls `btrfs_remap_file_range_prep()`, then dispatches to dedupe or clone. Preparation checks readonly destination rules, encryption compatibility, NODATASUM compatibility, flushes source NOCOW buffered writes, waits for ordered extents on source and destination aligned ranges, and then delegates generic VFS validation.

For clone, `btrfs_clone_files()` expands destination holes if `destoff` is past EOF, waits for writeback around a possibly truncated EOF block, locks the destination extent range, and calls `btrfs_clone()`. `btrfs_clone()` walks source extent items from `off` to `off + aligned_len`, handles overlap with the first extent, skips extents already processed due to races with ordered completion, maps source offsets to destination offsets, drops implicit destination holes, and either calls `btrfs_replace_file_extents()` for regular/prealloc extents or `clone_copy_inline_extent()` for inline extents. After each replacement it updates `last_reflink_trans` as needed for fsync correctness, finishes inode updates in a transaction, and reschedules between iterations. At the end it punches/replaces trailing implicit holes if the clone range extends beyond the last found extent.

Inline extents are special. If they cannot be represented as a destination inline extent, `copy_inline_to_page()` reserves delalloc, creates and dirties a folio, decompresses inline data when required, zero-fills the rest of the sector, and marks the inode as temporarily not flushable for delalloc to avoid deadlocks. `clone_copy_inline_extent()` chooses between inserting an inline item at offset zero and copying into page cache, then opens a transaction only after releasing tree paths and performing reservations that could flush.

For dedupe, `btrfs_extent_same()` increments a destination root `dedupe_in_progress` counter unless send is active, chunks the request into at most `BTRFS_MAX_DEDUPE_LEN` ranges, and calls `btrfs_extent_same_range()` for each. The range helper locks the destination extent range and calls `btrfs_clone()` with `no_time_update=true`.

## State and Persistence Behavior

Persistent effects are changes to destination file extent items, inode size, inode timestamps for clone, inode version, inode bytes, and fsync tracking state. Shared extents increase reference counts via `btrfs_replace_file_extents()` rather than copying data. Inline-data fallbacks may create delalloc dirty folios that are later flushed into regular extents. The code updates `last_reflink_trans` for source and destination to force correct checksum logging during fsync when extent items share subranges of physical extents.

Transient state includes tree paths, extent locks, mmap locks, transaction handles, delalloc reservations, temporary node-sized buffers, cached extent state, and root `dedupe_in_progress` counters. `BTRFS_INODE_NO_DELALLOC_FLUSH` is set around inline-copy paths to avoid a deadlock and cleared on exit from `btrfs_clone()`.

## Dependencies and Integration Points

The file depends on VFS remap helpers and inode locking, fscrypt/encryption state, Btrfs transaction handling, extent and file item manipulation, delalloc reservation/accounting, ordered extent waiting, compression/decompression, page cache invalidation, inode update routines, send/dedupe coordination, root readonly checks, and sync-file handling. It is the implementation behind the prototype in `reflink.h` and is called from Btrfs file operations.

## Risks and Edge Cases

Deadlock avoidance is a major concern: paths release B-tree paths before starting transactions or doing reservations, flush ordered extents before cloning, lock mmap state in a stable order, and temporarily suppress delalloc flushing for inline copies. Inline extents have strict offset and size assumptions; compressed inline data must decompress into the correct folio range and zero-fill the rest of the sector. Hole handling must account for NO_HOLES files and implicit holes at the beginning or end of ranges.

Correctness also depends on alignment. The code rounds clone lengths to sectors at EOF but preserves the user's original length for final i_size updates. Dedupe is chunked to 16 MiB to limit work per range. It rejects encryption mismatches and NODATASUM mismatches to avoid incompatible sharing. Send in progress prevents dedupe into a root. After clone, page cache invalidation can fail if dirty folios remain, so the code waits for ordered ranges before invalidation.

## Test Signals

Relevant fstests include clone and dedupe across holes, inline extents, compressed inline extents, EOF-unaligned files, same-inode remaps, readonly roots, encrypted files, NODATASUM mismatches, send-in-progress roots, sync-file semantics, and concurrent mmap/read/write workloads. Signals include transaction aborts, `-EAGAIN` during send, `-EINVAL` validation failures, page-cache invalidation failures, fsync correctness after shared extents, and lockdep coverage for inode/mmap/extent lock ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/reflink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/reflink.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/reflink.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/reflink.h` declares the Btrfs file-range remap entry point implemented by `reflink.c`. The source was read as a complete 14-line file.

## Important APIs, Types, and Functions

The only public declaration is `loff_t btrfs_remap_file_range(struct file *file_in, loff_t pos_in, struct file *file_out, loff_t pos_out, loff_t len, unsigned int remap_flags);`. It forwards `struct file` and includes Linux integer/types support.

## Control Flow

There is no runtime control flow in the header. It connects Btrfs file operation tables or call sites to the implementation that handles clone and dedupe.

## State and Persistence Behavior

The header owns no state. Persistent behavior is entirely in `reflink.c`, where destination extent items and inode metadata are updated.

## Dependencies and Integration Points

The header depends only on `<linux/types.h>` and a forward declaration of `struct file`. It is included by Btrfs file-operation code that exposes VFS remap support.

## Risks and Edge Cases

The signature must match the VFS remap-file-range expectations and the implementation. Callers must pass file objects from the same Btrfs filesystem after VFS-level checks, and must interpret a non-negative return as the number of bytes remapped.

## Test Signals

Compile coverage catches prototype drift. Functional signals are the reflink and dedupe tests that call the public entry point through VFS operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/reflink.h -->
