# Group Research: group_668_kvdo_sources_block_storage_kvdo_vdo_vdo_page_cache_c_sources_block_s_d4221818ccb6

Scope: `Docs/research_subset_a.md`  
Files read completely: 25 source/header files under `sources/block-storage/kvdo/vdo/`.

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-page-cache.c -->
# File Research: sources/block-storage/kvdo/vdo/vdo-page-cache.c

## Purpose
Implements VDO's asynchronous metadata page cache, primarily for block map pages. It manages page allocation, lookup, LRU replacement, dirty-period tracking, reads, writes, flush-before-write ordering, wait queues, statistics, and drain/invalidation behavior.

## Main Concepts
- Each cache slot is represented by `struct page_info`, with a PBN, buffer, state, busy count, waiter queue, LRU entry, and metadata `vio`.
- Page state moves through `PS_FREE`, `PS_INCOMING`, `PS_FAILED`, `PS_RESIDENT`, `PS_DIRTY`, and `PS_OUTGOING`.
- `cache->page_map` maps physical block numbers to resident/in-flight page slots.
- `busy` pins a page while page completions hold references.
- Dirty pages are tracked by `dirty_lists` and written when their period expires or during drain.
- Writes are batched behind an explicit flush so journal entries that dirtied pages are stable before metadata pages are written.

## Key Functions
- `vdo_make_page_cache()` allocates page metadata, buffers, page map, per-slot metadata VIOs, dirty lists, and queues.
- `vdo_free_page_cache()` releases all per-page VIOs, dirty lists, maps, buffers, and cache storage.
- `vdo_init_page_completion()` initializes an async request for a specific page.
- `vdo_get_page()` resolves a page request from cache, waits on in-flight pages, launches a load, or queues behind replacement.
- `vdo_release_page_completion()` drops a busy reference and may trigger deferred write/replacement work.
- `vdo_mark_completed_page_dirty()` marks a writable completed page dirty and places it in dirty-period lists.
- `vdo_request_page_write()` forces a dirty page to be saved as soon as possible.
- `vdo_dereference_readable_page()` and `vdo_dereference_writable_page()` expose page memory after validating completion state.
- `vdo_drain_page_cache()` flushes dirty pages during block map drain unless suspending.
- `vdo_invalidate_page_cache()` asserts no dirty pages and rebuilds the PBN map.
- `vdo_get_page_cache_statistics()` returns cross-thread-safe snapshots using `READ_ONCE`.

## I/O Flow
- Reads use `launch_page_load()`, transition a slot to `PS_INCOMING`, submit metadata read I/O, optionally run `read_hook`, then distribute the loaded page to waiters.
- Rebuild-mode read errors are treated as zero-filled uninitialized pages.
- Dirty writes use `schedule_page_save()`, `save_pages()`, a flush VIO, then `write_pages()` to submit page writes.
- `write_hook` can request a rewrite after a page write completes.
- Persistent write/flush/load failures enter read-only mode and complete queued waiters with the error.

## Replacement And Waiters
- Free pages are used first.
- If no free page exists, `discard_a_page()` selects an unbusy, non-in-flight LRU page.
- Clean pages can be immediately reset and reused.
- Dirty pages are written first, with `WRITE_STATUS_DISCARD` indicating replacement-driven writeback.
- If all pages are busy or in flight, requests wait on `free_waiters` and cache pressure stats are incremented.

## Important Invariants
- Most mutations must run on the owning logical zone thread.
- A page must have no waiters and `busy == 0` before reset.
- `set_info_pbn()` requires either the old or new PBN to be `NO_PAGE`.
- Writable requests fail immediately when the zone is read-only.
- Outgoing pages are readable but not writable.
- `outstanding_reads` and `outstanding_writes` are decremented only immediately before drain-complete checks to avoid use-after-free during callbacks.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-page-cache.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-page-cache.h -->
# File Research: sources/block-storage/kvdo/vdo/vdo-page-cache.h

## Purpose
Defines the VDO page cache data structures, page state model, page completion API, and statistics/drain interfaces.

## Key Types
- `vdo_page_read_function`: optional callback after a page is read.
- `vdo_page_write_function`: optional callback after a page is written; can request rewrite.
- `struct vdo_page_cache`: owns page slots, raw buffers, LRU/free/outgoing lists, dirty lists, waiters, stats, and owning block map zone.
- `enum vdo_page_buffer_state`: page slot lifecycle state.
- `enum vdo_page_write_status`: normal, discard-driven, or deferred write status.
- `struct page_info`: per-page slot metadata and per-page client context.
- `struct vdo_page_completion`: async page request and live page reference.

