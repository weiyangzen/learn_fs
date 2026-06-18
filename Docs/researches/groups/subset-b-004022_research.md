# subset-b-004022 research

Grouped research for the device-mapper cache and clone sources under `sources/distributed-fs/ceph-client/drivers/md`. Each section preserves the source path and is bounded for reconciliation into the per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-target.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-cache-target.c

## Purpose
`dm-cache-target.c` implements the Linux device-mapper `cache` target. It presents an origin device through a cache device and persistent metadata device, using cache policy plugins to decide when origin blocks (`oblock`) are mapped into cache blocks (`cblock`), when dirty cache blocks are written back, and when mappings are invalidated. It supports writeback, writethrough, and passthrough modes; discard tracking; policy hints; target table/status/message handling; suspend/resume persistence; and module registration for target version `{2, 4, 0}`.

## Important APIs, Types, And Functions
The central state object is `struct cache`, which owns the target, metadata handle (`struct dm_cache_metadata *cmd`), three devices, cache/origin sizing, dirty/discard/invalid bitsets, policy object, bio prison, kcopyd client, workqueue, migration mempool, deferred bios, stats, background-work gating, and the commit `batcher`. `struct per_bio_data` stores per-bio target-bio number, bio prison cell, tick state, hook information, and accounting length. `struct dm_cache_migration` represents promotion, demotion, writeback, and invalidation state.

The target entry points are `cache_ctr`, `cache_dtr`, `cache_map`, `cache_end_io`, `cache_postsuspend`, `cache_preresume`, `cache_resume`, `cache_status`, `cache_message`, `cache_iterate_devices`, and `cache_io_hints`. Metadata and state helpers include `set_cache_mode`, `abort_transaction`, `metadata_operation_failed`, `commit`, `sync_metadata`, `write_dirty_bitset`, `write_discard_bitset`, and `write_hints`. Mapping and migration logic is concentrated in `map_bio`, `process_bio`, `process_flush_bio`, `process_discard_bio`, `mg_start`, `mg_lock_writes`, `mg_copy`, `mg_full_copy`, `mg_upgrade_lock`, `mg_update_metadata`, `mg_complete`, `invalidate_start`, and `invalidate_cblock`.

## Control Flow
Construction parses `<metadata dev> <cache dev> <origin dev> <block size> <features> <policy> <policy args>`, opens devices, validates block size, calculates cache and origin block counts, creates the policy, opens or formats metadata through `dm_cache_metadata_open`, allocates bitsets/mempools/workqueue/prison/kcopyd, initializes stats and the commit batcher, and starts with background work blocked until resume. `cache_preresume` resizes metadata if the cache device shrank, loads mappings into the policy and dirty bitset, marks mappings beyond the target as invalid, removes those invalid mappings from metadata, then loads discard state. `cache_resume` enables background work and starts the periodic waker.

Normal `cache_map` initializes per-bio data, bypasses partial trailing origin blocks, defers flushes and discards, then calls `map_bio`. `map_bio` detains the origin block in the bio prison, asks the policy for a mapping or background work, updates hit/miss stats, and remaps misses to origin. Hits are remapped to cache, to origin and cache for clean writethrough writes, or to origin in passthrough. Writeback full-block overwrites and writes to discarded oblocks can avoid a source copy by starting a promotion with the bio as the overwrite payload. FUA bios are queued through the batcher so metadata is committed before the bio is issued.

Migration is asynchronous. Background work comes from `policy_get_background_work`; foreground overwrite promotions can come from `policy_lookup_with_work`. `mg_start` takes a background-work read lock, allocates a migration, acquires a bio-prison lock at write or read/write level, quiesces conflicting bios when needed, copies through kcopyd or submits an overwrite bio, upgrades the lock to block reads and writes, updates metadata, commits when demotion requires it, completes policy work, unlocks the cell, and requeues detained bios. Invalidation, used by passthrough writes and the `invalidate_cblocks` message, locks the oblock, removes the mapping from policy and metadata, commits, then issues the waiting write to origin.

## State And Persistence Behavior
Persistent state lives in dm-cache metadata: cblock-to-oblock mappings, dirty bits, discard bits, policy hints, stats, and clean-shutdown metadata. In-memory mirrors include `dirty_bitset`, `discard_bitset`, `invalid_bitset`, policy state, and accounting counters. Dirty state is set on writeback writes and cleared after successful demotion or writeback. Discard state is tracked at a coarser dblock size chosen to cap memory use, and is persisted on suspend.

