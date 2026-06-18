# Group Research: KVDO slab/refcount/journal subset A

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/ref-counts.c -->
# File Research: sources/block-storage/kvdo/vdo/ref-counts.c

Implements the per-slab physical block reference-count engine and its persistence path. It owns in-memory byte counters, free-block searching, provisional allocations, replay/rebuild adjustments, dirty reference-count block writeback, loading saved reference blocks, and coordination with slab journal locks and slab summary cleanliness.

Key behavior:
- `vdo_make_ref_counts()` allocates a `struct ref_counts` with an extended `reference_block` array and a padded counter array sized by `vdo_get_saved_reference_count_size()`.
- Reference counts are interpreted as `RS_FREE`, `RS_SINGLE`, `RS_SHARED`, or `RS_PROVISIONAL`.
- Data increments transition free/provisional blocks to count `1`, increment shared counts up to `MAXIMUM_REFERENCE_COUNT`, and clear provisional PBN-lock bookkeeping.
- Data decrements reject free blocks, reduce shared counts, or transition single/provisional blocks to empty unless a PBN lock requires preserving a provisional reference.
- Block-map increments use `MAXIMUM_REFERENCE_COUNT` to prevent dedupe against block-map blocks. In normal operation they are expected to come from provisional state; rebuild/replay may create them from free state.
- `vdo_adjust_reference_count()` is the normal entry point. It validates slab openness, maps PBN to slab block number, updates the counter, and manages slab-journal lock conversion/release.
- `vdo_adjust_reference_count_for_rebuild()` applies non-normal-operation updates and dirties the affected reference block.
- `vdo_replay_reference_count_change()` skips slab journal entries already reflected in the saved per-sector commit point, otherwise replays and dirties the block.

Free-space management:
- `search_cursor` keeps a per-slab free-search hint.
- `vdo_find_free_block()` scans byte counters using word-sized little-endian reads and a padded counter array.
- `vdo_allocate_unreferenced_block()` finds a zero counter, marks it `PROVISIONAL_REFERENCE_COUNT`, updates free/allocated accounting, and advances the cursor.
- `vdo_provisionally_reference_block()` marks a specific free block provisional and optionally records that on a `pbn_lock`.

Persistence:
- Dirty reference blocks are waiters on `ref_counts->dirty_blocks`.
- `vdo_pack_reference_block()` writes the current slab journal point into every sector and copies the sector’s counters.
- Writes use `REQ_OP_WRITE | REQ_PREFLUSH` so the recovery/slab journal entries covering the reference update are stable before the refcount block reaches disk.
- `finish_reference_block_write()` releases the slab journal block lock associated with that saved reference block and requeues the block if it was dirtied during the write.
- When all dirty/writing work is done, `update_slab_summary_as_clean()` marks the slab clean in the slab summary with the current free-block count.
- Loading unpacks per-sector commit points, warns on torn writes where sector commit points differ, recomputes allocated counts, clears stale provisional references, and recomputes free blocks.

Drain/state behavior:
- `vdo_drain_ref_counts()` chooses load or save behavior based on slab admin state: scrubbing may load saved counts; save-for-scrubbing/rebuilding/saving may dirty and write blocks.
- `vdo_acquire_dirty_block_locks()` dirties all reference blocks and makes them hold lock `1` in the slab journal, used for first-journal initialization.
- I/O errors enter read-only mode through the slab’s read-only notifier.

Dependencies:
- Slab state and PBN translation from `slab.h`.
- Journal positions from `journal-point.h`.
- Slab journal lock operations from `slab-journal.h`.
- Slab summary updates from `slab-summary.h`.
- VIO pool and metadata I/O for async reads/writes.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/ref-counts.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/ref-counts.h -->
# File Research: sources/block-storage/kvdo/vdo/ref-counts.h

Declares the reference-count subsystem used by each `vdo_slab`.

Important types:
- `enum reference_status`: logical states for a counter: free, single, shared, provisional.
- `struct reference_block`: tracks one persisted refcount block, including dirty/writing state, allocated counter count, slab journal locks, and per-sector commit points.
- `struct search_cursor`: stores the current block/index/end range for free-block scans.
- `struct ref_counts`: owns the slab pointer, counter array, free count, dirty queue, active I/O count, slab summary update waiter, read-only notifier, shared statistics, persisted origin, latest slab journal point, and flexible array of `reference_block`s.

