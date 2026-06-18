# Group Research: Device Mapper cache and clone target sources

This group covers Linux Device Mapper cache target I/O routing and metadata commits, dm-clone persistent hydration metadata, dm-clone target-side hydration scheduling, and core internal DM table/device structures.

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-target.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-target.c

## Purpose
Implements the Device Mapper `cache` target, which maps an origin device through a faster cache device using persistent metadata, a cache replacement policy, dirty/discard tracking, background migration, and writeback/writethrough/passthrough I/O modes.

## Main Interfaces
- Target lifecycle: `cache_ctr()`, `cache_dtr()`, `cache_preresume()`, `cache_resume()`, `cache_postsuspend()`.
- I/O path: `cache_map()`, `cache_end_io()`, `map_bio()`, `process_deferred_bios()`.
- Metadata persistence: `commit()`, `commit_op()`, `sync_metadata()`, `write_dirty_bitset()`, `write_discard_bitset()`, `write_hints()`.
- Migration/invalidation: `mg_start()`, `mg_lock_writes()`, `mg_copy()`, `mg_update_metadata()`, `invalidate_start()`, `invalidate_cblock()`.
- User/control reporting: `cache_status()`, `cache_message()`, `cache_io_hints()`, `cache_iterate_devices()`.

## Control Flow
Incoming bios are converted to cache origin blocks and routed through `map_bio()`. Flushes and discards are deferred to the worker; partial trailing blocks bypass cache and go to origin. Normal bios acquire a bio-prison cell so concurrent access to the same block can be serialized against migration or invalidation.

Policy lookup decides whether a bio is a hit, miss, or should trigger background work. Misses go to origin; hits normally go to cache, with writeback marking cache blocks dirty. Writethrough writes to clean cached blocks are cloned to both origin and cache. Passthrough mode routes to origin and invalidates cached blocks on writes.

Background policy work drives promotions, demotions, and writebacks. Migrations lock writes first, quiesce conflicting bios, copy with kcopyd or use an overwrite optimization, upgrade to a read/write exclusion lock, update metadata, commit when required, then release detained bios.

## State And Synchronization
`struct cache` owns metadata, origin/cache devices, policy state, dirty/discard bitsets, stats, bio prison, kcopyd client, workqueue, delayed commit waker, migration mempool, deferred bio lists, and an I/O tracker. A spinlock protects deferred bios and discard state. The bio prison serializes per-block accesses. `background_work_lock` prevents new background migrations during suspend. The `batcher` groups bios and continuations behind metadata commits.

## Integration Points
Uses `dm-cache-metadata` for persistent mappings, dirty bits, discards, stats, and hints; `dm_cache_policy` for lookup and replacement decisions; `dm-bio-prison-v2` for per-block exclusion; `dm-kcopyd` for data movement; and Device Mapper target hooks for table status, messages, queue limits, and device iteration.

## Notable Behaviors
- Supports `writeback`, `writethrough`, `passthrough`, `metadata2`, and `no_discard_passdown` features.
- Refuses passthrough construction unless all cached blocks are clean.
- FUA and flush bios are issued only after needed metadata commits.
- Suspend drains workers, requeues deferred bios if needed, writes dirty/discard/hint/stat metadata, and commits clean-shutdown state.
- Cache shrinking is refused if any block that would be dropped is dirty.
- `invalidate_cblocks` messages are only allowed in passthrough mode.

## Risks And Review Focus
- Commit ordering is central to correctness, especially demotion, FUA, flush, and suspend paths.
- Dirty-bit and policy state must stay synchronized across migration success and failure.
- Bio-prison lock levels and release paths are sensitive to races with migration, invalidation, and deferred bios.
- Discard tracking uses a coarser discard-block bitmap and must preserve range/granularity correctness.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-target.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-clone-metadata.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-clone-metadata.c

## Purpose
Implements persistent metadata for the Device Mapper `clone` target. It tracks which destination regions have been hydrated from the source device using an on-disk bitset plus an in-memory region bitmap and transaction-local dirty maps.