`sync_metadata` writes dirty bits, discard bits, stats, and policy hints, then commits. If one of the pre-commit writes fails, it still commits but does not mark clean shutdown, which forces conservative dirty reconstruction on reload. Metadata failures abort the current transaction, set `needs_check`, and switch the cache to read-only mode; fail mode is terminal. Passthrough resume is rejected after unclean shutdown, and passthrough cannot load dirty mappings. Demotions commit before releasing mappings so a reused cache block cannot be exposed as stale data after crash recovery.

## Dependencies And Integration Points
This target depends on device-mapper core target hooks, `dm-cache-metadata`, cache policy plugins, `dm-bio-prison-v2` for per-oblock exclusion, `dm-kcopyd` for block copying, `dm-io-tracker` for migration throttling, `dm-cache-background-tracker`, block queue discard limits, biosets for writethrough duplicate writes, and kernel workqueues/mempools/bitsets. It reports table, info, and IMA status; accepts target messages for `migration_threshold` and `invalidate_cblocks`; emits table events on mode switch and dirty-count transitions; and registers through `dm_register_target`.

## Risks And Edge Cases
Crash consistency depends on ordering data copies, metadata updates, and commits; demotion and FUA/flush handling are especially sensitive. The bio prison lock levels must prevent writes during copies and reads during metadata switch-over, otherwise callers may observe stale or mixed data. Passthrough is intentionally constrained because dirty mappings or unclean metadata can break coherency. Resize and shrink paths reject dirty out-of-range mappings but allow clean out-of-range mappings to be invalidated. Discard handling has an explicit FIXME about concurrent discard versus other I/O and uses coarse-grained discard blocks, so tests should cover overlapping I/O/discard behavior. Metadata read-only/fail transitions must not allow messages or writes to mutate metadata.

## Test Signals
Useful signals are dmsetup table/status output for all three modes, metadata mode (`rw`, `ro`, `Fail`) and `needs_check`, dirty count changes, policy residency, hit/miss counters, migration/demotion/promotion/writeback counters, discard passdown limits, and I/O behavior across suspend/resume. Targeted tests should exercise writeback crash recovery, demotion commit ordering, writethrough duplicate-bio handling, passthrough invalidation, FUA and REQ_PREFLUSH batching, discard persistence, cache-device shrink with dirty and clean out-of-range mappings, metadata failure injection, and policy message handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-target.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-clone-metadata.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-clone-metadata.c

## Purpose
`dm-clone-metadata.c` implements the persistent metadata layer for the device-mapper `clone` target. It stores and retrieves a region hydration bitmap on a metadata device, tracks in-memory dirty updates for the current metadata transaction, validates and writes the metadata superblock, and exposes nonblocking update APIs that the target can call from I/O completion context.

## Important APIs, Types, And Functions
The on-disk format is `struct superblock_disk`, containing checksum, block number, magic, version, metadata space-map root, `region_size`, `target_size`, and `bitset_root`. `struct dm_clone_metadata` owns the metadata block device, region geometry, two dirty maps, the active and committing dirty-map pointers, the in-core `region_map`, block manager, space map, transaction manager, disk bitset metadata, locks, and terminal flags (`hydration_done`, `fail_io`, `read_only`). `struct dirty_map` has `dirty_words`, `dirty_regions`, and a `changed` flag.

Public functions implement the header contract: `dm_clone_metadata_open`, `dm_clone_metadata_close`, `dm_clone_set_region_hydrated`, `dm_clone_cond_set_range`, `dm_clone_metadata_pre_commit`, `dm_clone_metadata_commit`, `dm_clone_reload_in_core_bitset`, `dm_clone_changed_this_transaction`, `dm_clone_metadata_abort`, read-only/read-write mode setters, hydration query helpers, `dm_clone_find_next_unhydrated_region`, and metadata-space accounting helpers. Internal superblock and transaction helpers include `sb_prepare_for_write`, `sb_check`, `__superblock_all_zeroes`, `__open_metadata`, `__format_metadata`, `__copy_sm_root`, `__prepare_superblock`, `__load_bitset_in_core`, `__flush_dmap`, and `__metadata_commit`.

