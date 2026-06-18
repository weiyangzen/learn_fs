# subset-b-008890 Research

Grouped research for TiKV `tidb_query_executors` aggregation, table scan, TopN, shared executor utilities, and the `tidb_query_expr` crate manifest. Each section preserves the source path for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/slow_hash_aggr_executor.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/slow_hash_aggr_executor.rs

## Purpose

`slow_hash_aggr_executor.rs` implements `BatchSlowHashAggregationExecutor`, a grouped hash aggregation executor for batch coprocessor execution. It supports multiple GROUP BY expressions by serializing group keys into a backing byte buffer and using unsafe references into that buffer as `HashMap` keys. The file explicitly labels the approach as slow and notes a correctness caveat: serialized data is not always a fully correct group key representation, referencing TiDB issue `pingcap/tidb#10467`.

## Important APIs, Types, and Functions

- `BatchSlowHashAggregationExecutor<Src>` is a thin wrapper around the shared `AggregationExecutor<Src, SlowHashAggregationImpl>`. It forwards `BatchExecutor` methods such as `schema`, `next_batch`, stats collection, scanned range, storage stats, and cacheability to the shared executor.
- `BatchSlowHashAggregationExecutor::check_supported` requires at least one group-by expression, validates each group-by expression with `RpnExpressionBuilder::check_expr_tree_supported`, and validates aggregate functions with `AllAggrDefinitionParser`.
- `BatchSlowHashAggregationExecutor::new` builds RPN group-by expressions from protobuf `Expr` descriptors using the source schema length, then calls `new_impl`.
- `new_impl` prepares group-key bookkeeping: a leading zero in `group_key_offsets`, the list of byte-typed group-by columns that need duplicate original encoding for output, the `original_group_by_col_index` remap, and buffers/caches sized for batch processing.
- `SlowHashAggregationImpl` is the concrete `AggregationExecutorImpl`. Its main state is `states`, `groups`, `group_key_buffer`, `group_key_offsets`, `states_offset_each_logical_row`, `group_by_results_unsafe`, and `cached_encoded_result`.
- `GroupKeyRefUnsafe` stores a raw pointer plus begin/end offsets into `group_key_buffer` and implements `Hash`, `PartialEq`, and `Eq` by dereferencing those ranges.

## Control Flow

Construction builds group-by RPN expressions and creates `AggregationExecutor::new`, which parses aggregate function descriptors and then calls `prepare_entities`. `prepare_entities` appends group-by result field types after aggregate result columns in the output schema.

On each input batch, `AggregationExecutor` calls `process_batch_input`. The slow hash implementation first decodes all source columns needed by the group-by expressions, then evaluates group-by RPN expressions into `group_by_results_unsafe` with erased lifetimes. For each logical row, it appends sort-key encoded group-by values to `group_key_buffer`. Byte-typed group-by expressions are stored twice: sort-key form for grouping and original datum form for later output. Scalar expression encodings are cached in `cached_encoded_result` so constants do not re-encode for every row.

After encoding a candidate key, the executor builds a `GroupKeyRefUnsafe` over the sort-key slice and probes `groups`. A vacant entry gets the next group index and creates one aggregate state per aggregate function. An occupied entry truncates the newly appended duplicate key material and offsets, then reuses the existing group index. The selected state offset is recorded per logical row. Finally, `HashAggregationHelper::update_each_row_states_by_offset` evaluates aggregate argument expressions and updates the correct group state for each row.

The executor only emits after the source is drained. `iterate_available_groups` asserts `src_is_drained.stop()`, takes the `groups` map, iterates group indices, pushes aggregate results through the shared iteratee, and reconstructs group-by output columns from `group_key_buffer` and `group_key_offsets`. Because hash map iteration order is unspecified, output group order is intentionally unstable.

## State and Persistence Behavior

All state is in-memory and per executor instance. There is no durable persistence. `states` persists aggregate states across input batches until final output. `group_key_buffer` and `group_key_offsets` retain the canonical encoded key material for unique groups; duplicate row keys are rolled back immediately. `group_by_results_unsafe` contains batch-local expression outputs and is explicitly cleared after updating states. `cached_encoded_result` persists encoded scalar group-by values for the lifetime of the executor.

The unsafe key references require `group_key_buffer` to remain allocated and not move. The file boxes the `Vec<u8>` so the `Vec` object address is stable for `NonNull<Vec<u8>>`, while the vector's internal allocation may grow; `GroupKeyRefUnsafe` dereferences the current `Vec` and indexes by offsets, so it does not store raw element pointers.

## Dependencies and Integration Points

This executor integrates with `crate::interface::BatchExecutor`, the shared `util::aggr_executor::AggregationExecutor`, `tidb_query_aggr` aggregate function state/update traits, `tidb_query_expr` RPN expression evaluation, and `LazyBatchColumnVec` storage from `tidb_query_datatype`. It relies on `collections::HashMap` for grouping, `AllAggrDefinitionParser` for aggregate metadata, and `HashAggregationHelper` for row-to-state updates. Runtime drain, paging, warnings, stats, scanned ranges, and storage stats are handled by the shared aggregation wrapper and source executor.

## Risks and Edge Cases

