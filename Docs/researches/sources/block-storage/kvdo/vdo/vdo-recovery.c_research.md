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