## Control Flow
Open allocates `struct dm_clone_metadata`, computes `nr_regions` and `nr_words`, allocates the in-core region bitmap, creates a persistent block manager, then either formats an all-zero metadata device or opens existing metadata. Formatting creates a transaction manager and metadata space map, creates and resizes an empty disk bitset to `nr_regions`, pre-commits metadata blocks, copies the space-map root, writes the superblock, and commits it. Opening validates the superblock, checks that target and region sizes match the table, opens the transaction manager from the stored space-map root, initializes disk-bitset access, and records the bitset root.

After open, `__load_bitset_in_core` flushes the disk-bitset cache and walks all region bits into `region_map`; dirty maps are allocated and initialized. Hydration updates call `dm_clone_set_region_hydrated` for one region or `dm_clone_cond_set_range` for a range. Both update `region_map`, set the corresponding dirty region bits, set dirty word bits, and mark the active dirty map changed under `bitmap_lock`; the single-region variant uses irqsave and is documented as interrupt-context safe.

Commits are two phase. `dm_clone_metadata_pre_commit` takes the write semaphore, rejects read-only/fail state, swaps `current_dmap` to the clean inactive map under the bitmap spinlock, and marks the old map as `committing_dmap`. New hydration updates now land in the next transaction. `dm_clone_metadata_commit` flushes only the bits recorded in `committing_dmap`, flushes disk-bitset and transaction-manager state, writes a fresh superblock with updated roots, clears the dirty map's changed flag, and releases `committing_dmap`.

## State And Persistence Behavior
The persistent source of truth is the disk bitset referenced by the superblock. `region_map` is a fast in-core copy used by I/O path queries and background hydration scanning. The two dirty maps are the crash-consistency bridge: one map is active for new completions while the other is being committed. The target is expected to flush destination data after `pre_commit` and before `commit`, so persisted hydration bits only describe regions whose destination contents reached stable storage.

`dm_clone_metadata_abort` destroys and recreates persistent data structures from the last committed superblock without formatting. If that fails, `fail_io` is set, after which queries that need the space map fail and close avoids destroying invalid persistent structures. `dm_clone_reload_in_core_bitset` reloads the disk bitmap after abort/read-only transition; it deliberately does not take `bitmap_lock` because it can block, and the header documents that callers must prevent concurrent bitmap writers by setting read-only first.

## Dependencies And Integration Points
This file depends on persistent-data primitives: `dm-block-manager`, `dm-transaction-manager`, `dm-space-map`, and `dm-bitset`. It is consumed by `dm-clone-target.c`, which uses the nonblocking hydration update calls from kcopyd and bio completion paths and wraps commits with destination-device flushes. It also integrates with device-mapper logging through `DMERR` and exposes metadata block accounting for target status.

## Risks And Edge Cases
The dirty-map swap assumes the inactive map is clean and that no commit is already in progress; violations return errors and trigger target-level failure handling. The commit path must not persist bits before destination data is durable. `dm_clone_cond_set_range` is not safe in interrupt-disabled contexts because it uses `spin_lock_irq`, while `dm_clone_set_region_hydrated` is irqsave-safe. Range overflow checks and the `2^31` region limit in the target protect bitmap operations. If reload is called while updates can still occur, `region_map` can diverge from dirty maps; the API comments make this a caller responsibility.

## Test Signals
Metadata tests should cover formatting an all-zero device, opening existing metadata, rejecting changed target or region sizes, superblock checksum/magic/version failures, setting single and range hydration bits, two-phase commit with updates arriving between pre-commit and commit, abort/reload behavior, read-only failures, free/total metadata block status, all-regions-hydrated detection, and fault injection in block-manager, bitset, and transaction-manager calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-clone-metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-clone-metadata.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-clone-metadata.h

## Purpose
`dm-clone-metadata.h` is the private interface between the dm-clone target and its persistent metadata implementation. It defines metadata sizing constants, declares the opaque `struct dm_clone_metadata`, and documents the threading and transaction contract for region hydration bitmap updates.

