# Research Group subset-b-008943

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/txn_status_cache.rs -->
# sources/storage-engines/tikv/src/storage/txn/txn_status_cache.rs

## Purpose
`txn_status_cache.rs` implements TiKV's in-memory cache of recent transaction states keyed by `start_ts`. It exists primarily to make late, stale prewrite retries safer: if a transaction is already known committed, the storage path can avoid an optimization that skips WRITE CF constraint checks for non-unique index keys. The file also contains the newer dual-cache design for ongoing large transactions, where `min_commit_ts` must remain visible while locks are still being resolved.

## Important APIs, Types, and Functions
`TxnState` models `Ongoing { min_commit_ts }`, `Committed { commit_ts }`, and `RolledBack`; `from_ts` converts raw timestamps and rollback state into this enum. `CacheEntry` pairs state with insertion/update time. `TxnStatusCacheEvictPolicy` is an `lru::EvictPolicy` that evicts entries only after a required keep duration or capacity pressure. `TxnStatusCache` owns sharded `normal_cache` and `large_txn_cache` vectors of padded mutex-protected LRU caches. Its public surface includes `new`, `new_for_test`, `with_slots_and_time_limit`, `upsert`, `insert_committed`, `get`, `get_committed_no_promote`, `get_committed`, and `remove_large_txn`.

## Control Flow
Construction divides total capacity across slots and builds two cache sets with separate retention durations. `upsert` routes ongoing entries with `min_commit_ts > start_ts` into the large-transaction cache; committed, rolled-back, and normal ongoing states use the normal cache and also update any existing large-cache entry. Retrieval checks the large cache first because it can hold a newer view of a transaction that also exists in normal cache. Normal committed-only reads intentionally skip large-cache lookup and can avoid LRU promotion.

## State and Persistence Behavior
All cache state is process-local memory; it is not persisted and is not replicated across TiKV nodes. Each entry records wall-clock milliseconds for eviction. Metrics update used and allocated cache size under the assumption that one cache instance exists per process. The cache can be disabled by zero capacity, making operations no-ops.

## Dependencies and Integration Points
The module depends on TiKV's custom `lru` implementation, `parking_lot::Mutex`, `crossbeam::CachePadded`, `txn_types::TimeStamp`, failpoints, and storage scheduler metrics. It integrates with transaction prewrite/commit/rollback paths that can upsert or query status, and with resolved-ts/large-transaction handling through the large cache.

## Risks and Test Signals
Risk centers on incomplete cluster-wide visibility, wall-clock changes, capacity eviction before stale requests arrive, and lock ordering between large and normal cache locks. The code documents the unsolved leader-transfer gap. Tests cover insertion, time and capacity eviction, disabled cache behavior, normal/large transitions, immutability of decided states, large-txn removal, and failpoint-driven lock-order deadlock resistance. Benchmarks cover insert/get and manual concurrent contention behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/txn_status_cache.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/types.rs -->
# sources/storage-engines/tikv/src/storage/types.rs

## Purpose
`types.rs` defines shared storage-layer result and callback value types used by TiKV's MVCC, transaction, lock-manager, and raw APIs. It is a contract bridge between internal transaction processing results and protobuf-facing RPC responses.

## Important APIs, Types, and Functions
`MvccInfo` stores a key's optional lock, write records, and value records, with `into_proto` converting internal `Lock`, `Write`, `LastChange`, and timestamp fields into `kvrpcpb::MvccInfo`. `TxnStatus` represents primary-lock status outcomes such as rolled back, TTL expired, lock missing, uncommitted with pushed min-commit-ts signal, committed, pessimistic rollback, and do-nothing lock absence. `PrewriteResult`, `PessimisticLockParameters`, `PessimisticLockKeyResult`, `PessimisticLockResults`, and `SecondaryLocksStatus` carry transaction command results. The `storage_callback!` macro defines `StorageCallback` variants and maps `ProcessResult` variants into typed callback payloads.

## Control Flow
Storage commands produce `ProcessResult`; `StorageCallback::execute` matches the expected variant and calls the saved `Callback<T>` with either a typed success value or the shared error. Pessimistic lock results aggregate per-key outcomes, can be converted to protobuf tuples with a first shared error, and can also be converted into legacy `(values, not_founds)` vectors for older response shapes.

## State and Persistence Behavior
The file defines transient value objects. It does not persist data directly, but its conversions expose persisted MVCC metadata such as write type, start/commit timestamps, short values, GC fences, overlapped rollback flags, and last-change hints to clients.

## Dependencies and Integration Points
It depends on `kvproto::kvrpcpb`, `txn_types`, storage `Lock`, `Write`, `WriteType`, `WaitTimeout`, `SharedError`, and `txn::ProcessResult`. It is used throughout TiKV storage RPC handling as the common callback/result language.

## Risks and Test Signals
The main risk is mismatching a callback with the wrong `ProcessResult`, which intentionally panics. `PessimisticLockResults::into_legacy_values_and_not_founds` assumes all entries share the same response shape. Conversion logic must track protobuf field evolution, especially last-change and lock result fields. Local test helpers assert exact pessimistic lock result shapes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/types.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/Cargo.toml -->
# sources/storage-engines/tikv/tests/Cargo.toml

## Purpose
This manifest defines TiKV's private `tests` crate. It wires integration/failpoint tests and benchmark targets for raftstore, coprocessor executors, hierarchy, misc, deadlock detector, and memory quota benchmarks.

## Important APIs, Types, and Functions
The manifest declares test targets `failpoints` and `integrations`, and bench targets with mixed harness modes. Feature flags expose failpoints, test exports, test engine choices, allocators, CPU portability/SSE, mem profiling, and Docker-specific tests.

## Control Flow
Cargo selects targets and features from this file. Default features enable failpoints, testexport, RocksDB KV testing, and raft-engine raft testing. Criterion-style benchmarks use `harness = false`; the `misc` bench keeps the Rust test harness and nightly `test` feature.

## State and Persistence Behavior
The file has no runtime state. It controls compile-time dependency resolution and therefore which TiKV internal APIs are visible to tests and benchmarks.

## Dependencies and Integration Points
Dependencies include workspace crates for storage, raftstore, PD, engines, query executors, server/service, resource control, and test helpers. Dev dependencies include Criterion, perf events on Linux x86_64, engine/test crates, backup/import helpers, and JSON/test utilities.

## Risks and Test Signals
Risks are feature drift, duplicated dependencies, target-specific dev-dependency breakage, and bench target mismatches. A useful signal is successful `cargo test -p tests` or selected bench compilation under the default feature set and under alternate engine/allocator feature combinations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/hash_aggr/mod.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/hash_aggr/mod.rs

## Purpose
This module defines Criterion benchmark cases for TiKV batch hash aggregation executors. It measures COUNT/FIRST aggregates with different group-by expressions, cardinalities, and input types.

## Important APIs, Types, and Functions
Benchmark functions build `FixtureBuilder` inputs and TiDB expression protobufs with `ExprDefBuilder`. Cases include integer group-by with one group per row or two groups, scalar-function group-by, decimal group-by, multi-column group-by, and COUNT plus FIRST. `Input<M>` carries source row count and a boxed `HashAggrBencher`. `bench` registers sorted `BenchCase` values and expands rows/cases based on `TIKV_BENCH_LEVEL`.

