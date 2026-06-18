# sources/storage-engines/wiredtiger/src/support/stat.c lines 1-4527

## Chunk Scope

This chunk is the generated front portion of WiredTiger's statistic support implementation. It starts with the `DO NOT EDIT: automatically built by dist/stat.py` banner, includes `wt_internal.h`, defines the full data-source statistic description table, implements data-source statistic initialization, clearing, and aggregation, then defines the connection statistic description table and implements connection statistic initialization and clearing. The chunk ends in the early cache/capacity section of `__wt_stat_connection_aggregate`; the rest of connection aggregation and the later session-stat helpers are outside this work item.

The researched span is `sources/storage-engines/wiredtiger/src/support/stat.c:1-4527`.

## Purpose

The file gives WiredTiger's statistics cursor and internal monitoring paths a generated mapping between stable statistic slots, human-readable descriptions, and concrete `int64_t` fields in generated statistic structures. It also provides the lifecycle helpers that allocate per-slot statistic arrays, reset clearable counters, and aggregate per-session/per-handle counters into a single visible result.

The chunk covers two statistic families:

- Data-source statistics for a `WT_DATA_HANDLE`, including btree shape, block manager, cache, cursor, layered table, reconciliation, rollback-to-stable, and transaction counters.
- Connection statistics for a `WT_CONNECTION_IMPL`, including global versions of many data-source counters plus background compaction, backup, block cache, connection, capacity, checkpoint, cursor sweep, data-handle, disaggregated, live-restore, load-control, lock, log, perf histogram, prefetch, session, thread, tiered, and transaction counters.

Because this file is generated, the durable API contract is not the hand-written C logic but the generated slot ordering and descriptions that must stay synchronized with `src/include/stat.h` and public statistic ids.

## Important APIs, Types, and Data Structures

### Description tables

`__stats_dsrc_desc[]` maps every data-source statistic slot to the string returned by a `statistics:` cursor. The table includes categories such as `autocommit`, `backup`, `block-disagg`, `block-manager`, `btree`, `cache`, `cache_walk`, `checkpoint-cleanup`, `checkpoint`, `compression`, `cursor`, `layered`, `reconciliation`, `session`, and `transaction`.

`__stats_connection_desc[]` performs the same role for connection statistics. Its categories are broader and include connection-only systems such as background compaction, block cache, capacity, data-handle sweeping, live restore, load control, lock manager, logging, performance histograms, prefetch, thread-state, thread-yield, and tiered storage.

The accessors `__wt_stat_dsrc_desc` and `__wt_stat_connection_desc` ignore the cursor argument and return `desc[slot]` through an output pointer. They assume the caller has already bounded `slot` with the cursor's statistic count.

### Statistic storage

`WT_DSRC_STATS` and `WT_CONNECTION_STATS` are generated structures in `src/include/stat.h`. That header documents that statistic structures are treated as arrays of `int64_t`, allowing macros to translate a field name into a slot offset.

Both statistic families use 23 counter slots:

- `WT_STAT_DSRC_COUNTER_SLOTS`
- `WT_STAT_CONN_COUNTER_SLOTS`

Each session writes to a slot derived from its session id (`session->id % slot_count`). This reduces write contention without requiring per-CPU ids. Reads aggregate all slots by field offset.

`WT_DATA_HANDLE` stores:

- `WT_DSRC_STATS *stats[WT_STAT_DSRC_COUNTER_SLOTS]`
- `WT_DSRC_STATS *stat_array`

`WT_CONNECTION_IMPL` stores the analogous connection arrays.

### Data-source functions

- `__wt_stat_dsrc_init_single(WT_DSRC_STATS *stats)` zeroes one data-source stat struct with `memset`.
- `__wt_stat_dsrc_init(WT_SESSION_IMPL *session, WT_DATA_HANDLE *handle)` allocates `WT_STAT_DSRC_COUNTER_SLOTS` contiguous structs with `__wt_calloc`, stores each element address in `handle->stats[i]`, and zeroes it.
- `__wt_stat_dsrc_discard(WT_SESSION_IMPL *session, WT_DATA_HANDLE *handle)` frees `handle->stat_array`.
- `__wt_stat_dsrc_clear_single(WT_DSRC_STATS *stats)` resets generated clearable fields and intentionally leaves current-state or high-water fields untouched, annotated with `/* not clearing ... */`.
- `__wt_stat_dsrc_clear_all(WT_DSRC_STATS **stats)` clears every per-session slot by calling `__wt_stat_dsrc_clear_single`.
- `__wt_stat_dsrc_aggregate_single(WT_DSRC_STATS *from, WT_DSRC_STATS *to)` merges one already-materialized source struct into `to`.
- `__wt_stat_dsrc_aggregate(WT_DSRC_STATS **from, WT_DSRC_STATS *to)` reads and sums across all per-slot structs using `WT_STAT_DSRC_READ`.

### Connection functions

- `__wt_stat_connection_init_single(WT_CONNECTION_STATS *stats)` zeroes one connection stat struct.
- `__wt_stat_connection_init(WT_SESSION_IMPL *session, WT_CONNECTION_IMPL *handle)` allocates and initializes the connection stat slots.
- `__wt_stat_connection_discard(WT_SESSION_IMPL *session, WT_CONNECTION_IMPL *handle)` frees the contiguous connection stat array.
- `__wt_stat_connection_clear_single(WT_CONNECTION_STATS *stats)` resets clearable counters while preserving gauges, configuration values, current states, min/max/recent timing fields, and other persistent observability values.
- `__wt_stat_connection_clear_all(WT_CONNECTION_STATS **stats)` clears every connection stat slot.
- `__wt_stat_connection_aggregate(WT_CONNECTION_STATS **from, WT_CONNECTION_STATS *to)` begins at line 4017. In this chunk it aggregates from autocommit through `capacity_bytes_log`; the function continues after line 4527.

