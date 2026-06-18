# Group Research: group_649_kdave_linux_sources_local_fs_kdave_linux_fs_btrfs_raid56_c_sources_l_4ea08bd4a1ed

Scope checked: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/raid56.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/raid56.c

## Purpose

`raid56.c` implements Btrfs RAID5/RAID6 full-stripe handling: parity writes, read recovery, read-modify-write, stripe locking/merging, stripe cache reuse, scrub parity verification/repair, and device-replace duplication for RAID56 stripes.

The core unit is `struct btrfs_raid_bio` from `raid56.h`, which represents one full RAID56 stripe: data stripes plus P/Q parity stripes.

## Main Responsibilities

- Allocate and free RAID56 stripe state.
- Convert logical stripe sectors into page/physical-address arrays used for block IO.
- Merge partial writes into larger/full stripe writes when possible.
- Serialize access to a full stripe with a per-filesystem stripe hash table.
- Cache recently read/reconstructed data stripe pages to avoid repeated disk reads.
- Generate RAID5 P parity or RAID6 P/Q syndrome data.
- Recover failed data/parity sectors from remaining stripes.
- Verify data checksums during RMW reads when available.
- Scrub parity stripes and repair parity mismatches.
- Duplicate writes to a device-replace target when RAID56 replace is active.

## Key Data Structures

- `struct btrfs_stripe_hash`: one hash bucket, with `hash_list` and lock.
- `struct btrfs_stripe_hash_table`: owns the hash table plus an LRU `stripe_cache`.
- `struct btrfs_raid_bio`: full-stripe operation state, including bio list, stripe pages, physical-address arrays, error bitmap, uptodate bitmap, checksum buffers, work item, and stripe/cache lists.

Important internal flags:

- `RBIO_RMW_LOCKED_BIT`: no more bios may merge into this rbio.
- `RBIO_CACHE_BIT`: rbio is stored as a stripe cache entry.
- `RBIO_CACHE_READY_BIT`: stripe pages are valid for cache reuse.

## Stripe Hashing, Locking, and Cache

`btrfs_alloc_stripe_hash_table()` allocates the per-filesystem stripe hash table. The code hashes on `bioc->full_stripe_logical` via `rbio_bucket()`.

`lock_stripe_add()` is the central stripe serialization routine. It handles three cases:

- No existing rbio for the full stripe: insert this rbio as lock owner.
- Existing compatible rbio: merge bios with `merge_rbio()`.
- Existing incompatible/running rbio: append to the lock owner’s `plug_list`.

If a cached rbio exists and has no active IO, the new rbio can steal cached data pages with `steal_rbio()`.

`unlock_stripe()` releases ownership and either keeps the rbio in cache, removes it, or hands the stripe lock to the next waiting rbio. Depending on the waiting rbio operation, it schedules recovery, write RMW, or scrub work.

The cache is an LRU bounded by `RBIO_CACHE_SIZE`. `cache_rbio_pages()` copies bio-backed sectors into private stripe pages and marks sectors uptodate; `cache_rbio()` inserts/moves the rbio on the LRU. `remove_rbio_from_cache()` and `btrfs_clear_rbio_cache()` prune cached entries.

## Addressing and Page Indexing

The file supports sector sizes both smaller and larger than `PAGE_SIZE`. It uses:

- `sector_nsteps`: number of page-sized steps needed for one filesystem sector.
- `bio_paddrs[]`: physical addresses from upper-layer bios.
- `stripe_paddrs[]`: physical addresses from rbio-owned stripe pages.
- `stripe_pages[]`: allocated pages for full stripe data/parity.

Important helpers:

- `rbio_sector_index()`
- `rbio_paddr_index()`
- `rbio_stripe_paddr()`
- `rbio_stripe_paddrs()`
- `sector_paddrs_in_rbio()`
- `sector_paddr_in_rbio()`
- `index_rbio_pages()`
- `index_stripe_sectors()`

These helpers abstract whether a sector is sourced from the original bio list or rbio-private pages.

## Write Path

Public entry point: `raid56_parity_write()`.

Flow:

1. Allocate rbio with `alloc_rbio()`.
2. Add the incoming bio with `rbio_add_bio()`, updating `dbitmap`.
3. If the stripe is partial and there is a block plug, queue it for later batching.
4. Otherwise schedule `rmw_rbio_work()`.

