# Group Research: group_952_linux_stable_sources_os_linux_linux_stable_fs_btrfs_raid56_c_sources_1bfe9ec20a9b

Scope: `Docs/research_subset_a`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/raid56.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/raid56.c

## Purpose

Implements Btrfs RAID5/RAID6 parity I/O for writes, failed-read reconstruction, parity scrub, and device-replace duplication. The central object is `struct btrfs_raid_bio` (`rbio`), representing one full RAID56 stripe: all data stripes plus P and optional Q parity stripes.

The file handles:

- Partial-stripe read-modify-write (RMW).
- Full-stripe write fast paths.
- Stripe locking and rbio merging.
- Stripe cache reuse for recently read data stripes.
- RAID5 XOR parity and RAID6 P/Q syndrome generation.
- Recovery from missing devices, read errors, and checksum mismatches.
- Parity scrub validation and repair.
- Replace target writes for affected stripes.

## Core Concepts

`rbio` tracks one full stripe. The code distinguishes:

- `bio_paddrs`: physical addresses borrowed from upper-layer bios.
- `stripe_pages` / `stripe_paddrs`: pages allocated internally for reads, parity, recovery, scrub, and cache.
- `error_bitmap`: per-sector failures across all stripes.
- `stripe_uptodate_bitmap`: per-sector validity of `stripe_paddrs`.
- `dbitmap`: horizontal-sector bitmap showing which vertical stripes are touched by the upper-layer write or scrub.

The implementation supports sector sizes both smaller and larger than page size through `sector_nsteps`, where a filesystem block may map to one or more page-sized steps.

## Stripe Locking and Cache

The file defines a global per-filesystem stripe hash table via `btrfs_alloc_stripe_hash_table()` and frees it with `btrfs_free_stripe_hash_table()`.

Important behavior:

- `lock_stripe_add()` serializes work for the same full stripe.
- Compatible rbios can be merged before final RMW locking.
- Incompatible rbios are queued on `plug_list` and started when the current rbio unlocks.
- Cached rbios can donate uptodate data pages to later rbios with `steal_rbio()`.
- `unlock_stripe()` either keeps an rbio in cache, hands the lock to the next queued rbio, or removes it from the hash/cache.

Cache entries are LRU-limited by `RBIO_CACHE_SIZE`. Cached data is considered reusable only after `RBIO_CACHE_READY_BIT` is set.

## Rbio Allocation and Address Indexing

`alloc_rbio()` allocates the rbio and its pointer arrays/bitmaps from the `btrfs_io_context`. It computes:

- `real_stripes`, excluding replace target stripes.
- `nr_data`, derived from RAID parity count.
- `stripe_npages`, `stripe_nsectors`, and `sector_nsteps`.
- `nr_pages` and `nr_sectors` for the full stripe.

Address helpers include:

- `rbio_sector_index()`
- `rbio_paddr_index()`
- `rbio_stripe_paddr()`
- `rbio_pstripe_paddr()`
- `rbio_qstripe_paddr()`
- `sector_paddrs_in_rbio()`
- `sector_paddr_in_rbio()`

These centralize stripe/sector/step translation and preserve support for block size greater than page size.

## Write Path

Entry point: `raid56_parity_write()`.

Flow:

1. Allocate an rbio.
2. Add the caller bio with `rbio_add_bio()`.
3. If partial and block-layer plugging is active, queue it for `raid_unplug()`.
4. Otherwise queue `rmw_rbio_work()`.

`raid_unplug()` sorts rbios by logical sector and merges adjacent compatible rbios where possible, improving the chance of full-stripe writes.

`rmw_rbio()` performs the actual write:

- Allocates parity pages first.
- If the rbio is partial and cache is insufficient, reads all needed data/parity sectors with `rmw_read_wait_recover()`.
- Uses checksums for data verification where available.
- Sets `RBIO_RMW_LOCKED_BIT` to prevent further merging.
- Caches partial-stripe data pages after read/repair.
- Regenerates parity for every sector with `generate_pq_vertical()`.
- Assembles write bios with `rmw_assemble_write_bios()`.
- Submits writes and waits for completion.
- Reports `-EIO` if post-write error count exceeds RAID tolerance.

Full-stripe writes avoid reading old data because every data sector is supplied by upper layers.

## Read Recovery Path

Entry point: `raid56_parity_recover()`.

Used after a normal read fails. It:

1. Allocates an rbio.
2. Adds the failed bio.
3. Marks the failed range in `error_bitmap` with `set_rbio_range_error()`.
4. For RAID6 retry mirrors greater than 2, marks an additional synthetic failed stripe with `set_rbio_raid6_extra_error()`.
5. Queues `recover_rbio_work()`.