Public API:
- Construction/destruction: `vdo_make_ref_counts()`, `vdo_free_ref_counts()`.
- State/queries: `vdo_are_ref_counts_active()`, `vdo_get_unreferenced_block_count()`, `vdo_get_available_references()`, `vdo_count_unreferenced_blocks()`.
- Allocation/reference updates: `vdo_allocate_unreferenced_block()`, `vdo_provisionally_reference_block()`, `vdo_adjust_reference_count()`, `vdo_adjust_reference_count_for_rebuild()`, `vdo_replay_reference_count_change()`.
- Persistence/drain: `vdo_save_several_reference_blocks()`, `vdo_save_dirty_reference_blocks()`, `vdo_dirty_all_reference_blocks()`, `vdo_drain_ref_counts()`, `vdo_acquire_dirty_block_locks()`.
- Diagnostics: `vdo_dump_ref_counts()`.

The header exposes enough internals for adjacent slab/journal code to reason about refcount block activity, but most mutation logic stays in `ref-counts.c`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/ref-counts.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/reference-count-rebuild.c -->
# File Research: sources/block-storage/kvdo/vdo/reference-count-rebuild.c

Implements read-only reference-count rebuild from the VDO block map. It reconstructs slab refcounts by traversing block-map tree pages and leaf pages, repairing invalid mappings as needed, then flushing block-map changes.

Core object:
- `struct rebuild_completion` extends `vdo_completion` and stores block map/depot pointers, logical/admin thread IDs, counters returned to the caller, current page fetch state, outstanding reads, and an array of page completions.

Flow:
- `vdo_rebuild_reference_counts()` creates the rebuild completion, invalidates the block-map page cache to avoid deep completion chaining, then traverses the block-map forest.
- `process_entry()` handles interior block-map tree pages. Each tree-page PBN is validated as a physical data block and counted as `VDO_JOURNAL_BLOCK_MAP_INCREMENT` with refcount set to the block-map maximum reference value.
- After tree traversal, `rebuild_from_leaves()` computes the last legal block-map slot, launches a bounded number of asynchronous leaf-page fetches, and tracks outstanding requests.
- `rebuild_reference_counts_from_page()` processes every leaf page entry:
  - clears initialized mappings beyond the logical end,
  - clears invalid encoded locations,
  - skips unmapped and zero-block mappings,
  - clears mappings to non-data PBNs,
  - increments data refcounts for valid mapped PBNs,
  - counts logical blocks used.
- `finish_if_done()` waits for all fetches and outstanding work, then drains/flushes the block map through `vdo_drain_block_map()` on the admin thread.
- Errors mark the rebuild aborted, release page completions, and finish the parent with the saved result.

Notable design points:
- Leaf page completions keep pages locked until processed.
- Rebuild modifies block-map pages to remove bogus mappings and requests page writes for repairs.
- Refcount increments call `vdo_adjust_reference_count_for_rebuild()`, so normal-operation provisional/reference assumptions are relaxed.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/reference-count-rebuild.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/reference-count-rebuild.h -->
# File Research: sources/block-storage/kvdo/vdo/reference-count-rebuild.h

Small public interface for block-map-based reference-count rebuild.

Exports:
- `vdo_rebuild_reference_counts(struct vdo *vdo, struct vdo_completion *parent, block_count_t *logical_blocks_used, block_count_t *block_map_data_blocks)`

The function asynchronously rebuilds refcounts and reports:
- number of mapped logical blocks observed,
- number of block-map data/tree blocks referenced,
- completion result through the parent completion.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/reference-count-rebuild.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/reference-operation.c -->
# File Research: sources/block-storage/kvdo/vdo/reference-operation.c

Implements helpers for constructing `struct reference_operation`.

Functions:
- `vdo_set_up_reference_operation_with_lock()` stores a direct `pbn_lock` pointer in the operation context and uses `return_pbn_lock()` as the getter.
- `vdo_set_up_reference_operation_with_zone()` stores a `physical_zone` pointer and uses `look_up_pbn_lock()` to retrieve the current lock for the PBN later.

Purpose:
- Lets reference-count update code use a uniform operation object while supporting both already-known locks and lazy lookup from a zone.
- Keeps PBN-lock coupling out of `ref-counts.c` callers.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/reference-operation.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/reference-operation.h -->
# File Research: sources/block-storage/kvdo/vdo/reference-operation.h

