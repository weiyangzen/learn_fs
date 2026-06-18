# Research: subset-b-008889

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/partition_top_n_executor.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/partition_top_n_executor.rs

## Purpose

`partition_top_n_executor.rs` implements `BatchPartitionTopNExecutor`, a vectorized TiKV coprocessor executor for `TOP N ... PARTITION BY ...` and for partitioned `LIMIT` without order keys. It sits between a child `BatchExecutor` and the runner, keeps a bounded `TopNHeap` per currently observed partition, and emits rows when a partition boundary is seen or the child drains. The code assumes input is sorted by the partition expressions for early per-partition flushing; if input is not ordered, the executor remains safe for the two-stage TopN plan but treats non-contiguous equal keys as separate local partitions.

## Important APIs, Types, and Functions

- `BatchPartitionTopNExecutor<Src>` stores the child executor, evaluation context, partition/order RPN expressions, return field types, ordering flags, heap state, and the last partition key.
- `new(config, src, partition_exprs_def, order_exprs_def, order_is_desc, n)` builds RPN expressions with `RpnExpressionBuilder::build_from_expr_tree`, derives expression return field types from the child schema, creates the heap, and initializes evaluation context and partition comparison metadata.
- `new_for_test` and `new_for_test_with_config` mirror construction for test-built RPN expressions and support explicit paging configuration.
- `check_partition_equal_or_update(current)` compares the incoming partition key with `last_partition_key` using `HeapItemUnsafe` comparison logic. On inequality it stores the new key and returns false.
- `handle_next_batch()` reads one child batch, decodes columns required by order and partition expressions, evaluates expressions with `eval_exprs_decoded_no_lifetime`, wraps source batch data in `Arc<HeapItemSourceData>`, pushes order rows into `TopNHeap`, and flushes heap contents on partition changes or final drain.
- `next_batch(scan_rows)` implements the `BatchExecutor` contract. It short-circuits `n == 0`, optionally bypasses the optimization when `2 * n > paging_size`, converts flushed columns into logical rows `0..rows_len`, and returns evaluation warnings or errors.
- The `BatchExecutor` delegation methods forward schema, intermediate output, stats, storage stats, scanned range, and cacheability to the child.

The executor uses `HeapItemUnsafe` and `TopNHeap` from `crate::util::top_n_heap`. `HeapItemUnsafe` stores non-owning pointers to expression evaluation buffers, field type arrays, order flags, and source batch data. The executor marks itself `Send` with an explicit unsafe impl because these pointers remain internal and are not intentionally shared across threads.

## Control Flow

Construction is descriptor driven: the DAG runner extracts `partition_by` and `order_by` expressions from `Limit` or `TopN` descriptors and calls `BatchPartitionTopNExecutor::new`. During each `next_batch` call, the executor fetches up to `BATCH_MAX_SIZE` rows from its child, installs the child warnings into its `EvalContext`, and reads the child drain status. Empty child logical rows are skipped except that a final drain still flushes pending heap contents.

For non-empty batches, the executor first ensures all order and partition referenced columns are decoded. It pins the batch data in an `Arc`, evaluates order expressions into `eval_columns_buffer_unsafe`, records the offset, then evaluates partition expressions into the same buffer and records a second offset. For every logical row, it creates a partition-key `HeapItemUnsafe`; if it differs from `last_partition_key`, all rows currently retained in the heap are appended to the output columns and the heap is reset to capacity `n`. It then creates an order-key `HeapItemUnsafe` for the same row and inserts it into the heap. If the child reports a stop drain, the remaining heap rows are appended as the final partition.

The output `LazyBatchColumnVec` built by `TopNHeap::take_all_append_to` is already materialized as result columns, so `next_batch` resets output logical rows to a dense range. Errors from expression evaluation or heap comparison are returned through `BatchExecuteResult.is_drained = Err(...)` with warnings taken from the context and no data.

## State and Persistence Behavior

All state is volatile and per executor instance. Persistent state is not written. Important mutable state includes:

- `heap`: retained best rows for the current partition only.
- `last_partition_key`: current partition identity, represented as a reusable heap item.
- `eval_columns_buffer_unsafe`: an append-only buffer of expression results referenced by unsafe heap items. Its lifetime is tied to the executor and source batch `Arc`s.
- `context.warnings`: accumulated expression warnings; consumed with `take_warnings` after each public batch.