## Public API
- Construction/destruction: `vdo_make_page_cache()`, `vdo_free_page_cache()`.
- Period/rebuild state: `vdo_set_page_cache_initial_period()`, `vdo_set_page_cache_rebuild_mode()`, `vdo_advance_page_cache_period()`.
- Async page access: `vdo_init_page_completion()`, `vdo_get_page()`, `vdo_release_page_completion()`.
- Dirty/write control: `vdo_mark_completed_page_dirty()`, `vdo_request_page_write()`.
- Dereference/context access: `vdo_dereference_readable_page()`, `vdo_dereference_writable_page()`, `vdo_get_page_completion_context()`.
- Lifecycle/statistics: `vdo_is_page_cache_active()`, `vdo_drain_page_cache()`, `vdo_invalidate_page_cache()`, `vdo_get_page_cache_statistics()`.

## Important Invariant
A completed `vdo_page_completion` pins the page slot until `vdo_release_page_completion()` is called.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-page-cache.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-recovery.c -->
# File Research: sources/block-storage/kvdo/vdo/vdo-recovery.c

## Purpose
Implements offline VDO crash recovery from the recovery journal. It reads journal blocks, determines valid journal bounds, reconstructs slab journal state, synthesizes lost decrefs, rebuilds the block map, saves recovery progress, and finalizes recovery.

## Main Concepts
- `struct recovery_completion` owns the recovery state, loaded journal data, block map replay entries, missing-decref queues, recovery points, and usage counters.
- `struct recovery_point` identifies a precise journal entry by sequence number, sector, and entry index.
- `struct missing_decref` records an increment entry whose matching decrement was lost and must be synthesized.
- Recovery uses multiple VDO zones: logical zone 0 for block map access, physical zones for slab journal replay, and admin thread for orchestration.

## Recovery Flow
- `vdo_launch_recovery()` allocates recovery state and asynchronously loads the recovery journal.
- `prepare_to_apply_journal_entries()` finds journal head/tail positions and determines whether to replay entries.
- `find_contiguous_range()` scans from the earliest reap head to the highest tail and stops at the first invalid/torn block or sector.
- If already in `VDO_REPLAYING`, recovery skips slab replay and resumes block map recovery.
- Otherwise, `compute_usages()` derives logical and block-map-data usage as of the valid tail.
- `find_missing_decrefs()` scans backward to find increments without paired decrements.
- Missing decrefs with unknown prior mappings fetch block map pages via logical zone 0.
- `apply_to_depot()` queues synthesized decrefs by physical zone and loads the slab depot.
- `vdo_replay_into_slab_journals()` replays real recovery entries into each allocator's slab journals.
- `add_synthesized_entries()` appends synthesized decrefs to the appropriate slab journals.
- `finish_recovering_depot()` drains the depot, stores recovered usage counters, and saves progress.
- `launch_block_map_recovery()` extracts increment entries and calls `vdo_recover_block_map()`.
- `finish_recovery()` initializes the recovery journal post-recovery and allocates slab refcounts.

## Key Functions
- `increment_recovery_point()` and `decrement_recovery_point()` walk packed journal entries across sectors and blocks.
- `before_recovery_point()` orders recovery positions.
- `get_entry()` unpacks a journal entry from loaded journal data.
- `extract_journal_entries()` builds the numbered mapping array for block map recovery.
- `count_increment_entries()` counts block map replay entries for replay-resume mode.
- `record_missing_decref()` validates synthesized-decref target mappings.
- `process_fetched_page()` reads the penultimate mapping from a block map page for incomplete missing decrefs.
- `queue_on_physical_zone()` assigns synthesized decrefs to slab journal queues.
- `prepare_sub_task()` routes callbacks to admin, logical, or physical threads.

## Important Invariants
- Missing synthesized decrefs receive stable fake journal points after the tail block so retrying recovery with different zone counts remains deterministic.
- Decrefs of the zero block affect logical usage accounting but are not written to slab journals.
- Invalid journal entries or invalid mappings enter read-only mode and abort recovery.
- Block map pages are fetched only on logical zone 0.
- Slab journal replay is skipped when `journal_data == NULL` or the VDO is already in `VDO_REPLAYING`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-recovery.h -->
# File Research: sources/block-storage/kvdo/vdo/vdo-recovery.h