`recover_rbio()` reads all nonfailed sectors, then calls `recover_sectors()`.

Recovery is per vertical stripe:

- `get_rbio_vertical_errors()` finds failed stripe indexes.
- `recover_vertical()` rejects errors beyond `bioc->max_errors`.
- `recover_vertical_step()` performs RAID5 XOR or RAID6 recovery:
  - single RAID5/RAID6 failures can use P parity.
  - RAID6 two-data or data-plus-P failures use RAID6 library helpers.
  - P/Q-only corruption can be skipped for data-read recovery.
- `verify_one_sector()` validates recovered data against checksums if available.

## Checksum Handling

`fill_data_csums()` loads data checksums for data block groups during RMW. It intentionally skips metadata and mixed block groups to avoid deadlock while holding the stripe lock.

Read completion calls `verify_bio_data_sectors()` for data stripes. Checksum mismatches mark bits in `error_bitmap`, allowing reconstruction to repair stale or corrupt data before parity generation.

If checksum lookup fails, the code warns and continues without checksum protection for that sub-stripe write.

## Parity Generation

`generate_pq_vertical_step()` maps one step from every data stripe and parity stripe.

- RAID5 copies the first data block into P and XORs the remaining data blocks.
- RAID6 invokes `raid6_call.gen_syndrome()` over all real stripes.

`generate_pq_vertical()` repeats this for all steps in one filesystem sector and marks parity sectors uptodate.

## Scrub and Replace

Scrub allocation entry: `raid56_parity_alloc_scrub_rbio()`.

Submit entry: `raid56_parity_submit_scrub_rbio()`.

Scrub flow:

1. `alloc_rbio_essential_pages()` allocates pages only for sectors needed by `dbitmap`.
2. `scrub_assemble_read_bios()` reads missing sectors unless already supplied or cached.
3. `recover_scrub_rbio()` repairs failed data sectors where RAID tolerance and scrub constraints allow.
4. `finish_parity_scrub()` verifies recalculated parity against the scrubbed parity stripe.
5. If mismatched, parity is repaired and written.
6. If device replace targets the scrubbed parity stripe, writes are duplicated to the replacement stripe.

`raid56_parity_cache_data_folios()` lets scrub provide known-good data folios, avoiding redundant reads by copying them into rbio-managed pages and marking sectors uptodate.

## Error and Completion Model

Read bios use `raid_wait_read_end_io()`:

- Bio I/O errors update `error_bitmap`.
- Successful reads mark internal pages uptodate and may perform checksum verification.

Write bios use `raid_wait_write_end_io()`:

- Bio I/O errors update `error_bitmap`.

All submitted bios decrement `stripes_pending` and wake `io_wait`. Original upper-layer bios are completed by `rbio_orig_end_io()` after unlock/cache handling.

## Concurrency

Major concurrency mechanisms:

- Stripe hash bucket spinlocks serialize stripe ownership.
- `bio_list_lock` protects rbio bio lists, plug lists, and merge state.
- `RBIO_RMW_LOCKED_BIT` prevents late merges once final RMW begins.
- Work is queued to `fs_info->rmw_workers`.
- Plug callbacks gather partial writes within block-layer plugging windows.
- Wait queues synchronize submitted stripe bios.

## Important Invariants

The file uses `ASSERT_RBIO*` helpers to dump `bioc` and `rbio` context before asserting. Key invariants include:

- Real stripes are between 2 and 255.
- Data stripes are less than total stripes.
- Stripe sectors fit in a machine word because current stripe length is fixed at 64 KiB.
- Physical address entries must not be `INVALID_PADDR` when mapped.
- Cached rbios must have all data stripe pages present and uptodate.

## External Interface

Exported functions:

- `btrfs_alloc_stripe_hash_table()`
- `btrfs_free_stripe_hash_table()`
- `raid56_parity_write()`
- `raid56_parity_recover()`
- `raid56_parity_alloc_scrub_rbio()`
- `raid56_parity_submit_scrub_rbio()`
- `raid56_parity_cache_data_folios()`

These are consumed by Btrfs volume mapping, writeback/read recovery, scrub, and device replace code.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/raid56.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/raid56.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/raid56.h

## Purpose

Declares Btrfs RAID56 parity interfaces and defines the central `struct btrfs_raid_bio` used by `raid56.c`.

## Main Types

`enum btrfs_rbio_ops` identifies rbio operation mode:

- `BTRFS_RBIO_WRITE`
- `BTRFS_RBIO_READ_REBUILD`
- `BTRFS_RBIO_PARITY_SCRUB`

