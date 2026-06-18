# File Research: sources/block-storage/kvdo/vdo/block-map-recovery.c

## Purpose

Replays recovery-journal block mapping entries into the block map after recovery, batching work by block map page.

## Main Responsibilities

- Allocates a recovery completion containing a ring of page completions.
- Sorts/replays numbered journal entries by block map page and slot while preserving journal order for identical slots.
- Fetches block map pages concurrently up to a bounded count.
- Applies all entries for a page to that page.
- Requests page writeback after replay.
- Drains/flushes the block map after replay.
- Handles abort and cleanup.

## Key Structure

`struct block_map_recovery_completion` includes:
- main completion and sub-task completion,
- admin/logical thread IDs,
- target block map,
- abort/launch state,
- journal entry array,
- heap wrapper over entries,
- current entry cursors,
- outstanding page count,
- page completion array.

## Important Functions

- `vdo_make_recovery_completion()` allocates and initializes replay state and heap ordering.
- `compare_mappings()` orders mappings by page PBN, slot, then serial number, reversed for max-heap behavior.
- `find_entry_starting_next_page()` advances through entries until the next page boundary.
- `apply_journal_entries_to_page()` writes journal-provided entries into page slots.
- `fetch_page()` initializes and launches a writable page-cache fetch.
- `recover_ready_pages()` processes ready pages in sorted order, applies mappings, requests writes, releases completions, and launches more fetches.
- `vdo_recover_block_map()` is the public entry point.

## Behavior Details

The replay heap lets recovery iterate entries in sorted page/slot order without a separate full sort call. The serial `number` field preserves original journal order for multiple mappings to the same slot.

After all entries are applied, recovery launches a sub-task on the admin thread to drain the block map under `VDO_ADMIN_STATE_RECOVERING`, ensuring replayed changes are flushed.

## Dependencies and Interactions

- Uses block map page cache through page completions.
- Uses `heap` for sorted replay.
- Uses admin/completion mechanisms to switch between logical and admin threads.
- Uses `vdo_drain_block_map()` to flush changes before parent completion.

## Notable Edge Cases

- Page completions intentionally hold pages locked until recovery releases them.
- If recovery aborts, ready page completions are released before completing parent.
- Page fetch errors set the recovery result and abort further normal replay.
- Empty replay heap completes immediately.