## Purpose
Declares the public recovery entry points.

## Public API
- `vdo_replay_into_slab_journals()`: slab depot callback used to replay recovery journal entries into one allocator's slab journals.
- `vdo_launch_recovery()`: launches offline crash recovery and completes a parent completion when done.

## Dependencies
Includes `completion.h` and `vdo.h`; uses `struct block_allocator` through declarations available from included headers.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-recovery.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-resize-logical.c -->
# File Research: sources/block-storage/kvdo/vdo/vdo-resize-logical.c

## Purpose
Implements logical-size growth for a suspended VDO by saving the new logical block count and growing the block map.

## State Machine
Phases:
- `GROW_LOGICAL_PHASE_START`
- `GROW_LOGICAL_PHASE_GROW_BLOCK_MAP`
- `GROW_LOGICAL_PHASE_END`
- `GROW_LOGICAL_PHASE_ERROR`

All phases run on the admin thread.

## Key Functions
- `vdo_prepare_to_grow_logical()` prepares block map growth while the VDO is running.
- `vdo_perform_grow_logical()` commits the prepared logical size while the VDO is suspended.
- `grow_logical_callback()` drives the admin operation.
- `handle_growth_error()` rolls back in-memory logical block count and abandons block map growth if superblock save failed.

## Important Behavior
- No-op resume after a prepared grow abandons block map growth and succeeds.
- Growth fails with `VDO_PARAMETER_MISMATCH` if the prepared block map target does not match the requested new logical size.
- Read-only VDOs cannot grow logical size.
- The new logical size is first recorded in `states.vdo.config.logical_blocks`, saved, then the block map is grown.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-resize-logical.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-resize-logical.h -->
# File Research: sources/block-storage/kvdo/vdo/vdo-resize-logical.h

## Purpose
Declares logical resize operations.

## Public API
- `vdo_perform_grow_logical()`: commit a prepared logical grow.
- `vdo_prepare_to_grow_logical()`: prepare block map structures for a future logical grow.

## Context
The implementation requires preparation while running and commit while suspended.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-resize-logical.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-resize.c -->
# File Research: sources/block-storage/kvdo/vdo/vdo-resize.c

## Purpose
Implements physical-size growth for a suspended VDO, including layout growth, recovery journal/slab summary relocation, slab depot expansion, and component-state persistence.

## State Machine
Phases:
- `GROW_PHYSICAL_PHASE_START`
- `GROW_PHYSICAL_PHASE_COPY_SUMMARY`
- `GROW_PHYSICAL_PHASE_UPDATE_COMPONENTS`
- `GROW_PHYSICAL_PHASE_USE_NEW_SLABS`
- `GROW_PHYSICAL_PHASE_END`
- `GROW_PHYSICAL_PHASE_ERROR`

All phases run on the admin thread.

## Key Functions
- `vdo_prepare_to_grow_physical()` validates that growth is allowed, prepares layout growth, and prepares slab depot growth.
- `vdo_perform_grow_physical()` commits a previously prepared physical grow while suspended.
- `grow_physical_callback()` copies old layout partitions, updates component sizes, saves metadata, activates new slabs, and updates partition pointers.
- `check_may_grow_physical()` rejects prepare when read-only or in recovery mode.
- `handle_growth_error()` routes failures into the error phase and read-only mode.

## Important Behavior
- No-op grows return success.
- Commit requires `new_physical_blocks == vdo_get_next_layout_size()`.
- Prepared slab depot size must match the next block allocator partition size.
- On mismatch, pending layout growth and new slabs are abandoned.
- On success, recovery journal and slab summary partition origins are updated after new slabs are usable.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-resize.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-resize.h -->
# File Research: sources/block-storage/kvdo/vdo/vdo-resize.h

## Purpose
Declares physical resize operations.

## Public API
- `vdo_perform_grow_physical()`: commit prepared physical growth.
- `vdo_prepare_to_grow_physical()`: prepare layout and slab depot structures for physical growth.

## Context
Physical growth is prepared before suspend/resume commit and performed only while suspended.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-resize.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-resume.c -->
# File Research: sources/block-storage/kvdo/vdo/vdo-resume.c

