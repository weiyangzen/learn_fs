# Group Research: group_927_linux_dm_sources_block_storage_linux_dm_drivers_md_dm_writecache_c_s_15a894366d58

Scope: subset A from `Docs/research_subset_a.md`, covering the listed `sources/block-storage/linux-dm/drivers/md` files. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-writecache.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-writecache.c

## Scope

This file implements the Device Mapper `writecache` target. It accelerates an origin block device with either a persistent-memory/DAX cache device (`p` mode) or an SSD cache device (`s` mode), maintains persistent cache metadata, services reads/writes/flushes/discards, performs asynchronous writeback to the origin, and exposes status/messages for administrative control.

## Public And Internal APIs Covered

- DM target entry points: `writecache_ctr()`, `writecache_dtr()`, `writecache_map()`, `writecache_end_io()`, `writecache_suspend()`, `writecache_resume()`, `writecache_status()`, `writecache_message()`, `writecache_iterate_devices()`, `writecache_io_hints()`.
- Module lifecycle: `dm_writecache_init()` registers `writecache_target`; `dm_writecache_exit()` unregisters it.
- Persistent-memory helpers: `persistent_memory_claim()`, `persistent_memory_release()`, page/offset/cache flush helpers, and `pmem_assign()`.
- Persistent metadata helpers: superblock/entry accessors, `read_original_sector()`, `read_seq_count()`, `clear_seq_count()`, `write_original_sector_seq_count()`, `writecache_flush_region()`, `writecache_flush_all_metadata()`, `writecache_commit_flushed()`, `ssd_commit_flushed()`, `ssd_commit_superblock()`.
- Cache lookup/list management: `writecache_find_entry()`, `writecache_insert_entry()`, `writecache_unlink()`, `writecache_add_to_freelist()`, `writecache_pop_from_freelist()`, `writecache_free_entry()`, `writecache_discard()`.
- I/O mapping helpers: `writecache_map_read()`, `writecache_map_write()`, `writecache_map_flush()`, `writecache_map_discard()`, `writecache_map_remap_origin()`, `writecache_bio_copy_ssd()`, `bio_copy_block()`.
- Background workers: `writecache_flush_thread()`, `writecache_endio_thread()`, `writecache_writeback()`, `writecache_flush_work()`, timers for autocommit and max age.
- Writeback helpers: `__writecache_writeback_pmem()`, `__writecache_writeback_ssd()`, completion callbacks, and throttling.
- Control messages: `flush`, `flush_on_suspend`, `cleaner`, and `clear_stats`.

## Control Flow And Behavior

- Construction parses mode, origin device, cache device, block size, and optional arguments such as `start_sector`, watermarks, writeback job limit, autocommit thresholds, `max_age`, `cleaner`, `fua`/`nofua`, `metadata_only`, and `pause_writeback`.
- PMEM mode requires synchronous DAX, maps the cache device using `dax_direct_access()`, optionally vmaps discontiguous pages, and flushes/invalidate cache ranges directly. SSD mode allocates a volatile metadata map in kernel memory, reads/writes cache metadata through `dm-io`, uses a dirty bitmap to persist changed metadata sectors, creates a flush thread, and uses `dm_kcopyd` for writeback copies.
- The on-cache metadata contains a small superblock and one `wc_memory_entry` per cache block. `seq_count` distinguishes committed entries from current uncommitted writes. `original_sector == -1` and `seq_count == -1` mark free entries.
- `writecache_resume()` reloads cache metadata, rebuilds the RB tree of valid entries and the freelist, drops duplicate or uncommitted entries, repairs metadata if needed, starts max-age writeback, and validates against hardware memory errors with `copy_mc_to_kernel()` where available.
- `writecache_map()` serializes state changes with `wc->lock`, handles preflush before sector remapping, enforces cache-block alignment, and dispatches reads, writes, discards, and flushes to specialized helpers.
- Reads hit the cache by original sector. PMEM hits are copied directly into the bio with machine-check-safe reads; SSD hits are remapped to cache sectors and counted as in-progress reads. Misses are partially remapped to the origin up to the next cached sector.
- Writes update an existing uncommitted entry, overwrite a committed SSD entry when safe, allocate a free entry, or bypass to the origin in cleaner/metadata-only/no-free-entry cases. PMEM writes copy data immediately into persistent memory; SSD writes remap contiguous cache blocks to the cache device. Autocommit is triggered by block count, timer, or FUA.
- Flushes commit metadata and, for SSD mode, are offloaded to the flush thread so the target can handle the two flush-bio pattern. Discards invalidate matching cached entries and then pass the discard to the origin.
- `writecache_flush()` persists dirty data/metadata for all uncommitted LRU entries up to the next committed boundary, increments the superblock sequence count, writes the superblock, and frees older duplicate entries for the same original sector.
- Writeback is queued when free entries fall below watermarks, cleaner/writeback-all is active, max age expires, or messages request it. It selects committed LRU entries, skips entries shadowed by in-progress newer duplicates, batches adjacent sectors, marks entries `write_in_progress`, and submits PMEM bios or SSD `dm_kcopyd` copies.
- Completion callbacks add finished work to `endio_list`; `writecache_endio_thread()` performs required origin flushes, frees entries, commits metadata again, and wakes freelist waiters. SSD endio waits for reads before final metadata commit.
- Suspend stops timers, flushes metadata, optionally forces writeback-all, drains the workqueue, waits for in-flight writeback, flushes PMEM mappings, and poisons lists to catch access while suspended.

