# Group Research: group_710_linux_sources_os_linux_linux_fs_btrfs_raid56_c_sources_os_linux_linu_bf6641faa1bc

Scope: subset A from `Docs/research_subset_a.md`, covering the listed `sources/os/linux/linux/fs/btrfs` files. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/raid56.c -->
# File Research: sources/os/linux/linux/fs/btrfs/raid56.c

## Scope

`raid56.c` implements Btrfs RAID5/RAID6 parity I/O: read-modify-write parity writes, failed-read reconstruction, parity scrub/repair, stripe locking, full-stripe write merging, rbio caching, and device-replace write duplication.

The central object is `struct btrfs_raid_bio`, representing one full RAID56 stripe including data and P/Q parity stripes.

## Main APIs

- `btrfs_alloc_stripe_hash_table()` / `btrfs_free_stripe_hash_table()` allocate and tear down the per-filesystem stripe hash/cache table.
- `raid56_parity_write()` is the write entry point for RAID56 mapped bios.
- `raid56_parity_recover()` rebuilds a failed read from parity.
- `raid56_parity_alloc_scrub_rbio()` creates a parity scrub rbio.
- `raid56_parity_submit_scrub_rbio()` submits scrub/repair work.
- `raid56_parity_cache_data_folios()` preloads known-good scrub data folios into rbio private pages.

## Stripe Locking And Cache

The file uses a hash table keyed by `full_stripe_logical` to serialize operations on a full stripe. `lock_stripe_add()` either grants the stripe lock, merges compatible rbios, queues an rbio on the current owner’s plug list, or steals cached stripe pages from an idle cached rbio.

`unlock_stripe()` releases ownership, optionally keeps an rbio in the cache, or hands the lock to a queued rbio and schedules the correct worker.

The rbio cache stores recently read full-stripe data pages for future sub-stripe writes. Cached rbios are LRU-pruned by `RBIO_CACHE_SIZE`; only data pages are stolen because parity is regenerated.

## Rbio Layout And Indexing

`alloc_rbio()` sizes the rbio from the mapped `btrfs_io_context`: real stripes, data stripes, stripe sectors, stripe pages, and sector steps. It supports both block-size <= page-size and block-size > page-size cases by addressing each filesystem sector as one or more physical-address steps.

Important arrays:

- `bio_paddrs`: physical addresses from higher-level bios.
- `stripe_pages`: private pages allocated for data/parity reads and writes.
- `stripe_paddrs`: physical addresses into `stripe_pages`.
- `stripe_uptodate_bitmap`: valid private sectors.
- `error_bitmap`: per-sector read/write/csum failures.
- `dbitmap`: horizontal stripe sectors affected by submitted bios.

Helpers such as `rbio_sector_index()`, `rbio_paddr_index()`, `sector_paddrs_in_rbio()`, and `index_rbio_pages()` provide the address mapping used by all RMW, recovery, and scrub paths.

## Write Path

`raid56_parity_write()` builds an rbio for the incoming bio, records affected horizontal sectors in `dbitmap`, and uses block plugging to merge partial stripes before scheduling work.

`rmw_rbio()` handles both full-stripe and sub-stripe writes:

1. Allocate parity pages.
2. For sub-stripe writes, allocate/read missing data pages unless all data sectors were cached.
3. For data block groups, lookup checksums and verify read data; mixed metadata/data groups skip checksum lookup to avoid deadlock.
4. Recover any missing/corrupt sectors within RAID tolerance.
5. Set `RBIO_RMW_LOCKED_BIT` to prevent further merging.
6. Cache sub-stripe data pages if safe.
7. Generate P and Q parity with xor or `raid6_call.gen_syndrome()`.
8. Assemble writes for changed data and parity sectors.
9. Duplicate the replace source stripe to the replace target when device replace is active.
10. Wait for all submitted write bios and fail if vertical error counts exceed tolerance.

## Read Recovery