## Purpose
Implements VDO preresume behavior: commits any new table configuration, transitions metadata state to dirty when needed, and resumes subsystems in dependency order.

## Resume Phases
- Start resuming and write dirty superblock if needed.
- Allow read-only mode entry.
- Resume dedupe/hash zones.
- Resume slab depot.
- Resume recovery journal.
- Resume block map.
- Resume logical zones.
- Apply compression setting and resume packer.
- Resume flusher.
- Resume data VIO pool.
- Finish resuming.

## Key Functions
- `vdo_preresume_internal()` is the external entry point used during device-mapper preresume.
- `apply_new_vdo_configuration()` commits logical and physical growth requested by the new table.
- `resume_callback()` drives the admin operation across phase-specific threads.
- `write_super_block()` changes `VDO_CLEAN` or `VDO_NEW` to `VDO_DIRTY` before normal operation.

## Important Behavior
- The new `device_config` is installed after attempted configuration changes, whether they succeed or fail.
- Commit failures enter in-memory read-only mode because the device is suspended and disk state is not updated.
- `VDO_READ_ONLY` during resume is treated as successful resume.
- Compression is enabled/disabled from `device_config->compression` during packer resume.
- `VDO_REPLAYING` is invalid for resume superblock transition.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-resume.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-resume.h -->
# File Research: sources/block-storage/kvdo/vdo/vdo-resume.h

## Purpose
Declares the internal preresume entry point.

## Public API
- `vdo_preresume_internal()`: applies new config and resumes a suspended VDO for a named device.

## Context
Called from device-mapper resume/preresume integration; resume itself cannot fail externally, so this function performs fail-able work beforehand.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-resume.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-suspend.c -->
# File Research: sources/block-storage/kvdo/vdo/vdo-suspend.c

## Purpose
Implements VDO suspend by draining all active work, flushing persisted data, waiting for read-only transitions, and saving clean state when appropriate.

## Suspend Phases
- Start draining with the configured suspend type.
- Drain packer.
- Drain data VIO pool.
- Drain dedupe/hash zones.
- Drain flushes.
- Synchronously flush backing storage and drain logical zones.
- Drain block map.
- Drain recovery journal.
- Drain slab depot.
- Wait for read-only-mode entry to settle.
- Save clean superblock if this is a true suspend and no error occurred.
- Finish draining.

## Key Functions
- `vdo_suspend()` starts the admin suspend operation and maps expected read-only results to success.
- `suspend_callback()` drives phase transitions.
- `write_super_block()` records `VDO_CLEAN` for `VDO_DIRTY` or `VDO_NEW`, then saves components.
- `get_thread_id_for_phase()` routes packer/flusher phases to packer thread, data VIO phase to CPU thread, journal phase to journal thread, and others to admin.

## Important Behavior
- Device-mapper may suspend the device even if this post-suspend work reports an error.
- If already read-only, the operation records `VDO_READ_ONLY` so partially resumed components do not cause `VDO_INVALID_ADMIN_STATE`.
- Logical-zone phase issues `vdo_synchronous_flush()` before draining metadata paths.
- `VDO_READ_ONLY` is returned to callers as suspend success.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-suspend.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-suspend.h -->
# File Research: sources/block-storage/kvdo/vdo/vdo-suspend.h

## Purpose
Declares the VDO suspend entry point.

## Public API
- `vdo_suspend()`: drains and suspends a VDO.

## Context
Includes only `kernel-types.h`; implementation handles admin operation sequencing.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-suspend.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo.c -->
# File Research: sources/block-storage/kvdo/vdo/vdo.c

## Purpose
Provides core VDO lifecycle, construction/destruction, thread creation, resize preparation, state persistence, read-only notification, statistics, compression control, flush, status dump, and thread assertion helpers.

## Construction And Destruction
- `vdo_make()` allocates and initializes the VDO object, thread config, work queues, flusher, packer, data VIO pool, I/O submitter, optional bio ack queue, and CPU queue.
- `initialize_vdo()` reads the geometry block, creates thread configuration, allocates compression contexts, registers the device, and transitions admin state to initialized.
- `vdo_make_thread()` creates a work queue for a thread-config thread ID and validates repeated construction type.
- `vdo_destroy()` requires the VDO not be running, tears down sysfs stats, queues, subsystems, registry entries, thread config, compression contexts, instance number, and the VDO object/kobject.