## State And Data Structures

- `struct dm_writecache` is the target state: origin/cache devices, mapped metadata/data area, RB tree by original sector, LRU list, freelist/freetree, watermarks, sequence count, timers, workqueue, kthreads, dm-io/kcopyd clients, dirty bitmap, bioset/mempool, in-flight bio counters, and statistics.
- `struct wc_entry` represents one cache block and stores RB/LRU linkage, cache index, age, writeback state, contiguous-writeback hint, and optional shadow copies of persistent metadata for hardware-error handling.
- `struct wc_memory_superblock` and `struct wc_memory_entry` are the persistent metadata format.
- `struct writeback_struct` wraps a bio plus the cache entries it writes back in PMEM mode; `struct copy_struct` tracks SSD kcopyd writeback completion.
- `bio->bi_private` is used as a small tag: cache-device remaps decrement `bio_in_progress`, and origin write bypasses are tracked by `dm_io_tracker` for pause-writeback idleness.

## Dependencies

- Device Mapper target APIs, `dm-io`, `dm-kcopyd`, `dm-io-tracker`, target messages/status, and dm device lookup.
- Linux block layer bio cloning/remapping/submission, flush/FUA/discard flags, queue limits, biosets, mempools, kthreads, timers, workqueues, wait queues, RB trees, lists, vmalloc/vmap.
- DAX/libnvdimm/PMEM APIs when persistent-memory mode is compiled in.
- Architecture copy/flush helpers including `copy_mc_to_kernel()`, `memcpy_flushcache()`, `clflushopt`, and cache maintenance helpers.

## Risks And Invariants

- Metadata commit ordering is central: data and per-entry metadata must be durable before the superblock `seq_count` is advanced.
- Duplicate entries for the same original sector are legal only across sequence generations; stale duplicates must be freed only after newer committed data is safe.
- PMEM and SSD modes have different durability models. PMEM relies on cacheline writeback and memory barriers; SSD mode relies on explicit metadata writes, cache flushes, and a dirty bitmap.
- The freelist and writeback-size accounting gate forward progress; missed wakeups or unbalanced `write_in_progress` flags would block writes indefinitely.
- SSD overwrite of committed entries and discard handling wait for in-flight I/O where necessary so cached data is not freed while a remapped bio still references it.
- `copy_mc_to_kernel()` error handling is a reliability boundary for persistent-memory media errors.
- `writecache_map()` requires all I/O to be aligned to the configured cache block size; misaligned bios are failed.
- The target must not access normal list/tree structures while suspended after list poisoning.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-writecache.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-zero.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-zero.c

## Scope

This file implements the small Device Mapper `zero` target: a dummy mapping that returns zero-filled data for reads and silently drops writes/discards.

## Public And Internal APIs Covered

- DM target constructor: `zero_ctr()`.
- DM target mapper: `zero_map()`.
- Module lifecycle: `dm_zero_init()` and `dm_zero_exit()`.
- Target definition: `zero_target`.