Defines `struct reference_operation`, the common description of a physical-block reference update.

Fields:
- `type`: journal operation, such as data increment/decrement or block-map increment.
- `pbn`: physical block number being updated.
- `state`: block mapping state.
- `lock_getter`: optional callback for retrieving a `pbn_lock`.
- `context`: lock or zone context passed to the getter.

The inline `vdo_get_reference_operation_pbn_lock()` returns `NULL` when no getter is present, otherwise delegates to the callback. This abstraction lets refcount code handle lock-aware and lockless operations consistently.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/reference-operation.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/release-versions.h -->
# File Research: sources/block-storage/kvdo/vdo/release-versions.h

Defines numeric release version constants for VDO releases:
- Oxygen, Fluorine, Neon, Sodium, Magnesium, Aluminum.
- `VDO_HEAD_RELEASE_VERSION_NUMBER` is `0`.
- `VDO_CURRENT_RELEASE_VERSION_NUMBER` aliases the head value.

This is a compatibility/version header only; it has no runtime logic.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/release-versions.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/request-queue.c -->
# File Research: sources/block-storage/kvdo/vdo/request-queue.c

Implements a UDS request-processing worker queue over two lock-free funnel queues.

Architecture:
- `struct uds_request_queue` owns a Linux wait queue, processor callback, main queue, retry queue, worker thread, lifecycle flags, and an atomic dormant flag.
- Retry/requeued requests generally have priority over normal requests, but the file explicitly documents a race where a producer can enqueue retry then normal and have them processed in reverse order.

Worker behavior:
- `poll_queues()` checks retry queue first, then main queue.
- `dequeue_request()` returns a request, shutdown, or “must wait”.
- `request_queue_worker()` alternates between timed waiting and dormant indefinite waiting.
- Batch size feedback adjusts wait timeout:
  - small batches increase timeout,
  - large batches decrease timeout,
  - very long timeout switches to dormant mode.
- Dormant mode relies on enqueue-side wakeups and memory ordering around funnel-queue insertion and `dormant`.

Lifecycle:
- `make_uds_request_queue()` allocates the queue, creates both funnel queues, starts the worker thread, and publishes the queue after a memory barrier.
- `uds_request_queue_enqueue()` places the request on retry or main queue based on `request->requeued`, then wakes the worker if dormant or if `request->unbatched`.
- `uds_request_queue_finish()` marks the queue dead with ordering barriers, wakes and joins the worker, drains any remaining queued requests, and frees resources.

Concurrency notes:
- The code relies on funnel-queue barriers, explicit `smp_mb()`, `smp_wmb()`, and `smp_rmb()` to ensure shutdown and sleep/wakeup visibility.
- Shutdown still processes requests fully enqueued before `alive` is cleared.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/request-queue.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/request-queue.h -->
# File Research: sources/block-storage/kvdo/vdo/request-queue.h

Public interface for the UDS worker request queue.

Defines:
- Opaque `struct uds_request_queue`.
- `uds_request_queue_processor_t`, a callback that processes one `struct uds_request` and handles its own errors.

Exports:
- `make_uds_request_queue()` to allocate a queue and start its worker.
- `uds_request_queue_enqueue()` to enqueue normal or requeued requests.
- `uds_request_queue_finish()` to shut down, drain, join, and free the queue.

The header documents that requeued requests are usually processed ahead of normal requests, but exact ordering is not absolute under concurrent producer races.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/request-queue.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-depot-format.c -->
# File Research: sources/block-storage/kvdo/vdo/slab-depot-format.c

Implements encoding/decoding and layout calculation for the slab depot’s on-disk superblock component.

On-disk header:
- `VDO_SLAB_DEPOT_HEADER_2_0` identifies the slab depot component, version `2.0`, and payload size `sizeof(struct slab_depot_state_2_0)`.

Encoding/decoding:
- `encode_slab_config()` and `decode_slab_config()` serialize all `struct slab_config` fields as little-endian 64-bit values.
- `vdo_encode_slab_depot_state_2_0()` writes the component header, slab config, first/last block, and zone count.
- `vdo_decode_slab_depot_state_2_0()` validates the header, decodes fields, checks decoded size, and populates state.