## Configuration And Resize Preparation
- `vdo_prepare_to_modify()` validates a new device config, prepares logical growth, prepares physical growth, and logs backing-device name changes.
- Physical-growth `VDO_PARAMETER_MISMATCH` is mapped to `-EINVAL` for user-facing behavior.
- `vdo_get_backing_device()` and `vdo_get_device_name()` expose underlying block device and dm target name.

## State Persistence
- `vdo_get_state()` and `vdo_set_state()` use memory barriers around atomic state access.
- `record_vdo()` snapshots release version, VDO state, block map, recovery journal, slab depot, and layout into `vdo->states`.
- `vdo_save_components()` encodes component states and saves the superblock at the data-region start.
- `vdo_enable_read_only_entry()` registers a listener that saves `VDO_READ_ONLY_MODE` to disk when read-only mode is entered.

## Runtime Operations
- `vdo_synchronous_flush()` submits a flush bio and waits synchronously.
- `vdo_set_compressing()` synchronously toggles compression on the packer thread and flushes the packer when disabling.
- `vdo_get_compressing()` reads compression state with `READ_ONCE`.
- `vdo_enter_recovery_mode()` transitions to `VDO_RECOVERING` unless already read-only.

## Statistics
- `get_vdo_statistics()` populates `struct vdo_statistics` on the admin thread.
- It combines immutable config, slab depot usage, journal stats, packer stats, block map stats, dedupe stats, atomic error stats, bio stats, VIO pool usage, and memory usage.
- `vdo_fetch_statistics()` runs this synchronously on the admin thread.

## Thread And Zone Helpers
- `vdo_get_callback_thread_id()` identifies the current VDO work queue thread.
- `vdo_assert_on_admin_thread()`, `vdo_assert_on_logical_zone_thread()`, `vdo_assert_on_physical_zone_thread()`, and `assert_on_vdo_cpu_thread()` provide debug assertions.
- `vdo_get_physical_zone()` validates a PBN and maps it to the owning physical zone.
- `vdo_get_bio_zone()` maps PBNs to bio submission zones using rotation interval.

## Important Invariants
- A running VDO must be suspended before destruction.
- All superblock saves should flow through `vdo_save_components()` so component snapshots are consistent.
- Metadata overhead accounting subtracts data blocks and adds block-map journal data blocks.
- Invalid physical PBN checks avoid entering read-only mode in `vdo_get_physical_zone()`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo.h -->
# File Research: sources/block-storage/kvdo/vdo/vdo.h

## Purpose
Defines core `struct vdo`, VDO thread representation, and public APIs for lifecycle, state, statistics, compression, persistence, assertions, and zone lookup.

## Key Structures
- `struct vdo_thread`: wraps a work queue, owning VDO, thread ID, and allocation-thread registration.
- `struct vdo`: central object containing thread queues, atomic state, component states, read-only notifier, config, layout, block map, recovery journal, slab depot, packer, flusher, logical/physical/hash zones, I/O submitter, data VIO pool, admin state, statistics, sysfs objects, geometry, and compression contexts.

## Public API
- Lifecycle: `vdo_make()`, `vdo_destroy()`, `vdo_make_thread()`, `vdo_make_default_thread()`.
- Sysfs/stats: `vdo_add_sysfs_stats_dir()`, `vdo_fetch_statistics()`, `vdo_dump_status()`.
- Config: `vdo_prepare_to_modify()`, `vdo_get_backing_device()`, `vdo_get_device_name()`.
- State: `vdo_get_state()`, `vdo_set_state()`, `vdo_get_admin_state()`, `vdo_save_components()`.
- Modes: `vdo_enable_read_only_entry()`, `vdo_in_read_only_mode()`, `vdo_in_recovery_mode()`, `vdo_enter_recovery_mode()`.
- Compression: `vdo_set_compressing()`, `vdo_get_compressing()`.
- Thread assertions and helpers: admin/logical/physical/dedupe/CPU assertions, `vdo_get_callback_thread_id()`.
- Physical mapping: `vdo_get_physical_zone()`, `vdo_get_bio_zone()`.

## Inline Helpers
- `vdo_uses_bio_ack_queue()` checks whether a separate bio acknowledgement queue exists.
- `vdo_crc32()` preserves historical VDO CRC initialization/finalization behavior.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vio-pool.c -->
# File Research: sources/block-storage/kvdo/vdo/vio-pool.c