## Main Interfaces
- Open/close: `dm_clone_metadata_open()`, `dm_clone_metadata_close()`.
- Region updates: `dm_clone_set_region_hydrated()`, `dm_clone_cond_set_range()`.
- Commit/rollback: `dm_clone_metadata_pre_commit()`, `dm_clone_metadata_commit()`, `dm_clone_metadata_abort()`.
- Recovery/mode control: `dm_clone_reload_in_core_bitset()`, `dm_clone_metadata_set_read_only()`, `dm_clone_metadata_set_read_write()`.
- Queries: `dm_clone_is_hydration_done()`, `dm_clone_is_region_hydrated()`, `dm_clone_is_range_hydrated()`, `dm_clone_nr_of_hydrated_regions()`, `dm_clone_find_next_unhydrated_region()`.
- Metadata sizing: `dm_clone_get_free_metadata_block_count()`, `dm_clone_get_metadata_dev_size()`.

## Control Flow
Opening metadata creates a block manager, detects whether the superblock is all zeroes, then either formats fresh metadata or validates and opens existing metadata. Formatting creates a transaction manager, space map, empty disk bitset sized to `nr_regions`, and writes the superblock.

Runtime hydration updates set bits in the in-memory `region_map` and current dirty map under `bitmap_lock`. `pre_commit` atomically swaps the active dirty map so new hydration updates land in the next transaction while the old map is committed. `commit` flushes only dirty bitset words to disk, flushes the bitset cache, pre-commits the transaction manager, copies the space-map root, updates the superblock, and commits.

## State And Synchronization
`struct dm_clone_metadata` owns the block device, target geometry, persistent-data managers, disk bitset root, in-memory `region_map`, two dirty-map sets, and read-only/fail state. `bitmap_lock` protects bitmap mutation and dirty-map selection. `lock` serializes open-format/commit/abort/reload and space-map queries. Dirty maps separate fast interrupt-safe region updates from slower blocking metadata I/O.

## Integration Points
Uses Device Mapper persistent-data components: block manager, transaction manager, metadata space map, and disk bitset. The clone target calls these functions to mark kcopyd-completed, overwrite-completed, or discarded regions as hydrated and to enforce destination flush before metadata commit.

## Notable Behaviors
- Metadata version support is currently version 1 only.
- The metadata device is formatted only when the superblock is all zeroes.
- Region and target size must match existing metadata on reopen.
- `dm_clone_set_region_hydrated()` is nonblocking and safe for interrupt context.
- `dm_clone_cond_set_range()` uses spin locks but is documented as unsafe from disabled-interrupt contexts.
- Abort destroys and recreates persistent-data structures from the last committed state; failure enters `fail_io`.

## Risks And Review Focus
- The two-phase dirty-map swap is durability-critical: clone must flush destination data before committing hydrated bits.
- `dm_clone_reload_in_core_bitset()` intentionally bypasses `bitmap_lock` and must only be used after read-only transition.
- Dirty map failure leaves no clean spare dirty map, causing later `pre_commit` validation failure.
- Region range validation must avoid overflow and out-of-bounds bit operations.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-clone-metadata.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-clone-metadata.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-clone-metadata.h

## Purpose
Declares the public internal API used by `dm-clone-target.c` to manage clone metadata, region hydration state, commit/rollback behavior, read-only transitions, and metadata device accounting.

## Main Interfaces
- Constants: `DM_CLONE_METADATA_BLOCK_SIZE`, `DM_CLONE_METADATA_MAX_SECTORS`, warning threshold, and `SPACE_MAP_ROOT_SIZE`.
- Opaque metadata handle: `struct dm_clone_metadata`.
- Mutation APIs: `dm_clone_set_region_hydrated()`, `dm_clone_cond_set_range()`.
- Lifecycle APIs: `dm_clone_metadata_open()`, `dm_clone_metadata_close()`.
- Commit APIs: `dm_clone_metadata_pre_commit()`, `dm_clone_metadata_commit()`.
- Recovery/mode APIs: `dm_clone_reload_in_core_bitset()`, `dm_clone_metadata_abort()`, read-only/read-write setters.
- Query/accounting APIs for hydration completion, region/range state, hydrated counts, next unhydrated region, free metadata blocks, and metadata device size.