Layout helpers:
- `vdo_compute_slab_count()` computes full slabs as `(last_block - first_block) >> slab_size_shift`.
- `vdo_get_slab_depot_encoded_size()` returns header plus state payload size.
- `vdo_get_saved_reference_count_size()` returns `DIV_ROUND_UP(block_count, COUNTS_PER_BLOCK)`.

Configuration:
- `vdo_configure_slab_depot()` computes how many whole slabs fit in the block range, rejects zero slabs and too many slabs, and records first/last block and zone count.
- Runt slabs are not allowed; leftover blocks below one slab are wasted.
- `vdo_configure_slab()` computes per-slab metadata and data capacity:
  - reference-count blocks are sized from data capacity minus slab-journal blocks,
  - metadata blocks are reference-count blocks plus slab-journal blocks,
  - very small unit-test slabs may round data blocks down to a power of two,
  - journal flush/block/scrub thresholds are derived from journal block count.

Threshold meanings:
- Flush threshold: starts writing reference blocks, roughly three quarters of the journal.
- Blocking threshold: stops admitting new journal entries until reference blocks drain.
- Scrubbing threshold: leaves enough extra journal space for recovery behavior.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-depot-format.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-depot-format.h -->
# File Research: sources/block-storage/kvdo/vdo/slab-depot-format.h

Declares the slab depot persisted state format and configuration helpers.

Key type:
- `struct slab_depot_state_2_0`: packed on-disk state containing `slab_config`, first data block, last block, and zone count.

Exports:
- Format header: `VDO_SLAB_DEPOT_HEADER_2_0`.
- Slab count and encoded-size helpers.
- Encode/decode functions for version `2.0`.
- Depot/slab configuration functions.
- `vdo_get_saved_reference_count_size()` for sizing persisted refcount storage.

This header connects superblock state to runtime `slab_depot` construction.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-depot-format.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-depot.c -->
# File Research: sources/block-storage/kvdo/vdo/slab-depot.c

Implements the slab depot runtime: the top-level manager for all slabs, per-zone block allocators, slab summary, resize state, load/drain orchestration, scrub scheduling, and aggregated statistics.

Construction/allocation:
- `vdo_decode_slab_depot()` validates slab size is a power of two, allocates the depot with per-zone allocator slots, records persisted state, and calls `allocate_components()`.
- `allocate_components()` creates the action manager, slab summary, per-zone block allocators, and all slab objects.
- `allocate_slabs()` allocates or extends a slab pointer array, creates slabs assigned round-robin to physical zones, and preserves existing slabs during resize preparation.
- `vdo_allocate_slab_ref_counts()` walks slabs in reverse order through `slab_iterator` and allocates each slab’s refcounts.

Lookup/query API:
- `vdo_get_slab_number()` maps PBN to slab number using the depot’s `slab_size_shift`.
- `vdo_get_slab()` returns the owning slab, entering read-only mode on invalid non-zero PBNs.
- `vdo_get_slab_journal()` returns the owning slab journal.
- `vdo_get_increment_limit()` delegates to the slab’s refcounts unless the slab is unrecovered.
- `vdo_is_physical_data_block()` validates that a PBN is the zero block or maps into the data portion of a slab.
- `vdo_get_slab_depot_allocated_blocks()` sums allocator-owned allocated counts.
- `vdo_get_slab_depot_data_blocks()` returns slab count times data blocks per slab.

Action manager orchestration:
- The depot action manager fans operations out to block allocators on physical-zone threads.
- `vdo_load_slab_depot()` loads slab summary first, then block allocators.
- `vdo_prepare_slab_depot_to_allocate()` sets load type, initializes scrub-zone accounting, and prepares allocators.
- `vdo_drain_slab_depot()` drains allocator/slab metadata for save/flush/rebuild/suspend.
- `vdo_resume_slab_depot()` resumes allocators unless read-only.
- `vdo_commit_oldest_slab_journal_tail_blocks()` records a recovery-journal block release request and schedules the default action; the action eventually runs `vdo_release_tail_block_locks()` across zones.

Resize:
- `vdo_prepare_to_grow_slab_depot()` validates growth, computes new slab count, abandons stale prepared slabs, allocates new slabs, and records old/new sizes.
- `vdo_use_new_slabs()` schedules allocator registration for prepared slabs and finalizes the active slab array.
- `vdo_abandon_new_slabs()` frees prepared-but-unused resize slabs.