## Important APIs, Types, And Functions
The header defines `DM_CLONE_METADATA_BLOCK_SIZE`, `DM_CLONE_METADATA_MAX_SECTORS`, `DM_CLONE_METADATA_MAX_SECTORS_WARNING`, and `SPACE_MAP_ROOT_SIZE`. The opaque `struct dm_clone_metadata` hides the implementation details from the target. Creation and teardown use `dm_clone_metadata_open` and `dm_clone_metadata_close`. Mutation APIs are `dm_clone_set_region_hydrated` and `dm_clone_cond_set_range`. Transaction APIs are `dm_clone_metadata_pre_commit`, `dm_clone_metadata_commit`, `dm_clone_metadata_abort`, `dm_clone_metadata_set_read_only`, and `dm_clone_metadata_set_read_write`. Query APIs include hydration completion/range checks, hydrated-region count, next-unhydrated lookup, metadata changed state, and metadata block accounting.

## Control Flow Contract
The intended flow is: open metadata for a target size and region size; handle I/O by marking hydrated regions as they become valid on the destination device; periodically call `dm_clone_metadata_pre_commit`; flush destination data; then call `dm_clone_metadata_commit`. After `pre_commit`, subsequent metadata updates belong to the next transaction, allowing the target to commit exactly the bits covered by the data flush. On metadata errors, the target should set metadata read-only, abort, reload the in-core bitset if needed, and avoid future mutating calls until recovery.

## State And Persistence Behavior
The header makes the crash-consistency contract explicit. Hydrated-region bits may be updated without blocking, but they are not durable until the two-phase commit completes. `dm_clone_metadata_pre_commit` freezes the current set of dirty region bits; `dm_clone_metadata_commit` persists them. The target must flush destination data between those phases so committed metadata never claims that a region is hydrated before its data is durable. `dm_clone_reload_in_core_bitset` is reserved for abort/read-only recovery because it performs I/O and rewrites the in-core bitmap without taking the bitmap spinlock.

## Dependencies And Integration Points
The interface includes persistent-data block manager and space-map headers for metadata block sizing and `dm_block_t` types. It is used directly by `dm-clone-target.c` and implemented by `dm-clone-metadata.c`. The comments encode context rules that the target relies on: single-region updates are safe from interrupt context; conditional range updates are nonblocking but not safe when interrupts are already disabled; reload must not run concurrently with mutation.

## Risks And Edge Cases
Callers must respect context restrictions or risk deadlocks and bitmap corruption. Failing to pair pre-commit with destination flush and commit breaks crash consistency. Calling reload while writes are still allowed can lose in-core updates. Read-only mode intentionally makes mutating functions return `-EPERM`, and target error paths must handle that without retry loops that keep accepting writes. The metadata device has maximum and warning sizes; excess space is not part of the managed metadata space.

## Test Signals
Header-level contract tests map to target and metadata integration tests: interrupt-context single-bit updates, non-interrupt range discard updates, FUA/flush-triggered two-phase commits, read-only error propagation, abort-and-reload recovery, hydration completion detection, next-unhydrated scanning, and status queries for free and total metadata blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-clone-metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-clone-target.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-clone-target.c

## Purpose
`dm-clone-target.c` implements the Linux device-mapper `clone` target. It exposes a destination device that is lazily hydrated from a read-only source device. Reads for unhydrated regions come from the source, writes to unhydrated regions trigger immediate hydration or overwrite optimization, background work copies remaining regions, and persistent metadata records which destination regions are already valid.

## Important APIs, Types, And Functions
The central `struct clone` owns target devices, region geometry, metadata handle, commit lock, hydration hash table, mempool, kcopyd client, workqueue, deferred bio lists, counters for in-flight I/O and hydrations, hydration throttles, copied constructor args, and flags. `struct dm_clone_region_hydration` tracks one region hydration, optional overwrite bio, deferred bios waiting for the region, completion status, batch-list linkage, and hash linkage. The hash table serializes concurrent hydrations per region with one spinlock per bucket.

Target methods are `clone_ctr`, `clone_dtr`, `clone_map`, `clone_endio`, `clone_postsuspend`, `clone_resume`, `clone_status`, `clone_message`, `clone_io_hints`, and `clone_iterate_devices`. Hydration logic is in `hydrate_bio_region`, `hydration_copy`, `hydration_overwrite`, `hydration_kcopyd_callback`, `hydration_update_metadata`, `hydration_complete`, `__start_next_hydration`, `__batch_hydration`, and `do_hydration`. Commit and deferred work are handled by `commit_metadata`, `process_deferred_bios`, `process_deferred_discards`, `process_deferred_flush_bios`, `do_worker`, and `do_waker`.