## Control Flow And Behavior

- `zero_ctr()` rejects all table arguments and advertises one discard bio so discard requests are accepted and silently consumed instead of returning unsupported-operation errors.
- `zero_map()` zero-fills normal read bios and completes them immediately.
- Readahead reads are killed with `DM_MAPIO_KILL` to avoid wasting page cache on predictable zero data.
- Writes are silently accepted and completed without forwarding to any backing device.
- Any operation other than read/write is killed.
- The target has `DM_TARGET_NOWAIT` because it does not need to sleep on backing I/O.

## State And Data Structures

- No per-target private state is allocated.
- `zero_target` declares name `zero`, version `{1, 1, 0}`, constructor, mapper, and module owner.

## Dependencies

- Device Mapper target registration and bio completion APIs.
- Block-layer helpers `bio_op()`, `zero_fill_bio()`, `bio_endio()`, and request op/flag constants.

## Risks And Invariants

- The target intentionally discards writes and discards. It is useful for tests/sinks but must not be mistaken for persistent storage.
- Readahead bios are killed rather than completed with zeros, changing behavior from normal reads to avoid cache pollution.
- Since there is no backing device, every accepted bio must be completed in `zero_map()`.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-zero.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-zone.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-zone.c

## Scope

This file provides generic Device Mapper support for zoned block devices. It implements report-zones dispatch/remapping across a DM table, maintains resources for zone-append emulation, tracks sequential-zone write pointers, serializes writes per zone, and adjusts completion semantics for native or emulated zone append.

## Public And Internal APIs Covered

- Zone reporting: `dm_blk_report_zones()`, internal `dm_blk_do_report_zones()`, helper `dm_report_zones()`, and callback `dm_report_zones_cb()`.
- Zoned-device setup/cleanup: `dm_set_zones_restrictions()`, `dm_cleanup_zoned_dev()`, `dm_revalidate_zones()`.
- Zone write classification: `dm_is_zone_write()`, `dm_need_zone_wp_tracking()`.
- Zone append emulation: `dm_zone_map_bio()`, `dm_zone_endio()`, `dm_zone_map_bio_begin()`, `dm_zone_map_bio_end()`.
- Write-pointer state helpers: `dm_get_zone_wp_offset()`, `dm_update_zone_wp_offset()`, `dm_update_zone_wp_offset_cb()`.
- Per-zone locking helpers: `dm_zone_lock()` and `dm_zone_unlock()`.

## Control Flow And Behavior

- `dm_blk_report_zones()` obtains the live table under SRCU, refuses reports while suspended, and walks targets by sector. Each target must provide `report_zones`.
- `dm_report_zones()` is the helper target drivers call to report a backing block device; its callback remaps zone starts and write pointers from target-relative sectors back into the mapped-device address space.
- `dm_set_zones_restrictions()` sets the mapped queue zone count, detects whether all targets and backing devices support native zone append, and either clears append emulation or allocates emulation state.
- Revalidation scans all zones while the mapped device is suspended, builds the conventional-zone bitmap, sequential-zone write-lock bitmap, and `md->zwp_offset` write-pointer offset array. It uses `memalloc_noio_save()` because the bind path must not recurse into I/O allocation.
- `dm_zone_map_bio()` is the special map path for targets needing zone append emulation. It locks the sequential zone, verifies writes/reset/finish/append against the tracked write pointer, rewrites zone append into a non-mergeable regular write at the current write pointer, calls the target mapper, updates `zwp_offset`, and drops an extra pending I/O reference.
- `dm_zone_endio()` unlocks the zone at clone completion. For native append, it adjusts the original bio sector by the lower bits of the completed clone sector. For emulated append, failed write-pointer-changing operations invalidate the tracked offset, and successful appends report the actual sector by using the offset after write completion.
- If a tracked write pointer is invalid, the next mapping path re-reports the single zone to recover the current offset before proceeding.

## State And Data Structures

