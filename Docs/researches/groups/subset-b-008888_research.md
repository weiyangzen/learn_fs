# subset-b-008888 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/index_scan_executor.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/index_scan_executor.rs

## Purpose
`index_scan_executor.rs` implements `BatchIndexScanExecutor`, the batch executor that scans TiDB index key/value records from a `Storage` implementation and exposes index columns, handles, partition ids, and physical table ids as `LazyBatchColumnVec` batches. It is a thin public wrapper around the generic `ScanExecutor<S, IndexScanExecutorImpl, F>` plus a large `IndexScanExecutorImpl` responsible for TiDB index-value format decoding.

The executor supports old and newer index encodings, unique and non-unique indexes, int handles and common handles, local and global indexes, V1/V2 partition-id placement, old collation data, restored-data formats from TiDB 4.0/5.0, and optional `extra_common_handle_keys` needed by higher-level common-handle paths.

## Important APIs, Types, and Functions
- `BatchIndexScanExecutor<S, F>(ScanExecutor<...>)`: public batch executor exported by the crate. It delegates all `BatchExecutor` methods to `ScanExecutor`.
- `BatchIndexScanExecutor::check_supported`: validates pushed-down `IndexScan` column metadata through `check_columns_info_supported`.
- `BatchIndexScanExecutor::new`: derives schema and handle/partition layout from `ColumnInfo`, creates `IndexScanExecutorImpl`, and wires it into `ScanExecutor::new` with `ExecutorName::batch_index_scan`.
- `DecodeHandleStrategy`: selects `NoDecode`, `DecodeIntHandle`, or `DecodeCommonHandle`.
- `IndexScanExecutorImpl`: stores `EvalContext`, output schema, index-column ids, common-handle column ids, partition/physical-table-id column counts, cached `index_version`, and the `fill_extra_common_handle_key` flag.
- `ScanExecutorImpl` implementation: supplies `schema`, `mut_context`, `build_column_vec`, and `process_kv_pair`.
- Decoding helpers: `decode_int_handle_from_value`, `decode_int_handle_from_key`, `decode_int_handle_and_partition_from_key`, `extract_columns_from_row_format`, `extract_columns_from_datum_format`, `restore_original_data`, `get_index_version`, `process_old_collation_kv`, `process_kv_general`, `build_operations`, `decode_index_columns`, `decode_handle_columns`, `process_physical_table_id_column`, `decode_pid_columns`, `split_common_handle`, `split_partition_id`, and `split_restore_data`.
- Operation enums `DecodeHandleOp`, `RestoreData`, and `DecodePartitionIdOp` decouple byte-format parsing from column writes.

## Control Flow
Construction first inspects the tail of `columns_info`. `EXTRA_PHYSICAL_TABLE_ID_COL_ID` must be last if present, `EXTRA_PARTITION_ID_COL_ID` must precede it, and an int handle column must precede those special columns. `primary_column_ids_len` determines whether common-handle decoding is needed. The constructor rejects the invalid case where both int and common handles are pushed down, computes normal index column ids and common-handle column ids, then creates a `ScanExecutor` configured with direction, ranges, point-range acceptance for unique probes, and scanned-range awareness.

At execution time, `ScanExecutor` calls `IndexScanExecutorImpl::build_column_vec` to allocate raw columns for index columns, decoded `Int` columns for int handles and special ids, and raw columns for common-handle components. `process_kv_pair` validates the index key, strips the table/index prefix to get `key_payload`, lazily detects the index encoding version from the first value, and routes to either `process_kv_general` for new/extensible encodings or `process_old_collation_kv` for short legacy values.

The legacy path decodes indexed columns from the key payload first. For int handles, it uses the value when the remaining key payload is empty, otherwise parses the handle from the key and may also extract a partition id prefix. For common handles, it decodes the remaining key payload into the common-handle columns and optionally records the raw common handle. Partition id and physical table id output columns are filled either from the parsed global-index partition id or by falling back to the table id encoded in the key prefix.