## Control Flow
Each benchmark creates a synthetic batch fixture, builds group-by and aggregate expression lists, and delegates execution to `input.bencher.bench`. The default path benchmarks the batch bencher over 5000 rows; higher bench levels add smaller row counts and more cases.

## State and Persistence Behavior
State is temporary in-memory fixture columns and Criterion measurements. No durable store is used in this file.

## Dependencies and Integration Points
It depends on `hash_aggr::util`, common `BenchCase`/`FixtureBuilder`, `tidb_query_datatype`, `tipb`, and `tipb_helper`. It integrates into the top-level coprocessor executor benchmark runner through `hash_aggr::bench`.

## Risks and Test Signals
The benchmarks are sensitive to expression support in fast versus slow hash aggregation and to deterministic fixture generation. Compilation and Criterion output for all registered case/input names are the main signals; high bench levels exercise broader operator shapes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/hash_aggr/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/hash_aggr/util.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/hash_aggr/util.rs

## Purpose
This utility module adapts hash aggregation executor construction to the shared benchmark harness.

## Important APIs, Types, and Functions
`HashAggrBencher<M>` defines `name`, `bench`, and `box_clone`. `BatchBencher` implements it by creating a fixture source, building a `tipb::Aggregation` metadata object, selecting `BatchFastHashAggregationExecutor` when `check_supported` succeeds, otherwise falling back to `BatchSlowHashAggregationExecutor`, and running through `BatchNextAllBencher`.

## Control Flow
For each Criterion iteration, the closure clones the fixture into a fresh `BatchFixtureExecutor`, clones expression vectors, creates an `EvalConfig`, instantiates the appropriate batch hash aggregation executor, and drains it in 1024-row batches.

## State and Persistence Behavior
All state is per-iteration memory. No external storage is touched.

## Dependencies and Integration Points
It depends on `criterion`, `tidb_query_executors` hash aggregation executors, `tidb_query_datatype::expr::EvalConfig`, `tikv::storage::Statistics`, and common fixture/bencher utilities.

## Risks and Test Signals
`unwrap()` makes unsupported construction fail fast. The fast/slow selection path is a key test signal: cases that stop satisfying fast aggregation constraints should still run through slow aggregation or fail clearly.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/hash_aggr/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/index_scan/fixture.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/index_scan/fixture.rs

## Purpose
This fixture module creates the common table and store used by index-scan benchmarks.

## Important APIs, Types, and Functions
`table_with_2_columns_and_one_index(rows)` returns `(index_id, Table, Store<RocksEngine>)`. It builds a table with primary-key `id` and indexed `foo`, allocates a fresh index id with `next_id`, and fills rows using `FixtureBuilder`.

## Control Flow
The helper constructs column metadata, creates the table, generates an `id` column as `0..n` and a random `foo` column, then writes rows into the test coprocessor store.

## State and Persistence Behavior
State lives in the returned in-memory/test store abstraction backed by `RocksEngine` fixtures. It is rebuilt per benchmark case.

## Dependencies and Integration Points
It depends on `test_coprocessor` table/column builders and common `FixtureBuilder`. `index_scan::mod` uses the returned table metadata to produce index ranges and selected column lists.

## Risks and Test Signals
The fixture assumes `foo` is indexed and `id` is the primary key. If table/index encoding changes, benchmark compilation or scan results through executor construction will reveal drift.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/index_scan/fixture.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/index_scan/mod.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/index_scan/mod.rs

## Purpose
This module benchmarks index scan executor paths for retrieving either primary-key columns or indexed columns from a synthetic table.

## Important APIs, Types, and Functions
`bench_index_scan_primary_key` measures scanning an index while returning the primary key, modeling index lookup/double-read needs. `bench_index_scan_index` measures returning the indexed column itself. `Input<M>` wraps a `ScanBencher<IndexScanParam, M>`, and `bench` registers batch and DAG scan benchers for memory/RocksDB stores depending on bench level.

## Control Flow
Each case builds the fixture table/store, selects column metadata, creates an all-index key range, and calls the selected scan bencher with `unique = false`. Criterion groups are named by case and input display string.

## State and Persistence Behavior
Fixtures are generated per benchmark invocation. No persistent state is retained outside Criterion measurements and temporary RocksDB stores created by test utilities.

## Dependencies and Integration Points
It integrates with `index_scan::fixture`, `index_scan::util`, common `BenchCase`, `ScanBencher`, and store descriptors. The top-level coprocessor runner calls `index_scan::bench`.

## Risks and Test Signals
The benchmark only uses non-unique index mode. Higher bench levels add RocksDB direct batch scans and memory DAG variants, which are useful signals for store abstraction regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/index_scan/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/index_scan/util.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/index_scan/util.rs

## Purpose
This utility module builds batch and DAG index-scan executors for shared scan benchmarks.

## Important APIs, Types, and Functions
`IndexScanParam = bool` carries the unique-index flag. `BatchIndexScanExecutorBuilder<T>` implements `ScanExecutorBuilder` and returns a boxed `BatchExecutor<StorageStats = Statistics>`. `IndexScanExecutorDagBuilder<T>` implements `ScanExecutorDagHandlerBuilder` by creating a protobuf index-scan descriptor. Type aliases expose `BatchIndexScanNext1024Bencher` and `IndexScanDagBencher`.

## Control Flow
The batch builder constructs `TikvStorage` from the chosen store type, builds `BatchIndexScanExecutor<ApiV1>`, performs a one-row warm-up batch to pay scanner construction cost outside the measured loop, and returns the executor. The DAG builder delegates to `build_dag_handler`.

## State and Persistence Behavior
No persistent state is owned. The executor reads from the passed test store.

## Dependencies and Integration Points
It depends on API V1 query storage, futures `block_on`, `BatchIndexScanExecutor`, common executor descriptors, and scan bencher traits.

## Risks and Test Signals
Constructor parameters such as unique flag, index id `0`, and scan flags must match executor expectations. Compilation and successful warm-up are the main signals for interface drift.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/index_scan/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/integrated/fixture.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/integrated/fixture.rs

## Purpose
This fixture module provides table/store shapes for integrated DAG executor benchmarks.

## Important APIs, Types, and Functions
It defines `table_with_int_column_two_groups`, `table_with_int_column_two_groups_ordered`, `table_with_int_column_n_groups`, and `table_with_3_int_columns_random`. The first three build `id` plus `foo` integer tables with sampled, ordered, or one-group-per-row values. The last builds `id`, `col1`, and `col2` random integer columns.

## Control Flow
Each helper constructs `test_coprocessor` table metadata, fills a `Store<RocksEngine>` through `FixtureBuilder`, and returns table/store pairs consumed by integrated benchmark cases.

## State and Persistence Behavior
Data is benchmark fixture state only. Ordered variants are used where stream aggregation requires grouped input.

## Dependencies and Integration Points
It depends on `test_coprocessor`, `tikv::storage::RocksEngine`, and common fixture building. `integrated/mod.rs` uses these helpers to build selection, aggregation, and top-N DAG pipelines.

## Risks and Test Signals
The fixture must keep column names/types aligned with expressions in integrated cases. Stream aggregation benchmarks rely on ordered grouping fixtures; using random fixtures there would change semantics and measured behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/integrated/fixture.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/integrated/mod.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/integrated/mod.rs

## Purpose
This module benchmarks multi-executor DAG pipelines that combine table scan, selection, aggregation, stream aggregation, hash aggregation, and top-N operators.