## Control Flow
Construction parses `clone <metadata dev> <destination dev> <source dev> <region size> [features] [core args]`, opens metadata and destination read/write and source read-only, validates power-of-two region size and logical block alignment, computes the region count, opens metadata, allocates the hydration hash table, workqueue, kcopyd client, mempool, and copies table args. It enables flush and discard support and starts with hydration suspended until resume.

`clone_map` increments `ios_in_flight`, kills I/O in fail mode, remaps flushes to destination through `issue_bio`, offsets normal bios to target-relative sectors, and handles discards specially. Hydrated-region bios go to destination. Reads for unhydrated regions go to source. Writes for unhydrated regions are remapped to destination and passed to `hydrate_bio_region`, which either attaches the bio to an existing hydration, notices the region became hydrated, starts a kcopyd copy, or uses full-region overwrite as the hydration data without copying from source.

The worker drains normal deferred bios, processes deferred discards by conditionally marking covered regions hydrated, commits metadata for deferred flush/FUA completions or periodic timeout, and then attempts background hydration. Background hydration scans from `hydration_offset` for unhydrated regions not already in the hash table, batches adjacent regions up to `hydration_batch_size`, and starts kcopyd copies while under `hydration_threshold` and while no foreground I/O is in flight. kcopyd completion updates metadata, removes hash entries, completes overwrite bios, issues deferred bios, wakes suspend waiters when the last hydration exits, and restarts background hydration if enabled and idle.

## State And Persistence Behavior
Hydration state is persisted by `dm-clone-metadata.c`; this target controls when bits become durable. `commit_metadata` serializes with `commit_lock`, calls `dm_clone_metadata_pre_commit`, flushes the destination block device, then calls `dm_clone_metadata_commit`. This ordering ensures the destination regions represented by the committing dirty map are stable before their metadata bits are committed. FUA overwrite completions and REQ_PREFLUSH bios are deferred until after this commit; if the destination was already flushed by commit, a deferred preflush can be completed without submitting another flush.

Runtime state includes the hash table of active hydrations, deferred bio lists for region waits, flush waits, flush completions, and discards, plus `ios_in_flight` and `hydrations_in_flight`. Suspend cancels the periodic waker, sets `DM_CLONE_HYDRATION_SUSPENDED`, uses a memory barrier paired with `do_hydration`, waits for hydrations to drain, flushes the workqueue, and commits metadata. Metadata failures abort the current transaction, switch to read-only, reload the in-core bitset, and may progress to fail mode if recovery fails.

## Dependencies And Integration Points
The target integrates with device-mapper target registration, `dm-clone-metadata`, `dm-kcopyd`, block-layer flush/discard APIs, workqueues, mempools, atomic counters, wait queues, and queue-limit stacking. It exposes target messages `enable_hydration`, `disable_hydration`, `hydration_threshold`, and `hydration_batch_size`. Status reports metadata usage, region size, hydrated/total region counts, in-flight hydrations, feature flags, core args, and metadata mode. `clone_iterate_devices` reports source and destination devices; metadata is not part of data-limit stacking.

## Risks And Edge Cases
Crash consistency relies on deferring FUA and flush completion until metadata commit has flushed destination data. Active hydration hash locking must be correct in process and interrupt contexts because bios can be attached from map paths and completions can remove entries. Background hydration must stop cleanly on suspend; the paired memory barriers around `DM_CLONE_HYDRATION_SUSPENDED` and `hydrations_in_flight` are critical. Full-region overwrite optimization must only mark a region hydrated after the overwrite bio completes successfully. Discards fast-hydrate regions without copying, so discard range alignment and passdown trimming matter. The code intentionally stops background hydration while foreground I/O is in flight, which is a performance tradeoff visible in tests.

## Test Signals
Test coverage should include reads from unhydrated regions, writes that trigger copy hydration, full-region overwrite hydration, concurrent writes/read waits on the same region, adjacent background batching, throttling through `hydration_threshold`, disabling/enabling hydration by message, discard fast hydration with and without passdown, FUA and preflush ordering, periodic commits, suspend/resume drain behavior, metadata failure injection, status output transitions to `ro` and `Fail`, and final all-regions-hydrated table events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-clone-target.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-core.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-core.h