Scrubbing/recovery:
- `vdo_scrub_all_unrecovered_slabs()` schedules zone scrub actions.
- `vdo_notify_zone_finished_scrubbing()` decrements zone scrub count and, when last, transitions VDO from recovering to dirty if appropriate.

Statistics/diagnostics:
- Aggregates block allocator, refcount, slab journal, and slab summary stats into `vdo_statistics`.
- `vdo_dump_slab_depot()` logs zone counts, slab count, and release request state.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-depot.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-depot.h -->
# File Research: sources/block-storage/kvdo/vdo/slab-depot.h

Defines `struct slab_depot` and its public management API.

Concept:
- A slab depot owns every slab and every per-physical-zone block allocator for a VDO.
- It keeps one slab pointer array to simplify PBN-to-slab mapping.
- Operations have thread constraints: load/save from load thread, allocation/refcount updates on physical-zone threads, recovery-journal tail commits on the journal-zone thread.

Important fields:
- Zone counts, VDO pointer, `slab_config`, slab summary, action manager.
- First/last/origin block and `slab_size_shift`.
- Load type and recovery-journal lock release request state.
- Scrubbing zone counter.
- Current slabs plus prepared resize slabs.
- Per-zone `block_allocator *allocators[]`.

Public API covers:
- Decode/free/record persisted state.
- Allocate refcounts.
- Zone allocator and PBN/slab/journal lookup.
- Data-block validity and increment limit queries.
- Capacity/statistics.
- Load, prepare-to-allocate, drain, resume.
- Resize prepare/use/abandon.
- Slab journal tail-block commit requests.
- Slab summary access.
- Scrubbing and diagnostics.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-depot.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-iterator.h -->
# File Research: sources/block-storage/kvdo/vdo/slab-iterator.h

Defines an inline reverse iterator for arrays of `struct vdo_slab *`.

Type:
- `struct slab_iterator` stores the slab array, next slab pointer, end slab number, and stride.

Functions:
- `vdo_iterate_slabs()` initializes iteration from `start` down to `end` by `stride`. If the array is `NULL` or `start < end`, iteration is empty.
- `vdo_has_next_slab()` reports whether another slab is available.
- `vdo_next_slab()` returns the current slab and advances to `slab_number - stride`, stopping once it would pass the end.

Used by depot code to walk slabs from higher to lower numbers, for example when allocating refcount objects.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-iterator.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-journal-format.c -->
# File Research: sources/block-storage/kvdo/vdo/slab-journal-format.c

Implements decoding of one slab journal entry from a packed slab journal block.

Function:
- `vdo_decode_slab_journal_entry()`

Behavior:
- Starts with `vdo_unpack_slab_journal_entry()`, which decodes SBN and data increment/decrement from the packed entry.
- If the block header says the block has block-map increments, checks the entry-type bitmap.
- If the bitmap bit is set, overrides the operation to `VDO_JOURNAL_BLOCK_MAP_INCREMENT`.

This supports the dual slab-journal format: dense data-only entries and a lower-capacity “full” format that can distinguish block-map increments.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-journal-format.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-journal-format.h -->
# File Research: sources/block-storage/kvdo/vdo/slab-journal-format.h

Defines the on-disk format for slab journal blocks.

Key formats:
- `struct slab_journal_entry`: unpacked SBN plus journal operation.
- `packed_slab_journal_entry`: 24-bit packed offset with one bit used for increment/decrement.
- `struct slab_journal_block_header`: unpacked header with head, sequence number, nonce, recovery point, metadata type, block-map-increment flag, and entry count.
- `struct packed_slab_journal_block_header`: little-endian on-disk header.
- `struct full_slab_journal_entries`: packed entries plus bitmap for entries that are block-map increments.
- `slab_journal_payload`: union of full-entry layout, data-only dense layout, and raw payload space.
- `struct packed_slab_journal_block`: header plus payload.

Capacity constants:
- `VDO_SLAB_JOURNAL_PAYLOAD_SIZE`
- `VDO_SLAB_JOURNAL_FULL_ENTRIES_PER_BLOCK`
- `VDO_SLAB_JOURNAL_ENTRY_TYPES_SIZE`
- `VDO_SLAB_JOURNAL_ENTRIES_PER_BLOCK`