`raid56_parity_recover()` is called after normal reads fail. It marks failed sectors in `error_bitmap`, optionally injects an extra RAID6 failure for alternate mirror retry attempts, and schedules recovery.

`recover_rbio()` reads all non-failed sectors, including parity, without trusting cached sectors. `recover_sectors()` reconstructs failed vertical stripes using RAID5 XOR, RAID6 data+P recovery, or RAID6 two-data recovery as appropriate. Reconstructed data sectors are checksum-verified when checksums are available.

## Parity Scrub

Scrub rbios are special zero-length-bio rbios used to verify or repair parity stripes. `raid56_parity_alloc_scrub_rbio()` identifies the parity stripe being scrubbed and copies the caller’s data bitmap.

`scrub_rbio()` allocates only essential pages, reads missing sectors, recovers recoverable data failures, then `finish_parity_scrub()` recalculates parity and writes only sectors whose scrubbed parity differs. During device replace, parity writes are duplicated to the replacement target when the scrubbed stripe is the replace source.

`raid56_parity_cache_data_folios()` lets scrub preload known-good file data and avoid unnecessary reads.

## Dependencies

This file depends on Btrfs volume mapping, checksums, workqueues, bio submission, extent/page helpers, device replace mapping, Linux RAID6 syndrome/recovery helpers, XOR helpers, tracepoints, and filesystem-sector/page-size alignment invariants.

## Concurrency And Error Handling

- Stripe ownership is protected by per-bucket spinlocks and each rbio’s `bio_list_lock`.
- Async work runs on `fs_info->rmw_workers`.
- Submitted bios are counted with `stripes_pending`; waiters sleep on `io_wait`.
- End I/O updates `error_bitmap` atomically per bit.
- Missing devices are treated as sector errors and checked against `bioc->max_errors`.
- Public entry points end the original bio with translated block status on allocation, read, write, recovery, or scrub failure.

## Risks And Invariants

- The stripe lock/hash logic must keep rbio references, hash membership, cache membership, and plug-list ownership balanced.
- `RBIO_RMW_LOCKED_BIT` is the boundary after which no more bios may merge into a write.
- Cached data is trusted only when `RBIO_CACHE_READY_BIT` and uptodate bits are set.
- Checksum lookup is intentionally skipped for metadata or mixed block groups to avoid recursive RAID56 recovery deadlocks.
- Device replace uses `replace_stripe_src` and the synthetic target stripe index; wrong stripe selection would miss replacement writes.
- RAID6 retry mirror numbering deliberately marks an additional stripe failed to try alternate reconstruction.

## Testing Signals

Relevant tests should cover full-stripe writes, sub-stripe RMW, cached RMW reuse, degraded writes, missing devices, RAID5 and RAID6 read recovery, RAID6 alternate mirror retries, checksum mismatch recovery, parity scrub repair, scrub with cached folios, device replace duplication, and block-size greater than page-size configurations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/raid56.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/raid56.h -->
# File Research: sources/os/linux/linux/fs/btrfs/raid56.h

## Scope

`raid56.h` declares the RAID56 rbio model, operation types, trace metadata, helper constants, and public interfaces implemented by `raid56.c`.

## Key Types And Constants

- `enum btrfs_rbio_ops`: write, read rebuild, and parity scrub operations.
- `struct btrfs_raid_bio`: full-stripe state for RAID5/6 data and parity I/O.
- `struct raid56_bio_trace_info`: devid, stripe offset, and stripe number for trace events.
- `RAID5_P_STRIPE` and `RAID6_Q_STRIPE`: sentinel parity stripe identifiers.
- `is_parity_stripe()`: tests those parity sentinels.

## Rbio Data Model

The header documents two page sources:

- Higher-layer bios stored in `bio_list`, indexed by `bio_paddrs`.
- Internal rbio pages stored in `stripe_pages`, indexed by `stripe_paddrs`.