- The file-level FIXME is a real correctness risk: serialized group keys may not be semantically correct for all SQL equality/collation cases.
- Unsafe lifetime erasure and raw pointer key wrappers demand strict ownership discipline. Any future mutation that invalidates offsets or moves the boxed `Vec` object would be dangerous.
- Hash output order is nondeterministic, so consumers and tests must not depend on order unless sorted externally.
- The executor withholds all results until source drain; memory grows with number of groups and stored key bytes. Paging can force a `PagingDrain` once group count reaches the configured threshold, but partial result readiness remains `false` in this implementation.
- `check_supported` asserts non-empty group-by; this executor is not the no-group aggregate path.

## Test Signals

The integration test builds grouped aggregation over mixed `Real`, `Bytes`, nullable values, constants, arithmetic expressions, and UTF-8 collation. It verifies empty batches before drain, final group count, output schema cardinality, aggregate results, original byte group-by output, scalar group-by values, and order-independent validation by sorting returned groups. Shared aggregation paging tests in `util/aggr_executor.rs` also exercise slow hash behavior with paging sizes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/slow_hash_aggr_executor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/stream_aggr_executor.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/stream_aggr_executor.rs

## Purpose

`stream_aggr_executor.rs` implements `BatchStreamAggregationExecutor`, the batch executor for stream aggregation. It assumes rows are already ordered by the GROUP BY keys, so it can aggregate consecutive equal keys and release complete groups before the entire source is drained. This makes it lower-memory than hash aggregation for sorted streams.

## Important APIs, Types, and Functions

- `BatchStreamAggregationExecutor<Src>` wraps `AggregationExecutor<Src, BatchStreamAggregationImpl>` and forwards the `BatchExecutor` interface.
- `check_supported` requires non-empty group-by expressions, validates group-by RPN support, and validates aggregate functions through `AllAggrDefinitionParser`.
- `new` builds RPN group-by expressions from protobuf descriptors and delegates to `new_impl`.
- `BatchStreamAggregationImpl` stores `group_by_exps`, `group_by_exps_types`, `group_by_field_type`, the current buffered group `keys`, aggregate `states`, and unsafe expression result buffers for group-by and aggregate arguments.
- `update_current_states` updates the most recent group's aggregate states for a logical row range, with scalar inputs handled via `update_repeat!` and vector inputs via `update_vector!`.

## Control Flow

Construction records group-by field types and eval types, creates the concrete implementation, and passes it to the shared aggregation wrapper. `prepare_entities` appends group-by fields after aggregate result columns.

For each source batch, `process_batch_input` decodes all columns used by both group-by expressions and aggregate argument expressions, evaluates both sets into batch-local unsafe buffers, then scans logical rows in order. For each row it forms scalar references for the group key and compares them with the last buffered key via `ScalarValueRef::cmp_sort_key` and the group-by field type. If the key matches the last group, it continues accumulating. If the key changes, it updates the previous current group over the row range `[group_start_logical_row, logical_row_idx)`, stores the new key as owned `ScalarValue`s, creates one state per aggregate function, and starts a new group. After the loop, it updates the current group over the remaining range.

`iterate_available_groups` is where stream aggregation differs from hash aggregation. If the source is drained, all buffered groups are complete. If the source remains, the trailing group might continue in a future batch, so it emits only `groups_len - 1` groups. It drains the emitted states and keys from the front of the vectors, pushes aggregate result columns through the shared iteratee, and materializes group-by columns as decoded columns. `is_partial_results_ready` returns true once at least two groups are buffered, because that means at least one complete group is available.

## State and Persistence Behavior

The executor keeps only the not-yet-emitted group keys and aggregate states in memory. Complete groups are drained from `keys` and `states` whenever partial results are emitted. The last group is retained across batch boundaries until a different key arrives or the source drains. Unsafe expression result buffers are batch-local allocation reuse buffers and are cleared after processing each batch. There is no durable persistence.

## Dependencies and Integration Points

The file integrates with `AggregationExecutor`, `BatchExecutor`, `tidb_query_aggr` state/update macros, `tidb_query_expr` RPN evaluation, and `tidb_query_datatype` scalar comparison/collation behavior. It delegates warning/drain/result wrapping and paging to the shared aggregation executor. Its correctness depends on an upstream planner or executor preserving GROUP BY sort order.

## Risks and Edge Cases

- The executor assumes sorted input. If upstream ordering is wrong, equal groups separated by another group will be emitted as separate groups.
- Partial emission excludes the trailing group; arithmetic around `groups_len - 1` is guarded by `is_partial_results_ready`, but future changes must preserve that invariant.
- Unsafe lifetime erasure is used for expression result buffers. Results must not outlive the current batch.
- Group comparison uses sort-key semantics and field types, making collation correctness dependent on datatype comparison implementation.
- The no-aggregate-function case is supported: groups can be emitted with only GROUP BY columns.

## Test Signals

Tests cover normal stream aggregation with `COUNT` and `AVG`, nulls, arithmetic expressions, UTF-8 general collation, partial output before drain, empty intermediate batches, final drain output, and a query shape with GROUP BY columns but no aggregate functions. Shared paging tests compare stream aggregation with hash variants and verify partial output row counts under paging sizes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/stream_aggr_executor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/table_scan_executor.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/table_scan_executor.rs