Plug handling is done by `struct btrfs_plug_cb` and `raid_unplug()`, which sorts rbios by sector and merges compatible adjacent work before scheduling.

`rmw_rbio()` handles the actual write:

- Allocates parity pages first.
- If partial and missing data, allocates data pages and reads the stripe with `rmw_read_wait_recover()`.
- Locks the rbio against further merging.
- Caches partial-stripe data if suitable.
- Regenerates parity for every vertical sector with `generate_pq_vertical()`.
- Builds write bios with `rmw_assemble_write_bios()`.
- Submits writes and waits for completion.
- Checks if write errors exceeded RAID tolerance.

## Parity Generation

`generate_pq_vertical_step()` maps one sector step from each data stripe plus parity buffers. For RAID6 it calls `raid6_call.gen_syndrome()`. For RAID5 it copies the first data stripe into P and XORs the rest with `xor_gen()`.

`generate_pq_vertical()` repeats that per step and marks P/Q sectors uptodate.

## Read Recovery

Public entry point: `raid56_parity_recover()`.

It is called after normal read failure. It:

1. Allocates an rbio.
2. Adds the failed bio to the bio list.
3. Marks failed sectors in `error_bitmap` with `set_rbio_range_error()`.
4. For RAID6 mirror retries above mirror 2, marks an extra stripe failed with `set_rbio_raid6_extra_error()`.
5. Schedules `recover_rbio_work()`.

`recover_rbio()` reads all non-failed sectors, then `recover_sectors()` reconstructs failed vertical sectors. Recovery uses `recover_vertical()` and `recover_vertical_step()`.

Recovery supports:

- RAID5 single failure via P XOR reconstruction.
- RAID6 single failure via RAID5-style reconstruction when applicable.
- RAID6 two-data failure via `raid6_2data_recov()`.
- RAID6 data+P failure via `raid6_datap_recov()`.

`verify_one_sector()` optionally verifies reconstructed data against checksums.

## Checksum-Aware RMW

`fill_data_csums()` looks up data checksums for a full stripe before partial-stripe RMW reads. It avoids mixed data/metadata groups to prevent deadlocks while the full stripe lock is held.

`verify_bio_data_sectors()` checks read data sectors against the checksum buffer and marks mismatches in `error_bitmap`. This allows RMW to reconstruct corrupted data before parity is regenerated, reducing the risk of writing parity based on bad data.

If checksum lookup fails, the file warns that the sub-stripe write is not safe but continues without checksum protection.

## Scrub and Replace

Scrub entry points:

- `raid56_parity_alloc_scrub_rbio()`
- `raid56_parity_submit_scrub_rbio()`
- `raid56_parity_cache_data_folios()`

Scrub allocates an rbio for parity checking and tracks the parity stripe being scrubbed in `scrubp`.

`scrub_rbio()`:

1. Allocates only pages needed for sectors present in `dbitmap`.
2. Reads missing sectors.
3. Recovers failed sectors if possible with `recover_scrub_rbio()`.
4. Recomputes and verifies parity with `finish_parity_scrub()`.
5. Writes repaired parity sectors.

`finish_parity_scrub()` recomputes expected parity into temporary pages, compares against the scrubbed parity stripe, repairs mismatches in memory, then writes changed parity sectors. If device replace is active and the scrubbed parity stripe is the replace source, it also writes to the replace target.

`raid56_parity_cache_data_folios()` lets scrub preload known-good data folios into rbio-owned pages to avoid extra reads.

## Error Handling and Completion

Read and write bios are submitted through bio lists. Completion handlers update error/uptodate state and wake waiters through `stripes_pending` and `io_wait`.

- `raid_wait_read_end_io()` marks IO errors or sets pages uptodate and verifies checksums.
- `raid_wait_write_end_io()` records write errors.
- `rbio_orig_end_io()` ends upper-layer bios, frees checksum buffers, unlocks the stripe, and frees the rbio reference.

The code uses `error_bitmap` at sector granularity and checks failures per vertical stripe with `get_rbio_vertical_errors()` against `bioc->max_errors`.

## Notable Invariants