Addressing is by stripe number, sector number, and step number. Step addressing exists for block-size greater than page-size support, where one filesystem sector spans multiple pages.

`struct btrfs_raid_bio` also stores hash/cache lists, plug list, operation flags, stripe geometry, refcount, pending I/O counter, waitqueue, data/parity bitmaps, checksum buffers, and error tracking.

## Public APIs

- `raid56_parity_write()`
- `raid56_parity_recover()`
- `raid56_parity_alloc_scrub_rbio()`
- `raid56_parity_submit_scrub_rbio()`
- `raid56_parity_cache_data_folios()`
- `btrfs_alloc_stripe_hash_table()`
- `btrfs_free_stripe_hash_table()`

Inline helpers compute data stripe counts from chunk maps and bio contexts.

## Dependencies

The header depends on Linux list, spinlock, bio, refcount, workqueue APIs, and Btrfs volume mapping definitions.

## Risks And Invariants

The structure layout encodes key assumptions used by `raid56.c`: fixed 64K stripe length, parity stripes placed after data stripes, all rbio sector arrays covering the full stripe, and `error_bitmap`/`stripe_uptodate_bitmap` sized per full-stripe sector.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/raid56.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ref-verify.c -->
# File Research: sources/os/linux/linux/fs/btrfs/ref-verify.c

## Scope

`ref-verify.c` implements the debug-only Btrfs reference verifier. It builds an in-memory model of extent references from the extent tree at mount, updates that model when delayed refs are added or dropped, records action history with optional stack traces, and disables reference verification if an invariant fails.

## Data Structures

- `root_entry`: tracks direct reference counts per root for one block.
- `ref_entry`: models one expected extent reference keyed by root, parent, owner, and offset.
- `ref_action`: records a delayed-ref action, root, reference snapshot, list node, and stack trace.
- `block_entry`: models one referenced bytenr, its length, total refs, metadata/data classification, from-disk status, root/ref rbtrees, and action history.

All block entries live in `fs_info->block_tree` and are protected by `fs_info->ref_verify_lock`.

## Mount-Time Tree Build

`btrfs_build_ref_tree()` walks the extent root under read locks and populates the verifier tree. It processes:

- `BTRFS_EXTENT_ITEM_KEY`
- `BTRFS_METADATA_ITEM_KEY`
- `BTRFS_TREE_BLOCK_REF_KEY`
- `BTRFS_SHARED_BLOCK_REF_KEY`
- `BTRFS_EXTENT_DATA_REF_KEY`
- `BTRFS_SHARED_DATA_REF_KEY`
- `BTRFS_EXTENT_OWNER_REF_KEY` validation for simple quotas

Inline and keyed refs are normalized into `ref_entry` records. Metadata tree blocks are tracked with level information, and data refs are tracked by root, owner objectid, and offset.

If the extent root is unavailable or verification fails, the mount option is cleared and the cache is freed.

## Runtime Ref Updates

`btrfs_ref_tree_mod()` updates the verifier for delayed-ref operations when `REF_VERIFY` is enabled.

For `BTRFS_ADD_DELAYED_EXTENT`, it creates or reuses a block entry, increments total refs, marks metadata if appropriate, and checks that the allocation is not reusing a block that still has references.

For `BTRFS_ADD_DELAYED_REF`, it inserts or increments a matching `ref_entry`, increments total/root refs, and rejects duplicate metadata refs.

For `BTRFS_DROP_DELAYED_REF`, it decrements or removes a matching `ref_entry`, decrements total/root refs, and reports attempts to drop nonexistent refs or refs from zero-ref blocks.

Every successful update appends a `ref_action` with the delayed-ref action and stack trace.

## Cleanup APIs

`btrfs_free_ref_cache()` releases the entire verifier tree at unmount or after fatal verifier errors.

`btrfs_free_ref_tree_range()` removes verifier entries for a block-group range and reports block entries that overlap the range boundaries.

## Diagnostics