- Uses `mapped_device` fields `nr_zones`, `zwp_offset`, `flags` including `DMF_EMULATE_ZONE_APPEND`, and the mapped queue fields `conv_zones_bitmap` and `seq_zones_wlock`.
- `DM_ZONE_INVALID_WP_OFST` marks a sequential zone whose write pointer must be rediscovered.
- `struct dm_report_zones_args` carries original callback/data, target, start sector, next sector, and zone index through target reports.
- The clone bio flag `BIO_ZONE_WRITE_LOCKED` records ownership of the per-zone write lock.

## Dependencies

- DM core table/target/SRCU APIs and `dm_target_io`/`dm_io` pending-count helpers.
- Linux zoned block APIs: `blkdev_report_zones()`, `blkdev_nr_zones()`, `bio_zone_no()`, `bio_zone_is_seq()`, `blk_queue_zone_sectors()`, zone conditions/types, and queue zone bitmaps.
- Bit wait/wakeup primitives for per-zone write locking.

## Risks And Invariants

- Zone-append emulation depends on strict serialization per sequential zone; `BIO_ZONE_WRITE_LOCKED` and `seq_zones_wlock` must be balanced on every map/completion path.
- `zwp_offset` must be updated only after target mapping has accepted the write-pointer-changing operation, and invalidated on uncertain failures.
- Zone append must not be truncated; the emulation path treats truncated append writes as I/O errors.
- Report-zone remapping must stop at target boundaries to avoid exposing backing zones beyond a target range.
- Memory allocations during revalidation and single-zone update run under NOIO constraints to avoid block-layer recursion.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-zone.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-zoned-metadata.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-zoned-metadata.c

## Scope

This file implements the dm-zoned metadata layer. It discovers zones, loads and validates the on-disk metadata format, caches metadata blocks, maintains chunk-to-zone mappings, tracks per-zone valid-block bitmaps and weights, allocates/frees zones, coordinates active I/O with reclaim, and flushes metadata using a dual-superblock/logging scheme.

## Public And Internal APIs Covered

- Constructor/destructor/resume: `dmz_ctr_metadata()`, `dmz_dtr_metadata()`, `dmz_resume_metadata()`.
- Locks: `dmz_lock_map()`, `dmz_unlock_map()`, `dmz_lock_metadata()`, `dmz_unlock_metadata()`, `dmz_lock_flush()`, `dmz_unlock_flush()`.
- Geometry/accessors: `dmz_start_sect()`, `dmz_start_block()`, `dmz_nr_chunks()`, `dmz_nr_zones()`, zone-size and zone-count helpers, `dmz_metadata_label()`.
- Device health: `dmz_check_dev()`, `dmz_dev_is_dying()`.
- Metadata flushing: `dmz_flush_metadata()` and internal dirty-block/superblock write helpers.
- Zone mapping/allocation: `dmz_get_chunk_mapping()`, `dmz_put_chunk_mapping()`, `dmz_get_chunk_buffer()`, `dmz_alloc_zone()`, `dmz_free_zone()`, `dmz_map_zone()`, `dmz_unmap_zone()`.
- Reclaim coordination: `dmz_lock_zone_reclaim()`, `dmz_unlock_zone_reclaim()`, `dmz_get_zone_for_reclaim()`.
- Valid-block bitmap operations: `dmz_validate_blocks()`, `dmz_invalidate_blocks()`, `dmz_block_valid()`, `dmz_first_valid_block()`, `dmz_copy_valid_blocks()`, `dmz_merge_valid_blocks()`.

## Control Flow And Behavior