## Important APIs, Types, and Functions
It defines benchmark functions for `SELECT COUNT(1)`, `COUNT(column)`, plain selection, selection with low/medium/high selectivity, grouped counts with hash or stream aggregation, scalar group-by expressions, two-column group-by, selection plus group-by, three-column top-N, filtered top-N, and 50-column projection plus top-N. `Input<M>` combines row count and an `IntegratedBencher`.

## Control Flow
Every case builds table/store fixtures and a slice of protobuf executor descriptors using helpers from `executor_descriptor`. The selected bencher either constructs batch executors directly or wraps the protobuf DAG into a `RequestHandler`. `bench` expands row counts and bencher implementations by `bench_level`, registers a default set of representative cases, and adds broader cases at higher levels. Cases with limit 4000 skip work when row count is smaller.

## State and Persistence Behavior
State is per-benchmark fixture data and Criterion measurements. RocksDB-backed inputs use temporary test store state; memory inputs use fixture store state.

## Dependencies and Integration Points
It integrates the table-scan fixture module, local integrated fixtures, `integrated::util`, common executor descriptor builders, store descriptors, TiDB expression protobuf builders, and top-level coprocessor benchmark dispatch.

## Risks and Test Signals
Risks include expression column-index mismatches, stream aggregation requiring ordered input, and differences between batch executor and DAG handler behavior. Criterion compilation/runs across normal DAG, batch DAG, memory batch, and RocksDB batch inputs are the key regression signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/integrated/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/integrated/util.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/integrated/util.rs

## Purpose
This utility module abstracts integrated DAG benchmark execution over direct batch executors and request-handler DAG paths.

## Important APIs, Types, and Functions
`IntegratedBencher<M>` defines `name`, `bench`, and `box_clone`. `BatchBencher<T>` builds batch executors through `tidb_query_executors::runner::build_executors::<_, ApiV1>`. `DagBencher<T>` builds a full `RequestHandler` with `build_dag_handler`; its `batch` flag affects only the display tag through the shared helper path.

## Control Flow
Each Criterion iteration creates fresh executor state. Batch mode converts the fixture store into `TikvStorage`, passes executor descriptors and ranges to the runner, and drains with `BatchNextAllBencher`. DAG mode creates a handler and runs `handle_request` through `DagHandleBencher`.

## State and Persistence Behavior
The module keeps no durable state. Generic store type `T` selects memory or RocksDB-backed store behavior supplied by the caller.

## Dependencies and Integration Points
It depends on API V1 storage, `StubAccessor`, `EvalConfig`, `TikvStorage`, common bencher utilities, and store descriptors.

## Risks and Test Signals
Because it constructs real executor pipelines, `unwrap()` failures expose invalid descriptors or runner interface drift. Comparing batch and DAG benchmark names/results helps catch divergent execution paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/integrated/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/mod.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/mod.rs

## Purpose
This is the entry point for Criterion coprocessor executor benchmarks.

## Important APIs, Types, and Functions
It declares benchmark modules for hash aggregation, index scan, integrated DAGs, selection, simple aggregation, stream aggregation, table scan, top-N, and utilities. `execute` calls each module's `bench`. `run_bench` selects Criterion measurement backends: CPU time by default, Linux perf events when requested and compiled for x86_64 Linux, or wall time.

## Control Flow
`main` reads `TIKV_BENCH_MEASUREMENT`, builds an appropriate Criterion instance with `configure_from_args`, invokes all benchmark module registration, and prints the final summary.

## State and Persistence Behavior
No persistent state is owned. State is Criterion configuration and generated benchmark artifacts/profiles from lower-level benchers.

## Dependencies and Integration Points
It integrates the entire coprocessor executor bench tree and optional crates `criterion-cpu-time` and `criterion-perf-events`.

## Risks and Test Signals
Measurement backend selection is platform-sensitive. Unsupported measurement strings panic. Successful startup under the three supported measurement modes validates feature-gated dependencies and benchmark registration.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/selection/mod.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/selection/mod.rs

## Purpose
This module benchmarks batch selection executor predicates over synthetic columns.

## Important APIs, Types, and Functions
Cases cover `WHERE column`, column-column real comparison, column-constant real comparison, and multiple predicates combining real and integer comparisons. `Input<M>` carries row count and `SelectionBencher`. `bench` registers default and higher-level cases.

## Control Flow
Each case builds fixture columns, constructs predicate expressions with `ExprDefBuilder`, and delegates to the selected bencher. Default runs focus on column-constant comparison over 5000 rows; higher levels add more predicates and smaller row counts.

## State and Persistence Behavior
All state is in-memory fixture data and Criterion measurement state.

## Dependencies and Integration Points
It depends on local `selection::util`, common `BenchCase` and `FixtureBuilder`, TiDB field types, scalar function signatures, and expression builder helpers.

## Risks and Test Signals
The benchmarks assume predicate result types and column indexes match generated fixture schema. Adding higher bench levels is useful for catching less common expression construction regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/selection/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/selection/util.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/selection/util.rs

## Purpose
This utility module adapts `BatchSelectionExecutor` into the shared Criterion bench interface.

## Important APIs, Types, and Functions
`SelectionBencher<M>` defines benchmark naming, execution, and clone-boxing. `BatchBencher` implements it by wrapping a cloned `BatchFixtureExecutor` and predicate vector in `BatchSelectionExecutor`.

## Control Flow
For each benchmark iteration, the fixture is cloned, an `EvalConfig` is allocated, expressions are cloned, and the batch selection executor is drained through `BatchNextAllBencher`.

## State and Persistence Behavior
No persistent state is used; executor and fixture state are per iteration.

## Dependencies and Integration Points
It depends on `criterion`, `BatchSelectionExecutor`, `EvalConfig`, `tikv::storage::Statistics`, and shared bencher/fixture utilities.

## Risks and Test Signals
`unwrap()` surfaces unsupported or malformed expressions. Benchmark output under the `batch` name is the main signal that the selection executor still builds and drains correctly.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/selection/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/simple_aggr/mod.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/simple_aggr/mod.rs

## Purpose
This module benchmarks simple, no-group aggregation executor cases such as `COUNT(1)` and `COUNT(column)`.

## Important APIs, Types, and Functions
Benchmark functions cover count of a constant, integer column, real column, and bytes column. `Input<M>` carries row count and `SimpleAggrBencher`. `bench` uses bench level to choose row counts and case breadth.

## Control Flow
Cases create fixture columns, build aggregate expression protobufs with `ExprDefBuilder`, and call the configured simple aggregation bencher. Criterion groups are sorted by `BenchCase` names and parameterized by input display strings.

## State and Persistence Behavior
State is in-memory fixture data only. There is no durable engine access in this module.

## Dependencies and Integration Points
It depends on `simple_aggr::util`, shared `FixtureBuilder`/`BenchCase`, TiDB field types, and `tipb::ExprType`. The top-level coprocessor runner calls `simple_aggr::bench`.

## Risks and Test Signals
The benchmark is sensitive to aggregate expression encoding and fixture schema alignment. High bench levels add non-default aggregate cases that catch broader executor construction drift.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/simple_aggr/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/simple_aggr/util.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/simple_aggr/util.rs

## Purpose
This utility module wraps `BatchSimpleAggregationExecutor` for Criterion benchmarks.

## Important APIs, Types, and Functions
`SimpleAggrBencher<M>` defines `name`, `bench`, and `box_clone`. `BatchBencher` constructs `BatchSimpleAggregationExecutor` from a cloned fixture source, default `EvalConfig`, and aggregate expression vector.