`dump_block_entry()` logs a block’s refs, roots, and action history. `dump_ref_action()` logs action fields and prints a stack trace when `CONFIG_STACKTRACE` is available.

Error paths dump the relevant model state, free the verifier cache, and clear `REF_VERIFY` to avoid continued use of a corrupted debug model.

## Dependencies

The file depends on Btrfs extent-tree formats, delayed-ref action constants, path/tree read locking, accessors, rbtrees, spinlocks, stacktrace support, and filesystem mount options.

## Risks And Invariants

- The verifier assumes all updates happen under `ref_verify_lock`.
- Metadata blocks may not gain duplicate matching refs.
- Total block refs and per-root refs must never underflow or disagree with actions.
- Shared refs and direct refs are keyed differently; confusing parent-vs-root refs would produce false verifier failures.
- The build walk must preserve current bytenr/length across extent items and separate ref-key items.

## Testing Signals

Relevant coverage includes enabling `ref_verify` on mount, loading trees with inline and external refs, shared data/block refs, metadata item refs, delayed ref add/drop sequences, reallocation after free, block-group removal, simple-quota owner refs, and stacktrace-enabled diagnostics.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ref-verify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ref-verify.h -->
# File Research: sources/os/linux/linux/fs/btrfs/ref-verify.h

## Scope

`ref-verify.h` declares the reference verifier interface and provides debug/non-debug build variants.

## APIs

When `CONFIG_BTRFS_DEBUG` is enabled:

- `btrfs_build_ref_tree()`
- `btrfs_free_ref_cache()`
- `btrfs_ref_tree_mod()`
- `btrfs_free_ref_tree_range()`
- `btrfs_init_ref_verify()`

`btrfs_init_ref_verify()` initializes `fs_info->ref_verify_lock` and sets `fs_info->block_tree` to `RB_ROOT`.

When debug support is disabled, all functions are inline no-ops returning success where needed.

## Dependencies

The debug path uses Linux spinlocks and rbtrees plus forward declarations of `btrfs_fs_info` and `btrfs_ref`.

## Risks And Invariants

Callers can invoke these APIs unconditionally because the header compiles them out in non-debug builds. Debug builds require `btrfs_init_ref_verify()` before verifier tree use.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/ref-verify.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/reflink.c -->
# File Research: sources/os/linux/linux/fs/btrfs/reflink.c

## Scope

`reflink.c` implements Btrfs file range remapping for clone and dedupe operations. It handles VFS remap preparation, source/destination locking, extent sharing, inline extent copying, hole handling, inode updates, page-cache invalidation, writeback ordering, and synchronous-file durability behavior.

## Main Entry Point

`btrfs_remap_file_range()` validates remap flags, rejects shutdown filesystems, locks one or two inodes plus mmap locks, prepares the remap, dispatches to dedupe or clone, unlocks, and fsyncs both source and destination ranges when either file requires synchronous writes.

It returns the remapped length on success or a negative errno.

## Remap Preparation

`btrfs_remap_file_range_prep()` enforces Btrfs-specific constraints before the generic VFS helper:

- Non-dedupe clone cannot target a read-only root.
- Source and destination encryption state must match.
- Source and destination `NODATASUM` state must match.
- Source writeback is flushed to force NOCOW buffered writes to land before sharing references.
- Ordered extents are waited on for both source and destination aligned ranges.
- Then `generic_remap_file_range_prep()` performs generic overlap, EOF, dedupe comparison, and alignment checks.

## Clone Core

`btrfs_clone()` walks source file extent items from the source root and maps them into destination offsets. It handles:

- Regular and prealloc extents via `btrfs_replace_file_extents()`.
- Inline extents via `clone_copy_inline_extent()`.
- Implicit holes, including `NO_HOLES` cases, by dropping/replacing destination extents.
- Source ranges that begin in the middle of an extent.
- Destination i_size growth and inode updates after each transaction.
- `last_reflink_trans` updates to make fsync log checksums and shared extent state safely.
- Full-sync marking where hole logging would otherwise be skipped.