- A full stripe is fixed around `BTRFS_STRIPE_LEN`.
- `real_stripes` excludes replace target stripes.
- `nr_data = real_stripes - parity_stripes`.
- Cached rbios must have all data stripe pages present and uptodate.
- Parity pages are regenerated for writes rather than stolen from cache.
- `RBIO_RMW_LOCKED_BIT` prevents late merge after the write/recovery phase becomes immutable.

<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/raid56.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/raid56.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/raid56.h

## Purpose

`raid56.h` declares Btrfs RAID5/RAID6 parity interfaces and defines the core `struct btrfs_raid_bio` state object used by `raid56.c`.

## Main Types

`enum btrfs_rbio_ops` identifies the operation type:

- `BTRFS_RBIO_WRITE`
- `BTRFS_RBIO_READ_REBUILD`
- `BTRFS_RBIO_PARITY_SCRUB`

`struct btrfs_raid_bio` represents one full RAID56 stripe, including data stripes and P/Q parity. The header documents how upper-layer bio pages and rbio-private stripe pages are represented.

Important fields:

- `bioc`: mapped IO context containing stripes/devices.
- `hash_list`: full-stripe lock hash membership.
- `stripe_cache`: LRU cache membership.
- `work`: workqueue item for async processing.
- `bio_list` and `bio_list_lock`: upper-layer bios and merge protection.
- `plug_list`: pending rbios for plugged writes and stripe lock handoff.
- `flags`: merge/cache/lock state bits.
- `operation`: current rbio operation.
- `nr_pages`, `nr_sectors`, `nr_data`, `real_stripes`: stripe geometry.
- `stripe_npages`, `stripe_nsectors`, `sector_nsteps`: page/sector layout.
- `scrubp`: parity stripe being scrubbed.
- `dbitmap`: horizontal sectors that contain data for the current operation.
- `stripe_pages`: rbio-owned pages.
- `bio_paddrs`: physical addresses from upper-layer bios.
- `stripe_paddrs`: physical addresses from `stripe_pages`.
- `stripe_uptodate_bitmap`: sectors in private stripe storage known valid.
- `error_bitmap`: sectors with IO/checksum errors.
- `csum_buf`, `csum_bitmap`: optional checksum verification state.

The header’s long comment is important because it defines the addressing model: sectors are located by `stripe_nr`, `sector_nr`, `step_nr`, and source array (`bio_paddrs` versus `stripe_paddrs`). `step_nr` exists for block-size-greater-than-page-size support.

`struct raid56_bio_trace_info` carries trace metadata for submitted device bios: device id, offset inside stripe, and stripe number.

## Helper Macros and Inline Functions

- `nr_data_stripes()` returns data stripe count from a chunk map.
- `nr_bioc_data_stripes()` returns data stripe count from an IO context.
- `RAID5_P_STRIPE` and `RAID6_Q_STRIPE` encode parity stripe sentinels.
- `is_parity_stripe()` checks those sentinel values.

## Public Interfaces

- `raid56_parity_recover()`: recover a failed read bio.
- `raid56_parity_write()`: submit a RAID56 parity write.
- `raid56_parity_alloc_scrub_rbio()`: allocate scrub rbio.
- `raid56_parity_submit_scrub_rbio()`: submit scrub rbio.
- `raid56_parity_cache_data_folios()`: preload scrub data.
- `btrfs_alloc_stripe_hash_table()`: initialize stripe locking/cache table.
- `btrfs_free_stripe_hash_table()`: free stripe locking/cache table.

## Relationships

This header is consumed by the RAID56 implementation and by Btrfs scrub, volume mapping, and IO paths that need to submit RAID56 writes, recovery, or parity scrub operations.

<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/raid56.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ref-verify.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/ref-verify.c

## Purpose

`ref-verify.c` implements the debug-only Btrfs reference verifier. It builds and maintains an in-memory model of extent references and compares delayed-reference operations against expected reference state. On inconsistency it prints detailed block/ref/action history, disables `REF_VERIFY`, and frees the cache.

This file is compiled only when enabled through `ref-verify.h` under `CONFIG_BTRFS_DEBUG`, and runtime behavior is gated by the `REF_VERIFY` mount option.

## Core Model

The verifier stores block reference state in red-black trees.

`struct block_entry` tracks one referenced extent/block:

- `bytenr`
- `len`
- `num_refs`
- `metadata`
- `from_disk`
- `roots`: root reference counts for direct refs.
- `refs`: expected detailed references.
- `actions`: chronological ref actions with stack traces.
- `node`: rb-tree membership in `fs_info->block_tree`.

`struct ref_entry` models a reference expected in the extent tree:

- `root_objectid`
- `parent`
- `owner`
- `offset`
- `num_refs`

`struct root_entry` tracks direct reference counts per root for a block.

`struct ref_action` records a mutation:

- delayed-ref action type.
- real root that caused it.
- copied reference details.
- stack trace up to `MAX_TRACE`.

## Tree Helpers

The file defines rb-tree comparison/insert/lookup helpers for:

- block entries by `bytenr`.
- root entries by `root_objectid`.
- ref entries by `(root_objectid, parent, owner, offset)`.

`free_block_entry()` releases root entries, ref entries, action history, and the block entry itself.

`add_block_entry()` allocates or finds a block entry and optionally initializes a root entry.

## Building State From Disk

`btrfs_build_ref_tree()` walks the extent tree at mount time when `REF_VERIFY` is enabled. It locks and walks the tree manually using:

- `walk_down_tree()`
- `walk_up_tree()`
- `process_leaf()`
- `process_extent_item()`

It parses extent items and standalone ref items:

- `BTRFS_EXTENT_ITEM_KEY`
- `BTRFS_METADATA_ITEM_KEY`
- `BTRFS_TREE_BLOCK_REF_KEY`
- `BTRFS_SHARED_BLOCK_REF_KEY`
- `BTRFS_EXTENT_DATA_REF_KEY`
- `BTRFS_SHARED_DATA_REF_KEY`
- `BTRFS_EXTENT_OWNER_REF_KEY`

Handlers populate the in-memory model:

- `add_tree_block()` for tree block refs.
- `add_extent_data_ref()` for direct data refs.
- `add_shared_data_ref()` for shared data refs.

For `BTRFS_EXTENT_OWNER_REF_KEY`, the verifier accepts it only when simple quotas are enabled.

If the extent root is unavailable, the verifier warns and disables `REF_VERIFY`.

## Tracking Runtime Ref Modifications

`btrfs_ref_tree_mod()` is the main runtime entry point. It is called when a Btrfs delayed reference is added or dropped.

It converts `struct btrfs_ref` into the verifier’s `ref_entry` key fields:

- metadata refs use tree level as owner.
- non-shared data refs use objectid and file offset.
- parent refs represent shared refs.
- direct refs track roots.

It then records the action and updates the in-memory block/ref/root counters under `fs_info->ref_verify_lock`.

Important checked cases:

- Adding an extent to a block that still has references is reported as reallocation of a live block.
- Modifying a bytenr with no existing entry is an error.
- Dropping a ref from a block with zero total refs is an error.
- Dropping a non-existing detailed ref is an error.
- Adding a duplicate metadata tree-block ref is an error.
- Root reference counts are incremented/decremented for direct refs.

For `BTRFS_ADD_DELAYED_EXTENT`, it creates or reuses the block entry, increments total refs, marks metadata when relevant, and clears stale action history if the allocation is valid.

For `BTRFS_DROP_DELAYED_REF`, it decrements or removes matching `ref_entry` state and decrements block/root counts.

For `BTRFS_ADD_DELAYED_REF`, it increments existing data refs or adds new refs, and increments block/root counts.

On any verifier failure, it calls:

- `btrfs_free_ref_cache()`
- `btrfs_clear_opt(..., REF_VERIFY)`

This prevents cascading verifier noise after the first detected inconsistency.

## Diagnostics

`dump_block_entry()` prints block state, refs, root entries, and action history. `dump_ref_action()` prints action details and a stack trace.

Stack trace support is conditional on `CONFIG_STACKTRACE`:

- enabled: records with `stack_trace_save()` and prints with `stack_trace_print()`.
- disabled: prints a no-stacktrace-support message.

## Cache Freeing and Range Removal

`btrfs_free_ref_cache()` frees the entire verifier cache, but only if `REF_VERIFY` is active.

`btrfs_free_ref_tree_range()` removes cached block entries within a block-group range. It also detects and reports entries that overlap the range boundaries, which indicates inconsistent tracking around block group removal or extent lifetime.

## Concurrency