## Purpose

`table_scan_executor.rs` implements `BatchTableScanExecutor`, the table row scan executor for TiKV coprocessor batch execution. It adapts the generic `ScanExecutor` to TiDB table row encodings, decodes row values into requested columns, fills primary key handle columns, supplies defaults for missing columns, and supports common handles plus special extra columns such as physical table id and commit timestamp.

## Important APIs, Types, and Functions

- `BatchTableScanExecutor<S, F>` wraps `ScanExecutor<S, TableScanExecutorImpl, F>` where `S: Storage` and `F: KvFormat`.
- `check_supported` delegates to `check_columns_info_supported`, currently validating primary-key handle eval types.
- `new` analyzes `ColumnInfo` descriptors, builds output schema via `field_type_from_column_info`, collects default values, maps column IDs to output indices, records handle indices, determines whether key-only scanning is sufficient, and configures `ScanExecutorOptions`.
- `TableScanExecutorImpl` stores `EvalContext`, schema, per-column defaults, `column_id_index`, `handle_indices`, `primary_column_ids`, and reusable `is_column_filled`.
- `process_v1` decodes old row format where value is datum-encoded column-id/value pairs.
- `process_v2` decodes row-v2 data through `RowSlice`, searching non-null and null column IDs and using `V1CompatibleEncoder` to write datum-compatible raw bytes.
- `build_column_vec` creates decoded integer columns for primary handles and special physical table/commit-ts columns, and raw columns for normal row data.
- `process_kv_pair` is the core row materializer for each scanned KV entry.

## Control Flow

At construction, non-PK requested columns are inserted into `column_id_index`, while PK-handle columns are recorded in `handle_indices`. `is_key_only` remains true only when all requested data can be derived from the key and no prefix common-handle/restored-data case requires the row value. `load_commit_ts` is enabled when `_tidb_commit_ts` is requested. `accept_point_range` is true only when there is no common handle.

For every batch, the generic scan wrapper calls `build_column_vec`, then calls `process_kv_pair` for each scanned KV. `process_kv_pair` first decodes value bytes if present. Row v2 and row v1 take separate decoding paths and push only requested columns, ignoring duplicate row-v1 column IDs after logging. Next, if integer PK handles are requested, it decodes the int handle from the key and pushes it to all handle output indices. If common-handle primary column IDs exist, it decodes each datum from the common handle and fills requested primary columns from key data. Otherwise it validates the record key.

After normal columns and handles, special extra columns are filled. `_tidb_rowid`-style physical table id is decoded from the key when requested. `_tidb_commit_ts` is pushed from the storage entry's commit timestamp; absence is an error if requested. Finally, every unfilled requested column gets its default value, NULL if nullable and no default exists, or an error if the column is NOT NULL and missing. Filled flags are reset for the next row.

## State and Persistence Behavior

The executor keeps no durable state. Per-instance persistent state consists of immutable schema/default/mapping metadata and a reusable `is_column_filled` vector. `EvalContext` accumulates warnings and is drained by the generic scan wrapper per result. Scan cursor progress, range awareness, storage statistics, and cacheability live in `ScanExecutor` and its `RangesScanner`.

## Dependencies and Integration Points

This file depends on `api_version::{ApiV1, KvFormat}`, TiDB row/table codecs, `kvproto::coprocessor::KeyRange`, `tidb_query_common::storage::Storage`, `smallvec` for handle indices, and `collections::HashMap`. It integrates with `util::scan_executor::ScanExecutor` for range scanning and `BatchExecutor` for batch pipeline semantics. It also integrates with storage commit timestamp loading and special TiDB column IDs from `tidb_query_datatype::codec::table`.

## Risks and Edge Cases

- Corrupted row data may partially fill columns before error. The generic scan executor truncates columns to equal length, but table decoding changes must preserve that contract.
- Missing NOT NULL data is treated as corruption and returns an error.
- Duplicate row-v1 column IDs are logged and ignored rather than aborting, which preserves availability but may hide upstream data issues.
- Common handle prefix columns can require restored data from row value rather than key-only scan; `is_key_only` calculation is sensitive to `primary_prefix_column_ids` and `need_restored_data`.
- Requesting `_tidb_commit_ts` requires storage to load commit timestamps; missing commit_ts is an error.
- Multiple PK handle columns or duplicate column IDs preserve only the last mapping in some cases as documented by comments.

## Test Signals

The tests are extensive. They cover point/range/mixed scans, varying column orders and PK positions, batch sizes, execution summary/scanned row stats, corrupted values, locked storage errors, multiple handle columns, common handles, prefix common-handle columns, restored data, and physical table id special columns. These tests validate drain behavior, partial rows on error, default value handling, raw versus decoded column representation, and schema/value alignment.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/table_scan_executor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/top_n_executor.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/top_n_executor.rs

## Purpose

`top_n_executor.rs` implements `BatchTopNExecutor`, a batch executor for ORDER BY ... LIMIT style top-N pushdown. It consumes its source to completion, evaluates order expressions, keeps only the best N rows in a heap, and emits sorted rows once the source is drained. It also has a paging shortcut where a TopN larger than the paging size is bypassed and source batches are returned directly.