The general path first calls `build_operations`. That routine uses `tail_len`, `index_version`, common-handle flag segments, partition-id segments, and restore-data segments to produce high-level operations. It prefers partition id from value for backward compatibility, otherwise falls back to partition id from key for V2 global index values. Then `process_kv_general` writes the physical table id or partition id columns, decodes normal index columns, and decodes handle columns. For TiDB 4.0 restore data it decodes all index columns from row-format restore data. For TiDB 5.0 restore data it decodes sort-key datums first and then `restore_original_data` reconstructs original non-binary string values, including `_bin` padding restoration.

## State and Persistence Behavior
The executor is runtime-stateful but not persistently stateful. It owns an `EvalContext` that accumulates evaluation warnings/behavior during decoding. `index_version` is initialized to `-1` and cached after the first processed KV, so a single executor assumes a consistent value format across its scan. Output state is per batch in `LazyBatchColumnVec`; raw columns may be lazily decoded by parent executors. `extra_common_handle_keys` are appended per processed row when requested. Statistics, scanned ranges, storage stats, and cacheability are delegated to the inner `ScanExecutor`.

The source of persistent truth is the TiKV/TiDB encoded key/value bytes in storage. This file only interprets those bytes; it does not write storage data.

## Dependencies and Integration Points
- Integrates with `BatchExecutor` from `interface.rs` and with the generic scan machinery in `util::scan_executor`.
- Depends on `tidb_query_datatype` for datum encoding/decoding, row v2 decoding, table key helpers, collations, field type accessors, and lazy batch columns.
- Depends on `tidb_query_common::storage::Storage` and `kvproto::coprocessor::KeyRange` for scan input.
- Uses `api_version::KvFormat` and defaults the support-check type alias to `ApiV1`.
- Uses `tipb::{IndexScan, ColumnInfo, FieldType}` as the TiDB pushed-down plan contract.
- Exported from `lib.rs` as `BatchIndexScanExecutor`, so runner/planner code can instantiate it for pushed-down index scans.

## Risks and Edge Cases
- Column ordering is part of the wire contract. Normal index columns, common-handle columns, int handle, partition id, and physical table id must be ordered exactly as expected; wrong order can produce raw bytes that later fail schema decoding rather than failing construction.
- `index_version` is cached from the first KV. Mixed encodings in one scan would be risky because later rows reuse the initial version decision.
- `tail_len`, common-handle length, partition-id segment length, and remaining bytes are all corruption-sensitive. The code returns explicit errors for malformed tails, unexpected extra bytes, invalid handle flags, missing row-format columns, and mismatched common-handle mode.
- Global index support has compatibility complexity: V1 may carry partition id in both key and value, while V2 carries it only in the key. The implementation must return partition id for global physical-table-id columns instead of the index table id.
- Restore-data semantics depend on collation and column type. `_bin` string reconstruction combines key sort data with restored padding counts; non-binary collations use restored row data. Mistakes here produce semantically wrong string values while preserving sort order.
- `fill_extra_common_handle_key` is valid only when the decoded handle operation is `CommonHandle`; other operations are rejected.

## Test Signals
The in-file tests are extensive. `test_basic` covers normal and unique int-handle scans, reverse scans, prefix/point ranges, physical table id output, and wrong column order behavior. Common-handle tests cover unique and non-unique common handles, extra common handle keys, and global index partition id output. Collation tests cover char/varchar restoration for int handles and common handles across `_bin`, Unicode/general CI, and Latin1 binary cases. Global index tests cover V1/V2 partition-id placement, optional legacy partition columns, optional physical-table-id columns, malformed key handling, and the new-encoding V2 path through `process_kv_general`. `test_index_version` pins version detection.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/index_scan_executor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/interface.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/interface.rs

## Purpose
`interface.rs` defines the common batch-executor contract used by TiKV's pushed-down SQL executor pipeline. It describes how executors expose schemas, pull batches, propagate intermediate results, collect execution and storage statistics, return scanned ranges, and report whether their output can be cached. It also defines the batch result container and the drain-state enum used by all batch executors.