The executor relies on child executors for scanned range and storage statistics. It does not maintain its own range cursor. The paging guard is notable state behavior: when `paging_size` exists and `n * 2 > paging_size`, the executor bypasses local partition TopN and simply returns child batches. This avoids worst-case output growth above a page target but means the optimization can be disabled by request configuration.

## Dependencies and Integration Points

This file integrates with:

- `crate::interface::{BatchExecutor, BatchExecuteResult, BatchExecIsDrain, ExecuteStats}` for the vectorized executor contract.
- `tidb_query_expr::{RpnExpression, RpnExpressionBuilder, RpnStackNode}` for descriptor parsing and vector expression evaluation.
- `tidb_query_datatype::codec::batch::LazyBatchColumnVec` and `data_type::BATCH_MAX_SIZE` for columnar batch data.
- `crate::util::{ensure_columns_decoded, eval_exprs_decoded_no_lifetime, top_n_heap::*}` for decoded expression input and heap ordering.
- `runner.rs`, where partitioned `Limit` and partitioned `TopN` descriptors are mapped to this executor.

The executor preserves the child schema because partition TopN filters/reorders rows but does not add or remove result columns. Intermediate result APIs are delegated so it can be composed above index lookup or other executors that expose intermediate outputs.

## Risks and Edge Cases

- The unsafe pointer design is the primary risk. `eval_columns_buffer_unsafe` and `HeapItemUnsafe` must not be moved, cleared, or exposed in a way that invalidates internal pointers while heap items remain. The `Send` impl relies on this invariant.
- Partition correctness depends on input partition ordering for single-stage semantics. The file comment and test show unordered keys are treated as separate partitions; correctness is expected only after the plan's second-stage TopN.
- Memory can exceed the caller's requested page size in boundary cases. The code documents a worst case of `2*n - 1` output rows and uses a bypass guard when `2*n > paging_size`.
- `last_partition_key` compares via heap item equality with dummy `partition_is_desc` flags. This reuses sort-key comparison machinery and is marked for future refactoring.
- Expression errors clear the output for the batch and surface as executor drain errors. Partial rows before an error are not emitted.
- Empty order expression lists are supported and behave as first `n` rows per partition according to heap behavior; tests cover partitioned limit without order keys.

## Test Signals

The module has extensive unit tests using `MockExecutor`. Covered signals include `n == 0`, constant partitions, multiple and null partition keys, partition expressions, descending and ascending order, unordered partition keys, integrated byte and timestamp-like data, paging size interactions, no-partition behavior copied from TopN tests, unsigned integer ordering, collation-sensitive bytes ordering, and pass-through behavior when paging limits make local TopN unsafe. These tests also exercise empty child batches and multi-call draining behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/partition_top_n_executor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/projection_executor.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/projection_executor.rs

## Purpose

`projection_executor.rs` implements the vectorized batch projection executor. It evaluates TiDB RPN expressions over a child batch and returns a new column set matching the projection expression list. It also contains a fast path for projections that are only non-duplicate column references, avoiding expression evaluation and unnecessary column copying.

## Important APIs, Types, and Functions

- `BatchProjectionExecutor<Src>` stores `EvalContext`, child executor, output schema, RPN expressions, and fast-path metadata.
- `check_supported(descriptor: &Projection)` validates every expression tree with `RpnExpressionBuilder::check_expr_tree_supported`.
- `get_schema_from_exprs(child_schema, exprs)` derives the projected schema from each expression return field type.
- `new(config, src, exprs_def)` parses tipb `Expr` descriptors into RPN expressions, detects the no-duplicate column-reference-only fast path, and builds the output schema.
- `new_for_test` performs the same setup for prebuilt test expressions.
- `check_column_ref(...)` recognizes a single-node `RpnExpressionNode::ColumnRef` and rejects duplicate offsets by tracking a `HashSet<usize>`.
- `next_batch(scan_rows)` pulls one child batch and either swaps out referenced columns directly or evaluates every expression into new `LazyBatchColumn`s.
- Standard `BatchExecutor` methods expose the projected schema and delegate intermediate results, stats, range, storage stats, and cacheability to the child.

## Control Flow

On construction, the executor walks projection expressions in order. While every expression is a single unique column reference, it records column offsets and keeps `no_dup_column_ref_only = true`. Any constant, function call, multi-node expression, or duplicate column reference disables the optimization.