## Important APIs, Types, and Functions

- `BatchTopNExecutor<Src>` implements `BatchExecutor` over any source executor.
- `check_supported` requires at least one order-by expression and validates each RPN expression tree.
- `new` converts protobuf order expressions into `RpnExpression`s and records return field types and descending flags.
- `handle_next_batch` pulls source batches at `BATCH_MAX_SIZE`, propagates warnings, processes rows into the heap, and returns heap output only when the source drains.
- `process_batch_input` records approximate comparison work metrics, decodes order-expression columns, pins source batch data in an `Arc<HeapItemSourceData>`, evaluates order expressions into `eval_columns_buffer_unsafe`, creates `HeapItemUnsafe` rows, and inserts them into `TopNHeap`.
- `next_batch` handles `n == 0`, paging bypass, error-to-empty-result behavior, remain-with-empty-output behavior, and final drain output.

## Control Flow

Construction stores the source, order expressions, order field types, order direction flags, evaluation context, heap, and reusable unsafe evaluation buffer. On each `next_batch`, `n == 0` immediately returns an empty drained result. If paging is configured and `n` exceeds paging size, the executor delegates directly to the source, effectively disabling TopN collection for that paging mode.

Otherwise, `handle_next_batch` reads the source using max batch size because TopN needs global ordering. For non-empty logical rows, `process_batch_input` ensures columns referenced by order expressions are decoded, evaluates order expressions, pins the full physical batch plus logical row mapping in an `Arc`, and adds each logical row to the heap. While the source remains, it returns empty remain results. On source drain, it calls `heap.take_all()` to materialize the retained rows in sorted order and returns a drained result.

Errors from the source or expression evaluation end the executor and produce empty columns with the error in `is_drained`, preserving warnings from the context.

## State and Persistence Behavior

State is in-memory. `TopNHeap` retains at most N `HeapItemUnsafe` records. Each heap item owns an `Arc` to the source batch data it references, so physical columns remain alive while any retained row points into them. `eval_columns_buffer_unsafe` accumulates evaluated order columns for processed batches and must outlive heap items; field order in the struct is deliberately arranged so heap drops before the data it points into. There is no durable persistence. After final output, the heap is drained.

## Dependencies and Integration Points

This executor integrates with `util::top_n_heap::{TopNHeap, HeapItemSourceData, HeapItemUnsafe}`, shared utility functions for decoding/evaluating RPN expressions, `tidb_query_expr`, `tidb_query_datatype` vector columns, `tidb_query_common::metrics::record_executor_work`, and `BatchExecutor` delegation for schema/intermediate results/stats/scanned ranges/cacheability.

## Risks and Edge Cases

- Unsafe pointers connect heap items to `order_is_desc`, order field types, and the evaluation buffer. The struct field order comments are part of the safety contract.
- TopN emits only after full drain unless paging bypass is active, so memory is bounded by N retained rows plus retained source batches for heap winners, but latency waits for the full source.
- When `n > paging_size`, the executor bypasses TopN and returns source order. That is an intentional paging behavior but surprising if callers expect global TopN in all modes.
- `eval_columns_buffer_unsafe` is not cleared after each batch because heap items may reference earlier evaluated columns. Long-running scans with many batches can retain expression result storage.
- Order comparison is non-stable for ties, matching test comments; callers must not require stable order among equal sort keys.
- Collation, unsigned integer ordering, null ordering, and expression errors depend on `ScalarValueRef::cmp_sort_key`.

## Test Signals

Tests cover `top 0`, empty logical batches, single and multi-column ordering, expression ordering, descending flags, null ordering, byte collations, unsigned integer ordering, paging bypass versus normal TopN, and propagation of extra common handle keys. The tests also confirm remain-empty outputs before source drain and final sorted outputs after drain.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/top_n_executor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/util/aggr_executor.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/util/aggr_executor.rs

## Purpose

`util/aggr_executor.rs` provides the shared aggregation executor framework used by simple, hash, and stream aggregation implementations. It parses aggregate definitions, owns common aggregation entities, drives source consumption, coordinates paging/drain semantics, materializes aggregate results, and forwards batch executor plumbing.

## Important APIs, Types, and Functions

- `AggregationExecutorImpl<Src>` is the strategy trait implemented by concrete aggregation modes. It defines `prepare_entities`, `process_batch_input`, `groups_len`, `iterate_available_groups`, and `is_partial_results_ready`.
- `Entities<Src>` bundles shared mutable state: source executor, `EvalContext`, output schema, aggregate function objects, per-function result cardinalities, aggregate argument RPN expressions, and result eval types.
- `AggregationExecutor<Src, I>` owns an implementation, `Entities`, an ended flag, and optional paging row target.
- `AggregationExecutor::new` parses protobuf aggregate expressions through an `AggrDefinitionParser`, builds result schema and aggregate argument expressions, computes result eval types, creates `Entities`, and lets the implementation append group-by fields.
- `handle_next_batch` consumes source batches at `BATCH_MAX_SIZE`, propagates warnings, delegates input processing, applies paging drain rules, and decides whether partial results are available.
- `aggregate_partial_results` allocates result columns by aggregate output eval type, asks the implementation to iterate available groups, pushes aggregate state results, appends group-by columns, and verifies column lengths.