## Important APIs, Types, and Functions
- `BatchExecutor`: async pull-based executor trait. It is `Send`, has an associated `StorageStats`, and is the central interface implemented by scan, limit, selection, projection, aggregation, top-n, lookup, and wrapper executors.
- `BatchExecutor::schema`: returns output `FieldType` schema.
- `intermediate_schema` and `consume_and_fill_intermediate_results`: support executor families that produce/consume intermediate results, such as aggregation or multi-stage plans.
- `next_batch(scan_rows)`: async batch pull. It may return zero logical rows while still not drained.
- `collect_exec_stats`, `peek_scanned_rows_sum`, `collect_storage_stats`, `take_scanned_range`, and `can_be_cached`: stats/range/cache hooks that parents and runners call recursively.
- `collect_summary`: wraps an executor in `WithSummaryCollector<ExecSummaryCollectorEnabled, Self>` for per-executor execution summaries.
- `WithSummaryCollector<C, T>`: transparent executor wrapper that measures `next_batch` iteration time and row count, collects summary data, and delegates all other behavior to the inner executor.
- `BatchExecuteResult`: columnar batch result with `physical_columns`, logical row offsets, warnings, and drain status.
- `BatchExecIsDrain`: `Remain`, `Drain`, and `PagingDrain`; `is_remain` and `stop` are convenience methods for loop control.
- Blanket `BatchExecutor for Box<T>`: lets dynamic executors be used through `Box<dyn BatchExecutor<...>>`.

## Control Flow
Executors are pulled by repeatedly calling `next_batch`. A returned `BatchExecuteResult` contains physical column storage plus a `logical_rows` vector that selects and orders valid row offsets. Parent executors must not infer completion from an empty logical batch; they must inspect `is_drained`. `Drain` means the executor is completely exhausted, `PagingDrain` means a paging request should stop and return a scanned range, and `Remain` means callers should continue.

Stats collection is out-of-band from batch data flow. `collect_exec_stats` and `collect_storage_stats` may be called multiple times and must drain accumulated metrics since the previous call. `WithSummaryCollector::next_batch` surrounds the inner call with `on_start_iterate`/`on_finish_iterate` and records logical row count. Its `collect_exec_stats` first collects summary data into `dest.summary_per_executor`, then asks the inner executor to collect its stats.

## State and Persistence Behavior
`BatchExecuteResult` owns each batch's data and warnings; it is `Send` but intentionally not `Sync`. `WithSummaryCollector` carries mutable summary state and an inner executor. The trait methods imply ephemeral execution state: stats and storage stats are accumulated in executor instances and reset on collection, scanned range is taken by value, and no persistence is performed here.

## Dependencies and Integration Points
- Uses `async_trait` because `BatchExecutor::next_batch` is async in a trait.
- Re-exports `ExecSummaryCollector` and `ExecuteStats` from `tidb_query_common`.
- Uses `LazyBatchColumnVec` and `EvalWarnings` from `tidb_query_datatype` for batch data and warnings.
- Uses `tipb::FieldType` as the schema representation shared with pushed-down TiDB plans.
- Used directly by `index_scan_executor.rs`, `limit_executor.rs`, and other executors exported by `lib.rs`.

## Risks and Edge Cases
- Callers must respect `logical_rows`; `physical_columns.rows_len()` can include filtered or unordered rows and is not the logical output cardinality.
- Empty batches with `Remain` are legal, so loops that stop on empty output can truncate results.
- `is_drained` is a `Result<BatchExecIsDrain>`. Error means retrieval failed and the executor should be considered drained, but the batch can still contain valid remaining data that should be processed.
- `PagingDrain` stops execution for the current request without meaning the entire underlying range is permanently exhausted.
- Implementors must recursively call stats collection on children; missed calls hide metrics.

## Test Signals
This file has no local test module, but its behavior is exercised indirectly by executor tests. `limit_executor.rs` tests empty-remain batches, errors before/at limits, drain propagation, and `BatchExecIsDrain::stop`. `index_scan_executor.rs` verifies scan executor integration with `BatchExecuteResult` layout and logical/physical columns. Test-only fields and helpers on `WithSummaryCollector` and `BatchLimitExecutor` show that wrapper identity and execution-path selection are expected to be observable in tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/interface.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/lib.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/lib.rs

## Purpose
`lib.rs` is the crate root for TiKV's `tidb_query_executors` component. It configures nightly Rust features/macros, declares executor modules, exposes common test-only query expression/aggregration imports, and re-exports the public batch executor types used by runner/planner code.