## Control Flow
The header documents the two-phase commit contract: first `pre_commit` freezes the current transaction’s dirty region set, then the clone target flushes destination data, then `commit` persists metadata. This ordering ensures a crash cannot expose metadata claiming a region is hydrated before its destination contents are durable.

## State And Synchronization
The comments specify context constraints. Single-region hydration is nonblocking and interrupt-safe. Range hydration is nonblocking but uses `spin_lock_irq()` and must not be called with interrupts disabled. Reloading the in-core bitset may block and must not race with hydration updates unless metadata has first been made read-only.

## Integration Points
This header is consumed by the clone target and backed by `dm-clone-metadata.c`. It also exposes persistent-data metadata limits to constructor code so target validation can warn about oversized metadata devices.

## Notable Behaviors
- Read-only mode causes commit, mutation, and abort operations to reject updates with `-EPERM`.
- Hydration completion can be queried globally, per region, or over a range.
- `find_next_unhydrated_region()` supports background hydration scanning.

## Risks And Review Focus
- Callers must honor the commit sequence and reload synchronization rules from the comments.
- Context-safety differences between single-region and range updates are easy to misuse.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-clone-metadata.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-clone-target.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-clone-target.c

## Purpose
Implements the Device Mapper `clone` target, which presents a destination device as a gradually hydrated clone of a read-only source device. Reads from unhydrated regions go to the source; writes trigger immediate hydration or overwrite optimization; background work eventually hydrates all regions.

## Main Interfaces
- Target lifecycle: `clone_ctr()`, `clone_dtr()`, `clone_postsuspend()`, `clone_resume()`.
- I/O path: `clone_map()`, `clone_endio()`, `issue_bio()`, `process_discard_bio()`.
- Hydration: `hydrate_bio_region()`, `hydration_copy()`, `hydration_overwrite()`, `hydration_complete()`, `do_hydration()`.
- Metadata commit: `commit_metadata()`, `process_deferred_flush_bios()`, `process_deferred_discards()`.
- Reporting/control: `clone_status()`, `clone_message()`, `clone_io_hints()`, `clone_iterate_devices()`.

## Control Flow
`clone_map()` increments in-flight I/O, handles flushes first, offsets data bios to target-relative sectors, and special-cases discards. Hydrated-region I/O is sent to the destination. Reads from unhydrated regions are sent to the source. Writes to unhydrated regions are remapped to destination and attach to a region hydration descriptor.

Per-region hydration descriptors are stored in a hash table. If a region is already hydrating, additional bios are deferred on that descriptor. If a full-region write arrives, it can overwrite the destination directly without copying from source. Otherwise kcopyd copies the region from source to destination. Completion updates metadata, completes overwrite bios, and issues deferred bios.

Background hydration scans for unhydrated regions, avoids starting while foreground I/O is in flight, respects `hydration_threshold`, batches adjacent regions up to `hydration_batch_size`, and resumes from `hydration_offset`.

## State And Synchronization
`struct clone` owns metadata, source/destination devices, region geometry, commit mutex, hydration hash table, hydration mempool, deferred bio lists, workqueue, delayed waker, kcopyd client, mode, flags, and in-flight counters. Hash buckets each have IRQ-safe spinlocks. `commit_lock` serializes metadata commit and failure handling. `hydrations_in_flight` and `hydration_stopped` coordinate suspend with active hydration.

## Integration Points
Uses `dm-clone-metadata` for region state and commit semantics, `dm-kcopyd` for source-to-destination copies, Device Mapper target hooks for mapping/status/messages/queue limits, and block-layer flush/discard APIs. Queue-limit code inherits discard limits from the destination device when passdown is enabled.