- The on-disk format consists of a superblock, a chunk mapping table, and per-zone valid-block bitmap blocks. Two metadata sets are maintained; the non-primary set acts as a log while updating the primary.
- `dmz_ctr_metadata()` initializes locks/lists/xarray, reports or emulates zones, loads the best superblock set, marks metadata zones, loads the mapping table, registers a shrinker for cached metadata blocks, and prints geometry.
- Zone discovery sets `DMZ_RND`, `DMZ_SEQ`, or `DMZ_CACHE`, records write-pointer block offsets for sequential zones, marks offline/read-only zones, detects the primary superblock zone, and handles regular-device cache zones in multi-device configurations.
- `dmz_load_sb()` reads primary and secondary superblocks, validates magic/version/checksum/position/UUID/label/device UUIDs, recovers a bad set from the good set, and selects the highest generation as primary. Version 2 also checks tertiary superblocks on additional zoned devices.
- Metadata blocks are cached in an RB tree by metadata block number. Reads insert blocks in `DMZ_META_READING` state and waiters synchronize on bit wait queues. Dirty blocks sit on `mblk_dirty_list`; clean unused blocks sit on `mblk_lru_list` and can be reclaimed by the shrinker.
- `dmz_flush_metadata()` takes the metadata semaphore for write, serializes with the flush mutex, moves dirty blocks to a local write list, writes them to the secondary/log set, writes that set's superblock, writes the same blocks to the primary set, writes the primary superblock, clears dirty flags, and increments generation. On error it requeues dirty blocks and checks backing-device health.
- `dmz_load_mapping()` reads all mapping blocks, assigns each mapped data zone and optional buffer zone to a chunk, computes zone weights from bitmaps, populates mapped/unmapped lists, reserves configured sequential zones for reclaim, and counts cache/random/sequential zones per device.
- `dmz_get_chunk_mapping()` returns the active data zone for a chunk. Writes to unmapped chunks allocate a cache/random zone and update the mapping. If the mapped zone is under reclaim, it asks reclaim to terminate, waits, and retries. Sequential write-error zones are re-reported and invalidated after the real write pointer if needed.
- `dmz_put_chunk_mapping()` deactivates the data zone after I/O and opportunistically unmaps/frees empty inactive data or buffer zones.
- `dmz_get_chunk_buffer()` allocates a random/cache buffer zone for unaligned writes into a sequential data zone and records it as the mapping's `bzone_id`.
- `dmz_alloc_zone()` removes a zone from the appropriate unmapped list, schedules reclaim for normal allocations, can search other devices or reserved sequential zones for reclaim allocations, and skips offline/metadata zones. `dmz_free_zone()` resets sequential zones and returns them to the correct free/reserved list.
- Bitmap functions validate/invalidate ranges, find valid extents, copy/merge validity maps during reclaim, and keep each zone's `weight` in sync with set bits.
- `dmz_resume_metadata()` re-reports every zone and verifies that sequential write pointers match the saved metadata state, invalidating blocks beyond a changed write pointer.

## State And Data Structures

- `struct dmz_metadata` stores device array, label/UUID, zone/block geometry, counts, zone xarray, two superblock descriptors, metadata-block cache state, locks, mapping blocks, zone lists, counters, reserved sequential zones, and waitqueue for free zones.
- `struct dmz_super` is the on-disk superblock with magic/version/generation, block counts, mapping/bitmap sizes, label/UUIDs, and CRC.
- `struct dmz_map` maps each logical chunk to a data zone and optional buffer zone.
- `struct dmz_mblock` caches one 4 KiB metadata block with RB/list linkage, refcount, state bits, page, and data pointer.
- `struct dm_zone` is defined in `dm-zoned.h` and holds zone type/state flags, write pointer, validity weight, mapped chunk, buffer/data peer, refcount, and device pointer.
- Lists divide zones by cache/random/sequential, mapped/unmapped, reserved, and LRU order for reclaim selection.

## Dependencies

- Linux block zone APIs for zone reports, zone reset, zone conditions/types, device cache flush, and bio submission.
- DM-zoned target/reclaim callbacks through `dm-zoned.h`, especially `dmz_schedule_reclaim()` and backing-device health checks.
- Kernel xarray, RB tree, lists, shrinker, pages, bios, wait-bit primitives, rwsem/mutex/spinlock, CRC32, UUID helpers, and NOIO allocation contexts.

## Risks And Invariants

- The two-set metadata protocol assumes the primary remains clean until the log/secondary set is fully durable.
- `mblk_sem` prevents metadata flush from racing with target metadata mutation; `map_lock` protects the mapping table and all zone lists.
- Active zones cannot be reclaimed. Reclaim uses `DMZ_RECLAIM`, zone refcounts, termination bits, and wait queues to avoid moving data under I/O.
- Mapping-table entries, zone `chunk` fields, `bzone` back-pointers, zone list membership, and valid-block weights must remain consistent or reads may return stale data or zeros incorrectly.
- Sequential zone write pointers are authoritative for append-only data placement; write errors trigger re-report and bitmap invalidation to avoid trusting unwritten blocks.
- Regular cache devices in multi-device mode are emulated as cache zones, while tertiary superblocks and offsets bind all devices into one metadata set.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-zoned-metadata.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-zoned-reclaim.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-zoned-reclaim.c