## Control Flow

`next_batch` ignores the caller's `scan_rows` and asks `handle_next_batch` for any available aggregate output. The source is always polled at max batch size because aggregation must process all relevant rows or all currently available partial groups. If the source returns an error, the executor stops and returns empty output with the error. If the source has rows, the concrete implementation updates its group/global states. Paging compares `groups_len` with `required_row`; when enough groups exist it changes the drain state to `PagingDrain`. For partial-capable implementations such as stream aggregation, `required_row` is adjusted to account for groups that can be returned before full source drain.

When results are available, `aggregate_partial_results` invokes the implementation's `iterate_available_groups`. The callback receives the aggregate states for one group at a time and calls `push_result` on each state, respecting multi-column aggregate outputs such as AVG's count/sum cardinality. The return columns are aggregate result columns followed by any group-by columns supplied by the implementation.

## State and Persistence Behavior

State is in-memory and generic over the source executor. `Entities.context` holds warnings and evaluation settings, including paging size. `required_row` persists paging progress across calls. Concrete implementations own aggregate states and group metadata. `is_ended` prevents calls after drain/error. There is no durable persistence.

## Dependencies and Integration Points

The module depends on `tidb_query_aggr` for aggregate function parsing/state, `tidb_query_expr::RpnExpression`, `tidb_query_datatype` vector/value types and eval context/config, `tipb::Expr`/`FieldType`, and the crate `BatchExecutor` interface. It is the integration layer used by slow hash, fast hash, stream, and likely simple aggregation executors. It forwards intermediate-result, execution stats, storage stats, scanned range, and cacheability calls to the source executor.

## Risks and Edge Cases

- The parser asserts each aggregate currently has exactly one argument expression; adding multi-argument aggregate functions would require changes.
- Errors from the source suppress aggregate output even if prior state exists.
- Paging behavior depends on concrete `groups_len` semantics. For stream aggregation, `groups_len` includes the partial trailing group, so wrapper logic adjusts `required_row`.
- `all_result_column_types` uses `EvalType::try_from(...).unwrap()` because aggregate parsers are expected to produce supported types; parser bugs can panic.
- `scan_rows` passed to aggregation `next_batch` is intentionally ignored, which can surprise consumers expecting strict row budgeting.

## Test Signals

The test module defines unreachable aggregate machinery, reusable mock sources, and `test_agg_paging`. Paging tests compare fast hash, slow hash, and stream aggregation behavior with paging sizes 2, 5, and 7, validating call counts, drain states, and output row counts. The shared fixtures include nulls, empty logical batches, multiple physical rows, and multi-batch sources.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/util/aggr_executor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/util/hash_aggr_helper.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/util/hash_aggr_helper.rs

## Purpose

`util/hash_aggr_helper.rs` contains a shared helper for hash aggregation implementations. It updates aggregate function states when each logical input row may belong to a different group and the caller has already computed the state offset for every row.

## Important APIs, Types, and Functions

- `HashAggregationHelper` is a zero-sized namespace struct.
- `update_each_row_states_by_offset` accepts shared aggregation `Entities`, mutable input columns, logical rows, a flat slice of aggregate states, and `states_offset_each_logical_row`.
- It evaluates each aggregate argument expression once per aggregate function, then dispatches updates through `tidb_query_aggr::update!` for scalar and vector expression results.

## Control Flow

The helper loops over aggregate functions by index. For each function, it evaluates the corresponding aggregate argument RPN expression against the source schema, input physical columns, logical rows, and logical row count. If the expression result is scalar, the same scalar value is applied to every row's target state offset. If the result is vector, it zips each row's state offset with the expression result's logical row mapping and updates the state with the row-specific value. The `idx` is added to each row's group state offset to select the aggregate function state within that group.

## State and Persistence Behavior

The helper owns no persistent state. It mutates the caller-provided aggregate states and evaluation context. Any warnings or evaluation side effects accumulate in `entities.context`. Input columns may be used by expression evaluation and remain owned by the caller.

## Dependencies and Integration Points

This helper depends on `tidb_query_aggr::{AggrFunctionState, update}`, `RpnStackNode`, vector/scalar datatypes, and `Entities` from `aggr_executor`. It is used by hash aggregation executors after they map logical rows to group-state offsets.

## Risks and Edge Cases

- The `states_offset_each_logical_row` slice must align exactly with `input_logical_rows`; otherwise updates target wrong groups or panic on out-of-bounds state access.
- The flat state layout must be group-major with each group's aggregate states in aggregate definition order.
- Expression evaluation is repeated per aggregate function; shared common subexpressions are not cached here.
- Scalar aggregate arguments update every row with the same value, which is correct for constants but relies on expression evaluation's scalar/vector distinction.

## Test Signals

This file has no direct tests. It is exercised through slow and fast hash aggregation integration tests and shared aggregation paging tests, which validate grouped state updates for constants, vector expressions, nulls, and multi-batch input.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/util/hash_aggr_helper.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/util/mock_executor.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/util/mock_executor.rs

## Purpose

`util/mock_executor.rs` provides test-only mock implementations of batch executors, storage, and region storage accessors. It supplies deterministic fixture batches for executor unit tests and lightweight storage/accessor behavior for code paths that require storage abstractions.