At runtime `next_batch` gets one child `BatchExecuteResult`. It destructures drain status, logical rows, and warnings, but keeps mutable access to physical columns. If the child produced no logical rows or already carries a drain error, the executor skips evaluation and returns empty projected columns while preserving drain/error state.

For the fast path, the executor moves selected physical columns out of the child vector with a push-placeholder plus `swap_remove` trick. This avoids shifting all columns after each selected offset. Logical rows remain the child's original logical row indexes, and `extra_common_handle_keys` are preserved as-is because the physical row layout still corresponds to the child columns.

For the general path, it evaluates each RPN expression over the child's physical columns and current logical rows. Scalar results are expanded into a vector column with `VectorValue::from_scalar(..., logical_len)`, while vector results are taken directly. On the first expression error, the executor combines the error into `is_drained`, clears logical rows, and stops evaluating later expressions. If all expressions succeed, it compacts `extra_common_handle_keys` to match logical row order, resets logical rows to `0..logical_len`, and returns only projected columns.

At the end, child warnings and projection evaluation warnings are merged, and a `LazyBatchColumnVec::with_columns_and_extra_common_handle_keys` is returned.

## State and Persistence Behavior

The executor has no durable persistence. Runtime state is limited to the expression evaluation context and immutable construction metadata. `EvalContext` accumulates warnings across expression evaluations and is merged into child warnings before returning. Child storage/range state remains owned by the child.

The most important state distinction is physical/logical row indexing. The fast path preserves child logical rows and extra common handles. The general path creates freshly materialized projected columns and therefore normalizes logical rows to dense indexes, remapping common handle keys through the old logical rows.

## Dependencies and Integration Points

This file integrates with:

- `crate::interface` for the `BatchExecutor` trait and `BatchExecuteResult`.
- `tidb_query_expr::{RpnExpression, RpnExpressionBuilder, RpnExpressionNode}` for projection expression support.
- `tidb_query_datatype::codec::batch::{LazyBatchColumn, LazyBatchColumnVec}` and `VectorValue` for materialized batch columns.
- `runner.rs`, which constructs this executor for `ExecType::TypeProjection` and uses its schema for output-offset validation and encoding decisions.
- Index lookup/common handle support through `LazyBatchColumnVec` extra common handle key plumbing.

## Risks and Edge Cases

- The fast path uses `swap_remove` by original offsets. It is safe because it only enables when references are unique, but offset order and mutation need care. Future changes to allow duplicates must not use this path without preserving column semantics.
- General expression evaluation resets logical rows to dense indexes. Any metadata keyed by old physical rows must be explicitly remapped, as done for extra common handle keys.
- On expression error, all rows in the batch are dropped, even rows whose earlier expression results were valid.
- Empty projection expression lists produce no columns; only when `exprs` is non-empty and evaluation succeeds are logical rows normalized in the general branch.
- Warning merging must include both child and projection warnings; callers rely on warning counts in `runner.rs`.

## Test Signals

Tests cover empty child batches without invoking expression functions, constant projection, full column projection, simple expression projection, expression errors, and extra common handle propagation in both the fast and general paths. The tests assert logical rows, column counts, decoded values, drain states, and common handle key ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/projection_executor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/runner.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/runner.rs

## Purpose

`runner.rs` is the batch coprocessor DAG runner. It validates supported tipb executor descriptors, builds a tree of vectorized `BatchExecutor`s from a `DagRequest`, drives that tree until drain, paging, streaming row limits, deadlines, or `max_keys_read` limits are reached, and encodes main and intermediate results into `SelectResponse` or `StreamResponse`.

## Important APIs, Types, and Functions