## Control Flow

Initialization is simple and allocation-driven. The owner (`WT_DATA_HANDLE` or `WT_CONNECTION_IMPL`) calls the generated init routine, which allocates one contiguous array sized by the generated slot count. The pointer array is then populated with addresses into that allocation. If allocation fails, `WT_RET` returns the error before any later setup.

Statistics writes happen elsewhere in WiredTiger through macros and subsystem code. This file's main runtime paths are read/reset paths:

1. Statistics cursors call the description function for a slot to expose the stable textual name.
2. If a cursor requests current values, cursor/stat code points at the relevant `WT_*_STATS` struct or an aggregate buffer.
3. For multi-slot owners, aggregate helpers add each field from all slots into a single output struct. Data-source aggregation is complete in this chunk; connection aggregation begins here and continues later.
4. If statistics are opened with clear semantics, clear helpers reset only counters that are meant to restart from zero.

The aggregation functions are deliberately mechanical. Most fields use addition. Some scalar configuration or high-water fields use a maximum merge, for example data-source `allocation_size`, block version fields, btree page-size limits, maximum tree depth, `rec_multiblock_max`, and connection fields such as `npos_evict_walk_max`, `cache_hazard_max`, and `npos_read_walk_max`.

## State and Persistence Behavior

This code manages in-memory observability state only. It does not write WiredTiger metadata, table data, logs, or checkpoints directly.

The state model is nevertheless important:

- Per-slot arrays are persistent for the lifetime of their owning connection or data handle and are released through the matching discard routine.
- Clear routines intentionally do not fully zero the structures. Gauges, current states, configured limits, recent/min/max timings, and some cumulative state remain visible across a clear operation.
- Aggregation is race-tolerant rather than transactional. `src/include/stat.h` notes that summing per-slot `int64_t` counters can race with concurrent writers; negative aggregate results are clamped to zero for API compatibility.
- Statistic ordering is externally visible through statistic cursor slots and `WT_STAT_*` ids. Reordering fields or descriptions without regenerating all related artifacts would break callers that depend on stable ids.

Persistence relevance is indirect. Many counters describe persistent subsystems such as block allocation, checkpoint, history store, recovery, logging, rollback-to-stable, tiered storage, and disaggregated metadata. The counters report those systems' behavior, but their values are not themselves durable state.

## Dependencies and Integration Points

Direct dependencies include:

- `wt_internal.h`, which brings in all WiredTiger internal types, allocation helpers, stat macros, and generated declarations.
- `src/include/stat.h`, which defines slot counts, field-offset macros, read/write macros, clear flags, generated `WT_CONNECTION_STATS` and `WT_DSRC_STATS`, and public statistic base ids.
- `__wt_calloc`, `__wt_free`, `WT_RET`, and `WT_UNUSED`.
- Generated extern declarations in `src/include/extern.h`.

Runtime integration points include:

- `src/cursor/cur_stat.c`, which sets statistic cursor bases/counts and exposes connection/data-source stats to users.
- `src/schema/schema_stat.c`, which builds data-source statistic cursor views.
- `src/conn/conn_stat.c`, which gathers connection-level stats.
- Subsystems that write fields through statistic macros, including block managers, btree tree-walk stats, cache/eviction, reconciliation, transaction/rollback-to-stable, cursor operations, checkpoint, logging, tiered/disaggregated storage, live restore, and lock/load-control code.
- Data-handle and connection lifecycle code, which owns when the generated init/discard helpers are called.

## Risks and Maintenance Notes

- The file is generated by `dist/stat.py`; manual edits will be overwritten and can desynchronize descriptions, structures, public ids, and aggregate/clear behavior.
- The description arrays must match generated struct field order exactly. An off-by-one slot bug would surface as statistics cursors returning the wrong name for a value.
- Clear semantics are encoded as generated assignments and `not clearing` omissions. Misclassifying a field changes user-visible behavior for statistics opened with clear/reset options.
- Aggregation semantics are per-field. Counters usually sum, but gauges/high-water/configuration fields often need max or preservation semantics. Generator changes that turn max fields into sums can produce misleading observability data.
- Aggregation reads race with writers by design. This is acceptable for approximate statistics but unsuitable for code that would rely on these helpers for correctness decisions.
- The assigned chunk ends mid-`__wt_stat_connection_aggregate`; any final per-file research must merge this note with later chunks to describe the full connection aggregation function and session stat helpers.

## Test Signals

Useful validation signals for this chunk are statistics-cursor and generated-file consistency tests:

- Opening `statistics:` and `statistics:<uri>` cursors should return stable ids, descriptions, and values for connection and data-source stats.
- Statistics opened with clear behavior should reset clearable counters while preserving current-state gauges and documented high-water/configuration values.
- Workloads that exercise cursor operations, cache eviction, checkpoint, reconciliation, rollback-to-stable, logging, backup, tiered storage, disaggregated storage, and live restore should show expected non-zero counters in their matching categories.
- Multi-session workloads should verify aggregation across per-session slots, not just one writer slot.
- Generated drift checks should rerun `dist/stat.py` and verify `src/support/stat.c`, `src/include/stat.h`, and generated extern declarations remain synchronized.