## Control Flow
Each iteration gets a fresh source executor and aggregation executor, then drains all batches through `BatchNextAllBencher`.

## State and Persistence Behavior
No persistent state; all data is memory fixture state.

## Dependencies and Integration Points
It depends on `tidb_query_executors::BatchSimpleAggregationExecutor`, `EvalConfig`, storage statistics, and common fixture/bencher utilities.

## Risks and Test Signals
Unsupported aggregate expressions panic through `unwrap()`. Successful runs validate that simple aggregation still consumes the shared fixture executor schema and batch interface.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/simple_aggr/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/stream_aggr/mod.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/stream_aggr/mod.rs

## Purpose
This module benchmarks stream aggregation where input rows are ordered by group keys.

## Important APIs, Types, and Functions
Cases mirror hash aggregation scenarios: COUNT by integer or decimal group key, two-group variants, two-column integer/real group-by, and COUNT plus FIRST. `Input<M>` carries source rows and a `StreamAggrBencher`.

## Control Flow
Fixtures use ordered column builders for low-cardinality stream cases and sequential columns for one-group-per-row cases. Each benchmark constructs group-by and aggregate expressions, then delegates to the stream aggregation bencher. `bench` chooses representative defaults and adds wider cases by bench level.

## State and Persistence Behavior
No durable state is used. Correct benchmark semantics depend on fixture ordering.

## Dependencies and Integration Points
It depends on `stream_aggr::util`, common benchmark helpers, TiDB field types, and expression builders. It is registered by the coprocessor executor runner.

## Risks and Test Signals
Stream aggregation assumes grouped input order; changing fixture order would alter behavior. Successful Criterion registration and execution across ordered two-group and many-group cases is the useful signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/stream_aggr/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/stream_aggr/util.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/stream_aggr/util.rs

## Purpose
This utility module adapts `BatchStreamAggregationExecutor` to the benchmark harness.

## Important APIs, Types, and Functions
`StreamAggrBencher<M>` defines the bench interface. `BatchBencher` builds a batch stream aggregation executor with cloned fixture input, default evaluation config, group-by expressions, and aggregate expressions.

## Control Flow
The executor is constructed per iteration and drained with `BatchNextAllBencher`, measuring the full aggregation pipeline over the fixture source.

## State and Persistence Behavior
State is per-iteration memory. There is no storage engine persistence.

## Dependencies and Integration Points
It depends on `BatchStreamAggregationExecutor`, `EvalConfig`, `tikv::storage::Statistics`, and shared fixture/bencher utilities.

## Risks and Test Signals
`unwrap()` exposes unsupported descriptors. The stream executor's dependence on input ordering is handled by calling modules rather than this utility, so misuse by new cases is a risk.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/stream_aggr/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/table_scan/fixture.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/table_scan/fixture.rs

## Purpose
This module provides table/store fixtures for table scan benchmarks.

## Important APIs, Types, and Functions
`table_with_2_columns` builds `id` primary key plus `foo`. `table_with_multi_columns` builds `col0..colN` random integer columns. `table_with_missing_column` builds metadata for many columns but omits `col0` from stored rows so default-value behavior is measured. `table_with_long_column` builds `id`, `foo`, and a long varchar `bar`.

## Control Flow
Each helper constructs `test_coprocessor` table metadata and fills a `Store<RocksEngine>` via `FixtureBuilder` with deterministic row counts and column generators.

## State and Persistence Behavior
Fixture data is generated per benchmark. The returned store is test-only state.

## Dependencies and Integration Points
It depends on `test_coprocessor`, `RocksEngine`, and common fixture building. `table_scan/mod.rs` consumes these helpers to benchmark projection location, absent columns, long columns, and point ranges.

## Risks and Test Signals
Risks are column-name mismatches and unintended default handling changes. Compilation plus successful scan executor construction for missing/long column cases are the main signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/table_scan/fixture.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/table_scan/mod.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/table_scan/mod.rs

## Purpose
This module benchmarks table scan executor performance across projection patterns, row widths, missing columns, long values, and point ranges.

## Important APIs, Types, and Functions
Benchmark cases include primary-key-only scan, front/end/all datum projections from 100-column rows, long-column projections, absent/default column reads, absent columns in large rows, and many point ranges. `Input<M>` wraps a `ScanBencher<TableScanParam, M>`. `bench` configures memory batch, RocksDB DAG normal/batch, and additional high-level store combinations.

## Control Flow
Each case builds an appropriate fixture table/store, selects `ColumnInfo` values and ranges, then calls the selected scan bencher. Cases are sorted and registered under Criterion benchmark groups.

## State and Persistence Behavior
All data is benchmark fixture state. RocksDB-backed inputs may create temporary test engine state through common store helpers.

## Dependencies and Integration Points
It depends on table scan fixtures, `table_scan::util`, common `BenchCase`, scan benchers, and store descriptors. It is invoked by the top-level coprocessor executor benchmark entry point.

## Risks and Test Signals
The benchmark is a useful signal for scan decoder regressions: primary-key extraction, row datum decoding position, default-value handling, long varchars, and point-range overhead. Higher bench levels broaden store/execution modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/table_scan/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/table_scan/util.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/table_scan/util.rs

## Purpose
This utility module builds batch and DAG table-scan executors for scan benchmarks.

## Important APIs, Types, and Functions
`TableScanParam = ()`. `BatchTableScanExecutorBuilder<T>` implements `ScanExecutorBuilder` and returns a boxed batch executor. `TableScanExecutorDagBuilder<T>` builds protobuf table-scan descriptors for DAG handlers. Type aliases expose `BatchTableScanNext1024Bencher` and `TableScanDagBencher`.

## Control Flow
The batch builder creates `TikvStorage`, builds `BatchTableScanExecutor<ApiV1>`, performs a one-row warm-up to exclude scanner initialization, and returns the executor. The DAG builder delegates descriptor execution to `build_dag_handler`.

## State and Persistence Behavior
The module owns no durable state. Executors read from caller-provided fixture stores.

## Dependencies and Integration Points
It depends on API V1 query storage, futures `block_on`, `BatchTableScanExecutor`, common executor descriptors, and scan bencher traits.

## Risks and Test Signals
Constructor flags must track table scan executor signature changes. Warm-up behavior is intentional; removing it changes benchmark meaning.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/table_scan/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/top_n/mod.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/top_n/mod.rs

## Purpose
This module benchmarks batch TopN executor sorting and limiting behavior over different projection widths and order-by expression counts.

## Important APIs, Types, and Functions
Helper functions build one-order-by and three-order-by cases with configurable projection column count and limit. Cases include 1 or 50 columns with limit 10 or 4000, and three-key ordering using `IntIsNull`, ascending column, and descending column. `Input<M>` carries row count and `TopNBencher`.

## Control Flow
Each benchmark builds random integer columns, constructs order-by expressions, and delegates to the selected bencher. Default cases cover three-key ordering; higher bench levels add simpler one-key variants and small row counts.

## State and Persistence Behavior
All benchmark data is in-memory fixture state.

## Dependencies and Integration Points
It depends on `top_n::util`, common `FixtureBuilder`/`BenchCase`, TiDB field types, scalar signatures, and expression builders.