`clone_finish_inode_update()` increments inode version, updates timestamps when needed, adjusts i_size without over-rounding the user length, writes safe disk i_size state, updates the inode item, and ends the transaction.

## Inline Extent Handling

`clone_copy_inline_extent()` tries to preserve an inline extent in the destination when legal: destination offset 0, compatible file size, and at most one extent adjustment. Otherwise it copies inline data into a destination folio through `copy_inline_to_page()`.

`copy_inline_to_page()` reserves delalloc space, creates/locks the destination folio, maps and marks delalloc state, temporarily sets `BTRFS_INODE_NO_DELALLOC_FLUSH`, copies or decompresses inline data, zero-fills the rest of the sector, marks the folio uptodate/dirty, and releases reservation state. This avoids starting a transaction while holding locks that could deadlock with delalloc flushing.

The code has explicit deadlock avoidance for copying inline data beyond EOF before starting the inode-update transaction.

## Clone And Dedupe Wrappers

`btrfs_clone_files()` expands the destination with `btrfs_cont_expand()` if cloning beyond EOF, waits ordered writeback for the expanded tail, locks the destination extent range, calls `btrfs_clone()`, waits ordered writeback for any inline-copy delalloc, invalidates destination page cache, and balances dirty btrees.

`btrfs_extent_same()` protects against concurrent send by incrementing `dedupe_in_progress`, then dedupes in chunks of at most `BTRFS_MAX_DEDUPE_LEN` using `btrfs_extent_same_range()`. Dedupe uses `no_time_update = true`.

## Locking And Concurrency

- Same-inode remaps use `btrfs_inode_lock(..., BTRFS_ILOCK_MMAP)`.
- Cross-inode remaps use `lock_two_nondirectories()` plus ordered double mmap locking.
- Destination extent ranges are locked during clone/dedupe replacement.
- The source mmap lock protects against relocation races.
- Range writeback and ordered extent waits ensure source extents are stable and destination dirty state is not racing replacement.
- `send_in_progress` prevents dedupe from modifying roots used by send.

## Dependencies

The file relies on Btrfs transaction handling, extent replacement/drop helpers, inode item updates, delalloc reservation/accounting, compression decompression, folio/page-cache APIs, VFS remap helpers, ordered extent waiting, root send/dedupe counters, and fsync.

## Risks And Invariants

- Inline extents can only be cloned as inline at offset 0 and within sector-size limits; otherwise data must be copied to a page.
- Source and destination checksum policy must match to avoid partially checksummed files.
- NOCOW writeback must complete before increasing extent references.
- Page cache must be invalidated after clone so future reads do not see stale destination data.
- `last_reflink_trans` updates are required to avoid fsync logging overlapping checksum items incorrectly.
- Hole cloning with `NO_HOLES` may require full fsync marking when i_size changes.

## Testing Signals

Relevant coverage includes clone and dedupe across files and within one file, inline-to-inline clone, inline-to-page clone, compressed inline extents, holes with `NO_HOLES`, clone beyond EOF, unaligned EOF clone, NODATASUM mismatch, encryption mismatch, read-only roots, send-in-progress dedupe blocking, O_SYNC/O_DSYNC remaps, NOCOW buffered writes, and page-cache coherency after clone.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/reflink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/reflink.h -->
# File Research: sources/os/linux/linux/fs/btrfs/reflink.h

## Scope

`reflink.h` declares the Btrfs remap/reflink entry point.

## API

- `btrfs_remap_file_range(struct file *file_in, loff_t pos_in, struct file *file_out, loff_t pos_out, loff_t len, unsigned int remap_flags)`

This function is implemented in `reflink.c` and is used as the filesystem-specific clone/dedupe remap handler.

## Dependencies And Invariants

The header forward-declares `struct file` and includes Linux basic types. Callers must pass VFS file objects and remap flags accepted by the implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/reflink.h -->