All verifier tree and counter mutations are protected by `fs_info->ref_verify_lock`. Long frees use `cond_resched_lock()` to avoid monopolizing CPU while holding the spinlock during teardown.

## Dependencies

The file depends on Btrfs extent tree accessors, delayed reference definitions, path/tree locking helpers, and filesystem mount options. It is a diagnostic integrity tool rather than production IO-path functionality.

<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ref-verify.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ref-verify.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/ref-verify.h

## Purpose

`ref-verify.h` declares the debug reference verifier interface and provides no-op stubs when `CONFIG_BTRFS_DEBUG` is disabled.

## Debug Build Interface

When `CONFIG_BTRFS_DEBUG` is enabled, it declares:

- `btrfs_build_ref_tree()`: build verifier cache from the extent tree.
- `btrfs_free_ref_cache()`: free verifier state.
- `btrfs_ref_tree_mod()`: record/check one reference modification.
- `btrfs_free_ref_tree_range()`: remove verifier entries in a byte range.
- `btrfs_init_ref_verify()`: initialize the spinlock and block rb-tree.

`btrfs_init_ref_verify()` initializes:

- `fs_info->ref_verify_lock`
- `fs_info->block_tree = RB_ROOT`

## Non-Debug Build Behavior

When `CONFIG_BTRFS_DEBUG` is disabled, all functions are inline no-ops or return success. This removes verifier overhead from normal builds while allowing call sites to remain unconditional.

## Relationship

This header is the integration boundary between delayed-ref/extent-tree code and the verifier implementation in `ref-verify.c`.

<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/ref-verify.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/reflink.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/reflink.c

## Purpose

`reflink.c` implements Btrfs file range cloning and deduplication through the VFS `remap_file_range` operation. It handles regular extents, prealloc extents, inline extents, implicit holes, inode size updates, ordered extent/writeback synchronization, page cache invalidation, and sync semantics.

Public entry point: `btrfs_remap_file_range()`.

## Main Operations

The file supports two remap modes:

- Clone/reflink: share source extents with the destination.
- Dedupe: verify sameness through generic VFS preparation, then share extents without updating destination times.

## Inline Extent Handling

Inline extents need special handling because Btrfs inline extents normally live only at file offset 0 and cannot be partially cloned in the same way as regular extents.

`copy_inline_to_page()` materializes inline data into a destination folio:

- Reserves delalloc space.
- Gets/creates and locks the destination folio.
- Marks extent delalloc.
- Temporarily sets `BTRFS_INODE_NO_DELALLOC_FLUSH` to avoid deadlock while ranges are locked.
- Copies or decompresses inline data into the folio.
- Zero-fills the rest of the sector if inline data is shorter than a sector.
- Marks the folio uptodate, unchecked, and dirty.
- Releases reservations on error.

`clone_copy_inline_extent()` decides whether to copy an inline extent as an inline metadata item or materialize it into a page. It directly inserts an inline item only when destination offset is 0 and destination size constraints allow it. Otherwise it calls `copy_inline_to_page()`.

The function contains explicit transaction/deadlock avoidance: it releases paths before reserving data or starting transactions, and updates i_size before starting a transaction when copying inline data beyond EOF to avoid flush-on-commit deadlock.

## Core Clone Logic

`btrfs_clone()` performs the actual range clone.

Inputs include source/destination offsets, original user length, block-aligned clone length, and whether destination mtime/ctime updates should be skipped.

Flow:

1. Allocate a path and a temporary buffer sized to `nodesize`.
2. Search the source inode’s file extent items starting at the source offset.
3. If needed, back up to a previous extent that overlaps the range.
4. Iterate extent items until the clone range is covered.
5. For regular/prealloc extents:
   - Trim leading/trailing portions outside the requested source range.
   - Fill `btrfs_replace_extent_info`.
   - Call `btrfs_replace_file_extents()` over the destination range.
6. For inline extents:
   - Validate inline constraints.
   - Delegate to `clone_copy_inline_extent()`.
7. Update `last_reflink_trans` for source/destination to keep fsync checksum logging correct.
8. Update inode metadata with `clone_finish_inode_update()`.
9. Handle trailing implicit holes with `btrfs_replace_file_extents(..., NULL, ...)`.

The function carefully tracks:

- `last_dest_end`: cloned destination coverage.
- `prev_extent_end`: source extent progress, including races with ordered extent completion.
- `drop_start`: start of destination region to drop/replace, including implicit holes.

It clears `BTRFS_INODE_NO_DELALLOC_FLUSH` on exit.

## Inode Update

`clone_finish_inode_update()`:

- increments inode version.
- updates mtime/ctime unless suppressed.
- caps EOF expansion to the original requested length.
- updates `i_size` and safe disk i_size as needed.
- calls `btrfs_update_inode()`.
- aborts transaction on inode update failure.
- ends the transaction.

## Dedupe Path

`btrfs_extent_same()` handles dedupe after VFS preparation. It increments `root_dst->dedupe_in_progress` unless send is in progress, in which case it returns `-EAGAIN`.

Dedupe work is chunked by `BTRFS_MAX_DEDUPE_LEN` (`16 MiB`) through `btrfs_extent_same_range()`.

`btrfs_extent_same_range()`:

- Locks the destination extent range.
- Calls `btrfs_clone()` with `no_time_update = true`.
- Unlocks the range.
- Balances dirty btree pages.

## Clone Path

`btrfs_clone_files()` handles non-dedupe clone:

- Expands `len` to cover the aligned EOF block when cloning to source EOF.
- If cloning beyond destination EOF, calls `btrfs_cont_expand()` and waits for ordered extents to finish over the expanded range.
- Locks the destination extent range.
- Calls `btrfs_clone()` with time updates enabled.
- Waits for ordered range completion after clone because inline data may have been copied into dirty folios.
- Invalidates destination page cache over the cloned range so future reads see cloned data.
- Balances dirty btree pages.

## Remap Preparation

`btrfs_remap_file_range_prep()` performs Btrfs-specific validation and synchronization before calling `generic_remap_file_range_prep()`.

Checks and preparation include:

- Non-dedupe clone cannot target a read-only root.
- Source and destination encryption state must match.
- Source and destination `NODATASUM` flags must match, preventing a partly checksummed destination file.
- Flush source mapping before reflink to force NOCOW buffered writes to disk as NOCOW before extent refs are increased.
- Wait for ordered extents on both source and destination aligned ranges.
- Computes writeback length carefully for full-file clone (`len == 0`) and sector alignment.

## Top-Level Entry Point

`btrfs_remap_file_range()`:

1. Rejects operation if filesystem is shut down.
2. Rejects unsupported remap flags.
3. Locks either one inode or both source/destination non-directory inodes.
4. Takes exclusive Btrfs mmap locks in stable pointer order for two-inode operations.
5. Calls Btrfs remap preparation.
6. Dispatches to dedupe or clone.
7. Unlocks inodes and mmap locks.
8. If either file is synchronous (`O_SYNC`, `O_DSYNC`, or `S_SYNC`) and the remap succeeded, fsyncs both source and destination ranges.
9. Returns cloned/deduped length or error.

## Locking and Concurrency

- `btrfs_double_mmap_lock()` locks mmap semaphores in pointer order with nested locking.
- Destination extent ranges are locked during clone/dedupe replacement.
- Ordered extents are waited before sharing references to avoid races with not-yet-created file extent items.
- Page cache invalidation happens after clone completion and ordered extent waiting.
- Send and dedupe are coordinated through `send_in_progress` and `dedupe_in_progress`.

## Important Invariants

- Reflink ranges must obey sector-size alignment rules enforced by VFS/generic prep.
- Inline extents are whole-sector/offset-0 special cases.
- Destination cannot become partly checksummed.
- Encrypted and unencrypted files cannot be reflinked together.
- Sync writes require syncing both source and destination ranges after successful remap.

<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/reflink.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/reflink.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/reflink.h

## Purpose

`reflink.h` declares the Btrfs file range remap entry point implemented by `reflink.c`.

## Interface

It forward-declares `struct file` and exposes:

`loff_t btrfs_remap_file_range(struct file *file_in, loff_t pos_in, struct file *file_out, loff_t pos_out, loff_t len, unsigned int remap_flags);`

This function is the filesystem implementation for clone/dedupe remap operations.

## Build Role

The header is minimal: it provides include guards, includes `linux/types.h`, and lets other Btrfs file operation code call the remap implementation without pulling in the full implementation details.

<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/reflink.h -->