Helpers:
- `vdo_get_slab_journal_start_block()` computes journal origin inside a slab after data and reference-count blocks.
- `vdo_pack_slab_journal_block_header()` serializes header fields.
- `vdo_unpack_slab_journal_entry()` decodes data increment/decrement entries.
- `vdo_decode_slab_journal_entry()` handles the optional block-map-increment bitmap.

Design point:
- Most steady-state slab journal entries are data updates, so data-only blocks can store more entries. Blocks containing any block-map increments use the bitmap format.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-journal-format.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-journal.c -->
# File Research: sources/block-storage/kvdo/vdo/slab-journal.c

Implements the per-slab journal that records reference-count updates before applying/persisting them safely. It coordinates recovery-journal locks, slab summary tail updates, dirty refcount flush pressure, ring reaping, replay insertion, and normal data-VIO admission.

State model:
- `head`: oldest journal block on disk.
- `unreapable`: oldest block that cannot yet be reaped.
- `tail`: sequence number after the active journal interval.
- `next_commit`: oldest uncommitted write, or tail when none.
- `summarized`/`last_summarized`: tail positions recorded in slab summary.
- `recovery_lock`: recovery-journal block currently held by a dirty tail block.
- Per-block `journal_lock` entries track lock counts and recovery-journal start block.
- `uncommitted_blocks` tracks outstanding tail-block writes.
- `entry_waiters` queues data VIOs waiting to append entries.

Creation:
- `vdo_make_slab_journal()` sizes the journal from `slab_config`, initializes thresholds, statistics, summary pointer, recovery journal pointer, packed block buffer, dirty list entries, nonce/metadata header, and sequence state.
- `flushing_deadline` is normally just before the blocking threshold, leaving time to write refcount blocks before blocking.

Appending:
- `vdo_add_slab_journal_entry()` validates slab/open/read-only state, queues the `data_vio`, optionally registers unrecovered slabs for high-priority scrubbing, and calls `add_entries()`.
- `add_entries()` processes waiters in order so slab journal order matches recovery journal order.
- It stops adding entries during partial writes, rebuild, tail commit wait, blocking threshold, or full on-disk journal lock conditions.
- First entry in a new tail block:
  - acquires recovery-journal block reference,
  - marks the slab journal dirty in allocator order by recovery lock,
  - initializes journal block lock count,
  - may dirty all refcount blocks for the first-ever block.
- `add_entry_from_waiter()` appends the journal entry and then calls `vdo_modify_slab_reference_count()` with the slab journal point for that entry.

Writing and committing:
- `commit_tail()` writes a non-empty tail unless read-only or already waiting.
- Before writing, it removes the journal from the allocator dirty list because the recovery journal no longer needs to force that in-progress tail to commit.
- `write_slab_journal_block()` packs the header, copies the block to a VIO, adjusts unused per-entry locks for partial blocks, submits metadata write, advances `tail`, and reinitializes the in-memory tail block.
- `complete_write()` updates write statistics, advances `next_commit`, and triggers slab-summary tail update.

Slab summary and lock release:
- `update_tail_block_location()` writes the committed tail offset, dirty/clean status, load-refcounts flag, and free-block hint to the slab summary.
- `release_journal_locks()` runs after summary write, releases corresponding recovery-journal references and slab-journal block locks, then tries reaping and further summary updates.

Reaping:
- `reap_slab_journal()` advances `unreapable` while old journal blocks have no locks.
- It always issues a lower-layer flush before setting `head = unreapable`, preventing reference-block writes from being lost before overwriting old journal blocks.
- Lock decrement through `vdo_adjust_slab_journal_block_reference()` may trigger reaping.

Recovery/replay:
- `vdo_attempt_replay_into_slab_journal()` accepts only recovery points newer than the current tail header’s recovery point. It may commit a full tail first and wait for recovery if necessary.
- If the ring would overrun, replay advances `head`/`unreapable` because the old head must already have been reaped before crash.
- `vdo_decode_slab_journal()` reads the summarized tail block, validates nonce/type, restores `tail`, `head`, and tail header, or skips impossible default summary states.
- `vdo_slab_journal_requires_scrubbing()` checks journal length against scrubbing threshold.

Drain/resume:
- `vdo_drain_slab_journal()` commits the tail for most drain modes, but skips rebuilding, suspending, and save-for-scrubbing.
- `vdo_resume_slab_journal()` reopens/reset journals after successful save.
- `vdo_abort_slab_journal_waiters()` aborts queued VIOs with read-only errors.