## Purpose
Implements a fixed-size pool of preallocated metadata VIOs and block-sized buffers, with async waiters for pool exhaustion.

## Main Concepts
- `struct vio_pool` owns available and busy lists, waiter queue, busy count, thread ownership, shared buffer storage, and entries.
- Each `vio_pool_entry` owns one VIO and one `VDO_BLOCK_SIZE` buffer slice.
- The pool is thread-affine; acquire and return assert the configured thread ID.

## Key Functions
- `make_vio_pool()` allocates the pool, contiguous buffers, constructs each VIO with the supplied constructor, and places entries on the available list.
- `free_vio_pool()` asserts no waiters or busy entries, frees available VIOs, validates all entries were removed, and frees backing storage.
- `is_vio_pool_busy()` reports outstanding entries.
- `acquire_vio_from_pool()` immediately hands an available entry to the waiter callback or queues the waiter if empty.
- `return_vio_to_pool()` either hands the entry directly to the next waiter or moves it back to available and decrements busy count.

## Important Invariants
- Pool entries must be returned on the same thread from which they are acquired.
- `busy_count` remains unchanged when returning an entry directly to a waiting requestor.
- `entry->vio->completion.error_handler` is cleared on return.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vio-pool.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vio-pool.h -->
# File Research: sources/block-storage/kvdo/vdo/vio-pool.h

## Purpose
Declares the VIO pool API and `vio_pool_entry` type.

## Key Types
- `struct vio_pool_entry`: list entry, VIO pointer, data buffer, parent, and context.
- `vio_constructor`: callback used to construct each pooled VIO.

## Public API
- `make_vio_pool()`
- `free_vio_pool()`
- `is_vio_pool_busy()`
- `acquire_vio_from_pool()`
- `return_vio_to_pool()`
- `as_vio_pool_entry()`

## Usage
Used for metadata blocks that need preallocated VIOs and buffers without runtime allocation in the hot path.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vio-pool.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vio-read.c -->
# File Research: sources/block-storage/kvdo/vdo/vio-read.c

## Purpose
Implements the VDO read path and read-modify-write read phase for `data_vio` requests.

## Main Flow
- `launch_read_data_vio()` finds the block map slot for the LBN after the logical lock is acquired.
- `read_block_mapping()` requests the mapped block from the block map.
- `read_block()` handles zero mappings, compressed mappings, partial reads, read-modify-write reads, and full-block read cloning.
- `read_endio()` records completed bio stats and routes successful reads to the CPU queue.
- `complete_read()` decompresses if needed, performs partial copy-out, acknowledges the user bio, and completes the VIO.
- `cleanup_read_data_vio()` releases the logical lock on the logical-zone thread.

## Partial And RMW Behavior
- `modify_for_partial_write()` overlays discard zeroes or incoming bio data into the fetched block.
- It updates `is_zero_block`, switches the operation to write, clears the read error handler, and relaunches the write path.
- `complete_zero_read()` zero-fills a block buffer or user bio and can continue into partial-write modification.

## I/O Behavior
- Full 4 KiB uncompressed reads clone the user bio to avoid copying.
- Compressed and partial reads use the `data_block` or compression buffer.
- Only selected request flags are passed through: `REQ_PRIO`, `REQ_META`, `REQ_SYNC`, and `REQ_RAHEAD`.

## Important Invariants
- Mapping lookup and logical lock release happen on the logical zone.
- Decompression and bio copying happen on the CPU queue.
- Zero-block mappings avoid backing I/O.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vio-read.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vio-read.h -->
# File Research: sources/block-storage/kvdo/vdo/vio-read.h

## Purpose
Declares read-path entry and cleanup functions for `data_vio`.

## Public API
- `launch_read_data_vio()`: start async read or read-modify-write processing.
- `cleanup_read_data_vio()`: release read-path logical lock and return the VIO.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vio-read.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vio-write.c -->
# File Research: sources/block-storage/kvdo/vdo/vio-write.c

## Purpose
Implements most of the VDO write path, including allocation, early acknowledgment, dedupe, compression, recovery journal entries, slab reference updates, block map updates, discard continuation, and cleanup.