- `BATCH_INITIAL_SIZE`, exported `BATCH_MAX_SIZE`, and `BATCH_GROW_FACTOR` control adaptive batch size growth. Failpoints can override initial and growth factor values in tests.
- `IntermediateOutputChannel` records encode type, output offsets, and schema for intermediate outputs, primarily index lookup.
- `BatchExecutorsRunner<SS>` owns the root executor, request output offsets, eval config, execution stats, stream/paging/max-key controls, quota limiter, intermediate channel state, and reusable intermediate result buffers.
- `BatchExecutorsRunner<()>::check_supported(exec_descriptors)` validates each descriptor and rejects unsupported executor types such as joins, windows, sorts, exchanges, CTEs, and partition table scan.
- `is_arrow_encodable(schema_iter)` checks whether requested output field types support chunk encoding; unsupported fields force default row encoding.
- `is_executor_under_parent_tp(under_tp, executor, executor_index, left_executors)` walks explicit or natural parent links to detect whether an executor is under a parent type such as `TypeIndexLookUp`.
- `build_executors(...)` builds the executor chain/tree from tipb descriptors, storage, ranges, config, intermediate output descriptors, and optional region storage accessor.
- `from_request(...)` builds `EvalConfig`, injects paging and `max_keys_read`, builds executors, validates output offsets, chooses response encode types, and initializes runner state.
- `handle_request()` runs a non-streaming request and returns `(SelectResponse, Option<IntervalRange>)`.
- `handle_streaming_request()` returns one streaming `StreamResponse` chunk plus scanned range until the stream drains.
- `internal_handle_request(...)` performs one root `next_batch`, encodes main rows, merges warnings, and drains intermediate outputs.
- `consume_and_encode_intermediate_results(...)` pulls intermediate batches from executors and encodes them into their channel chunk vectors.
- `make_stream_response(...)` serializes a stream chunk, attaches scan stats and warnings, records iteration metrics, and clears execution stats for the next stream response.
- `encode_result_to_chunk(...)` serializes a `BatchExecuteResult` with default datum encoding for streaming/default mode or chunk encoding otherwise.
- `grow_batch_size(...)` doubles the batch size up to `BATCH_MAX_SIZE`.

## Executor Construction Flow

`build_executors` requires the first descriptor to be a table scan or index scan. It creates the bottom executor with scan summary collection and increments executor count metrics. For index scans under index lookup with common handles, it detects the parent relation so the scan can fill extra common handle keys.

The builder then walks the remaining descriptors using `parent_idx` to support a mostly linear chain plus index lookup's table-scan child. It wraps the current executor for selection, projection, simple aggregation, fast or slow hash aggregation, stream aggregation, limit, top n, partition top n, and index lookup. Limit descriptors with `partition_by` are treated as partition TopN without order keys. TopN descriptors with `partition_by` are routed to `BatchPartitionTopNExecutor`; otherwise to `BatchTopNExecutor`.

For `TypeIndexLookUp`, exactly one buffered child descriptor must exist and it must be `TypeTableScan`. The builder finds exactly one matching intermediate output channel, then calls `build_index_lookup_executor` with either `CommonHandle` or `IntHandle` depending on table scan primary column metadata. After each wrapper, unhandled children or invalid parent indexes cause immediate errors.

## Request Execution Flow

`from_request` consumes a `DagRequest` and prepares execution. It copies request execution-summary settings, creates `EvalConfig::from_request`, stores paging and `max_keys_read` in the config, and marks scans as range-aware when streaming, paging, or max-key stopping may require resume ranges. It validates main output offsets and chooses `EncodeType::TypeDefault` if any requested output field cannot be chunk-encoded. It repeats the same offset and encoding checks for intermediate channels using `out_most_executor.intermediate_schema(idx)`.

`handle_request` starts at `BATCH_INITIAL_SIZE` and loops. Each iteration:

1. Checks quota/cpu sampling around `internal_handle_request`.
2. Adds read bytes and applies quota limiter delay metrics.
3. Adds produced main/intermediate record counts.
4. When `max_keys_read` is enabled, peeks cumulative scanned rows via `out_most_executor.peek_scanned_rows_sum()` without draining stats.
5. Pushes non-empty chunks.
6. Stops on executor drain, paging output count, or scanned-key budget.

On stop it collects execution stats once, records total executor iterations, optionally returns scanned range when not fully drained and paging or `max_keys_read` caused partial execution, builds `SelectResponse`, attaches intermediate outputs, output counts, optional execution summaries, warnings, and encode type, then returns. If not stopped, it grows batch size.

`handle_streaming_request` does not allow intermediate channels. It repeatedly calls `internal_handle_request` until `stream_row_limit` is reached or the executor drains, concatenates rows data into one chunk, and returns `None` only when drained with no rows.

## State and Persistence Behavior

The runner has no durable persistence. Per-request mutable state includes:

- `exec_stats`: accumulated per-executor iteration, produced row, processed time, and scanned rows. Non-streaming clears only when runner is dropped; streaming clears after each response.
- `reserved_intermediate_results`: lazily allocated vectors reused to avoid repeated intermediate result allocation.
- `config`: shared immutable `Arc<EvalConfig>` with request flags plus paging and max-key controls.
- `deadline`: checked at each internal batch.
- `quota_limiter`: shared limiter used to sample CPU/read bytes and delay if needed.

Scanned ranges are delegated to the executor tree. The runner returns an `IntervalRange` only for partial paging/max-key/streaming paths, not for full drain. `max_keys_read` is explicitly best-effort inside TiKV; authoritative global enforcement is documented as living in TiDB.

## Dependencies and Integration Points

`runner.rs` is the integration hub for this directory. It directly references table scan, index scan, selection, projection, simple/hash/stream aggregation, limit, top n, partition top n, and index lookup executors. External dependencies include:

- `tipb` request/response/executor protobuf types.
- `kvproto::coprocessor::KeyRange` and storage abstractions from `tidb_query_common::storage`.
- `api_version::KvFormat` for storage key/value format specialization.
- `tidb_query_datatype` for field type, eval config/context, table handles, and encoding support.
- `tikv_util::deadline::Deadline` and `QuotaLimiter` for request limits and resource throttling.
- `protobuf::Message` for stream response serialization.
- Metrics in `tidb_query_common::metrics` and `tikv_util::metrics`.

The runner's output chunks are consumed by the coprocessor response layer. Its `collect_storage_stats`, `collect_scan_summary`, and `can_be_cached` methods are integration hooks for surrounding request handling.

## Risks and Edge Cases

- Parent index handling is delicate. Explicit `parent_idx` must be greater than the current index and within the descriptor list. Incorrect descriptors fail during build.
- Chunk encoding fallback is per requested output schema. Adding new field types without `EvalType` support silently falls back to default encoding, which affects response format and performance.
- Intermediate output channels must match executor indexes and schemas. Index lookup currently requires exactly one intermediate channel.
- `max_keys_read` uses `peek_scanned_rows_sum` from scan stats and intentionally avoids draining stats before final collection. Any executor that buffers scans without reflecting scan counts can under-report; the code notes index lookup pushdown is disabled elsewhere when max-key limiting is set.
- `handle_request` counts intermediate rows toward `record_all` for paging, not only main output rows. This is intentional in current code but important for response-size behavior.
- Streaming mode concatenates row data and always uses default-like serialization through `encode_result_to_chunk` because `is_streaming` forces row encoding.
- Deadline errors abort the request before encoding later batches. Quota limiter delay is applied after each internal batch, so large single batches can still do work before throttling.

## Test Signals

Tests cover chunk/default encoding correctness, index lookup executor construction and error cases, runner construction with intermediate channels and encoding fallback, intermediate output encoding and buffer reuse, response intermediate output attachment, non-streaming handle_request including paging and intermediate rows, parent traversal helper validation, and `max_keys_read` early stopping, unlimited mode, high limits, exact limits, and natural drain before limit. Failpoint-aware batch size helpers are also testable.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/runner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/selection_executor.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/selection_executor.rs

## Purpose

`selection_executor.rs` implements vectorized filtering for TiKV batch DAG execution. It evaluates one or more boolean-like RPN predicates over a child batch and mutates the batch logical row list so only rows satisfying every predicate remain. Physical columns are reused; selection does not materialize new result columns.

## Important APIs, Types, and Functions

- `BatchSelectionExecutor<Src>` stores an `EvalContext`, child executor, predicate RPN expressions, and a precomputed column-reference count per predicate.
- `check_supported(descriptor: &Selection)` validates that every selection condition can be converted to supported RPN evaluation.
- `new(config, src, conditions_def)` parses tipb `Expr` predicate trees into `RpnExpression`s and records `count_column_refs` for work metrics.
- `new_for_test` and `into_child` support unit tests.
- `handle_src_result(src_result)` mutates `src_result.logical_rows` by evaluating predicates in order, short-circuiting once no rows remain.
- `count_column_refs(expr)` counts `RpnExpressionNode::ColumnRef` nodes with saturating conversion to `u32`.
- `update_logical_rows_by_scalar_value(...)` applies scalar predicate truthiness to all rows.
- `update_logical_rows_by_vector_value(...)` applies vector predicate truthiness row by row using `retain`.
- `next_batch(scan_rows)` delegates to the child, runs filtering, merges warnings on success, or clears all rows and attaches an error on predicate failure.