## Important APIs, Types, and Functions
- Crate-level feature gates: `proc_macro_hygiene`, `specialization`, and `stmt_expr_attributes`, with `incomplete_features` allowed.
- Macro imports: `tikv_util` macros `box_try` and `warn`, and `tidb_query_common` macro `other_err`.
- Public modules: `interface` and `runner`.
- Private executor/util modules: fast/slow hash aggregation, simple/stream aggregation, index lookup, index scan, limit, partition top-n, projection, selection, table scan, top-n, and `util`.
- Public re-exports: `BatchFastHashAggregationExecutor`, `BatchIndexLookUpExecutor`, `BatchIndexScanExecutor`, `BatchLimitExecutor`, `BatchPartitionTopNExecutor`, `BatchProjectionExecutor`, `BatchSelectionExecutor`, `BatchSimpleAggregationExecutor`, `BatchSlowHashAggregationExecutor`, `BatchStreamAggregationExecutor`, `BatchTableScanExecutor`, and `BatchTopNExecutor`.

## Control Flow
There is no runtime control flow in this file. Its main job is compile-time crate assembly. Rust module declarations bring implementation files into the crate, and the final `pub use self::{...}` block defines the crate's external executor surface. Code outside the crate imports executor types from this root rather than from private module paths.

## State and Persistence Behavior
This file maintains no runtime state and performs no persistence. Its state effect is namespace-level: it determines which modules are compiled and which executor types are exported.

## Dependencies and Integration Points
- Integrates with the broader TiKV query stack by exporting executor types that implement the `BatchExecutor` trait from `interface.rs`.
- Test-only re-exports from `tidb_query_aggr` and `tidb_query_expr` simplify in-crate tests for executor expression/aggregation behavior.
- `runner` is public and likely coordinates construction/execution of the exported executors for coprocessor requests.

## Risks and Edge Cases
- Public API changes here have broad impact because downstream code imports executor types through crate-root re-exports.
- Feature gates tie the crate to nightly-only behavior. Removing or changing them may affect macro expansion, specialization, or statement expression attributes used elsewhere in the crate.
- Private module visibility means new executors must be both declared and explicitly re-exported if they are intended for external use.
- Test-only re-exports are gated by `#[cfg(test)]`; non-test code cannot depend on those symbols through this crate root.

## Test Signals
`lib.rs` contains no tests. Its validation is primarily compile-level: all declared modules must compile, exported executor names must resolve, and crate tests that import test-only expression/aggr helpers through the root must build.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/limit_executor.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/limit_executor.rs

## Purpose
`limit_executor.rs` implements `BatchLimitExecutor`, a parent executor that wraps another `BatchExecutor` and truncates the number of logical rows returned. It supports ordinary SQL `LIMIT` behavior and a rank-limit mode that returns all rows tied with the Nth row according to one or more truncate-key expressions. The rank-limit mode is used for top-N/rank-style semantics where peers with equal ordering keys must not be split.

## Important APIs, Types, and Functions
- `BatchLimitExecutor<Src>`: generic wrapper over a source executor. It stores the child, remaining row budget, whether the child is a scan executor, evaluation context, truncate-key expressions, truncate-key field types, previous/current key buffers, and debug-only execution flags.
- `new(src, limit, is_src_scan_executor)`: constructs a normal limit with no truncate-key expressions and default eval config.
- `new_rank_limit` and `new_rank_limit_impl`: construct rank-limit mode from TiDB `Expr` definitions or already-built `RpnExpression`s.
- `new_rank_limit_for_test` and `into_child`: test helpers.
- `record_truncate_key_values`: decodes/evaluates truncate-key expressions for a selected logical row and records owned previous key values.
- `cmp_row_truncate_key_with_prev`: compares current evaluated truncate keys against the previous boundary key using field-type sort semantics.
- `find_different_truncate_key_row`: evaluates truncate keys for a whole batch and binary-searches the first row whose keys differ from the recorded boundary.
- `BatchExecutor` implementation: delegates schema/intermediate/stats/storage/range/cache methods and implements the limiting logic in `next_batch`.

