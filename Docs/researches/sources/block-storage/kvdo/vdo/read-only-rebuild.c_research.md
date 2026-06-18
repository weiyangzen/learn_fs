# File Research: sources/block-storage/kvdo/vdo/read-only-rebuild.c

Read completely: 495 lines.

This file coordinates rebuilding VDO metadata to clear read-only mode or support upgrade rebuilds. It loads the recovery journal, extracts valid journal increment entries, replays them into the block map, rebuilds reference counts from the resulting block map, drains the slab depot to save rebuilt state, and reinitializes the recovery journal.

`struct read_only_rebuild_completion` owns the rebuild completion, a subtask completion, loaded journal bytes, extracted numbered block mappings, head/tail sequence numbers, and rebuilt usage counts. `vdo_launch_rebuild()` logs the rebuild type, increments read-only recovery statistics when appropriate, allocates the completion object, and starts by loading the slab depot. The subtask then loads the recovery journal from logical zone 0.

`apply_journal_entries()` finds valid journal head/tail blocks, extracts valid increment entries, enables block-map page-cache rebuild mode to suppress expected errors, and calls `vdo_recover_block_map()`. `extract_journal_entries()` scans exact journal blocks from head to tail, validates block headers and sectors, clamps claimed entry counts, and appends only valid increment operations. After block-map recovery, `vdo_rebuild_reference_counts()` rebuilds refcounts and records logical/block-map usage counts. `finish_rebuild()` updates recovery journal state with the new tail and usage counts.

Dependencies: recovery journal loading/scanning, packed journal sector layout, block map recovery, reference-count rebuild, slab depot load/drain, VDO completion framework, page-cache rebuild mode, and VDO component states.

Security/reliability notes: damaged entries are ignored during read-only recovery, but invalid allocation or structural errors abort the rebuild. The loaded journal buffer and extracted entry array are freed in all normal completion paths. The rebuild assumes logical zone 0 context for journal loading and replay.