## Risks and Test Signals
The cases stress comparator construction, multi-column projection retention, descending order flags, and large limit handling. `assert!` guards invalid helper inputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/top_n/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/top_n/util.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/top_n/util.rs

## Purpose
This utility module adapts `BatchTopNExecutor` to the shared benchmark interface.

## Important APIs, Types, and Functions
`TopNBencher<M>` defines benchmark execution with fixture builder, order-by expressions, sort directions, and limit. `BatchBencher` constructs `BatchTopNExecutor` from cloned fixture input and drains it through `BatchNextAllBencher`.

## Control Flow
Per iteration, it builds fresh source and TopN executor state, clones expression/order vectors, passes the limit, and drains all output batches.

## State and Persistence Behavior
The module is memory-only and owns no persistent state.

## Dependencies and Integration Points
It depends on `BatchTopNExecutor`, `EvalConfig`, Criterion black-boxing, and shared fixture/bencher utilities.

## Risks and Test Signals
`unwrap()` catches unsupported order-by definitions. Benchmark success across wide projection and high-limit cases validates TopN construction and batch draining.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/top_n/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/bencher.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/bencher.rs

## Purpose
This module defines reusable Criterion bench drivers for batch executors and DAG request handlers.

## Important APIs, Types, and Functions
`Bencher` is a trait with a generic `bench` method. `BatchNext1024Bencher` measures one `next_batch(1024)` call. `BatchNextAllBencher` repeatedly calls `next_batch(1024)` until the executor reports drained. `DagHandleBencher` measures `RequestHandler::handle_request`.

## Control Flow
Each driver uses `criterion::iter_batched_ref` to create fresh executor/handler state per sample, wraps work in `profiler::start/stop`, black-boxes results, and blocks async executor calls with `futures::executor::block_on`.

## State and Persistence Behavior
State is benchmark-local executor/handler state and generated profiler output files. No storage state is owned directly.

## Dependencies and Integration Points
It depends on `tidb_query_executors::BatchExecutor`, TiKV `RequestHandler`, Criterion, futures, and the optional profiler integration.

## Risks and Test Signals
The benchmark meaning depends on batch size 1024 and profiler overhead. `BatchNext1024Bencher` unwraps `is_drained`, so invalid executor results fail loudly. It is the common measurement layer for most coprocessor executor benchmarks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/bencher.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/executor_descriptor.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/executor_descriptor.rs

## Purpose
This module builds `tipb::Executor` protobuf descriptors used by DAG-based benchmarks.

## Important APIs, Types, and Functions
Functions include `table_scan`, `index_scan`, `selection`, `simple_aggregate`, `hash_aggregate`, `stream_aggregate`, and `top_n`. Each initializes a `PbExecutor`, sets the `ExecType`, and fills the relevant executor-specific protobuf fields.

## Control Flow
Descriptor builders clone column info and expression slices into protobuf repeated fields. `top_n` zips order expressions with direction flags into `ByItem`s and sets the limit.

## State and Persistence Behavior
No state is retained; descriptors are transient request metadata.

## Dependencies and Integration Points
It depends on `tipb` protobuf types and is used heavily by integrated, table scan, and index scan DAG benchmarks.

## Risks and Test Signals
Descriptor drift is the key risk: executor types, field names, or aggregation type conventions must remain aligned with TiDB/TiKV DAG handlers. Constructor compilation and DAG handler `unwrap()` failures catch regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/executor_descriptor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/fixture.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/fixture.rs

## Purpose
This module creates deterministic in-memory batch fixtures and test stores for coprocessor executor benchmarks.

## Important APIs, Types, and Functions
`FixtureBuilder` stores row count, field types, and per-column `Datum` vectors. It can push sequential/random/sampled/ordered integer and float columns, decimal columns, and random fixed-length bytes columns. `build_store` inserts rows into a `test_coprocessor::Store<RocksEngine>`. `build_batch_fixture_executor` converts datum columns into raw `LazyBatchColumn`s. `BatchFixtureExecutor` implements `BatchExecutor`.

## Control Flow
Fixture builder methods append schema and data columns. Store construction inserts row-by-row inside begin/commit calls. Batch executor construction encodes datums into raw column bytes. `next_batch` splits off up to `scan_rows` values from each column, constructs `LazyBatchColumnVec`, and marks drained when the first source column is empty.

## State and Persistence Behavior
Fixture state is cloned per benchmark iteration. `BatchFixtureExecutor` mutates its columns by shifting consumed rows. No durable state is owned except optional test store contents returned by `build_store`.

## Dependencies and Integration Points
It depends on `test_coprocessor`, TiDB datatype codecs, batch executor interfaces, `async_trait`, deterministic RNG seeds, and common bencher utilities.

## Risks and Test Signals
Column count/schema alignment is enforced with assertions. Drain status depends on the first column, so empty or uneven columns would be risky. The local utility benchmark checks fixture executor overhead at higher bench levels.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/fixture.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/mod.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/mod.rs

## Purpose
This module is the shared utility root for coprocessor executor benchmarks.

## Important APIs, Types, and Functions
It re-exports `FixtureBuilder`, declares utility submodules, provides `bench_level()` from `TIKV_BENCH_LEVEL`, and defines `build_dag_handler` for constructing `DagHandlerBuilder<ApiV1>`. It also defines generic `BenchCase` storage through `InnerBenchCase`, `IBenchCase`, and `BenchCase`.

## Control Flow
`build_dag_handler` builds a `DagRequest`, copies executor descriptors and key ranges, converts the test store to the requested transaction store type, supplies a deadline and quota limiter, and returns a boxed request handler. `BenchCase` boxes benchmark functions, exposes names/functions, and implements ordering by name for deterministic Criterion output.

## State and Persistence Behavior
The module holds no persistent state. DAG handler construction consumes caller-provided stores/ranges and creates per-benchmark request state.

## Dependencies and Integration Points
It depends on API V1, Criterion, `test_coprocessor`, TiKV coprocessor DAG handler APIs, `StubAccessor`, `QuotaLimiter`, and `tipb` descriptors. All coprocessor executor benchmark families use it.

## Risks and Test Signals
`bench_level` uses `unwrap()` on parse, so invalid environment values panic. DAG builder parameters such as deadline, batch flags, and concurrency defaults can affect benchmark comparability. Successful use by all child modules validates the shared harness.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/scan_bencher.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/scan_bencher.rs

## Purpose
This module provides generic scan benchmark abstractions shared by table scan and index scan benchmarks.

## Important APIs, Types, and Functions
`ScanExecutorBuilder` builds direct batch scan executors. `ScanExecutorDagHandlerBuilder` builds DAG handlers. `ScanBencher<P, M>` is the object-safe benchmark trait. `BatchScanNext1024Bencher<B>` adapts a scan executor builder to one-batch measurement. `ScanDagBencher<B>` adapts DAG handler builders and includes batch/normal tags plus display row count.

## Control Flow
Batch scan benching calls `B::build` and then `BatchNext1024Bencher`. DAG scan benching calls `B::build` with its batch flag and wraps the handler in `DagHandleBencher`. `box_clone` implementations allow input configurations to be duplicated for Criterion cases.

## State and Persistence Behavior
No persistent state is owned. Builder implementations in table/index modules decide store access.

## Dependencies and Integration Points
It depends on Criterion measurement traits, TiKV `RequestHandler`, batch executor interfaces, key ranges, column info, common benchers, and store descriptors.