## Important APIs, Types, and Functions

- `MockExecutor` implements `BatchExecutor` over a fixed iterator of `BatchExecuteResult`s, optional child executor, optional intermediate schema/results, optional scanned range, and pending scanned-row accounting.
- `MockExecutor::new`, `new_with_child`, `set_next_intermediate_results`, and `set_extra_common_handle_keys` build and mutate test fixtures.
- `MockScanExecutor` is a simple one-column integer batch source honoring `scan_rows`.
- `MockStorage` implements the `Storage` trait but leaves scan/get methods unimplemented; it primarily carries region/range data.
- `MockAccessorExpect` stores expected region lookup and local storage calls for expectation mode.
- `MockRegionStorageAccessor` supports expectation mode and data-driven mode for `RegionStorageAccessor`.

## Control Flow

`MockExecutor::next_batch` delegates to a child if present; otherwise it pops the next fixture result and increments `pending_scanned_rows` by the logical row count. Stats collection pushes pending scanned rows into `ExecuteStats.scanned_rows_per_range` and resets the counter, then delegates to any child. Intermediate schema and intermediate result consumption check local configuration first and then child configuration.

`MockScanExecutor::next_batch` emits up to `scan_rows` integer rows from its `rows` vector, building logical rows from `0..real_scan_rows` and returning drain when the position reaches the end.

`MockRegionStorageAccessor` in expectation mode consumes one preloaded expectation per method call and asserts keys or success flags. Data mode scans sorted regions to return `Found` or `NotFound` with the next region start. Local region storage returns a `MockStorage` containing the selected region and requested key ranges.

## State and Persistence Behavior

All state is process-local test state. `MockExecutor` consumes result iterators and tracks pending scanned rows until stats collection. `MockScanExecutor` advances `pos`. Expectation mode stores mutable expectations behind `Arc<Mutex<MockAccessorExpect>>`, allowing cloned accessors to share expectations. No durable persistence exists.

## Dependencies and Integration Points

The file depends on `BatchExecutor`, `BatchExecuteResult`, `ExecuteStats`, storage traits from `tidb_query_common`, `kvproto` region/range protobuf types, `EvalWarnings`, `LazyBatchColumnVec`, and TiKV region key checks. It is used by aggregation, TopN, and other executor tests to avoid real storage.

## Risks and Edge Cases

- `MockExecutor::next_batch` unwraps the next result; tests must provide enough fixture batches.
- `take_scanned_range` unwraps unless delegated to a child; callers must set `scanned_range`.
- `MockStorage` methods are unimplemented and will panic if used for real scanning.
- Expectation mode panics on missing, extra, or mismatched expectations; this is useful in tests but not a tolerant fake.
- `MockScanExecutor` calculates `real_scan_rows` as `min(scan_rows, self.rows.len())`, not remaining rows, but the loop also checks `self.pos`, so it may allocate more capacity than needed but still emits correctly.

## Test Signals

The file itself is test infrastructure and has no local test module. It is heavily exercised by executor tests in aggregation, stream aggregation, TopN, table scan-adjacent scenarios, and likely region-range tests elsewhere. The pending scanned row behavior was added to support tests that verify `max_keys_read`/execution stats semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/util/mock_executor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/util/mod.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/util/mod.rs

## Purpose

`util/mod.rs` declares shared executor utility modules and provides two common expression/column helpers used by aggregation and TopN executors.

## Important APIs, Types, and Functions

- Module exports: `aggr_executor`, `hash_aggr_helper`, test-only `mock_executor`, `scan_executor`, and `top_n_heap`.
- `ensure_columns_decoded` iterates over RPN expressions and asks each expression to decode any source columns it needs in the input `LazyBatchColumnVec`.
- `eval_exprs_decoded_no_lifetime` evaluates already-decoded expressions and appends `RpnStackNode` results into a caller-provided output vector after erasing lifetimes.

## Control Flow

Callers first use `ensure_columns_decoded` with an evaluation context, expression list, schema, mutable physical columns, and logical rows. Then, when they need to retain evaluated expression nodes in executor-owned buffers, they call the unsafe `eval_exprs_decoded_no_lifetime`. That function defines a local `erase_lifetime` helper, casts expression/schema/columns/logical-row references to a wider lifetime, evaluates each expression with `eval_decoded`, and pushes the result into the output vector.

## State and Persistence Behavior

The module has no own state. It mutates input columns by decoding lazy raw data and mutates the output vector by appending expression results. The lifetime-erased outputs are only valid as long as the referenced expressions, schemas, physical columns, and logical row slices stay alive according to the caller's safety contract.

## Dependencies and Integration Points

The helpers depend on `tidb_query_common::Result`, `LazyBatchColumnVec`, `EvalContext`, `tidb_query_expr::{RpnExpression, RpnStackNode}`, and `tipb::FieldType`. They are used by slow hash aggregation, stream aggregation, TopN, and likely other executor implementations needing batched expression evaluation.

## Risks and Edge Cases

- `eval_exprs_decoded_no_lifetime` is unsafe because it erases lifetimes. Callers must clear outputs before referenced batch data expires or pin referenced data for as long as outputs are used.
- `ensure_columns_decoded` may decode the same source column more than once across expressions unless lower layers deduplicate.
- The output vector is append-only; callers must account for existing offsets, as TopN does with `eval_offset`.