`struct btrfs_raid_bio` represents one full RAID56 stripe, including all data stripes and parity stripes. It stores:

- The `btrfs_io_context`.
- Hash/cache/plug list nodes.
- Work item for async processing.
- Upper-layer bio list and lock.
- Operation flags.
- Stripe geometry: pages, sectors, data stripes, real stripes, sector steps.
- Pending I/O accounting and waitqueue.
- Data bitmap and scrub/finish bitmap.
- Page/address arrays for upper bios and internal stripe pages.
- Uptodate and error bitmaps.
- Optional checksum buffer and checksum bitmap.

The header contains an extensive design comment explaining the mapping between upper-layer bios, internal pages, sector addressing, stripe numbers, and step numbers.

`struct raid56_bio_trace_info` records trace metadata for each physical bio: device id, stripe-relative offset, and stripe number.

## Helpers

Inline helpers:

- `nr_data_stripes()` computes chunk-map data stripe count.
- `nr_bioc_data_stripes()` computes io-context data stripe count.

Constants:

- `RAID5_P_STRIPE`
- `RAID6_Q_STRIPE`
- `is_parity_stripe()`

## Exported API

Declared functions:

- `raid56_parity_recover()`
- `raid56_parity_write()`
- `raid56_parity_alloc_scrub_rbio()`
- `raid56_parity_submit_scrub_rbio()`
- `raid56_parity_cache_data_folios()`
- `btrfs_alloc_stripe_hash_table()`
- `btrfs_free_stripe_hash_table()`

## Role in the Subsystem

This header is the RAID56 contract between the Btrfs volume/I/O layer and parity implementation. It exposes only high-level submission and lifecycle functions while keeping the RMW, recovery, and scrub algorithms private to `raid56.c`.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/raid56.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ref-verify.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/ref-verify.c

## Purpose

Implements the debug-only Btrfs reference verifier used when `REF_VERIFY` is enabled. It builds an in-memory model of extent references from the on-disk extent tree and then checks later delayed-reference mutations against that model.

The verifier is intended to catch reference accounting bugs, stale references, missing references, incorrect reallocation, and mismatches between expected and actual extent-tree state.

## In-Memory Model

The file defines four private structures:

- `root_entry`: direct reference count per root for a block.
- `ref_entry`: expected extent reference tuple: root, parent, owner, offset, count.
- `ref_action`: historical add/drop action with delayed-ref action code, root, ref tuple, list node, and optional stack trace.
- `block_entry`: one referenced extent/tree block, keyed by bytenr, with length, total refs, metadata flag, from-disk flag, root/ref rbtrees, and action history.

`fs_info->block_tree` stores `block_entry` records keyed by bytenr. Each block entry contains separate rbtrees for roots and refs.

## Rbtree Operations

The file provides comparison/lookup/insert helpers for:

- `block_entry` by bytenr.
- `root_entry` by root objectid.
- `ref_entry` by root, parent, owner, and offset.

Existing duplicate entries are returned so counts can be merged or errors detected.

## Stack Trace Support

When `CONFIG_STACKTRACE` is enabled:

- `__save_stack_trace()` records up to `MAX_TRACE` entries per ref action.
- `__print_stack_trace()` prints stored call stacks during diagnostics.

Without stacktrace support, diagnostics report that stacktrace support is unavailable.

## Building the Initial Ref Tree

Entry point: `btrfs_build_ref_tree()`.

At mount, if `REF_VERIFY` is enabled, it:

1. Gets the extent root.
2. Allocates a Btrfs path.
3. Locks the root node for read.
4. Walks the entire extent tree manually using `walk_down_tree()` and `walk_up_tree()`.
5. Processes each leaf with `process_leaf()`.

`process_leaf()` handles:

- `BTRFS_EXTENT_ITEM_KEY`
- `BTRFS_METADATA_ITEM_KEY`
- `BTRFS_TREE_BLOCK_REF_KEY`
- `BTRFS_SHARED_BLOCK_REF_KEY`
- `BTRFS_EXTENT_DATA_REF_KEY`
- `BTRFS_SHARED_DATA_REF_KEY`

`process_extent_item()` parses inline refs from extent items and delegates to:

- `add_tree_block()`
- `add_extent_data_ref()`
- `add_shared_data_ref()`

It tolerates `BTRFS_EXTENT_OWNER_REF_KEY` only when simple quotas are enabled.

## Reference Mutation Verification

Main mutation hook: `btrfs_ref_tree_mod()`.

It returns immediately unless `REF_VERIFY` is enabled.