## Risks and Test Signals
The abstractions assume builder-created executors are fresh and independent per iteration. Display names are used as Criterion parameters, so changes affect result continuity.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/scan_bencher.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/store.rs -->
# sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/store.rs

## Purpose
This module names and describes store implementations used by coprocessor executor benchmarks.

## Important APIs, Types, and Functions
`MemStore` aliases `FixtureStore`; `RocksStore` aliases `SnapshotStore<Arc<RocksSnapshot>>`. `StoreDescriber` provides a static display name. Specialization gives `Memory` for `MemStore` and `RocksDB` for `RocksStore`.

## Control Flow
Bench input display code calls `StoreDescriber::name()` to produce Criterion parameter names. Generic default implementation is intentionally unimplemented and relies on concrete specializations.

## State and Persistence Behavior
No state is held. Store aliases point at state owned by fixtures and snapshots.

## Dependencies and Integration Points
It depends on TiKV transaction store traits/types and Rocks snapshots. Scan and integrated benchers use it for names and generic type selection.

## Risks and Test Signals
The file uses Rust specialization-style default impls, so compiler feature compatibility matters. Any new store type needs an explicit `StoreDescriber` implementation before use.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/deadlock_detector/mod.rs -->
# sources/storage-engines/tikv/tests/benches/deadlock_detector/mod.rs

## Purpose
This Criterion benchmark measures TiKV deadlock detector table performance under dense wait-for graph insertion patterns with and without cleanup pressure.

## Important APIs, Types, and Functions
`DetectGenerator` produces `WaitForEntry` records with monotonically increasing transaction ids and random wait-for transactions/key hashes in a configurable range. `Config` carries request count per iteration, transaction range, and TTL. `bench_detect` feeds generated entries into `DetectTable::detect`.

## Control Flow
Two benchmark groups are registered. `bench_dense_detect_without_cleanup` varies wait-for range with huge TTL to reduce cleanup. `bench_dense_detect_with_cleanup` varies TTL at fixed range to exercise expiration/cleanup costs. `main` uses Criterion sample size 10.

## State and Persistence Behavior
State is an in-memory `DetectTable` per bench function and generator state. No durable storage is used.

## Dependencies and Integration Points
It depends on `kvproto::deadlock`, TiKV lock-manager `DetectTable`, Criterion, random generation, and TiKV duration utilities.

## Risks and Test Signals
Randomness can introduce noise, while dense ranges can produce different cycle/collision behavior. Useful signals are per-range and per-TTL performance trends plus compilation against deadlock detector API changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/deadlock_detector/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/hierarchy/engine/mod.rs -->
# sources/storage-engines/tikv/tests/benches/hierarchy/engine/mod.rs

## Purpose
This module benchmarks the low-level storage engine trait operations used by TiKV's hierarchy benchmarks.

## Important APIs, Types, and Functions
`bench_engine_put` measures `Engine::put` over generated key/value pairs. `bench_engine_snapshot` measures snapshot creation. `bench_engine_get` measures `Snapshot::get` excluding snapshot creation by creating a snapshot in setup. `bench_engine` registers all three for every `BenchConfig`.

## Control Flow
Criterion `iter_batched` creates deterministic generated data with `KvGenerator`, then runs the measured operation loop. Config display includes engine, key length, and value length.

## State and Persistence Behavior
Each benchmark builds a fresh engine from the configured factory. RocksDB factories create temporary test engines; BTree engines are in-memory.

## Dependencies and Integration Points
It depends on `tikv::storage::kv::{Engine, Snapshot}`, `txn_types::Key`, `test_util::KvGenerator`, and hierarchy `BenchConfig`/`EngineFactory`.

## Risks and Test Signals
Bench results compare BTree and Rocks engine behavior at trait level. Snapshot setup placement is intentional; moving it into the measured loop would change semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/hierarchy/engine/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/hierarchy/engine_factory.rs -->
# sources/storage-engines/tikv/tests/benches/hierarchy/engine_factory.rs

## Purpose
This module abstracts engine construction for hierarchy benchmarks.

## Important APIs, Types, and Functions
`EngineFactory<E>` defines `build`. `BTreeEngineFactory` builds `BTreeEngine::default()` and displays as `BTree`. `RocksEngineFactory` builds a `RocksEngine` via `TestEngineBuilder::new().build().unwrap()` and displays as `Rocks`.

## Control Flow
Benchmark configuration code passes factories into generic bench modules, allowing identical benchmark code to run against both engine implementations.

## State and Persistence Behavior
Factories are stateless, clone/copy values. Built engines own their own test state; Rocks engines may create temporary disk-backed resources through the builder.

## Dependencies and Integration Points
It depends on TiKV storage `Engine`, `TestEngineBuilder`, `BTreeEngine`, and `RocksEngine`. The hierarchy runner uses it for engine, MVCC, transaction, and storage benchmark suites.

## Risks and Test Signals
`unwrap()` on Rocks engine build fails loudly for environment or engine initialization regressions. Debug names are part of Criterion benchmark identifiers.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/hierarchy/engine_factory.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/hierarchy/mod.rs -->
# sources/storage-engines/tikv/tests/benches/hierarchy/mod.rs

## Purpose
This is the entry point for hierarchy benchmarks that compare costs at engine, MVCC, transaction, and storage API layers.

## Important APIs, Types, and Functions
It declares child modules, default iterations/key/value lengths, `BenchConfig<F>`, `load_configs`, and `main`. `BenchConfig` records key length, value length, and engine factory, with a compact debug representation.

## Control Flow
`main` creates Criterion from CLI args, loads BTree and Rocks configs, then runs `bench_engine`, `bench_mvcc`, `bench_txn`, and `bench_storage` for both engine families before final summary.

## State and Persistence Behavior
No persistent state is held in this module. Child benchmark modules create engines and stores per test.

## Dependencies and Integration Points
It depends on Criterion, TiKV storage `Engine`, local engine factories, and all hierarchy child benchmark modules.

## Risks and Test Signals
Default config breadth is small: one key length and two value lengths. It is useful for relative cost layering, not exhaustive performance characterization.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/hierarchy/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/hierarchy/mvcc/mod.rs -->
# sources/storage-engines/tikv/tests/benches/hierarchy/mvcc/mod.rs

## Purpose
This module benchmarks MVCC primitives directly, below the high-level storage command API but above raw engine calls.

## Important APIs, Types, and Functions
`setup_prewrite` populates locks for a generated key set and returns a snapshot plus keys. Benchmarks cover `mvcc_prewrite`, `mvcc_commit`, rollback of prewrote/conflict/non-prewrote keys, `MvccReader::load_lock`, and `MvccReader::seek_write`. `bench_mvcc` registers all cases for each config.

## Control Flow
Bench functions create engines, snapshots, `ConcurrencyManager`, `MvccTxn`, `SnapshotReader` or `MvccReader`, then call transaction helper functions such as `prewrite`, `commit`, and `cleanup`. Some cases write prewrite modifies to the engine in setup using `tikv_kv::write`.

## State and Persistence Behavior
Benchmark setup mutates fresh engine instances by writing lock/write data. Measured operations generally operate on snapshots and MVCC transaction buffers; durability belongs to setup writes.

## Dependencies and Integration Points
It depends on concurrency manager, TiKV MVCC reader/txn types, transaction helpers, `KvGenerator`, `txn_types`, and hierarchy engine factories.