Failure behavior:
- Metadata write/flush errors are recorded and force VDO read-only mode.
- Waiters are aborted after read-only transition.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-journal.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-journal.h -->
# File Research: sources/block-storage/kvdo/vdo/slab-journal.h

Declares the slab journal runtime structure and public operations.

Important types:
- `struct journal_lock`: per-slab-journal-block lock count plus the recovery-journal block sequence that lock protects.
- `struct slab_journal`: owns waiters, entry queue, parent slab, state flags, sequence numbers, recovery lock, entry capacities, recovery journal pointer, summary zone pointer, statistics, outstanding write list, current packed tail block, thresholds, dirty-list entry, reap pointer, and flexible array of journal locks.

Inline helpers:
- `vdo_pack_slab_journal_entry()` packs a slab block number and increment bit.
- `vdo_unpack_slab_journal_block_header()` decodes packed header fields and recovery point.
- `vdo_get_slab_journal_block_offset()` maps sequence numbers to ring offsets.

Public API:
- Construction/destruction and state: `vdo_make_slab_journal()`, `vdo_free_slab_journal()`, `vdo_is_slab_journal_blank()`, `vdo_is_slab_journal_active()`.
- Waiter/reopen/replay: `vdo_abort_slab_journal_waiters()`, `vdo_reopen_slab_journal()`, `vdo_attempt_replay_into_slab_journal()`.
- Normal operation: `vdo_add_slab_journal_entry()`, `vdo_adjust_slab_journal_block_reference()`, `vdo_release_recovery_journal_lock()`.
- Lifecycle: `vdo_drain_slab_journal()`, `vdo_decode_slab_journal()`, `vdo_resume_slab_journal()`.
- Recovery policy: `vdo_slab_journal_requires_scrubbing()`.
- Diagnostics: `vdo_dump_slab_journal()`.

This header is central to interactions among slabs, refcounts, recovery journal, block allocators, and slab summary.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-journal.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-scrubber.c -->
# File Research: sources/block-storage/kvdo/vdo/slab-scrubber.c

Implements slab scrubbing for unrecovered slabs. Scrubbing reads a slab’s journal, replays relevant entries into refcounts, saves rebuilt refcount blocks, and moves to the next queued slab.

Construction:
- `vdo_make_slab_scrubber()` allocates the scrubber, a multi-block metadata VIO, and a buffer large enough for one full slab journal.
- The scrubber starts suspended and has two slab queues: high-priority and normal.

Queueing:
- `vdo_register_slab_for_scrubbing()` removes the slab from allocator queues, increments scrubber slab count once, records that it was queued, and enqueues it on high-priority or normal list.
- High-priority mode is used when journal pressure requires urgent recovery before more entries can be admitted.

Scrub flow:
- `vdo_scrub_slabs()` prepares the scrubber completion and starts `scrub_next_slab()`.
- `scrub_next_slab()` notifies clean-slab waiters, handles read-only/drain/empty cases, selects the next slab, and starts a slab action in `VDO_ADMIN_STATE_SCRUBBING`.
- `start_scrubbing()` skips journal replay if the slab summary says the slab is clean; otherwise it reads the whole slab journal.
- `apply_journal_entries()` determines journal `head` from the last/tail block, validates every block from head to tail, replays entries, and then starts `VDO_ADMIN_STATE_SAVE_FOR_SCRUBBING` so rebuilt refcounts are persisted.
- `slab_scrubbed()` marks the slab finished, decrements slab count, and continues.

Replay validation:
- Each journal block must match nonce, metadata type, expected sequence number, and entry capacity constraints.
- `apply_block_entries()` decodes entries and rejects out-of-range slab block numbers.
- Entries are applied through `vdo_replay_reference_count_change()`, which skips changes already represented by saved refcount commit points.

Control API:
- `vdo_scrub_high_priority_slabs()` optionally promotes at least one normal slab, then scrubs only high-priority slabs.
- `vdo_stop_slab_scrubbing()` drains/suspends after the current slab.
- `vdo_resume_slab_scrubbing()` resumes if slabs remain.
- `vdo_enqueue_clean_slab_waiter()` lets callers wait for a clean slab while scrubber is active.

Failure:
- Metadata read errors and corrupt journal validation enter read-only mode and complete with the error.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-scrubber.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-scrubber.h -->
# File Research: sources/block-storage/kvdo/vdo/slab-scrubber.h