For each delayed reference operation, it:

1. Converts `struct btrfs_ref` into a verifier `ref_entry`.
2. Allocates a `ref_action` and records the stack.
3. Handles `BTRFS_ADD_DELAYED_EXTENT` as a new allocation.
4. For add/drop refs, finds the existing block entry and validates counts.
5. Inserts, increments, decrements, or removes matching `ref_entry` records.
6. Updates root-level and block-level counts.
7. Appends the action to the block history.

Detected errors include:

- Adding an extent to a bytenr that still has references.
- Dropping a ref for a block with no entry.
- Dropping a ref from a block with zero total refs.
- Dropping a nonexistent ref tuple.
- Adding a second metadata ref to an existing tree-block ref.
- Missing expected root entries.

On error, it dumps detailed state and disables `REF_VERIFY` after freeing the cache.

## Diagnostics

`dump_block_entry()` prints:

- Block bytenr/len.
- Total refs.
- Metadata/from-disk flags.
- All ref entries.
- All root entries.
- Historical ref actions with stack traces.

`dump_ref_action()` prints the action and reference tuple associated with a mutation.

## Cache Cleanup

`btrfs_free_ref_cache()` frees the entire verifier tree under `ref_verify_lock`.

`btrfs_free_ref_tree_range()` removes cached block entries in a given physical range, warning if existing entries overlap the range boundaries. This is used when a range is freed or otherwise no longer valid for verifier tracking.

## Locking

The verifier uses `fs_info->ref_verify_lock` to protect the global `block_tree` and all nested state. Some helper functions intentionally return with the lock still held so callers can continue mutating the relevant block entry before unlocking.

## Failure Policy

The verifier is diagnostic. On internal inconsistency or build failure, it frees its cache and clears `REF_VERIFY` from mount options rather than continuing with a corrupted model.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ref-verify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ref-verify.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/ref-verify.h

## Purpose

Declares the Btrfs reference verifier interface and provides no-op stubs when debug support is disabled.

## Debug Build Behavior

Under `CONFIG_BTRFS_DEBUG`, it declares:

- `btrfs_build_ref_tree()`
- `btrfs_free_ref_cache()`
- `btrfs_ref_tree_mod()`
- `btrfs_free_ref_tree_range()`

It also defines `btrfs_init_ref_verify()`, which initializes `fs_info->ref_verify_lock` and sets `fs_info->block_tree` to `RB_ROOT`.

## Non-Debug Build Behavior

Without `CONFIG_BTRFS_DEBUG`, all functions are inline no-ops or return success. This removes verifier overhead entirely from non-debug builds while preserving call-site simplicity.

## Role in the Subsystem

This header gates the verifier behind debug configuration and mount-option checks. Production code can call the verifier hooks unconditionally while compilation determines whether they do real work.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/ref-verify.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/reflink.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/reflink.c

## Purpose

Implements Btrfs file range remapping: clone/reflink and dedupe. It is the filesystem-specific backend for `remap_file_range`, handling Btrfs extent items, inline extents, ordered extents, delalloc, locking, fsync safety, and page-cache invalidation.

Main exported entry point: `btrfs_remap_file_range()`.

## Clone Completion

`clone_finish_inode_update()` finalizes a clone transaction by:

- Incrementing inode version.
- Updating mtime/ctime unless suppressed.
- Extending `i_size` if needed.
- Resetting safe disk i_size tracking.
- Updating the inode item.
- Ending or aborting the transaction.

It caps EOF growth to the user-requested clone length rather than the block-rounded internal length.

## Inline Extent Handling

Inline extents require special handling because they cannot always be represented as shared extent references in the destination.

`copy_inline_to_page()` copies or decompresses inline data into a destination folio and marks the range delalloc/dirty. It:

- Reserves delalloc space.
- Gets or creates the destination folio.
- Sets extent mapping and delalloc state.
- Sets `BTRFS_INODE_NO_DELALLOC_FLUSH` to avoid deadlock while reflink holds range locks.
- Copies uncompressed inline data or decompresses compressed inline data.
- Zero-fills the remainder of the block when inline data is shorter than a sector.
- Marks the folio uptodate, unchecked, and dirty.
- Releases space on error.

`clone_copy_inline_extent()` chooses whether to insert an inline extent directly into the destination tree or copy its data into a page:

- Inline-to-inline insertion is possible only at destination offset 0 and when file-size constraints allow.
- Otherwise data is copied to the page cache via `copy_inline_to_page()`.
- It carefully releases Btrfs paths before starting transactions or reserving space to avoid lockdep issues and deadlocks.
- If copied beyond EOF, it updates `i_size` before starting a transaction to avoid flush-on-commit deadlocks.