## Purpose
`dm-core.h` is an internal device-mapper header shared by core implementation files such as `dm.c`, `dm-rq.c`, and `dm-table.c`. It defines the private in-memory structures for mapped devices, tables, target I/O clones, original I/O tracking, and core flags. It is explicitly not an API for device-mapper targets to dereference directly.

## Important APIs, Types, And Functions
`struct mapped_device` contains suspend and table-device locks, the live table RCU pointer, queue type and request queue, holder/open counters, immutable-target fields, disk and DAX devices, pending I/O accounting, deferred and requeue work, event state, blk-mq tag set, statistics, internal suspend count, swap-bio throttling, mempools, kobject completion holder, SRCU I/O barrier, and optional zoned/IMA state. Flag bits include suspend/free/delete/no-flush/internal-suspend/post-suspend/emulated-zone-append/queue-stopped states.

`struct dm_table` contains the mapped device, queue mode, btree-style target index arrays, target array, immutable target type, integrity/singleton/flush-bypass booleans, open mode, devices list, event callback, mempools, and optional inline encryption profile. `struct dm_target_io` is embedded before each cloned bio and records clone flags, target bio number, original `dm_io`, target pointer, length pointer, old sector, and the clone bio. `struct dm_io` represents the original bio and embeds the first `dm_target_io`; it tracks accounting flags, status, original bio, mapped sector range, I/O count, and linked-list state for requeue.

Inline helpers include `dm_get_size`, `dm_get_stats`, `dm_emulate_zone_append`, `dm_table_get_target`, `dm_tio_flagged`, `dm_tio_set_flag`, `dm_tio_is_normal`, `dm_io_flagged`, `dm_io_set_flag`, `dm_get_completion_from_kobject`, and `dm_message_test_buffer_overflow`. External declarations include static keys for stats, swap bios, and zoned support; `dm_io_rewind`; `__dm_get_module_param`; global event state; and `dm_issue_global_event`.

## Control Flow And Integration Role
The header supports core mapping flow rather than implementing it directly. A submitted original bio is represented by `struct dm_io`; one or more `struct dm_target_io` clones point back to it and carry target-specific clone state. The table indexes sectors to targets. The mapped device maintains the active table behind RCU/SRCU and suspend locks, owns queues and deferred work, and emits events when table or target state changes. The flag helpers are used by core code to distinguish normal clone bios from duplicate bios and to track original bio accounting/splitting/statistics.

## State And Persistence Behavior
All structures here are volatile kernel state. Persistence is handled by specific targets or metadata libraries, not by the core header. The important state behavior is concurrency and lifetime: `mapped_device.map` must be dereferenced through the documented live-table helpers or under suspend locking; `pending_io`, `io_barrier`, deferred lists, and suspend flags coordinate table switching and suspension; kobject completion supports lifetime teardown; event counters and queues support userspace notification.

## Dependencies And Integration Points
The header includes block-mq, blk-crypto, jump labels, block trace events, `dm.h`, and `dm-ima.h`. It is consumed by device-mapper core source files and indirectly shapes how targets like `dm-cache-target.c` and `dm-clone-target.c` interact with core hooks. The cache target's per-bio data and target-bio-number logic rely on the core's cloned-bio model, and both cache and clone status/message paths feed into the buffer and event mechanisms declared here.

## Risks And Edge Cases
Because this is private core state, accidental target dereference of `mapped_device` or `dm_table` internals would be a layering violation and may break under core changes. Clone/original bio layout constants (`DM_TARGET_IO_BIO_OFFSET`, `DM_IO_BIO_OFFSET`) are sensitive to structure layout. Suspend, queue-stopped, internal suspend, and no-flush bits must remain consistent or bios can be lost, requeued incorrectly, or issued across a suspended table. Zoned emulation and optional inline encryption add configuration-dependent paths that need static-key and queue-state correctness.

## Test Signals
Core tests should watch suspend/resume with deferred bios, table replacement under I/O, request-based and bio-based target modes, clone splitting and requeue, stats accounting static-key toggles, global event notification, queue stopped/resumed transitions, zoned queue behavior, and message buffer overflow handling. Target-level tests for cache and clone indirectly exercise `dm_target_io` clone numbering, per-bio data allocation, flush/discard target counts, and end-I/O accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-core.h -->