## Risks and Test Signals
Start timestamp selection controls whether cleanup sees prewrote, conflict, or absent state. Snapshot reuse and setup placement affect what is measured. Compile/run signals validate direct MVCC helper APIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/hierarchy/mvcc/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/hierarchy/storage/mod.rs -->
# sources/storage-engines/tikv/tests/benches/hierarchy/storage/mod.rs

## Purpose
This module benchmarks TiKV's high-level synchronous test storage API for raw get, prewrite, and commit.

## Important APIs, Types, and Functions
`storage_raw_get` builds a `SyncTestStorageBuilderApiV1` store and measures `raw_get`. `storage_prewrite` measures one put mutation prewrite per generated key. `storage_commit` prewrites generated keys in setup, then measures commit calls. `bench_storage` registers all cases.

## Control Flow
Each benchmark builds a fresh engine-backed test storage. `iter_batched` generates request data and passes references to the store into measured closures. Commit setup writes locks before measured commit calls.

## State and Persistence Behavior
The storage object owns engine-backed test state. Prewrite and commit mutate that state through the storage API.

## Dependencies and Integration Points
It depends on engine traits, `SyncTestStorageBuilderApiV1`, `KvGenerator`, `txn_types::Mutation`, `engine_traits::CF_DEFAULT`, and hierarchy configs.

## Risks and Test Signals
These benchmarks include more scheduling/storage-stack overhead than MVCC helper benchmarks. They validate the test storage builder and API signatures across engine backends.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/hierarchy/storage/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/hierarchy/txn/mod.rs -->
# sources/storage-engines/tikv/tests/benches/hierarchy/txn/mod.rs

## Purpose
This module benchmarks transaction helper functions plus engine write persistence, sitting between direct MVCC helper benchmarks and high-level storage API benchmarks.

## Important APIs, Types, and Functions
`setup_prewrite` writes prewrite modifies into an engine and returns keys. Benchmarks cover prewrite, commit, rollback of prewrote locks, rollback conflict, and rollback of non-prewrote keys. `bench_txn` registers cases by config.

## Control Flow
For each measured key, the benchmark obtains a fresh snapshot, creates `MvccTxn` and `SnapshotReader`, invokes `prewrite`, `commit`, or `cleanup`, converts modifies into `WriteData`, and writes them to the engine. Commit/rollback cases use setup engines populated with lock state.

## State and Persistence Behavior
Unlike `mvcc/mod.rs`, measured closures include engine writes, so benchmarks include persistence cost to the selected engine. Engines are fresh per benchmark function but mutated through iterations.

## Dependencies and Integration Points
It depends on concurrency manager, transaction helper APIs, engine `WriteData`, `KvGenerator`, `txn_types`, and hierarchy engine factories.

## Risks and Test Signals
Engine cloning in setup must preserve intended lock state. Start timestamp differences distinguish conflict/non-conflict cases. Successful runs validate transaction helper and engine write integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/hierarchy/txn/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/memory/mod.rs -->
# sources/storage-engines/tikv/tests/benches/memory/mod.rs

## Purpose
This Criterion benchmark measures TiKV memory quota allocation/free paths in single-threaded and contended multi-threaded scenarios.

## Important APIs, Types, and Functions
`bench_memory_quota_alloc` measures successful and failed `MemoryQuota::alloc`. `bench_memory_quota_alloc_free` compares manual `alloc/free` with RAII `OwnedAllocated`. `bench_memory_quota_multi_threads` runs 32- and 64-thread contention scenarios through `memory_quota_multi_threads`.

## Control Flow
Multi-threaded benchmarks spawn background workers that repeatedly allocate and free quota until an atomic `done` flag is set. The Criterion-measured thread performs the same operations or RAII allocation while workers create contention.

## State and Persistence Behavior
State is in-memory quota counters and worker thread state. No persistence is involved.

## Dependencies and Integration Points
It depends on Criterion macros, `tikv_util::memory::{MemoryQuota, OwnedAllocated}`, atomics, threads, and `black_box`.

## Risks and Test Signals
The fixed 20 ns work-duration estimate and 500 ms check interval are CPU-sensitive. Join handling ensures background workers stop after the group. Useful signals are alloc fail/ok cost and contention scaling.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/memory/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/coprocessor/codec/mod.rs -->
# sources/storage-engines/tikv/tests/benches/misc/coprocessor/codec/mod.rs

## Purpose
This module benchmarks low-level table key prefix checks in TiDB/TiKV codec helpers.

## Important APIs, Types, and Functions
Benchmarks compare `starts_with(TABLE_PREFIX)`, manual first-byte table-prefix checks, `starts_with(RECORD_PREFIX_SEP)`, manual two-byte checks, and big-/little-endian `u16` prefix comparisons.

## Control Flow
Each `#[bench]` performs 1000 repeated checks inside the measured iteration with `black_box` to reduce optimization.

## State and Persistence Behavior
No state beyond fixed byte slices and local prefix values.

## Dependencies and Integration Points
It depends on nightly `test`, `byteorder`, and `tidb_query_datatype::codec::table` constants. It is included by `misc/coprocessor/mod.rs`.

## Risks and Test Signals
The benchmark is micro-architectural and sensitive to compiler optimization. It is a signal for choosing cheap prefix-check idioms, not functional correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/coprocessor/codec/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/coprocessor/codec/mysql/json/mod.rs -->
# sources/storage-engines/tikv/tests/benches/misc/coprocessor/codec/mysql/json/mod.rs

## Purpose
This module benchmarks TiDB JSON binary/text encode and decode paths using a downloaded world-bank JSON corpus.

## Important APIs, Types, and Functions
`download_and_extract_file` streams `curl` output into `tar xzf - --to-stdout` through a helper thread. `load_test_jsons` downloads and splits the corpus into non-empty JSON strings. Ignored benches cover binary encoding with `JsonEncoder`, text encoding through `serde_json`, text parsing into `Json`, and binary decoding with `JsonDecoder`.

## Control Flow
Each ignored bench loads the corpus once, prepares parsed or binary forms as needed, then iterates over every JSON entry inside the measured loop.

## State and Persistence Behavior
State is downloaded data held in memory. No local cache or persistence is implemented.

## Dependencies and Integration Points
It depends on external `curl`/`tar`, network access to PingCAP download resources, `serde_json`, and TiDB JSON codec traits.

## Risks and Test Signals
The benches are ignored because they need network and external tools. Risks include download URL availability, tar format changes, and large memory/time cost. Manual ignored bench runs validate codec performance against a realistic corpus.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/coprocessor/codec/mysql/json/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/coprocessor/codec/mysql/mod.rs -->
# sources/storage-engines/tikv/tests/benches/misc/coprocessor/codec/mysql/mod.rs

## Purpose
This module is a namespace wrapper for MySQL codec microbenchmarks.

## Important APIs, Types, and Functions
It declares `mod json`, exposing the JSON codec benchmark module to the misc benchmark tree.

## Control Flow
There is no runtime control flow beyond module inclusion by the Rust compiler.

## State and Persistence Behavior
No state is owned.

## Dependencies and Integration Points
It is included by `misc/coprocessor/codec/mod.rs` and pulls in `codec/mysql/json/mod.rs`.

## Risks and Test Signals
The main risk is module path drift. Compilation of the misc benchmark confirms inclusion remains valid.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/coprocessor/codec/mysql/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/coprocessor/dag/expr/mod.rs -->
# sources/storage-engines/tikv/tests/benches/misc/coprocessor/dag/expr/mod.rs