## Main Clone Engine

`btrfs_clone()` clones a range from source inode to destination inode.

Flow:

1. Allocate a temporary leaf-sized buffer and Btrfs path.
2. Search source file extent items starting at `off`.
3. Include a previous overlapping extent if the first search lands after `off`.
4. Iterate extent items until the requested aligned range is covered.
5. For regular/prealloc extents:
   - Trim leading/trailing parts outside the clone range.
   - Build `btrfs_replace_extent_info`.
   - Call `btrfs_replace_file_extents()` on the destination range.
6. For inline extents:
   - Validate inline assumptions.
   - Use `clone_copy_inline_extent()`.
7. Update `last_reflink_trans` for source/destination when needed for fsync correctness.
8. Finish inode update per cloned extent.
9. Replace trailing implicit holes if no-hole or mixed I/O behavior leaves gaps.

The function handles implicit holes by dropping/replacing destination ranges even when the source has no explicit hole extent item.

## Dedupe Path

`btrfs_extent_same()` implements dedupe after the VFS has confirmed byte equality.

It prevents dedupe into a root with send operations in progress by checking and incrementing `dedupe_in_progress`.

Large dedupe requests are split into `BTRFS_MAX_DEDUPE_LEN` chunks, currently 16 MiB, using `btrfs_extent_same_range()` for each chunk. Each range locks the destination extent range and calls `btrfs_clone()` with `no_time_update = true`.

## Clone File Path

`btrfs_clone_files()` performs non-dedupe clone work:

- Rounds the source EOF block when cloning through EOF.
- Expands destination holes if cloning beyond current destination size via `btrfs_cont_expand()`.
- Waits for ordered extents after expansion to avoid racing with extent reference increments.
- Locks the destination extent range.
- Calls `btrfs_clone()`.
- Waits for ordered extents in the destination range.
- Invalidates destination page cache so future reads see cloned data.
- Balances dirty btree state.

## Remap Preparation

`btrfs_remap_file_range_prep()` validates and prepares the operation before clone/dedupe:

- Rejects clone into read-only roots.
- Requires encrypted status to match between source and destination.
- Rejects mixing `NODATASUM` and checksummed inodes.
- Flushes source file mapping to force NOCOW buffered writes to disk before increasing extent references.
- Waits for ordered ranges on source and destination.
- Delegates final generic checks to `generic_remap_file_range_prep()`.

The function intentionally does Btrfs-specific writeback and ordered-extent waiting because generic VFS preparation is insufficient for compression, ordered extent completion, and NOCOW safety.

## Locking

`btrfs_remap_file_range()` locks:

- Same inode: `btrfs_inode_lock(..., BTRFS_ILOCK_MMAP)`.
- Different inodes: `lock_two_nondirectories()` plus ordered double `i_mmap_lock` acquisition via `btrfs_double_mmap_lock()`.

Range locking is performed around clone/dedupe modifications to serialize with readahead and protect against relocation/concurrency assumptions.

## Sync Semantics

`file_sync_write()` detects `O_SYNC`, `O_DSYNC`, or inode `S_SYNC`.

After a successful remap, if either file is sync-write, `btrfs_remap_file_range()` fsyncs both source and destination ranges so reflinked data remains readable from both after power loss.

## Error Handling

The file is careful to:

- Abort transactions on metadata update failures.
- Release paths before operations that may allocate, reserve, or start transactions.
- Clear `BTRFS_INODE_NO_DELALLOC_FLUSH` on clone exit.
- Return negative errors from validation, writeback, ordered range waits, page-cache invalidation, and transaction operations.
- Return the remapped length on success.

## External Interface

`btrfs_remap_file_range()` accepts source/destination files, offsets, length, and remap flags. It supports:

- `REMAP_FILE_DEDUP`
- `REMAP_FILE_ADVISORY`

Any other flag is rejected with `-EINVAL`.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/reflink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/reflink.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/reflink.h

## Purpose

Declares the Btrfs file range remap entry point implemented in `reflink.c`.

## API

The header declares:

```c
loff_t btrfs_remap_file_range(struct file *file_in, loff_t pos_in,
			      struct file *file_out, loff_t pos_out,
			      loff_t len, unsigned int remap_flags);
```

This is the Btrfs-specific clone/dedupe backend used by file operations.

## Structure

The header contains only include guards, `<linux/types.h>`, a forward declaration of `struct file`, and the function prototype. It keeps reflink implementation details private to `reflink.c`.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/reflink.h -->