## Control Flow
For normal limit mode, `next_batch` optionally reduces `scan_rows` to `min(scan_rows, remaining_rows)` when the child is a scan executor. It then pulls one child batch, records a batch-limit work metric using child logical row count, subtracts returned rows from `remaining_rows`, truncates `logical_rows` when the row budget is reached, marks the result as `Drain`, and returns the batch without changing physical columns.

Rank-limit mode starts similarly but has additional peer-group handling. If the configured limit is zero and no boundary key has been recorded, it returns an empty drained result immediately. If `real_scan_rows` becomes zero, it uses `runner::BATCH_MAX_SIZE` so it can still fetch rows to determine peer groups. After pulling a child batch, it records work metrics and exits early for empty batches. If the whole batch fits in the remaining budget, it emits it and, when the budget reaches zero, records truncate keys from the last emitted row. If the batch exceeds the remaining budget, it records the Nth row's truncate keys if needed, evaluates truncate keys for the batch, binary-searches for the first row with a different key, emits rows through that peer group, sets remaining rows to zero, and marks drain when output is shorter than the child batch.

The executor never compacts physical columns. It only truncates `logical_rows`, preserving physical storage and extra common handle keys from the source. Errors from decode/evaluation are returned in `is_drained: Err(err)` with the current physical/logical data attached.

## State and Persistence Behavior
`remaining_rows` is the central mutable state and persists across `next_batch` calls. In rank-limit mode, `prev_truncate_keys` stores owned scalar values for the boundary row after the nominal limit is reached; subsequent batches compare against that boundary to include all tied peers. `current_truncate_keys_unsafe` is a reusable expression-result buffer whose contents are only valid for the current batch despite its `'static` type parameter; the code confines its use to the active batch. `EvalContext` stores evaluation behavior and warnings. There is no durable persistence.

## Dependencies and Integration Points
- Implements the `BatchExecutor` trait from `interface.rs` and delegates most behavior to the source executor.
- Uses `LazyBatchColumnVec`, `ScalarValue`, `ScalarValueRef`, and `EvalWarnings` from `tidb_query_datatype`.
- Uses `tidb_query_expr::{RpnExpression, RpnExpressionBuilder, RpnStackNode}` for rank-limit truncate-key evaluation.
- Uses utility functions `ensure_columns_decoded` and `eval_exprs_decoded_no_lifetime` to decode/evaluate child columns.
- Uses `tipb::Expr` and `FieldType` as pushed-down expression/schema inputs.
- Records executor work metrics under `ExecutorName::batch_limit`.
- Refers to `crate::runner::BATCH_MAX_SIZE` when rank-limit needs to fetch after the ordinary scan row count reaches zero.

## Risks and Edge Cases
- Rank-limit correctness relies on input rows being sorted by truncate keys. The binary search assumes equal-to-boundary rows form a prefix of the remaining batch.
- The unsafe expression-result buffer is lifetime-sensitive. It is safe only because values are consumed within the same batch and owned copies are stored in `prev_truncate_keys`.
- Normal limit mode marks the result drained once it has emitted the limit, even if the child batch carried an error. Existing tests indicate the limit boundary suppresses a later child error in that batch.
- Empty batches with `Remain` must pass through so callers can continue pulling.
- `is_src_scan_executor` changes scan volume by reducing requested rows. Incorrectly setting it can affect how much work the child scan performs and how scanned ranges/paging behave.
- Physical columns are not truncated, so downstream consumers must use `logical_rows` and must preserve associated extra common handle key semantics.
- Rank-limit with `limit == 0` returns immediately only before any boundary key is recorded; after a boundary is known, it still needs to consume peer rows until keys differ.

## Test Signals
The test module covers normal limit zero, child errors before the limit, child drain before the limit, errors at the limit boundary, drain after the limit across empty batches, scan-source row-count reduction, and preservation of `extra_common_handle_keys`. Rank-limit tests cover zero limit, one-batch peer inclusion for several limits, full-batch decode when the same batch is reused for comparison, multi-batch peer groups crossing batch boundaries, and case-insensitive collation comparison. Debug-only flags verify whether normal or rank-limit paths executed.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/limit_executor.rs -->
