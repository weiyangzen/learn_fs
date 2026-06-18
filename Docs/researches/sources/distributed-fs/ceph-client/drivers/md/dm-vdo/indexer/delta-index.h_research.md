# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/delta-index.h

## Purpose
`delta-index.h` declares the UDS delta-index data structures and APIs for mutable volume/open-chapter indexes, immutable chapter-index pages, iteration, mutation, persistence, sizing, and statistics.

## Important APIs, Types, And Functions
- `struct delta_list` records bit start, bit size, and saved iterator position for one sorted list.
- `struct delta_zone` owns list memory, descriptors, save writer, coding constants, counters, list range, and tag.
- `struct delta_list_save_info` is the packed descriptor for one saved non-empty list.
- `struct delta_index` groups zones and records global list/zone sizing, load counts, mutability, and tag.
- `struct delta_index_page` embeds a one-zone immutable delta index over a page buffer.
- `struct delta_index_entry` is both iterator, found entry, and insertion/removal handle.
- `struct delta_index_stats` aggregates memory/rebalance/record/collision/discard/overflow/list counts.
- APIs cover initialize, page initialize, reset, pack, save/restore, guard lists, search/iterate, get/set payload, put/remove entries, stats, sizing, and logging.

## Control Flow And Data Flow
Callers create a mutable index with a zone/list/memory/coding configuration. They search a list to obtain a `delta_index_entry`, then use that entry as a mutation handle. Immutable pages expose the same search interface but reject mutation through `assert_mutable_entry()` in the implementation.

## State And Persistence Behavior
The header distinguishes mutable and immutable state via `delta_index.mutable` and by whether entry handles point to real `delta_list` descriptors or a temporary page-derived descriptor. Save-info structs and page descriptors are persistent-format contracts. Runtime counters are used for diagnostics and sizing feedback.

## Dependencies And Integration Points
The header depends on cache alignment, numeric/time helpers, config, and I/O factory types. It is included by chapter-index, volume-index, geometry, and other indexer modules.

## Risks
- Consumers must respect the private/public split in `struct delta_index_entry`; private fields are only stable across delta-index API calls.
- Mutating through an entry from an immutable page is invalid and returns bad-state errors.
- `MAX_ZONES` from configuration constrains `load_lists`.
- Tags must match between saved list data and the delta index being restored.

## Test Signals
API-level tests should verify mutable versus immutable operation handling, stats aggregation across zones, save-info packing assumptions, and iterator behavior at start, found, collision, insertion-point, and end-of-list states.