## Control Flow

Each public batch starts by fetching one child `BatchExecuteResult`. `handle_src_result` ignores any child drain error comment-wise, but predicate evaluation can still be skipped naturally if logical rows are empty. For each predicate, it clones the current logical row list into a scratch vector because expression evaluation needs the pre-filter row mapping while the original row list will be retained in place.

Before evaluating a predicate, the executor records approximate work as:

`rows * (rpn_node_count + column_ref_count)`

using `tidb_query_common::metrics::record_executor_work` with executor name `batch_selection`. It then evaluates the predicate. Scalar results are converted to MySQL boolean once; false clears all logical rows and true preserves all. Vector results are interpreted through the value's logical row mapping and MySQL truthiness, retaining only rows whose predicate value is true. Nulls convert through `AsMySqlBool` semantics, so they filter out as false. The loop stops when either all predicates have run or no logical rows remain.

If predicate evaluation or boolean conversion returns an error, `next_batch` combines that error into `is_drained`, clears all rows, and does not merge accumulated warnings. On success it merges evaluation warnings into the child warnings and returns the same physical columns with the reduced logical row list.

## State and Persistence Behavior

Selection maintains no durable state. It mutates only per-batch logical row vectors and its `EvalContext` warnings. Physical column storage, extra common handle keys, scan stats, storage stats, and range state remain owned by the child. Because the executor preserves the child physical columns, extra common handle keys remain unfiltered at the column-vector level and consumers must continue to respect logical rows.

## Dependencies and Integration Points

This file integrates with:

- `crate::interface` for `BatchExecutor` and batch result structures.
- `tidb_query_expr::{RpnExpression, RpnExpressionBuilder, RpnStackNode}` for predicate evaluation.
- `tidb_query_datatype::{match_template_evaltype, AsMySqlBool, ChunkRef, EvaluableRef, LogicalRows}` for typed vector truth conversion.
- Metrics via `tidb_query_common::metrics::record_executor_work`.
- `runner.rs`, which creates this executor for `ExecType::TypeSelection` and validates descriptors through `check_supported`.

Selection preserves the child schema and delegates intermediate result behavior, so it can be placed above scans, index lookup, or other operators without changing output column layout.

## Risks and Edge Cases

- On the first predicate error, the whole batch is dropped. A test notes a more precise future behavior could return innocent rows before the failing row.
- `src_logical_rows_copy` allocates per batch and is reused per predicate; the TODO calls out avoiding this allocation.
- Work metrics are approximate and deliberately weight column references in addition to RPN nodes.
- Since physical columns are not compacted, metadata and consumers must honor logical rows. Extra common handle keys are preserved unfiltered.
- Empty logical rows must not call predicate functions; tests enforce this with unreachable functions.
- Multiple predicates short-circuit only after each predicate; there is no row-level short-circuit across predicates inside a single expression.

## Test Signals

Tests cover empty batches, no predicate, always-true and always-false predicates, single and multiple predicates in different orders, predicate errors, and preservation of extra common handle keys with filtered logical rows. They assert logical row indexes and drain/error behavior across multiple child batches.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/selection_executor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/simple_aggr_executor.rs -->
# sources/storage-engines/tikv/components/tidb_query_executors/src/simple_aggr_executor.rs

## Purpose

`simple_aggr_executor.rs` implements aggregation without `GROUP BY` for the vectorized batch executor framework. It wraps the generic `AggregationExecutor` with `SimpleAggregationImpl`, maintaining one aggregate state set for the entire input stream and producing at most one output row when the child drains and at least one input row was seen.

## Important APIs, Types, and Functions