## Purpose
This module groups DAG expression microbenchmarks.

## Important APIs, Types, and Functions
It declares `mod scalar`, which contains scalar-function argument lookup benchmarks.

## Control Flow
Runtime behavior is delegated entirely to the scalar child module's `#[bench]` functions.

## State and Persistence Behavior
This wrapper owns no state.

## Dependencies and Integration Points
It is included by `misc/coprocessor/dag/mod.rs`.

## Risks and Test Signals
Only module path validity is at risk here. Misc bench compilation is the signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/coprocessor/dag/expr/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/coprocessor/dag/expr/scalar.rs -->
# sources/storage-engines/tikv/tests/benches/misc/coprocessor/dag/expr/scalar.rs

## Purpose
This microbenchmark compares scalar-function argument-count lookup by `match` versus `HashMap`.

## Important APIs, Types, and Functions
`get_scalar_args_with_match` matches selected `ScalarFuncSig` variants to min/max argument counts. `init_scalar_args_map` builds an equivalent map for selected signatures plus a default-like entry. `get_scalar_args_with_map` looks up values or returns `(0, 0)`. Two `#[bench]` functions call the match or map path 1000 times.

## Control Flow
The map benchmark initializes the map once before iteration. Both benches black-box the signature and result while repeatedly querying `ScalarFuncSig::AbsInt`, which falls through to default in the match path and misses in the map path.

## State and Persistence Behavior
State is an in-memory map for one benchmark. No persistence.

## Dependencies and Integration Points
It depends on TiKV `collections::HashMap`, nightly `test`, and `tipb::ScalarFuncSig`. It informs performance tradeoffs for expression metadata lookup designs.

## Risks and Test Signals
The tested signature set is small and synthetic, so results should not be overgeneralized. Enum evolution may require updating representative cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/coprocessor/dag/expr/scalar.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/coprocessor/dag/mod.rs -->
# sources/storage-engines/tikv/tests/benches/misc/coprocessor/dag/mod.rs

## Purpose
This module is the namespace wrapper for DAG-related misc coprocessor benchmarks.

## Important APIs, Types, and Functions
It declares `mod expr`, which includes expression benchmark modules.

## Control Flow
There is no direct runtime logic in this file.

## State and Persistence Behavior
No state is owned.

## Dependencies and Integration Points
It is included by `misc/coprocessor/mod.rs` and delegates to expression benchmarks.

## Risks and Test Signals
Compilation validates module tree integrity.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/coprocessor/dag/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/coprocessor/mod.rs -->
# sources/storage-engines/tikv/tests/benches/misc/coprocessor/mod.rs

## Purpose
This module groups miscellaneous coprocessor benchmarks under the `misc` bench target.

## Important APIs, Types, and Functions
It declares `mod codec` and `mod dag`.

## Control Flow
Benchmark functions are supplied by child modules. This file only controls module inclusion.

## State and Persistence Behavior
No state is owned.

## Dependencies and Integration Points
It is included by `tests/benches/misc/mod.rs`, making codec and DAG expression microbenchmarks part of the misc target.

## Risks and Test Signals
The file's risk is limited to module path drift. Misc bench compilation confirms correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/coprocessor/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/keybuilder/bench_keybuilder.rs -->
# sources/storage-engines/tikv/tests/benches/misc/keybuilder/bench_keybuilder.rs

## Purpose
This module benchmarks TiKV key construction helper paths.

## Important APIs, Types, and Functions
`gen_rand_str` creates random byte vectors with `thread_rng().fill_bytes`. `bench_key_builder_data_key` measures `keys::data_key` after cloning a 64-byte key. `bench_key_builder_from_slice` measures `KeyBuilder::from_slice`, `set_prefix`, and `build`.

## Control Flow
Each `#[bench]` prepares a random key outside the measured loop, then repeatedly constructs encoded/data keys inside the loop.

## State and Persistence Behavior
State is local random input only. No persistence.

## Dependencies and Integration Points
It depends on nightly `test`, `rand`, `keys::data_key`, and `tikv_util::keybuilder::KeyBuilder`.

## Risks and Test Signals
The benchmark includes allocation/cloning costs in the data-key case. It is a microbenchmark signal for key encoding helper overhead.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/keybuilder/bench_keybuilder.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/keybuilder/mod.rs -->
# sources/storage-engines/tikv/tests/benches/misc/keybuilder/mod.rs

## Purpose
This module groups keybuilder microbenchmarks.

## Important APIs, Types, and Functions
It declares `mod bench_keybuilder`.

## Control Flow
No direct runtime logic exists; child module bench functions are registered by the Rust test harness.

## State and Persistence Behavior
No state is owned.

## Dependencies and Integration Points
It is included by `tests/benches/misc/mod.rs`.

## Risks and Test Signals
Compilation of the misc benchmark target confirms the module path remains valid.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/keybuilder/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/mod.rs -->
# sources/storage-engines/tikv/tests/benches/misc/mod.rs

## Purpose
This is the root for legacy/nightly `test` harness miscellaneous benchmarks.

## Important APIs, Types, and Functions
It enables `#![feature(test)]`, imports `extern crate test`, declares child modules for coprocessor, keybuilder, raftkv, serialization, storage, util, and writebatch, and defines `_bench_check_requirement`.

## Control Flow
The Rust bench harness discovers `#[bench]` functions across this module tree. `_bench_check_requirement` validates the max-open-files requirement through `tikv_util::config::check_max_open_fds(4096)`.

## State and Persistence Behavior
No persistent state is owned by this root. Child benchmarks may create temporary engines or download data.

## Dependencies and Integration Points
It integrates older `test::Bencher` benchmarks that are separate from Criterion-based targets.

## Risks and Test Signals
It requires nightly Rust `test` feature. The open-fds requirement check can fail due to environment configuration rather than code changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/raftkv/mod.rs -->
# sources/storage-engines/tikv/tests/benches/misc/raftkv/mod.rs

## Purpose
This module benchmarks `RaftKv` async snapshot and async write wrapper overhead using a synchronous fake raftstore router.

## Important APIs, Types, and Functions
`SyncBenchRouter` stores a `RocksEngine` and `Region`, implements raftstore router traits, and directly invokes read/write callbacks. `new_engine` creates a temporary RocksDB engine with all CFs. Benchmarks include `bench_async_snapshots_noop`, `bench_async_snapshot`, and `bench_async_write`.

## Control Flow
The router's `invoke` builds a `RaftCmdResponse`, returns a `RegionSnapshot` for read callbacks, or returns a write response with the request command type. `bench_async_snapshots_noop` measures nested callback conversion without `RaftKv`. `bench_async_snapshot` constructs a region/context and calls `RaftKv::async_snapshot`. `bench_async_write` calls `tikv_kv::write` with a delete modify.

## State and Persistence Behavior
Temporary RocksDB engines are created under temp dirs. The fake router avoids real raft persistence/replication; writes are measured as wrapper/future construction through `RaftKv` and callback path rather than real raftstore execution.

## Dependencies and Integration Points
It depends on engine_rocks, engine_traits CF constants, raftstore router traits, `RaftKv`, region snapshot types, `tikv_kv::write`, and transaction key types.

## Risks and Test Signals
Because the router is synchronous and fake, results are lower-bound overhead signals rather than full raftstore performance. Trait implementation drift will show up as compilation failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/raftkv/mod.rs -->