## Scope

This file implements background reclaim for the dm-zoned target. Reclaim frees cache/random zones and buffer zones by copying still-valid blocks to other zones, merging validity metadata, remapping chunks, and flushing metadata, with throttling based on free-zone pressure and target idleness.

## Public And Internal APIs Covered

- Lifecycle/control: `dmz_ctr_reclaim()`, `dmz_dtr_reclaim()`, `dmz_suspend_reclaim()`, `dmz_resume_reclaim()`.
- Scheduling/accounting: `dmz_reclaim_bio_acc()`, `dmz_schedule_reclaim()`.
- Work function: `dmz_reclaim_work()`.
- Copy/reclaim helpers: `dmz_reclaim_copy()`, `dmz_reclaim_align_wp()`, `dmz_reclaim_buf()`, `dmz_reclaim_seq_data()`, `dmz_reclaim_rnd_data()`, `dmz_reclaim_empty()`, `dmz_do_reclaim()`.
- Policy helpers: `dmz_reclaim_percentage()`, `dmz_should_reclaim()`, `dmz_target_idle()`.
- `dm_kcopyd` completion: `dmz_reclaim_kcopy_end()`.

## Control Flow And Behavior

- `dmz_ctr_reclaim()` allocates one reclaim context for a device index, creates a throttled `dm_kcopyd` client, creates an ordered reclaim workqueue, and queues immediate reclaim work.
- Reclaim is considered idle after 10 seconds without target bio accounting. When idle, reclaim can run broadly; when busy, it starts only if unmapped cache/random zones fall below low-watermark pressure.
- `dmz_reclaim_work()` exits if a device is dying, computes free-zone percentage, configures kcopyd throttle, runs one reclaim attempt, checks devices after non-interrupt errors, and reschedules if reclaim is still needed.
- `dmz_do_reclaim()` asks metadata for a reclaim-locked candidate. Empty random/cache zones are freed directly. Weighted random/cache data zones are copied to a free sequential or fallback random zone. Buffered sequential zones either merge buffer into data or data into buffer depending on valid-block positions.
- `dmz_reclaim_copy()` iterates valid extents from the source zone, optionally zero-fills holes to advance a sequential destination's write pointer, submits synchronous `dm_kcopyd` copies, checks for dying devices, and honors reclaim termination requests.
- `dmz_reclaim_buf()` copies a buffer zone back into its sequential data zone at/after the data write pointer, merges valid blocks, invalidates/frees the buffer, and clears the reclaim lock.
- `dmz_reclaim_seq_data()` copies a sequential data zone into its buffer zone, merges valid blocks, frees the old data zone, and remaps the chunk to the buffer zone.
- `dmz_reclaim_rnd_data()` allocates a free sequential zone, or a random/cache fallback when cache zones exist, copies valid blocks, copies validity metadata, frees the old data zone, and remaps the chunk.
- Successful reclaim flushes metadata before reporting success.

## State And Data Structures

- `struct dmz_reclaim` stores metadata, delayed work/workqueue, kcopyd client/throttle/error, device index, state flags, and last access time.
- `DMZ_RECLAIM_KCOPY` marks an in-flight kcopyd operation and is waited on via bit wait queues.
- Watermark constants control policy: idle period, low free-zone percentage, and high free-zone percentage.

## Dependencies

- dm-zoned metadata APIs for zone selection, validity bitmap operations, map/unmap/free, flush locking, and free-zone counts.
- `dm_kcopyd` for copying valid extents between zones.
- Block APIs for zeroout when aligning sequential-zone write pointers.
- Kernel delayed workqueues, bit wait/wakeup, jiffies timing, and module infrastructure.

## Risks And Invariants

- Reclaim must hold metadata/map/flush locks in the right order around metadata mutations and release the zone reclaim lock exactly once.
- Sequential destinations require writes at the write pointer; holes are zeroed so later copied extents remain sequential.
- Candidate zones may become active or be requested to terminate; active/reclaim state prevents data movement under live I/O.
- Valid-block bitmap merge/copy must happen only after data copying succeeds, and metadata must be flushed before reclaimed zones are considered safely reusable.
- If free sequential zones are exhausted, reclaim may need to reclaim a buffered sequential zone first to make future random-zone reclaim possible.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-zoned-reclaim.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-zoned-target.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-zoned-target.c