## Test Signals

There are no direct tests. The helpers are indirectly exercised by aggregation and TopN tests that evaluate group-by, aggregate, and order-by expressions over decoded columns.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/util/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/util/scan_executor.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/util/scan_executor.rs

## Purpose

`util/scan_executor.rs` implements the generic scanning wrapper shared by table and index scan executors. It owns range scanning, batching, drain/error semantics, scanned work metrics, execution stats forwarding, storage stats forwarding, and small schema utilities.

## Important APIs, Types, and Functions

- `ScanExecutorImpl` is the strategy trait for scan-specific row materialization. Implementors provide schema, mutable eval context, column vector construction, and `process_kv_pair`.
- `ScanExecutor<S, I, F>` wraps a `RangesScanner<S, F>`, a concrete scan implementation, an executor name, and an ended flag.
- `ScanExecutorOptions` carries storage, key ranges, direction, key-only mode, point range acceptance, range-awareness, and commit timestamp loading.
- `ScanExecutor::new` validates table ranges, reverses range order for backward scans, converts protobuf ranges to storage `Range`s, and constructs `RangesScanner`.
- `fill_column_vec` pulls up to `scan_rows` KV entries, calls `process_kv_pair`, records scanned KV byte work, and normalizes columns on materialization errors.
- `field_type_from_column_info` converts `ColumnInfo` into `FieldType`.
- `check_columns_info_supported` validates primary-key handle types.

## Control Flow

`next_batch` asserts the executor has not ended and `scan_rows > 0`, asks the implementation for an empty column vector, and calls `fill_column_vec`. `fill_column_vec` loops until it has attempted `scan_rows` entries or the scanner drains. It calls `scanner.next_opt(i == scan_rows - 1)`, accumulates key/value byte sizes, and sends each KV entry to the concrete implementation. Storage errors return immediately after recording any work already done. Materialization errors truncate columns into equal length before returning the error. Drain returns `Ok(true)`, and a full batch returns `Ok(false)`.

Back in `next_batch`, columns are asserted equal length, logical rows are `0..rows_len`, and `is_drained` is translated to `Drain`, `Remain`, or error. Errors and full drain set `is_ended`; remain does not. Warnings are taken from the implementation context.

Stats methods collect scanned rows per range, peek scanned row sums, collect storage stats, return scanned ranges, and report cacheability through `RangesScanner`.

## State and Persistence Behavior

Scan progress is held in `RangesScanner`; `is_ended` is only an assertion/safety guard. The scan implementation owns its decoding context and reusable buffers. Scanned work metrics are emitted per batch through `record_executor_work`. There is no durable persistence.

## Dependencies and Integration Points

The module depends on API-version `KvFormat`, `RangesScanner`, `Storage`, protobuf `KeyRange`, `IntervalRange`, `Range`, `EvalContext`, `LazyBatchColumnVec`, `ColumnInfo`, `FieldType`, and `TimeStamp`. It is integrated by table scan and index scan implementations via `ScanExecutorImpl`.

## Risks and Edge Cases

- A TODO notes that if an error occurs after successfully retrieving rows, downstream operators such as TopN/Limit may consume only part of the rows and might need to ignore the error; current behavior returns rows plus error in `is_drained`.
- Concrete `process_kv_pair` implementations may partially fill columns before error. The wrapper truncates to equal length but cannot restore semantic row data.
- Backward scans reverse range order and configure backward in-range scanning; range conversion correctness is essential.
- Work metrics use key+value bytes and saturating addition.
- `intermediate_schema` always errors because scan executors have no child intermediate schema until root.

## Test Signals

Direct tests are in concrete scan modules such as table scan. Table scan tests exercise generic scan batching, drain states, corrupted row truncation, locked storage errors, scanned-row execution summaries, and storage range behavior through this wrapper.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/util/scan_executor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/util/top_n_heap.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/util/top_n_heap.rs

## Purpose

`util/top_n_heap.rs` implements the heap data structure used by TopN-like executors. It keeps the best N rows according to pre-evaluated order expressions and materializes retained rows back into a `LazyBatchColumnVec`.

## Important APIs, Types, and Functions

- `TopNHeap` stores `n` and a `BinaryHeap<HeapItemUnsafe>`.
- `TopNHeap::new` caps initial heap capacity at `min(n, 1024)` to avoid large allocation spikes.
- `add_row` validates a row's comparability, pushes while under capacity, and otherwise replaces the current greatest row if the new row sorts smaller.
- `take_all_append_to` drains the heap, obtains sorted items with `into_sorted_vec`, creates/appends result columns, preserves extra common handle keys, and copies raw or decoded values from source rows.
- `take_all` materializes into a new empty column vector.
- `HeapItemSourceData` pins a source batch's physical columns and logical rows.
- `HeapItemUnsafe` holds non-null pointers to order flags, order field types, and evaluation results, plus an `Arc` to source data and a logical row index.
- `HeapItemUnsafe::cmp_sort_key` compares order expression scalar refs by field type and desc flags.

## Control Flow