- `BatchSimpleAggregationExecutor<Src>(AggregationExecutor<Src, SimpleAggregationImpl>)` is a thin newtype wrapper that implements `BatchExecutor` by delegating to the generic aggregation executor.
- `check_supported(descriptor: &Aggregation)` asserts no group-by expressions, rejects empty aggregate definitions, and validates every aggregate definition through `AllAggrDefinitionParser`.
- `new(config, src, aggr_defs)` and test-only `new_for_test` call `new_impl` with an aggregate definition parser.
- `new_impl(...)` constructs `SimpleAggregationImpl { states: Vec::new(), has_input_rows: false }` and passes it to `AggregationExecutor::new`.
- `SimpleAggregationImpl` stores aggregate function states and a flag indicating whether any input rows have been processed.
- `prepare_entities(entities)` creates one state per aggregate function from `entities.each_aggr_fn` and clears `has_input_rows`.
- `process_batch_input(entities, input_physical_columns, input_logical_rows)` evaluates each aggregate argument expression and updates its state with either repeated scalar values or vector values.
- `groups_len()` returns `1` only after input rows have been seen.
- `iterate_available_groups(entities, src_is_drained, iteratee)` asserts the source is stopped, calls the result-pushing iteratee for the single state group if input exists, and returns no group-by columns.
- `is_partial_results_ready()` always returns false because simple aggregation emits only after full source drain.

## Control Flow

The generic aggregation executor owns the outer batching loop. `SimpleAggregationImpl` supplies the no-grouping behavior. At prepare time it creates all aggregate states from parsed aggregate function definitions. For every non-final input batch, `process_batch_input` receives child physical columns and logical rows. It marks `has_input_rows` when the logical row slice is non-empty and records approximate work as `rows * aggregate_expression_count` under executor name `batch_simple_aggr`.

For each aggregate expression, it evaluates the argument RPN expression against the child schema and current logical rows. Scalar results are applied with `update_repeat!`, which updates the state once per logical row using the same scalar value. Vector results use the vector's logical row mapping and `update_vector!`. Typed dispatch is handled by `match_template_evaltype!`, so the aggregate state receives its expected concrete value type.

When the child drains, the generic aggregation executor asks whether partial groups are ready and then iterates available groups. Simple aggregation only emits after `src_is_drained.stop()` and only when `has_input_rows` is true. The iteratee pushes aggregate state outputs into result vectors; there are no grouping key columns to append.

## State and Persistence Behavior

State is in-memory and per request:

- `states`: boxed aggregate function states, one per aggregate definition.
- `has_input_rows`: controls whether a no-group aggregation should emit a row.

There is no durable persistence. The comment explains a deliberate semantic choice: for TiKV first-stage aggregation, a no-input simple aggregation returns no row even though SQL final-stage no-group aggregation often returns one row. This avoids producing final-stage semantics in a pushdown executor until aggregation stage metadata is introduced.

All scan/storage/range stats and cache behavior are delegated through the wrapped generic `AggregationExecutor`.

## Dependencies and Integration Points

This file integrates with:

- `tidb_query_aggr` traits and macros, including aggregate function definitions and state update macros.
- `crate::util::aggr_executor::{AggregationExecutor, AggregationExecutorImpl, Entities, AggrDefinitionParser, AllAggrDefinitionParser}`.
- `tidb_query_expr::RpnStackNode` for evaluated aggregate arguments.
- `tidb_query_datatype::codec::batch::{LazyBatchColumn, LazyBatchColumnVec}` and typed `VectorValue`s.
- `runner.rs`, which selects this executor for `TypeAggregation` and `TypeStreamAgg` descriptors when `group_by` is empty.

The output schema is produced by aggregate definition parsing, not by this file directly. The generic aggregation executor handles final result column construction and warning/error propagation around this implementation.

## Risks and Edge Cases

- The file asserts `descriptor.get_group_by().len() == 0` in `check_supported`; callers must route grouped aggregations elsewhere.
- No-input behavior intentionally returns no rows for first-stage TiKV aggregation. Changing final-stage behavior requires explicit stage information to avoid SQL semantic regressions.
- Aggregate argument evaluation errors propagate through the generic executor and stop output for the current request.
- `iterate_available_groups` asserts drained source. Calling it early would panic, but `is_partial_results_ready` returns false to prevent that path.
- State vector length must match aggregate expression count; `process_batch_input` asserts this invariant.
- Work metrics are approximate and do not account for aggregate function complexity.

## Test Signals

Tests define custom aggregate functions and parsers to validate state preparation, scalar and vector updates, multi-column aggregate outputs, constants and nulls, integration with built-in `COUNT` and `AVG`, no-input behavior, and multi-batch drain behavior. Assertions cover output row count, output column count, decoded aggregate values, and drain states.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/simple_aggr_executor.rs -->