## Scope

This file implements the Device Mapper `zoned` target. It exposes a regular block device backed by one zoned device or by a regular cache device plus zoned devices, routes reads/writes/discards through dm-zoned metadata mappings, serializes work per logical chunk, manages flush/reclaim workers, and reports target status.

## Public And Internal APIs Covered

- DM target entry points: `dmz_ctr()`, `dmz_dtr()`, `dmz_map()`, `dmz_io_hints()`, `dmz_prepare_ioctl()`, `dmz_suspend()`, `dmz_resume()`, `dmz_iterate_devices()`, `dmz_status()`, `dmz_message()`.
- Module lifecycle: `dmz_init()` and `dmz_exit()`.
- Backing-device health helpers exported through the header: `dmz_bdev_is_dying()`, `dmz_check_bdev()`.
- Bio/chunk processing: `dmz_queue_chunk_work()`, `dmz_chunk_work()`, `dmz_handle_bio()`, read/write/discard helpers, clone submission and completion.
- Flush processing: `dmz_flush_work()`.
- Device setup helpers: `dmz_get_zoned_device()`, `dmz_put_zoned_device()`, `dmz_fixup_devices()`.

## Control Flow And Behavior

- Constructor accepts one or more devices. A single-device table must use a zoned block device. A multi-device table uses the first regular block device as cache zones and all later devices as zoned devices with matching zone sizes.
- Device setup rejects partial target offsets, records capacity/name/dev index, computes per-device zone counts and zone offsets, initializes metadata, sets target length to the number of mappable chunks, and creates biosets, chunk workqueue, flush workqueue, and per-device reclaim contexts.
- `dmz_map()` rejects I/O if any backing device is dying, ignores non-write empty bios, enforces 4 KiB dm-zoned block alignment, handles empty write bios as flush requests, splits bios at zone/chunk boundaries, and queues work for the bio's chunk.
- `dmz_queue_chunk_work()` uses a radix tree keyed by chunk number so all bios targeting the same chunk are serialized through one `dm_chunk_work`. References keep a work item alive while queued bios and the workqueue own it.
- `dmz_handle_bio()` takes the metadata read lock, obtains or allocates the chunk mapping, activates the zone, records reclaim access, dispatches by operation, releases the mapping, completes the original bio context, and unlocks metadata.
- Reads from unmapped chunks are zero-filled. Reads from mapped chunks consult valid-block bitmaps in the data zone and then optional buffer zone; valid extents are cloned to the correct backing zone and holes are zero-filled.
- Writes to random/cache zones or sequential zones exactly at the write pointer are direct writes. Unaligned writes to sequential zones allocate/use a random/cache buffer zone. Direct and buffered writes update valid-block bitmaps and invalidate overlapping stale blocks in the peer zone.
- Discards invalidate valid blocks in data and buffer zones and do nothing for unmapped chunks.
- `dmz_submit_bio()` clones the original bio to the selected zone/device, advances the original bio, increments per-bio context references, submits the clone, and advances sequential write pointers for write clones.
- Completion records backing-device check-needed on errors, marks sequential write errors for failed writes to sequential zones, deactivates zones, and completes the original bio when all clones finish.
- Flush work periodically and on empty-write flushes calls `dmz_flush_metadata()` and completes queued flush bios.
- Suspend flushes chunk work, stops reclaim, and cancels flush work. Resume restarts flush and reclaim work. The `reclaim` target message schedules reclaim on all devices.

## State And Data Structures

- `struct dmz_target` stores DM devices, dm-zoned device descriptors, metadata pointer, chunk radix tree/lock/workqueue, clone bioset, and flush list/workqueue.
- `struct dmz_bioctx` is per-original-bio context containing current backing device, active zone, original bio, and reference count.
- `struct dm_chunk_work` serializes bios for one logical chunk with a work item, refcount, chunk id, target pointer, and bio list.
- Target type `dmz_type` is named `zoned`, version `{2, 0, 0}`, and has `DM_TARGET_SINGLETON | DM_TARGET_MIXED_ZONED_MODEL`.