## Main Write Flow
- `launch_write_data_vio()` rejects read-only writes, acquires a flush generation lock, and locates the block map slot.
- `continue_write_with_block_map_slot()` handles unmapped trim shortcuts, data allocation, zero/discard mapping, and acknowledgment timing.
- `allocate_block()` allocates a physical block and sets `new_mapped`.
- `acknowledge_write_callback()` acknowledges user writes once safe under flush-generation rules.
- `prepare_for_dedupe()` hashes data and routes to the correct hash zone.
- `lock_hash_in_zone()` acquires or joins hash-lock state.
- Writes may then deduplicate, compress/pack, or write a newly allocated block.

## Dedupe And Compression
- `hash_data_vio()` computes MurmurHash3 over the 4 KiB block.
- `launch_deduplicate_data_vio()` maps the LBN to a verified duplicate PBN.
- `launch_compress_data_vio()` checks compression eligibility and sends compression work to the CPU queue.
- `pack_compressed_data()` attempts to pack compressed data on the packer thread.
- `continue_write_after_compression()` either proceeds with compressed mapping journal work or falls back to normal write.

## Journal And Refcount Ordering
- `journal_increment()` and `journal_decrement()` add recovery journal entries for mapping changes.
- `update_reference_count()` writes slab journal entries after validating physical data block ranges.
- Dedupe/compression path:
  - journal increment for new mapping
  - increment refcount
  - read old block mapping
  - journal unmapping
  - decrement old mapping if nonzero
  - update block map
- Normal write path:
  - write data
  - journal new mapping
  - increment new block if nonzero
  - read old mapping
  - journal unmapping
  - decrement old mapping if nonzero
  - update block map

## Cleanup
- Cleanup stages release allocation/PBN locks, verify recovery-journal lock state, release hash lock, release logical and flush-generation locks, then return or relaunch the VIO.
- Multi-block discards reuse the same `data_vio` for following logical blocks until the discard range is exhausted.
- Hash locks are notified on success and error so dependent VIOs can continue or update hash-lock state.

## Error Behavior
- `abort_on_error()` optionally enters read-only mode and routes errors through hash-lock cleanup when needed.
- `VDO_NO_SPACE` during allocation is not immediately fatal; the path attempts dedupe/compression before returning no space.
- Fatal write-path metadata errors generally enter read-only mode.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vio-write.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vio-write.h -->
# File Research: sources/block-storage/kvdo/vdo/vio-write.h

## Purpose
Declares write-path entry points and dedupe/compression re-entry points.

## Public API
- `launch_write_data_vio()`: start async write processing.
- `cleanup_write_data_vio()`: release write-path locks and return/reuse the VIO.
- `continue_write_after_compression()`: resume write path after packer compression result.
- `launch_compress_data_vio()`: attempt compression path.
- `launch_deduplicate_data_vio()`: commit a verified duplicate mapping.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vio-write.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vio.c -->
# File Research: sources/block-storage/kvdo/vdo/vio.c

## Purpose
Implements metadata VIO allocation/freeing and common VIO error logging/statistics helpers.

## Key Functions
- `create_multi_block_metadata_vio()` allocates a metadata `struct vio`, creates a bio sized for multiple VDO blocks, initializes completion/type/priority, and attaches caller data.
- `free_vio()` frees non-data VIOs and their bios.
- `update_vio_error_stats()` increments read-only/no-space/error stats and rate-limits error logging.
- `record_metadata_io_error()` formats operation type from bio flags and records a metadata I/O error.

## Important Behavior
- Metadata VIOs are allocated directly, not from the data bio buffer pool.
- `MAX_BLOCKS_PER_VIO` is enforced by assertion.
- `struct vio` is asserted to remain at or below 256 bytes.
- `VDO_READ_ONLY` increments stats but is not logged as an error.
- `VDO_NO_SPACE` is logged at debug priority.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vio.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vio.h -->
# File Research: sources/block-storage/kvdo/vdo/vio.h

## Purpose
Defines the base VIO structure and helpers for metadata/data VIO identification, bio preparation, zone routing, and I/O completion continuation.

## Key Types
- `struct vio`: generic VDO I/O object with completion, physical block, bio zone, priority, type, block count, data buffer, owned bio, and merged-bio list.
- `MAX_BLOCKS_PER_VIO`: derived from `BIO_MAX_VECS` and `VDO_BLOCK_SIZE`.

