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