TopN executors create a `HeapItemUnsafe` for each logical row after order expressions have been evaluated into an executor-owned buffer. `add_row` maintains a max heap where the worst retained row is at the top. If the heap is not full, the row is pushed after self-comparison validates collator/order expression data. If full, the row is compared with the current greatest row and replaces it only when it should rank earlier.

On output, `take_all_append_to` drains the heap and iterates sorted items. It initializes result columns from the first source batch's column shape when needed, handles extra common handle keys, and then copies each retained row's values column by column. Raw columns push raw datum slices; decoded columns borrow typed values and clone owned values into destination vectors. Column lengths are asserted at the end.

## State and Persistence Behavior

State is in-memory and emptied by `take_all`/`take_all_append_to`. Heap items keep source batches alive through `Arc<HeapItemSourceData>`, while unsafe pointers assume the parent executor's order metadata and evaluation buffer remain alive and unmoved. No durable persistence exists.

## Dependencies and Integration Points

The module depends on `BinaryHeap`, `Arc`, `NonNull`, `LazyBatchColumnVec`, `LazyBatchColumn`, vector datatypes, `RpnStackNode`, `FieldType`, and TiKV logging. It is consumed by `BatchTopNExecutor` and any future TopN-like batch executor.

## Risks and Edge Cases

- `HeapItemUnsafe::Ord` unwraps comparison results and can panic if data was not validated. `add_row` self-compares before insertion to reduce this risk.
- Unsafe non-null pointers rely on parent executor field lifetimes and drop order.
- `take_all_append_to` has a TODO for schema equality; it currently asserts only column count.
- Missing extra common handle keys log an error and push an empty key, which avoids panic but may degrade correctness for consumers needing handle keys.
- Cloning decoded values is marked as potentially unnecessary and may be a performance cost.
- `add_row` assumes `self.heap.peek_mut().unwrap()` when full; if `n == 0`, callers should avoid adding rows. `BatchTopNExecutor` handles `n == 0` before processing.

## Test Signals

There are no direct tests in this file. It is exercised by `top_n_executor.rs` tests that validate ordering, nulls, collations, unsigned integer comparison, extra common handle key propagation, and heap output materialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/util/top_n_heap.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/Cargo.toml -->
# sources/storage-engines/tikv/components/tidb_query_expr/Cargo.toml

## Purpose

This manifest defines the `tidb_query_expr` crate, which provides vectorized expression evaluation for TiDB pushed-down executors in TiKV. The crate is private to the workspace (`publish = false`), uses Rust 2021, and is licensed Apache-2.0.

## Important APIs, Types, and Functions

As a `Cargo.toml`, this file does not define Rust APIs directly. Its important contract is dependency and crate metadata configuration:

- Package: `tidb_query_expr`, version `0.0.1`, description "Vector expressions of query engine to run TiDB pushed down executors".
- Workspace dependencies include `codec`, `crypto`, `file_system`, `log_wrappers`, `openssl`, `tidb_query_codegen`, `tidb_query_common`, `tidb_query_datatype`, `tikv_util`, `time`, `tipb`, `chrono`, and test-only `panic_hook`/`profiler`.
- External dependencies include serialization/parsing/utility crates such as `base64`, `bstr`, `byteorder`, `chrono-tz`, `flate2` pinned to `=1.0.11` with zlib, `hex`, `match-template`, `memchr`, `num`, `num-traits`, `protobuf`, `rand`, `regex`, `serde`, `serde_json`, `static_assertions` with nightly feature, and `uuid`.

## Control Flow

There is no runtime control flow. Cargo uses this manifest to resolve dependencies, compile the expression crate, and compile dev-only test support. Feature flow is limited to dependency feature selection such as `flate2` using zlib and `uuid` enabling `v1`, `v4`, and `std`.

## State and Persistence Behavior

The manifest has no runtime state. It affects build reproducibility and dependency graph state through exact or semver dependency constraints. The pinned `flate2 = "=1.0.11"` is a notable reproducibility constraint.

## Dependencies and Integration Points

`tidb_query_expr` is a core integration crate for executor files in this work item. Aggregation, TopN, and utility modules use `RpnExpression`, `RpnExpressionBuilder`, `RpnStackNode`, arithmetic/operator function metadata, and expression support checking from this crate. The manifest links expression evaluation to datatype codecs, common query errors/results, generated aggregate/function code, protobuf Tipb expressions, logging wrappers, crypto/file utilities, and serialization libraries.

## Risks and Edge Cases

- `static_assertions` enables a `nightly` feature, which may constrain toolchain compatibility.
- Exact `flate2` pinning may be intentional for compatibility but can delay security or bugfix updates.
- Broad dependencies such as `openssl`, `regex`, `serde_json`, and `uuid` increase build surface for a low-level expression crate.
- Workspace dependency versions are controlled outside this file, so compatibility must be reviewed with the workspace manifest.

## Test Signals

Dev dependencies `tipb_helper`, `panic_hook`, `profiler`, and duplicate `bstr`/`chrono` entries support unit tests and profiling in the expression crate. The executor tests in this work item indirectly validate `tidb_query_expr` behavior through RPN expression construction, support checking, decoded evaluation, scalar/vector outputs, collation-aware comparison, arithmetic, and null tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/Cargo.toml -->