## Public/Inline API
- Conversion: `as_vio()`, `vio_as_completion()`, `vdo_from_vio()`.
- Construction: `create_multi_block_metadata_vio()`, `create_metadata_vio()`, `initialize_vio()`, `free_vio()`.
- Routing: `set_vio_physical()`, `get_vio_bio_zone_thread_id()`, `assert_vio_in_bio_zone()`.
- Classification: `is_data_vio()`, `is_metadata_vio()`.
- I/O: `prepare_vio_for_io()`, `continue_vio()`, `continue_vio_after_io()`.
- Errors: `update_vio_error_stats()`, `record_metadata_io_error()`.

## Important Invariants
- `set_vio_physical()` must be used before I/O so `bio_zone` matches the PBN.
- Metadata priority maps to work queue priority via `get_metadata_priority()`.
- `continue_vio_after_io()` counts completed bios, sets the next callback/thread, and enqueues the completion with the bio result.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vio.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-geometry.c -->
# File Research: sources/block-storage/kvdo/vdo/volume-geometry.c

## Purpose
Reads, decodes, validates, and checksums the on-disk VDO geometry block at block 0.

## On-Disk Format
- Magic number: `dmvdo001`.
- Header ID: `VDO_GEOMETRY_BLOCK`.
- Supported geometry block versions:
  - 4.0: no `bio_offset` in `volume_geometry`.
  - 5.0: includes `bio_offset`.
- Payload includes release version, nonce, UUID, volume regions, and index config.
- CRC32 covers all decoded bytes before the checksum field.

## Key Functions
- `is_loadable_release_version()` accepts current release plus compatible Magnesium and Aluminum releases.
- `decode_index_config()` decodes UDS index memory size and sparse flag, skipping an unused field.
- `decode_volume_region()` decodes region ID and start block.
- `decode_volume_geometry()` decodes version-dependent geometry fields.
- `decode_geometry_block()` checks magic, decodes and validates header, decodes geometry, and asserts position before checksum.
- `vdo_parse_geometry_block()` verifies checksum and release compatibility.
- `vdo_read_geometry_block()` synchronously reads block 0 from a block device and parses it.

## Important Behavior
- Version 4 geometries default `bio_offset` to zero.
- Header `size` is unusual: it includes the geometry block header and payload, not just payload.
- Synchronous read errors are logged and returned as `-EIO`.
- Unsupported release versions return `VDO_UNSUPPORTED_VERSION`.
- Checksum mismatch returns `VDO_CHECKSUM_MISMATCH`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-geometry.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-geometry.h -->
# File Research: sources/block-storage/kvdo/vdo/volume-geometry.h

## Purpose
Defines VDO geometry structures and helpers for locating index/data regions.

## Key Types
- `struct index_config`: UDS memory setting, unused field, and sparse flag.
- `enum volume_region_id`: index region and data region IDs.
- `struct volume_region`: region ID plus absolute start block.
- `struct volume_geometry`: release version, nonce, UUID, bio offset, regions, and index config.
- `struct volume_geometry_4_0`: legacy sizing-only geometry without bio offset.

## Public API
- `vdo_get_index_region_start()`
- `vdo_get_data_region_start()`
- `vdo_get_index_region_size()`
- `vdo_read_geometry_block()`

## Important Constant
- `VDO_GEOMETRY_BLOCK_LOCATION = 0`
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-geometry.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-index-ops.c -->
# File Research: sources/block-storage/kvdo/vdo/volume-index-ops.c

## Purpose
Provides format-dispatch wrappers for UDS volume index creation, save/load sizing, save, load, and combined statistics.

## Key Behavior
- Sparse configurations use volume index 006 operations.
- Dense configurations use volume index 005 operations.
- `get_volume_index_combined_stats()` merges dense and sparse stats fields into one aggregate.
- `compute_volume_index_save_blocks()` computes format-specific save bytes, adds `delta_list_save_info`, rounds to blocks, and adds `MAX_ZONES` guard capacity.
- `save_volume_index()` saves each zone sequentially, writes guard delta lists, and flushes each writer.
- `load_volume_index()` starts restore, finishes restore, validates guard delta lists, and aborts restore on failure after start.

## Key Functions
- `make_volume_index()`
- `compute_volume_index_save_blocks()`
- `save_volume_index()`
- `load_volume_index()`
- `get_volume_index_combined_stats()`

## Important Invariant
Save/load correctness depends on the sparse/dense dispatch matching the geometry used to create the volume index.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-index-ops.c -->