Defines the slab scrubber type and public API.

`struct slab_scrubber` contains:
- Completion for current scrub operation.
- High-priority and normal slab lists.
- Wait queue for callers waiting on scrubbed slabs.
- Cross-thread queried `slab_count`.
- Admin state.
- High-priority-only mode flag.
- Read-only notifier.
- Current slab.
- Metadata VIO and buffer for reading slab journal data.

Exports:
- Create/free scrubber.
- Register slabs for normal or high-priority scrubbing.
- Scrub all slabs or high-priority slabs.
- Stop/resume scrubbing.
- Queue clean-slab waiters.
- Query scrubber slab count and dump diagnostics.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-scrubber.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-summary-format.h -->
# File Research: sources/block-storage/kvdo/vdo/slab-summary-format.h

Defines the compact on-disk per-slab summary entry.

Key type:
- `tail_block_offset_t`: `uint8_t`, offset of the slab journal tail block.

`struct slab_summary_entry` packs:
- tail block offset,
- 6-bit fullness hint,
- `load_ref_counts` bit,
- `is_dirty` bit.

Helpers:
- `vdo_get_slab_summary_zone_size()` computes blocks per summary zone as `MAX_VDO_SLABS / entries_per_block`.
- `vdo_get_slab_summary_size()` multiplies zone size by `MAX_VDO_PHYSICAL_ZONES`.
- `vdo_get_slab_summary_hint_shift()` computes how much to shift free-block counts down to fit in the 6-bit fullness hint.

The summary is used by allocator load, slab journal decode, scrub decisions, and fast approximate free-space ordering.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-summary-format.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-summary.c -->
# File Research: sources/block-storage/kvdo/vdo/slab-summary.c

Implements the slab summary: a per-zone persisted table of compact per-slab state used for journal recovery, refcount loading, cleanliness, and free-space hints.

Fullness hints:
- `compute_fullness_hint()` compresses free-block count using `summary->hint_shift`, preserving nonzero free counts as at least `1`.
- `get_approximate_free_blocks()` expands the hint back to an approximate free count.

Construction:
- `vdo_make_slab_summary()` skips allocation for formatter use when no partition is supplied.
- Otherwise it allocates a `struct slab_summary` with one zone per physical zone, allocates all entries for all possible zones/slabs, initializes default entries, sets partition origin, and creates `slab_summary_block` objects with metadata VIOs.
- Default entries use tail block offset `0`, full free-space hint, `load_ref_counts = false`, and clean state.

Writing:
- Each `slab_summary_block` has current and next waiter queues plus a write VIO.
- `vdo_update_slab_summary_entry()` updates the in-memory entry, preserving `load_ref_counts` once set, queues the caller waiter, and launches a block write.
- `launch_write()` batches all pending waiters for the block, copies entries to an outgoing buffer, and submits `REQ_OP_WRITE | REQ_PREFLUSH`.
- The preflush ensures slab journal tail blocks and reference updates covered by the summary update are stable.
- Completion notifies current waiters with success or read-only status, clears writing state, and launches queued next updates if present.
- Write errors record metadata I/O failure and enter read-only mode.

Drain/resume:
- `vdo_drain_slab_summary_zone()` starts admin draining and completes when no writes remain.
- `vdo_resume_slab_summary_zone()` resumes a quiescent summary zone.

Read/query API:
- Tail offset: `vdo_get_summarized_tail_block_offset()`.
- Refcount load flag: `vdo_must_load_ref_counts()`.
- Cleanliness: `vdo_get_summarized_cleanliness()`.
- Approximate free count: `vdo_get_summarized_free_block_count()`.
- Per-slab statuses for allocator selection: `vdo_get_summarized_slab_statuses()`.

Loading/combining:
- `vdo_load_slab_summary()` creates a multi-block VIO over the whole summary partition.
- Formatting and loading-for-rebuild skip disk read and immediately use initialized/default data.
- Normal load reads all zone summaries, then `combine_zones()` merges old per-zone layouts into zone 0 and copies the combined summary to every zone region.
- The combined summary is written back to disk, then load completes.
- `zones_to_combine` supports old persisted zone counts during load.

Statistics:
- `vdo_get_slab_summary_statistics()` returns cumulative blocks written from an atomic counter.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-summary.c -->