## Notable Behaviors
- Features include `no_hydration` and `no_discard_passdown`.
- Core tunables include `hydration_threshold` and `hydration_batch_size`, adjustable by messages.
- Discards over unhydrated regions mark those regions hydrated without copying, then optionally pass discard to the destination.
- Metadata commits perform `pre_commit`, flush the destination block device, then commit metadata.
- FUA overwrite completions and PREFLUSH bios are deferred until after metadata commit.
- Suspend cancels the periodic waker, stops new background hydration, waits for active hydrations, flushes the workqueue, and commits metadata.

## Risks And Review Focus
- Suspend/hydration ordering depends on memory barriers around `hydrations_in_flight` and `DM_CLONE_HYDRATION_SUSPENDED`.
- Metadata failure handling aborts, switches to read-only, and reloads the bitmap; all later I/O paths must respect mode changes.
- Hash-table insertion/removal must avoid duplicate hydration descriptors for the same region.
- Deferred flush, FUA completion, discard, and normal bio lists have different completion/submit semantics and must not be merged incorrectly.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-clone-target.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-core.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-core.h

## Purpose
Defines Device Mapper core internal structures and helpers used by `dm.c`, `dm-rq.c`, and `dm-table.c`. It explicitly warns that DM targets must not directly dereference `mapped_device` or `dm_table` internals.

## Main Interfaces
- Core structures: `struct mapped_device`, `struct dm_table`, `struct dm_target_io`, `struct dm_io`.
- Flags: `DMF_BLOCK_IO_FOR_SUSPEND`, `DMF_SUSPENDED`, `DMF_FROZEN`, `DMF_FREEING`, `DMF_DELETING`, `DMF_NOFLUSH_SUSPENDING`, `DMF_DEFERRED_REMOVE`, `DMF_SUSPENDED_INTERNALLY`, `DMF_POST_SUSPENDING`, `DMF_EMULATE_ZONE_APPEND`.
- Helpers: `dm_get_size()`, `dm_get_stats()`, `dm_emulate_zone_append()`, `dm_io_inc_pending()`, `dm_get_completion_from_kobject()`, `dm_message_test_buffer_overflow()`.
- Declarations: discard/write-same/write-zeroes disabling, pending I/O decrement, module-param access, and global event signaling.

## Control Flow
The header does not implement target behavior; it establishes the shared in-memory shape of mapped devices, tables, cloned target bios, and original bio tracking. Inline helpers expose safe access to capacity, stats, zone-append emulation state, pending I/O count increment, kobject completion lookup, and message-buffer overflow checks.

## State And Synchronization
`mapped_device` carries suspend/table/device locks, RCU table pointer, queue/type lock, holder/open counts, deferred bio list, event queues, mempools, workqueue, stats, blk-mq tag set, SRCU I/O barrier, optional zoned state, and optional IMA measurements. `dm_table` stores the btree target index, target array, device list, event callback, mempools, mode, integrity, and optional inline crypto profile. `dm_io` and `dm_target_io` track original and cloned bio completion state.

## Integration Points
This is an internal dependency for DM core implementation files, not ordinary targets. It bridges block-layer types, DM public declarations, IMA measurement support, blk-mq, inline encryption, zoned block devices, and block trace events.

## Notable Behaviors
- `dm_table` supports up to `DM_TABLE_MAX_DEPTH` btree levels.
- `dm_target_io` embeds the cloned `bio` as its last field.
- `dm_io` embeds the first target I/O object and tracks aggregate completion status.
- Global DM event state is declared for cross-device event notification.

## Risks And Review Focus
- The internal-only boundary matters: target code should use exported helpers rather than depending on these layouts.
- Flag bits coordinate suspend, remove, noflush suspend, and zone append emulation, so changes have broad core behavior impact.
- Embedded bio/layout assumptions in `dm_target_io` and `dm_io` are allocation-sensitive.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-core.h -->