## Dependencies

- dm-zoned metadata and reclaim APIs from `dm-zoned.h`.
- Device Mapper target/device APIs, target status/messages, and `dm_accept_partial_bio()`.
- Linux block APIs for bio cloning/submission, zone geometry, queue limits, disk events, flush/discard/write-zeroes flags, biosets, workqueues, radix tree, and refcounts.

## Risks And Invariants

- All bios for the same chunk must be serialized; metadata valid-block maps are not independently protected against concurrent same-chunk mutation.
- The original bio is advanced as clones are submitted, so reference counting in `dmz_bioctx` must match every clone plus the original completion path.
- Sequential zone `wp_block` is advanced optimistically on write submission; later errors are recorded as `DMZ_SEQ_WRITE_ERR` so metadata can revalidate the actual device write pointer.
- Reads must prefer the zone whose bitmap marks a block valid and zero-fill invalid/unwritten regions.
- Device health flags switch the target into failing-I/O behavior when queues die or media-change events indicate offline backing devices.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-zoned-target.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-zoned.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-zoned.h

## Scope

This header defines the shared dm-zoned geometry constants, device and zone descriptors, zone state flags/accessors, logging helpers, and cross-file function prototypes used by `dm-zoned-target.c`, `dm-zoned-metadata.c`, and `dm-zoned-reclaim.c`.

## APIs And Constants

- Fixed logical block geometry: 4 KiB `DMZ_BLOCK_SIZE`, block/sector conversion macros, and bio-to-block/chunk helpers.
- Core structs: `struct dmz_dev` and `struct dm_zone`, plus opaque declarations for `dmz_metadata` and `dmz_reclaim`.
- Device flags: `DMZ_BDEV_DYING`, `DMZ_CHECK_BDEV`, `DMZ_BDEV_REGULAR`.
- Zone flags: cache/random/sequential type, offline/read-only condition, metadata/data/buffer/reserved use, reclaim state, sequential write error, and reclaim termination.
- Accessor macros: `dmz_is_cache()`, `dmz_is_rnd()`, `dmz_is_seq()`, `dmz_is_empty()`, `dmz_is_offline()`, `dmz_is_readonly()`, `dmz_in_reclaim()`, `dmz_is_meta()`, `dmz_is_buf()`, `dmz_is_data()`, `dmz_weight()`, and others.
- Metadata API prototypes for construction, locking, flushing, geometry, mapping/allocation, reclaim selection, and valid-block bitmap operations.
- Reclaim API prototypes for construction, suspend/resume, bio accounting, and scheduling.
- Target health prototypes: `dmz_bdev_is_dying()` and `dmz_check_bdev()`.
- Inline zone refcount helpers: `dmz_activate_zone()`, `dmz_deactivate_zone()`, and `dmz_is_active()`.

## State And Data Structures

- `struct dmz_dev` describes one backing device with block device pointer, metadata/reclaim back-pointers, name/UUID, capacity, index, zone count/offset, flags, zone size, and mapped/unmapped random/sequential zone lists and counters.
- `struct dm_zone` describes one logical dm-zoned zone with list linkage, parent device, flags, activation refcount, global zone id, write-pointer block, valid-block weight, mapped chunk id, and optional buffer/data peer pointer.
- A sequential data zone's `bzone` points to its random/cache buffer zone; a buffer zone's `bzone` points back to the data zone.

## Dependencies

- Linux block, Device Mapper, kcopyd, list, spinlock, mutex, workqueue, rwsem, RB tree, radix tree, and shrinker headers.
- The implementation files rely on these declarations to avoid circular dependencies among target, metadata, and reclaim code.

## Risks And Invariants

- All dm-zoned code assumes a 4 KiB block size regardless of backing-device sector size.
- Zone flags are bit positions in `unsigned long flags`; flag order is part of the local ABI between the header and implementation files.
- `dmz_deactivate_zone()` also accounts target activity to reclaim before decrementing the zone refcount, so callers should use the inline helper rather than raw atomic operations.
- The `bzone` bidirectional relationship must be maintained consistently by metadata mapping/unmapping and reclaim.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-zoned.h -->