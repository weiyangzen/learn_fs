# Research: subset-b-008286

Grouped research for `subset-b-008286`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/object_store.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/object_store.rs

## Purpose
This file adapts RustFS erasure-coded object storage to DataFusion's `object_store::ObjectStore` interface for S3 Select reads. It handles object metadata, ranged reads, S3 Select scan ranges, SSE-C read headers, CSV delimiter normalization, JSON DOCUMENT flattening to NDJSON, and test-only helpers for stream conversion.

## Important APIs, Types, And Functions
`EcObjectStore::new` resolves the global `ECStore`, detects multi-byte CSV field delimiters, and records whether JSON DOCUMENT mode needs whole-document flattening. `SelectScanRange` models inclusive S3 Select byte bounds. `scan_range_from_bounds` and `validate_scan_range_bounds` implement AWS-style validation, including suffix semantics for end-only ranges. The `ObjectStore` implementation supports `get_opts` and `get_ranges`; mutation, list, and copy operations intentionally return unsupported errors. `ConvertStream`, `DelimiterConverter`, `convert_field_delimiter_stream`, `scan_range_stream`, `json_document_ndjson_stream`, and `bytes_stream` are the main stream transformation helpers.

## Control Flow
`get_opts` builds `ObjectOptions` from DataFusion get options, loads object size when scan range context is needed, opens an `ECStore` reader with SSE-C headers and optional adjusted range, then selects a payload branch. Head requests return an empty stream. Explicit DataFusion ranges stream exactly the requested byte count. JSON DOCUMENT requests reject objects larger than `MAX_JSON_DOCUMENT_BYTES`, then lazily read the full object and parse in `spawn_blocking`. Scan-range CSV/JSON-line reads rewind by the record delimiter length, optionally prepend the CSV header record, and emit whole records whose start offset falls in the scan range. Multi-byte CSV field delimiters are converted to RustFS/DataFusion's default comma both in full-object and scan-range paths.

## State And Persistence Behavior
The adapter does not persist data. It holds an `Arc<SelectObjectContentInput>` and `Arc<ECStore>`, derives request-local flags, and streams bytes from the backing object. JSON DOCUMENT mode can allocate memory proportional to object size up to the 128 MiB cap. Scan-range state is kept in `ScanRangeState` with current object offset, pending record bytes, and queued output chunks.

## Dependencies And Integration Points
The file integrates `s3s` Select request DTOs, RustFS `ECStore` object readers, DataFusion/object_store abstractions, `tokio_util::ReaderStream`, `serde_json`, HTTP SSE-C headers, and `rustfs_common::DEFAULT_DELIMITER`. It is installed into `SessionCtxFactory` as the object store backing non-test S3 Select queries and is also used by parquet scan-range planning through `SelectScanRange`.

## Risks And Edge Cases
JSON sub-path extraction is a lightweight string parser over the SQL expression, so complex quoting, comments, or nested SQL syntax can diverge from the real SQL parser. JSON DOCUMENT fallback emits the whole root when the requested sub-path is missing, which may surprise callers expecting zero rows. `get_opts` only supports read paths; accidental DataFusion list/copy/delete calls surface as runtime unsupported errors. Scan ranges include records by record-start offset and must keep delimiter rewind logic synchronized with AWS S3 Select expectations. Multi-byte delimiter conversion is byte-based and does not understand CSV quoting. JSON DOCUMENT still buffers the full accepted object.

## Test Signals
The file has unit tests for delimiter replacement across chunks and EOF, scan-range record/header inclusion, multi-byte record delimiters, suffix and invalid scan range validation, bounded DataFusion range conversion, SSE-C header propagation, stream length limiting, JSON DOCUMENT flattening for arrays, objects, empty arrays, pretty JSON, nested values, invalid/empty input, sub-path fallback, and SQL sub-path extraction.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/object_store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/analyzer.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/query/analyzer.rs

## Purpose
This file defines the analyzer abstraction used between logical planning and optimization. It lets implementation crates run DataFusion logical-analysis rules without coupling callers to a concrete analyzer.

## Important APIs, Types, And Functions
`AnalyzerRef` is an `Arc<dyn Analyzer + Send + Sync>`. `Analyzer::analyze(&LogicalPlan, &SessionCtx) -> QueryResult<LogicalPlan>` accepts an immutable DataFusion logical plan and session wrapper and returns an analyzed logical plan.

## Control Flow
There is no local execution logic. Implementors receive the logical plan created by the planner, run their chosen analysis rules, and return a new plan for optimization or execution.

## State And Persistence Behavior
The trait is stateless. State is carried by the concrete implementation and the `SessionCtx`; no persistence or global mutation occurs here.

## Dependencies And Integration Points
The contract depends on DataFusion `LogicalPlan`, the API crate `SessionCtx`, and the crate-wide `QueryResult`. `rustfs-s3select-query/src/sql/analyzer.rs` provides the default implementation backed by DataFusion's analyzer.

## Risks And Edge Cases
Because the trait returns a full logical plan, implementations must preserve schema and table-provider semantics. Analyzer failures propagate as `QueryError` through `QueryResult`.

## Test Signals
No tests are local to this interface file. Coverage comes from the default analyzer and end-to-end query tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/analyzer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/ast.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/query/ast.rs

## Purpose
This file defines the API crate's extensible statement wrapper. It currently wraps DataFusion/sqlparser statements while leaving room for future non-SQL or RustFS-specific commands.

## Important APIs, Types, And Functions
`ExtStatement::SqlStatement(Box<Statement>)` is the only variant. The enum derives debug, clone, equality, and ordering-compatible equality semantics for parser and planner handoff.

## Control Flow
Parser implementations convert SQL text into `ExtStatement` values. Logical planners match the wrapper and translate the contained `Statement` into a DataFusion logical plan.

## State And Persistence Behavior
The enum is an in-memory AST carrier and has no persistent state.

## Dependencies And Integration Points
It depends on DataFusion's re-exported `sqlparser::ast::Statement`. It is consumed by the parser trait and by `LogicalPlanner::create_logical_plan`.

## Risks And Edge Cases
Only SQL is represented today, so any future S3 Select-specific command syntax must add variants and update parser, planner, dispatcher, and tests together.

## Test Signals
Parser tests in `s3select-query/src/sql/parser.rs` validate that normal SQL text produces this wrapper.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/ast.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/dispatcher.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/query/dispatcher.rs

## Purpose
This file defines the high-level query dispatcher contract. It separates database-manager callers from parsing, session creation, logical planning, and execution details.

## Important APIs, Types, And Functions
`QueryDispatcher` is an async trait with `execute_query`, `build_query_state_machine`, `build_logical_plan`, and `execute_logical_plan`. It passes `Query`, `QueryStateMachine`, `Plan`, and `Output` values across the API boundary.

## Control Flow
The intended flow is: build a state machine for the query and session, parse/build a logical plan, execute that plan, and return an `Output`. Implementors may expose the steps separately for callers that need staged execution.

## State And Persistence Behavior
The trait itself stores no state. Concrete dispatchers own reusable parser, factory, function metadata, and table-provider dependencies.

## Dependencies And Integration Points
It depends on the API crate's `Query`, `Output`, `QueryStateMachine`, and `Plan`. `SimpleQueryDispatcher` in `s3select-query` implements the full DataFusion-backed pipeline.

## Risks And Edge Cases
The trait has commented placeholders for query IDs, status, and cancellation, so lifecycle observability is incomplete at the interface level. Implementors must avoid recursive calls between trait and inherent methods with the same name.

## Test Signals
Integration tests exercise staged state-machine, logical-plan, and execute-plan calls through the `DatabaseManagerSystem` wrapper.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/dispatcher.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/execution.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/query/execution.rs

## Purpose
This file defines query execution contracts, query output handling, phase timing metrics, and a lightweight query state machine for S3 Select.

## Important APIs, Types, And Functions
`PhaseTimer` records histogram metrics and debug logs on drop. `QueryType` distinguishes batch and stream execution, although the default is batch. `QueryExecution` exposes `start` and `cancel`. `Output` wraps either `StreamData(SendableRecordBatchStream)` or `Nil(())` and can return a schema, collect batches, expose the stream, count rows, or act as a `Stream<Item = Result<RecordBatch, QueryError>>`. `QueryExecutionFactory` creates executions from `Plan` plus `QueryStateMachineRef`. `QueryStateMachine` stores `SessionCtx`, `Query`, current `QueryState`, and start time, with phase transitions for analyze, optimize, and schedule.

## Control Flow
Execution implementations call `begin_*` and `end_*` methods around phases. `Output::chunk_result` collects DataFusion stream batches and synthesizes an empty batch with the correct schema when no batches arrive. The stream implementation forwards polling to DataFusion for `StreamData` and ends immediately for `Nil`.

## State And Persistence Behavior
State is in memory under a `parking_lot::RwLock`. `finish`, `cancel`, and `fail` only translate the state enum; TODOs indicate missing cleanup or side effects. Metrics record phase durations and timestamps but no durable query history is written.

## Dependencies And Integration Points
The file connects DataFusion Arrow and physical stream types with the RustFS query API. `SqlQueryExecution` implements the trait, and `DatabaseManagerSystem` returns `Output` through `QueryHandle`.

## Risks And Edge Cases
`affected_rows` casts `usize` to `i64`, with a comment noting overflow risk. `num_rows` suppresses collection errors by returning zero. `Output::into_record_batch_stream` rejects `Nil`, so callers need to branch on empty output. State transitions are not validated, so invalid sequences are possible. `finish` is not called by the current query execution path.

## Test Signals
No direct tests are in this file. Integration tests cover output collection, staged execution, limit row counts, and concurrent query execution.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/execution.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/function.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/query/function.rs

## Purpose
This file defines the function metadata manager abstraction used by the SQL planner to resolve scalar, aggregate, and window UDFs.

## Important APIs, Types, And Functions
`FuncMetaManagerRef` is an `Arc<dyn FunctionMetadataManager + Send + Sync>`. `FunctionMetadataManager` supports registering and looking up `ScalarUDF`, `AggregateUDF`, and `WindowUDF`, and listing names for each category.

## Control Flow
Concrete managers receive registrations during setup and are later queried by the metadata provider while DataFusion resolves functions.

## State And Persistence Behavior
The trait has mutating registration methods, but persistence is left to implementations. The default implementation keeps in-memory hash maps.

## Dependencies And Integration Points
It depends on DataFusion UDF types and `QueryResult`. `SimpleFunctionMetadataManager` implements this trait and is injected into `MetadataProvider`.

## Risks And Edge Cases
Lookup semantics, duplicate registration behavior, and case sensitivity are not specified in the trait; implementations must define and test these choices.

## Test Signals
No local tests. Function-manager behavior is covered by its implementation and by query planning failures for unresolved functions.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/function.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/logical_planner.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/query/logical_planner.rs

## Purpose
This file defines logical plan types and the planner trait used to convert parsed statements into executable query plans.

## Important APIs, Types, And Functions
`Plan::Query(QueryPlan)` is the only plan kind. `Plan::schema` exposes the Arrow schema for the underlying DataFusion plan. `QueryPlan` stores `df_plan: DFPlan` and `is_tag_scan`. `QueryPlan::is_explain` detects DataFusion `Explain` and `Analyze` logical plans. `LogicalPlanner::create_logical_plan` is the async planner interface.

## Control Flow
Dispatchers call the planner after parsing. The planner returns a `Plan`, which the execution factory turns into a query execution.

## State And Persistence Behavior
Plans are immutable in-memory values. `is_tag_scan` is metadata for later stages; no persistence happens here.

## Dependencies And Integration Points
It depends on DataFusion logical plan and Arrow schema types, the API `ExtStatement`, and `SessionCtx`. `DefaultLogicalPlanner` in `s3select-query` implements the trait through the generic SQL planner.

## Risks And Edge Cases
The enum currently only supports query plans, so future DDL/control commands require new variants. `Plan::schema` clones the DataFusion schema into a new `Arc`, which is safe but assumes every plan has a valid schema.

## Test Signals
Integration tests build logical plans from state machines and execute them when present.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/logical_planner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/mod.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/query/mod.rs

## Purpose
This module declares the S3 Select query API surface and defines the core `Context` and `Query` values shared by parser, dispatcher, planner, and database-manager layers.

## Important APIs, Types, And Functions
The module exports `analyzer`, `ast`, `dispatcher`, `execution`, `function`, `logical_planner`, `optimizer`, `parser`, `physical_planner`, `scheduler`, and `session`. `Context` wraps `Arc<SelectObjectContentInput>`. `Query` stores a `Context` and SQL content string with `new`, `context`, and `content` accessors.

## Control Flow
Callers construct `Query::new(Context { input }, expression)` and pass it to `DatabaseManagerSystem` or `QueryDispatcher`. The context carries the S3 Select request details needed for object-store registration and table setup.

## State And Persistence Behavior
`Query` and `Context` are cloneable in-memory request descriptors. They do not persist state or own query execution resources.

## Dependencies And Integration Points
This is the package-level query namespace. It depends on `s3s::dto::SelectObjectContentInput` and is used by `RustFSms`, `QueryStateMachine`, `SessionCtxFactory`, tests, and external S3 Select handlers.

## Risks And Edge Cases
The query content is independent from `input.request.expression`; callers must keep them consistent. The context is immutable through `Arc`, but the underlying DTO is cloned in tests and database construction.

## Test Signals
All query integration and error-handling tests construct `Query` and `Context` through this module.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/optimizer.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/query/optimizer.rs

## Purpose
This file defines the optimizer abstraction that converts a logical `QueryPlan` into a DataFusion physical `ExecutionPlan`.

## Important APIs, Types, And Functions
`OptimizerRef` is an `Arc<dyn Optimizer + Send + Sync>`. `Optimizer::optimize(&QueryPlan, &SessionCtx) -> QueryResult<Arc<dyn ExecutionPlan>>` is async and returns the physical plan to schedule.

## Control Flow
`SqlQueryExecution` calls this trait during its optimize phase, then passes the returned physical plan to a scheduler.

## State And Persistence Behavior
The trait is stateless. Concrete optimizers may hold analyzer, logical optimizer, and physical planner components but produce in-memory plans only.

## Dependencies And Integration Points
It depends on DataFusion `ExecutionPlan`, API `QueryPlan`, and `SessionCtx`. `CascadeOptimizer` is the default implementation.

## Risks And Edge Cases
Since optimization is the boundary where logical plans become physical plans, errors include both logical optimizer and physical planner failures. Implementations must respect the `is_explain` path.

## Test Signals
Integration tests indirectly cover this path through normal query execution and explain/invalid-query behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/optimizer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/parser.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/query/parser.rs

## Purpose
This file defines the parser abstraction for turning SQL text into a deque of extended statements.

## Important APIs, Types, And Functions
`Parser::parse(&self, sql: &str) -> QueryResult<VecDeque<ExtStatement>>` is the single trait method. A deque is used so dispatchers can preserve statement order and inspect multi-statement input.

## Control Flow
Dispatchers call the parser before planning. They reject multiple statements and empty statement sets after parsing.

## State And Persistence Behavior
The interface is stateless and has no persistence behavior.

## Dependencies And Integration Points
It depends on `ExtStatement` and `QueryResult`. `DefaultParser` in `s3select-query` implements it with DataFusion/sqlparser plus `RustFsDialect`.

## Risks And Edge Cases
The trait permits multi-statement results, but S3 Select execution rejects them later. Parser implementations should preserve errors precisely enough for S3 API error mapping.

## Test Signals
Parser implementation tests cover simple selects, where clauses, multi-statements, semicolons, and syntax errors.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/parser.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/physical_planner.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/query/physical_planner.rs

## Purpose
This file defines a physical planner abstraction for converting a DataFusion logical plan to a DataFusion physical execution plan.

## Important APIs, Types, And Functions
`PhysicalPlannerRef` is an `Arc<dyn PhysicalPlanner + Send + Sync>`. `PhysicalPlanner::create_physical_plan(&LogicalPlan, &SessionCtx) -> QueryResult<Arc<dyn ExecutionPlan>>` is async, and `inject_physical_transform_rule` lets implementations add DataFusion extension planners.

## Control Flow
The default optimizer stack uses its own physical planner implementation to build the final DataFusion execution plan before scheduling.

## State And Persistence Behavior
This is a stateless interface; implementations produce in-memory execution plans.

## Dependencies And Integration Points
It depends on DataFusion `ExecutionPlan`, API `Plan`, and `SessionCtx`. It is implemented by `DefaultPhysicalPlanner` in the query crate.

## Risks And Edge Cases
The abstraction works below the API `Plan` layer: callers must extract or produce a DataFusion `LogicalPlan` before invoking it. Future custom logical extension nodes require matching physical extension planners.

## Test Signals
No local tests. End-to-end query execution verifies physical planning indirectly.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/physical_planner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/scheduler.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/query/scheduler.rs

## Purpose
This file defines the scheduling contract for running a DataFusion physical plan and returning a record-batch stream.

## Important APIs, Types, And Functions
`SchedulerRef` is an `Arc<dyn Scheduler + Send + Sync>`. `Scheduler::schedule(plan, task_context)` returns `ExecutionResults`. `ExecutionResults` wraps `SendableRecordBatchStream` and exposes it through `stream(self)`.

## Control Flow
`SqlQueryExecution` calls the scheduler after optimization, passing the plan and the session task context. The local scheduler delegates to DataFusion's `execute_stream`.

## State And Persistence Behavior
The scheduler interface is stateless; actual runtime state is in DataFusion's task context and stream.

## Dependencies And Integration Points
It depends on DataFusion `TaskContext`, `ExecutionPlan`, `SendableRecordBatchStream`, and DataFusion error results. `LocalScheduler` implements it for single-process execution.

## Risks And Edge Cases
Schedulers must manage stream ownership and cancellation carefully. This abstraction does not expose queueing, resource admission, or distributed scheduling metadata.

## Test Signals
Integration tests exercise scheduling through real query execution and concurrent query cases.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/scheduler.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/session.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/query/session.rs

## Purpose
This file builds the DataFusion session state used by S3 Select queries. It registers an object store for the target bucket and provides an in-memory test store with CSV, JSON, and parquet fixtures.

## Important APIs, Types, And Functions
`SessionCtx` wraps a DataFusion `SessionState` and exposes `inner()`. `SessionCtxFactory` has `is_test` and `create_session_ctx`. `build_df_session_context` constructs a runtime environment, default DataFusion features, and an object store for `s3://<bucket>`. Test mode uses `build_in_mem_store`; production mode uses `EcObjectStore::new`. Fixture helpers include `test_parquet_bytes` and `test_parquet_batch`.

## Control Flow
Session creation parses a bucket URL, builds `RuntimeEnv`, creates `SessionStateBuilder`, registers either `InMemory` or `EcObjectStore` under that URL, and returns the session state. Test store population writes `test.csv`, `test.json`, `test.jsonl`, and `test.parquet` into memory; errors are logged but the store is still returned.

## State And Persistence Behavior
Session state is per query and in memory. Production sessions reference the shared global `ECStore` through `EcObjectStore`. Test mode persists fixture bytes only in the `InMemory` object store for that session.

## Dependencies And Integration Points
It integrates DataFusion session/runtime APIs, object_store registration, Arrow/parquet writer APIs, `s3s` request context, and the `EcObjectStore` adapter. `SimpleQueryDispatcher` obtains sessions through this factory.

## Risks And Edge Cases
`Url::parse` unwraps the constructed bucket URL. Test store fixture writes log errors instead of failing session creation, so broken fixtures may surface later as schema/read errors. Production session creation depends on the global `ECStore` being initialized. Fixture names must match test input keys and listing extensions.

## Test Signals
The file embeds fixture-generation code rather than unit tests. Query crate integration tests rely on test sessions for CSV, JSON DOCUMENT, JSON LINES, parquet, scan-range, and concurrent query coverage.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/query/session.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/server/dbms.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/server/dbms.rs

## Purpose
This file defines the database-manager API that external S3 Select handlers use to execute queries or drive the query pipeline in stages.

## Important APIs, Types, And Functions
`QueryHandle` stores the original `Query` and `Output`, with `new`, `query`, and consuming `result` accessors. `DatabaseManagerSystem` is an async trait exposing `execute`, `build_query_state_machine`, `build_logical_plan`, and `execute_logical_plan`.

## Control Flow
`execute` is the one-shot path. The other methods support staged execution where callers can create a state machine, inspect or transform the logical plan, then execute it.

## State And Persistence Behavior
`QueryHandle` owns an in-memory output stream; consuming `result` transfers stream ownership. No persistent query catalog or status store exists.

## Dependencies And Integration Points
The trait depends on API `Query`, `Output`, `QueryStateMachineRef`, and `Plan`. `RustFSms` implements it by delegating to `QueryDispatcher`.

## Risks And Edge Cases
Since `QueryHandle::result` consumes the handle, callers cannot read output twice. The trait does not define cancellation or query status despite the lower-level execution contract having `cancel`.

## Test Signals
Integration tests create global/fresh databases, call `execute`, and exercise staged state-machine/logical-plan/execute-plan calls.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/server/dbms.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/server/mod.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/server/mod.rs

## Purpose
This module exposes the server-facing database manager namespace for the API crate.

## Important APIs, Types, And Functions
It declares `pub mod dbms;`, making `DatabaseManagerSystem` and `QueryHandle` available as `server::dbms`.

## Control Flow
No local logic exists. It is a namespace boundary.

## State And Persistence Behavior
No state is held or persisted.

## Dependencies And Integration Points
Consumers import `rustfs_s3select_api::server::dbms` from here. `rustfs-s3select-query` implements the exported trait.

## Risks And Edge Cases
Any future server modules must be explicitly exported here.

## Test Signals
No local tests; all DBMS tests go through the query crate.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/server/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/test/mod.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/test/mod.rs

## Purpose
This test module exposes API-crate query execution tests.

## Important APIs, Types, And Functions
It declares `pub mod query_execution_test;` under test configuration.

## Control Flow
Rust's test harness discovers the child test module when crate tests are compiled.

## State And Persistence Behavior
No runtime state is local to this module.

## Dependencies And Integration Points
It integrates the API crate's tests with Cargo's test module tree.

## Risks And Edge Cases
Only modules listed here are included. Adding new test files requires updating this mod file.

## Test Signals
The presence of `query_execution_test` links the API-level `Output` behavior tests into the suite.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/test/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/test/query_execution_test.rs -->
# sources/object-store/rustfs/crates/s3select-api/src/test/query_execution_test.rs

## Purpose
This file tests the API crate's query output and state-machine primitives independently from the full DataFusion-backed query implementation.

## Important APIs, Types, And Functions
The tests construct `Query`, `Context`, `QueryStateMachine`, and `Output` values. They verify `QueryStateMachine::begin`, phase transition methods, `cancel`, `fail`, `duration`, `QueryType` display, `Output::Nil`, and collecting stream output.

## Control Flow
Tests build a synthetic `SelectObjectContentInput`, create queries and state machines, advance phases, and assert `QueryState` strings. Stream-output tests create empty or simple record-batch streams and call `chunk_result`, `schema`, `num_rows`, and `affected_rows`.

## State And Persistence Behavior
All state is in memory. The tests verify that state transitions mutate the `RwLock` state and that output collection consumes the stream.

## Dependencies And Integration Points
The file uses Arrow record batches, futures streams, DataFusion physical stream types, and the API crate query modules. It is registered through `src/test/mod.rs`.

## Risks And Edge Cases
The tests focus on happy-path state transitions and output counts. They do not enforce invalid transition rejection, finish behavior in real execution, or cancellation of active DataFusion streams.

## Test Signals
This is itself the test signal for API primitives. It gives confidence that `Output::Nil` and stream collection behave predictably and that state names remain stable.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-api/src/test/query_execution_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/Cargo.toml -->
# sources/object-store/rustfs/crates/s3select-query/Cargo.toml

## Purpose
This manifest defines the `rustfs-s3select-query` crate, the DataFusion-backed S3 Select query engine implementation for RustFS.

## Important APIs, Types, And Functions
Package metadata identifies the crate, workspace versioning, Rust edition, license, docs URL, keywords, and categories. Dependencies include `rustfs-s3select-api`, `datafusion`, `async-trait`, `async-recursion`, `derive_builder`, `futures`, `parking_lot`, `s3s`, `snafu` with backtraces, `tokio`, and `tracing`. The `[lib]` section disables doctests.

## Control Flow
Cargo uses this file to compile the query engine and its test modules. Workspace dependencies keep versions aligned with the larger RustFS tree.

## State And Persistence Behavior
No runtime state exists in the manifest. Build-time state is derived from workspace dependency resolution.

## Dependencies And Integration Points
The crate depends on the API crate for contracts and on DataFusion for SQL planning/execution. `s3s` supplies Select request DTOs; `tokio` and `futures` support async execution.

## Risks And Edge Cases
Disabling doctests avoids documentation test failures but can hide stale examples. DataFusion version changes are high impact because parser, planner, table-provider, and physical-plan APIs are used directly.

## Test Signals
Cargo will include the unit and integration tests under `src/test` and inline module tests when this crate is tested.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/data_source/mod.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/data_source/mod.rs

## Purpose
This module exposes data-source adapters used by the query engine.

## Important APIs, Types, And Functions
It declares `pub mod table_source;`, exporting `TableSourceAdapter`, `TableHandle`, and related table-source functionality.

## Control Flow
No local control flow exists. Consumers use this module path to build metadata table sources.

## State And Persistence Behavior
No local state or persistence.

## Dependencies And Integration Points
`metadata` depends on `data_source::table_source` to expose registered table providers to DataFusion's planner.

## Risks And Edge Cases
Additional data-source modules must be exported here.

## Test Signals
No local tests; table-source behavior is exercised by metadata/planner integration.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/data_source/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/data_source/table_source.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/data_source/table_source.rs

## Purpose
This file adapts DataFusion `TableProvider` instances into planner-visible table sources with stable table names and logical plans.

## Important APIs, Types, And Functions
`TEMP_LOCATION_TABLE_NAME` is the synthetic name used for the current S3 object. `TableSourceAdapter::try_new` builds a logical scan plan from a table reference and provider. Accessors expose database name, table name, table handle, plan, schema, and filter pushdown. `TableHandle` wraps an `Arc<dyn TableProvider>`.

## Control Flow
`try_new` converts the provider to a `TableSource`. If the source exposes a logical plan, it uses that; otherwise it builds a scan through `LogicalPlanBuilder::scan`. Metadata providers later return the adapter as a `TableSource` to DataFusion SQL planning.

## State And Persistence Behavior
The adapter stores only in-memory provider handles and the derived logical plan. It does not persist metadata.

## Dependencies And Integration Points
It integrates DataFusion `TableProvider`, `TableSource`, `LogicalPlanBuilder`, filter pushdown, schemas, and table references. `MetadataProvider` uses it to resolve `S3Object` and aliases.

## Risks And Edge Cases
The database name is hard-coded to `default_db`. Filter pushdown relies on the underlying provider and may differ across CSV/JSON listing tables and parquet custom tables. Logical-plan caching means provider changes after adapter creation are not reflected.

## Test Signals
No direct tests. Planner and integration tests exercise it by resolving `S3Object` scans.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/data_source/table_source.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/dispatcher/manager.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/dispatcher/manager.rs

## Purpose
This file implements the default query dispatcher. It creates sessions, registers the current object as a DataFusion table, parses SQL, rejects unsupported multi-statement/empty input, builds logical plans, and executes them through the execution factory.

## Important APIs, Types, And Functions
`SimpleQueryDispatcher` owns the request input, session factory, parser, execution factory, function manager, and table provider. Its `QueryDispatcher` implementation exposes one-shot and staged execution. `build_scheme_provider` creates either a `ParquetSelectTable` or a DataFusion `ListingTable` for CSV/JSON. `TrackedRecordBatchStream` wraps output streams. `SimpleQueryDispatcherBuilder` validates required dependencies and returns an `Arc<SimpleQueryDispatcher>`.

## Control Flow
`execute_query` builds a state machine, builds a logical plan, returns `Nil` for absent plans, then executes. `build_logical_plan` builds metadata, parses statements, rejects more than one statement and empty SQL, and delegates to `DefaultLogicalPlanner`. CSV setup maps S3 `FileHeaderInfo`: `USE` keeps headers, `IGNORE` treats the first row as headers but renames columns to `_1`, `_2`, and `NONE` sets no header and renames DataFusion `column_N` fields to `_N`. JSON uses the actual key extension, defaulting to `.json`. Parquet uses the custom table provider so scan ranges can prune row groups.

## State And Persistence Behavior
The dispatcher is request-scoped but can share parser/function/execution components. It builds per-query sessions and metadata providers. No durable query state is stored; state-machine transitions and metrics are in memory.

## Dependencies And Integration Points
It integrates API dispatcher traits, DataFusion listing CSV/JSON formats, parquet table provider, `MetadataProvider`, `BaseTableProvider`, parser, logical planner, execution factory, and S3 Select input serialization options.

## Risks And Edge Cases
The trait method `execute_logical_plan` calls the inherent method with the same name; resolution must remain to the inherent method to avoid recursion. CSV `FileHeaderInfo` must be present or the dispatcher returns not implemented. Only the first byte of comment, escape, quote, and one-byte delimiters is used by DataFusion; multi-byte field delimiters rely on `EcObjectStore` conversion. The default table-provider field is stored but a fresh `BaseTableProvider` is built in `build_table_handle_provider`, so injected provider state is not used there.

## Test Signals
Integration tests cover database creation, simple select, where, order, limit, staged state-machine execution, concurrent queries, JSON, parquet, and scan-range cases. Error tests cover syntax errors, multi-statement rejection, unsupported operations, empty SQL, and complex invalid queries.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/dispatcher/manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/dispatcher/mod.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/dispatcher/mod.rs

## Purpose
This module declares dispatcher submodules.

## Important APIs, Types, And Functions
It exports `pub mod manager` and keeps `parquet_table` private to the dispatcher implementation.

## Control Flow
No local logic exists. Consumers use `dispatcher::manager` for `SimpleQueryDispatcher`.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
The private parquet table module is used by `manager` to support S3 Select parquet inputs.

## Risks And Edge Cases
External callers cannot use `ParquetSelectTable` directly because the module is private; this keeps surface area small but limits reuse.

## Test Signals
No local tests. Dispatcher behavior is covered in manager and integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/dispatcher/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/dispatcher/parquet_table.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/dispatcher/parquet_table.rs

## Purpose
This file implements a custom DataFusion `TableProvider` for a single parquet S3 Select object. It reads parquet metadata from the registered object store, exposes the file schema, and applies S3 Select scan ranges as parquet row-group access plans.

## Important APIs, Types, And Functions
`ParquetSelectTable` stores schema, object-store URL, object path, object size, and optional `ParquetAccessPlan`. `try_new` locates the object store, reads metadata with `ParquetObjectReader`, computes scan-range access, and constructs the provider. The `TableProvider` implementation returns `Base` table type, schema, exact filter pushdown, and a `DataSourceExec` built from `FileScanConfigBuilder` and `ParquetSource`. Helpers include `parquet_access_plan`, `access_plan_for_scan_range`, `row_group_start_offset`, and `non_negative_offset`.

## Control Flow
Construction parses `s3://bucket/key`, fetches object metadata, reads parquet footer metadata, computes a scan range from S3 bounds and object size, then builds an access plan that skips row groups whose starting byte offset falls outside the inclusive range. During scan, it creates one `PartitionedFile` with file size and parquet source, attaching the access plan when present.

## State And Persistence Behavior
The table provider is immutable and in memory. It reads object metadata and parquet footer data but does not persist anything.

## Dependencies And Integration Points
It integrates DataFusion catalog/session, object-store registry, parquet async reader, physical file scan config, `ParquetAccessPlan`, and API scan-range validation from `object_store.rs`. It is selected by `SimpleQueryDispatcher` when input serialization is parquet.

## Risks And Edge Cases
Row-group filtering is based on row-group start offset only, so row groups that overlap a range but start before it are skipped. Row groups with negative or missing file offsets are excluded. Scan-range validation errors are mapped into query store errors. Projection, limit, and filter pushdown rely on DataFusion after the file source is built.

## Test Signals
Inline tests cover access-plan construction and row-group offset handling. Integration tests verify parquet simple select, a tiny scan range returning zero rows, and a larger range returning all fixture rows.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/dispatcher/parquet_table.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/execution/factory.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/execution/factory.rs

## Purpose
This file implements the execution factory that turns API logical plans into concrete SQL query executions.

## Important APIs, Types, And Functions
`QueryExecutionFactoryRef` is an `Arc<dyn QueryExecutionFactory + Send + Sync>`. `SqlQueryExecutionFactory` stores an optimizer and scheduler. `new` constructs it, and the `QueryExecutionFactory` implementation returns `SqlQueryExecution` for `Plan::Query`.

## Control Flow
The dispatcher asks the factory to create an execution after logical planning. The factory pattern-matches the plan enum and injects the shared optimizer and scheduler.

## State And Persistence Behavior
The factory is immutable and shares `Arc` dependencies. It does not persist state.

## Dependencies And Integration Points
It depends on API execution/planner/optimizer/scheduler traits and the local `SqlQueryExecution`.

## Risks And Edge Cases
Only `Plan::Query` is supported. New plan variants require updating this factory or they will be unhandled at compile time.

## Test Signals
Covered indirectly by all successful query execution tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/execution/factory.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/execution/mod.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/execution/mod.rs

## Purpose
This module declares query execution submodules.

## Important APIs, Types, And Functions
It exports `factory`, `query`, and `scheduler`.

## Control Flow
No local logic exists. It is the namespace for concrete execution components.

## State And Persistence Behavior
No local state or persistence.

## Dependencies And Integration Points
`instance` and dispatcher code import execution factory and local scheduler through this module.

## Risks And Edge Cases
New scheduler or execution variants must be exported here.

## Test Signals
No direct tests; execution is covered by integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/execution/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/execution/query.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/execution/query.rs

## Purpose
This file implements SQL query execution: optimize a logical query plan, schedule the resulting physical plan, and expose the DataFusion record-batch stream.

## Important APIs, Types, And Functions
`SqlQueryExecution` stores the state machine, `QueryPlan`, optimizer, scheduler, and an optional `AbortHandle`. Its inherent `start` performs optimization and scheduling. The `QueryExecution` trait implementation wraps that future in `futures::future::abortable` and exposes `cancel`.

## Control Flow
Execution starts by timing and marking the optimize phase, calls `optimizer.optimize`, then times and marks the schedule phase, calls `scheduler.schedule`, and returns `Output::StreamData`. The trait `start` stores the abort handle before awaiting. `cancel` marks the state machine cancelled and aborts the stored future if present.

## State And Persistence Behavior
Cancellation state is held in a `parking_lot::Mutex<Option<AbortHandle>>`; query phase state is in `QueryStateMachine`. No durable state is written.

## Dependencies And Integration Points
It connects API `QueryExecution`, `Optimizer`, `Scheduler`, `Output`, and `QueryStateMachine` with the concrete query crate optimizer and scheduler.

## Risks And Edge Cases
The abort handle only cancels the future up to stream creation; after `start` returns a stream, later stream polling is not tied to this handle. `finish` and `fail` are not called on success or error. Cloning the physical plan before scheduling may be unnecessary but harmless with `Arc`.

## Test Signals
Integration tests exercise normal execution, concurrent starts, and staged execution. There are no focused cancellation tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/execution/query.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/execution/scheduler/local.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/execution/scheduler/local.rs

## Purpose
This file implements the local in-process scheduler for DataFusion execution plans.

## Important APIs, Types, And Functions
`LocalScheduler` implements API `Scheduler`. `schedule(plan, context)` calls DataFusion `execute_stream` and wraps the resulting stream in `ExecutionResults`.

## Control Flow
There is a single path: DataFusion executes the physical plan with the provided task context, and the stream is returned to the query execution layer.

## State And Persistence Behavior
The scheduler is stateless. Execution state lives in DataFusion's stream and task context.

## Dependencies And Integration Points
It depends on DataFusion `ExecutionPlan`, `TaskContext`, and `execute_stream`, plus API scheduler types. It is constructed in `instance` and the global component cache.

## Risks And Edge Cases
There is no admission control, parallelism tuning, distributed execution, or cancellation wrapper here. Errors from `execute_stream` propagate as DataFusion errors.

## Test Signals
All successful integration tests use this scheduler.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/execution/scheduler/local.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/execution/scheduler/mod.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/execution/scheduler/mod.rs

## Purpose
This module exposes execution scheduler implementations.

## Important APIs, Types, And Functions
It declares `pub mod local;`.

## Control Flow
No local logic.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
`LocalScheduler` is imported by `instance` and `lib` global component setup.

## Risks And Edge Cases
Future schedulers require exports here.

## Test Signals
No local tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/execution/scheduler/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/function/mod.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/function/mod.rs

## Purpose
This module exposes function metadata manager implementations.

## Important APIs, Types, And Functions
It declares `pub mod simple_func_manager;`.

## Control Flow
No local logic.

## State And Persistence Behavior
No local state or persistence.

## Dependencies And Integration Points
`SimpleFunctionMetadataManager` is used by `instance`, `lib`, and `MetadataProvider` to resolve UDFs.

## Risks And Edge Cases
New function managers must be exported here.

## Test Signals
No local tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/function/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/function/simple_func_manager.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/function/simple_func_manager.rs

## Purpose
This file implements an in-memory function metadata manager for DataFusion scalar, aggregate, and window UDFs.

## Important APIs, Types, And Functions
`SimpleFunctionMetadataManager` stores three `HashMap<String, Arc<...>>` collections for scalar, aggregate, and window UDFs. `Default` seeds the maps from DataFusion `SessionStateDefaults`. The trait implementation registers functions by name, resolves names, and returns name lists.

## Control Flow
Construction loads DataFusion built-ins/defaults, logging counts. Registration inserts by function name. Lookup returns a cloned `Arc` or a `QueryError::Datafusion`/lookup-style error when missing, depending on helper path.

## State And Persistence Behavior
All function metadata is in memory. The global DB path reuses a single `Arc<SimpleFunctionMetadataManager>`; fresh DB creation builds a new manager.

## Dependencies And Integration Points
It depends on DataFusion UDF types and default function registries, API `FunctionMetadataManager`, and `QueryError`. `MetadataProvider` calls it for UDF lookup.

## Risks And Edge Cases
The manager is not internally synchronized for mutation after sharing as an `Arc`; registrations require `&mut self`, so runtime mutation is effectively setup-only. Duplicate names overwrite prior entries. Name matching is exact and may be case-sensitive relative to SQL normalization.

## Test Signals
No local tests. Function resolution is indirectly tested through successful built-in SQL queries and unresolved-function error cases.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/function/simple_func_manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/instance.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/instance.rs

## Purpose
This file assembles a RustFS S3 Select database instance from dispatcher, session, parser, function manager, optimizer, scheduler, execution factory, and table provider components.

## Important APIs, Types, And Functions
`RustFSms<D>` stores an `Arc<D: QueryDispatcher>` and implements `DatabaseManagerSystem`. `make_rustfsms` constructs fresh default components. `make_rustfsms_with_components` accepts shared cached components. Inline ignored tests demonstrate simple SQL and custom delimiter use against the global DB.

## Control Flow
The DBMS implementation delegates `execute`, `build_query_state_machine`, `build_logical_plan`, and `execute_logical_plan` to the dispatcher, wrapping outputs in `QueryHandle`. Construction builds `SessionCtxFactory`, `DefaultParser`, `CascadeOptimizer`, `LocalScheduler`, `SqlQueryExecutionFactory`, `BaseTableProvider`, then uses `SimpleQueryDispatcherBuilder` and `RustFSmsBuilder`.

## State And Persistence Behavior
Instances hold in-memory component Arcs. `make_rustfsms` creates new components; `make_rustfsms_with_components` reuses shared parser/function/execution/table-provider state. No durable state is stored.

## Dependencies And Integration Points
It connects the API `DatabaseManagerSystem` trait with the concrete query crate implementation. `lib.rs` calls `make_rustfsms_with_components` for cached global DB creation.

## Risks And Edge Cases
Builder `.expect("build db server")` can panic if the builder state is inconsistent, although required fields are set immediately before. The `is_test` flag controls whether sessions use in-memory fixtures or production `ECStore`. Ignored tests rely on fixture formatting and are not run by default.

## Test Signals
Integration tests cover database creation through both `make_rustfsms` and `get_global_db`, plus fresh DB creation. Inline tests are ignored but document expected CSV result shape and multi-byte delimiter behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/instance.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/lib.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/lib.rs

## Purpose
This is the query crate root. It exports submodules and provides public helpers for creating global cached or fresh S3 Select database instances.

## Important APIs, Types, And Functions
It exports `data_source`, `dispatcher`, `execution`, `function`, `instance`, `metadata`, and `sql`. `GlobalComponents` caches the function manager, parser, execution factory, and default table provider in a `LazyLock`. `get_global_db(input, enable_debug)` creates a DBMS using cached components. `create_fresh_db()` creates a test DBMS with a default CSV Select input.

## Control Flow
The global cache initializes default function manager, parser, cascade optimizer, local scheduler, execution factory, and table provider once. Each `get_global_db` call passes the request input and cached components to `make_rustfsms_with_components`.

## State And Persistence Behavior
Global state is process-local and immutable after `LazyLock` initialization. Per-request DB instances are still constructed, but expensive reusable components are shared. No durable state is written.

## Dependencies And Integration Points
It is the public entry point used by S3 Select handlers and tests. It depends on API `DatabaseManagerSystem`, `SelectObjectContentInput`, the local component implementations, and `std::sync::LazyLock`.

## Risks And Edge Cases
`enable_debug` is passed as `is_test`, so naming can be misleading: true selects in-memory fixtures instead of production storage. Shared function manager state is immutable through `Arc`; dynamic UDF registration after startup is not supported by this path.

## Test Signals
Integration and error-handling tests use `get_global_db` extensively and `create_fresh_db` for fresh instance creation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/metadata/base_table.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/metadata/base_table.rs

## Purpose
This file implements a simple table-handle provider for resolving a default table provider from a `TableHandle`.

## Important APIs, Types, And Functions
`BaseTableProvider` is a zero-field default struct implementing `TableHandleProvider`. `build_table_handle(Arc<dyn TableProvider>) -> DFResult<TableHandle>` wraps a provider in a `TableHandle`.

## Control Flow
The method wraps the passed provider without additional lookup or authorization logic.

## State And Persistence Behavior
The provider is stateless and performs no persistence.

## Dependencies And Integration Points
It depends on DataFusion `TableProvider` and local `TableHandle`. `MetadataProvider` uses this interface to turn table handles into planner sources.

## Risks And Edge Cases
This provider does not maintain a catalog, so all table resolution must already have produced a valid `TableHandle`. Any future multi-table support needs a richer provider.

## Test Signals
Covered indirectly by all planner tests that resolve `S3Object`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/metadata/base_table.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/metadata/mod.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/metadata/mod.rs

## Purpose
This file implements the DataFusion `ContextProvider` used by SQL planning. It resolves S3 Select table references, function metadata, variables, and session configuration.

## Important APIs, Types, And Functions
`ContextProviderExtension` extends DataFusion `ContextProvider` with async `get_table_source`. `TableHandleProvider` abstracts table-provider retrieval. `MetadataProvider` stores the current object provider, a table-handle provider, a function manager, and session. `new` constructs it. Context-provider methods include table source lookup, function lookup, aggregate/window lookup, variable type resolution, options, and UDF listing.

## Control Flow
When the planner asks for a table, `get_table_source` checks for `S3Object`/temporary table references and builds a `TableSourceAdapter` around the current object provider. Function methods delegate to `FunctionMetadataManager`. Variable and config methods defer to DataFusion session/config behavior where supported.

## State And Persistence Behavior
The provider is per logical-planning operation and holds in-memory Arcs. It does not persist metadata or query state.

## Dependencies And Integration Points
It integrates DataFusion SQL planner traits, table-provider adapters, `BaseTableProvider`, `FuncMetaManagerRef`, DataFusion variable types, and API `SessionCtx`. It is built by `SimpleQueryDispatcher`.

## Risks And Edge Cases
Only the current S3 object table is supported. System variable handling is minimal. Table-reference matching must handle aliases and exact names consistently with `SqlPlanner`. Function lookup errors propagate through DataFusion planning.

## Test Signals
Integration tests exercise table resolution for `S3Object`, aliases, filters, order, grouping, JSON, CSV, and parquet.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/metadata/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/analyzer.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/sql/analyzer.rs

## Purpose
This file provides the default logical analyzer implementation backed by DataFusion's analyzer.

## Important APIs, Types, And Functions
`DefaultAnalyzer` wraps `datafusion::optimizer::analyzer::Analyzer`. `new` and `Default` create it with DataFusion defaults. The API `Analyzer` implementation calls `execute_and_check`.

## Control Flow
`analyze` clones the logical plan, runs DataFusion analyzer rules with session config options and an empty observer callback, then returns the analyzed plan.

## State And Persistence Behavior
The analyzer holds DataFusion analyzer state/rules in memory and persists nothing.

## Dependencies And Integration Points
It depends on API `Analyzer`, `SessionCtx`, and DataFusion logical analyzer APIs. It is used by `CascadeOptimizer`.

## Risks And Edge Cases
Analyzer behavior follows DataFusion version semantics. Custom analyzer rules are not added yet despite the extension comment.

## Test Signals
Covered indirectly by optimizer and query execution tests, especially invalid column/function cases.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/analyzer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/dialect.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/sql/dialect.rs

## Purpose
This file defines the SQL dialect accepted by the RustFS S3 Select parser.

## Important APIs, Types, And Functions
`RustFsDialect` implements `sqlparser::Dialect`. Identifier starts may be alphabetic, `_`, `#`, or `@`. Identifier parts may also include ASCII digits, `$`, `#`, `_`, and `@`. `supports_group_by_expr` returns true.

## Control Flow
The parser passes this dialect to DataFusion/sqlparser tokenization and parsing, allowing S3 Select-style pseudo columns such as `_1` and special identifier prefixes.

## State And Persistence Behavior
The dialect is zero-sized and stateless.

## Dependencies And Integration Points
It depends on DataFusion's sqlparser dialect trait and is used by `ExtParser::parse_sql`.

## Risks And Edge Cases
The dialect allows broad Unicode alphabetic starts but only ASCII digits in identifier parts. `$` is allowed after the first character but not at the start. Changes can break CSV header aliases and parser compatibility.

## Test Signals
Extensive unit tests cover construction, debug output, valid/invalid identifier starts and parts, Unicode letters, control characters, digit handling, consistency, memory size, and trait behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/dialect.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/logical/mod.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/sql/logical/mod.rs

## Purpose
This module exposes logical SQL planner and optimizer components.

## Important APIs, Types, And Functions
It declares `pub mod optimizer;` and `pub mod planner;`.

## Control Flow
No local logic.

## State And Persistence Behavior
No local state or persistence.

## Dependencies And Integration Points
`CascadeOptimizer` and dispatcher planning import logical components from here.

## Risks And Edge Cases
Future logical stages must be exported here.

## Test Signals
No local tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/logical/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/logical/optimizer.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/sql/logical/optimizer.rs

## Purpose
This file implements logical optimization using DataFusion's optimizer rules.

## Important APIs, Types, And Functions
`DefaultLogicalOptimizer` wraps DataFusion `Optimizer`. `new` builds it with default rules. The API `LogicalOptimizer` implementation optimizes a `QueryPlan` using session state and returns a new `QueryPlan`.

## Control Flow
The optimizer calls DataFusion `optimize` against the plan's `df_plan` and session state/config, preserving `is_tag_scan` in the returned `QueryPlan`.

## State And Persistence Behavior
The optimizer holds rule state in memory only. It produces immutable logical plans.

## Dependencies And Integration Points
It depends on DataFusion optimizer APIs and API `QueryPlan`/`SessionCtx`. `CascadeOptimizer` runs it after analysis and before physical planning.

## Risks And Edge Cases
Logical optimizer behavior is tightly coupled to DataFusion version and may rewrite scans/filters in ways that interact with custom parquet access planning. `is_tag_scan` is only preserved, not interpreted.

## Test Signals
Covered indirectly through query execution tests and DataFusion plan success/failure.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/logical/optimizer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/logical/planner.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/sql/logical/planner.rs

## Purpose
This file provides the default logical planner type alias/wrapper for SQL statements.

## Important APIs, Types, And Functions
`DefaultLogicalPlanner<'a, S>` wraps or aliases the generic `SqlPlanner<'a, S>` from `sql/planner.rs` for a `ContextProviderExtension`.

## Control Flow
The dispatcher constructs this planner with a `MetadataProvider`, then calls `create_logical_plan`.

## State And Persistence Behavior
Planner state is borrowed metadata context only; no persistence.

## Dependencies And Integration Points
It depends on the generic SQL planner and metadata provider extension trait.

## Risks And Edge Cases
This thin layer inherits all SQL planner limitations. Type aliases/wrappers must remain synchronized with `SqlPlanner` generics.

## Test Signals
Covered by parser/planner integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/logical/planner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/mod.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/sql/mod.rs

## Purpose
This module exports the SQL stack for the query crate.

## Important APIs, Types, And Functions
It declares `analyzer`, `dialect`, `logical`, `optimizer`, `parser`, `physical`, and `planner`.

## Control Flow
No local logic.

## State And Persistence Behavior
No local state or persistence.

## Dependencies And Integration Points
The dispatcher, instance construction, and optimizer import SQL components through this namespace.

## Risks And Edge Cases
Adding SQL pipeline stages requires updating this module.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/optimizer.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/sql/optimizer.rs

## Purpose
This file implements the cascade optimizer that turns a logical query plan into a physical execution plan by composing analysis, logical optimization, and physical planning.

## Important APIs, Types, And Functions
`CascadeOptimizer` stores an analyzer, logical optimizer, and physical planner. It implements API `Optimizer`. `CascadeOptimizerBuilder` constructs the default stack from `DefaultAnalyzer`, `DefaultLogicalOptimizer`, and `DefaultPhysicalPlanner`.

## Control Flow
`optimize` logs the input logical plan, runs analysis, wraps the analyzed plan back into `QueryPlan`, runs logical optimization, then calls the physical planner. Explain/analyze plans are detected to avoid inappropriate optimizer behavior where needed by the implementation.

## State And Persistence Behavior
The optimizer stack is shared in memory and produces plans only. It writes no durable state.

## Dependencies And Integration Points
It integrates API optimizer contracts with local analyzer, logical optimizer, and physical planner implementations. `SqlQueryExecutionFactory` receives it from `instance` or the global cache.

## Risks And Edge Cases
DataFusion optimizer/planner errors propagate to query execution. Explain/analyze handling must remain aligned with DataFusion logical-plan variants. Debug logging can expose query plans and schemas.

## Test Signals
End-to-end CSV, JSON, parquet, filter, aggregation, order, limit, invalid SQL, and invalid function tests exercise this optimizer path.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/optimizer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/parser.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/sql/parser.rs

## Purpose
This file implements SQL parsing for RustFS S3 Select using DataFusion/sqlparser with `RustFsDialect`.

## Important APIs, Types, And Functions
`DefaultParser` implements the API `Parser` trait. `ExtParser` wraps `sqlparser::Parser`. `parse_sql` uses `RustFsDialect`; `parse_sql_with_dialect` tokenizes SQL, ignores empty semicolon-separated statements, parses statements into `ExtStatement::SqlStatement`, and errors when a statement delimiter is missing. The `parser_err!` macro builds parser errors.

## Control Flow
Parsing tokenizes input, repeatedly consumes extra semicolons, stops at EOF, parses one statement at a time, and enforces that non-EOF tokens after a parsed statement must be semicolon-delimited. The dispatcher later rejects multiple statements.

## State And Persistence Behavior
Parser state is transient token/parser state. `DefaultParser` is zero-sized and safe to share.

## Dependencies And Integration Points
It depends on DataFusion/sqlparser tokens, tokenizer, parser errors, SNAFU `ParserSnafu`, API `ExtStatement`, and `RustFsDialect`. `SimpleQueryDispatcher` uses it for all SQL input.

## Risks And Edge Cases
Empty SQL parses to an empty deque and is converted to a parser error by the dispatcher. Multiple statements parse successfully here and are rejected later. The parser mostly delegates syntax support to DataFusion/sqlparser, so S3 Select dialect gaps require custom parsing extensions.

## Test Signals
Unit tests cover parser creation, simple select, selected columns, where clauses, and related parse behavior. Error-handling tests cover invalid syntax, empty SQL, multi-statement rejection, unsupported DML/DDL, and long queries.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/parser.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/physical/mod.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/sql/physical/mod.rs

## Purpose
This module exposes physical SQL planning and optimization components.

## Important APIs, Types, And Functions
It declares `pub mod optimizer;` and `pub mod planner;`.

## Control Flow
No local logic.

## State And Persistence Behavior
No local state or persistence.

## Dependencies And Integration Points
`CascadeOptimizer` imports the default physical planner through this module.

## Risks And Edge Cases
Future physical stages must be exported here.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/physical/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/physical/optimizer.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/sql/physical/optimizer.rs

## Purpose
This file defines the local physical optimizer abstraction used after DataFusion physical planning.

## Important APIs, Types, And Functions
`PhysicalOptimizer` declares `optimize(plan, session) -> QueryResult<Arc<dyn ExecutionPlan>>` and `inject_optimizer_rule`, which accepts DataFusion `PhysicalOptimizerRule` instances.

## Control Flow
Concrete implementors receive a physical plan, optionally rewrite it with configured rules, and return the optimized plan. In the current stack, `DefaultPhysicalPlanner` implements this trait and returns the plan unchanged after DataFusion's session-level physical optimizer rules have already run during planning.

## State And Persistence Behavior
The trait has no persistence behavior. Implementations may hold in-memory rule lists.

## Dependencies And Integration Points
It is exported by `sql/physical/mod.rs` and consumed by `CascadeOptimizer` as the final physical-plan optimization stage.

## Risks And Edge Cases
The trait is separate from the API `PhysicalPlanner`, so implementors must keep planner-time DataFusion rules and post-planning optimization behavior synchronized. The default implementation currently performs no additional rewrite in `optimize`.

## Test Signals
No direct tests are local to this trait. `CascadeOptimizerBuilder` tests verify that a default physical optimizer component is installed, and integration tests cover the resulting execution plans.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/physical/optimizer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/physical/planner.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/sql/physical/planner.rs

## Purpose
This file implements the default physical planner that converts logical query plans to DataFusion execution plans.

## Important APIs, Types, And Functions
`DefaultPhysicalPlanner` wraps DataFusion physical planning facilities. Its API `PhysicalPlanner` implementation accepts a DataFusion `LogicalPlan` and creates an `Arc<dyn ExecutionPlan>` using a session state augmented with physical optimizer rules.

## Control Flow
The planner is called after analysis/logical optimization. It delegates physical-plan creation to DataFusion with the query session, preserving explain/analyze behavior through the logical plan supplied by earlier stages.

## State And Persistence Behavior
The planner is stateless and produces in-memory execution plans.

## Dependencies And Integration Points
It depends on API `PhysicalPlanner`, `Plan`, `SessionCtx`, and DataFusion physical planner APIs. `CascadeOptimizer` uses it as the final step.

## Risks And Edge Cases
Physical planning is version-sensitive to DataFusion APIs and to custom table providers. Errors here usually indicate unsupported logical plans, missing table metadata, or object-store/table-source mismatches.

## Test Signals
All successful query integration tests exercise this planner.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/physical/planner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/planner.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/sql/planner.rs

## Purpose
This file implements the generic SQL-to-logical-plan adapter over DataFusion's `SqlToRel`.

## Important APIs, Types, And Functions
`SqlPlanner<'a, S: ContextProviderExtension>` stores a schema/context provider. Its `LogicalPlanner` implementation accepts `ExtStatement` and returns API `Plan`. The implementation uses async recursion to resolve SQL statements through DataFusion and wrap the resulting logical plan in `QueryPlan`.

## Control Flow
When passed an `ExtStatement::SqlStatement`, the planner calls DataFusion's SQL-to-rel planner with the metadata provider. It rejects unsupported statements through DataFusion/planner errors and marks the resulting plan as a query with `is_tag_scan: false`.

## State And Persistence Behavior
The planner borrows metadata context for the lifetime of planning and persists nothing.

## Dependencies And Integration Points
It depends on DataFusion `SqlToRel`, sqlparser statements, API `LogicalPlanner`, `Plan`, `QueryPlan`, and the metadata `ContextProviderExtension`. `DefaultLogicalPlanner` wraps this type.

## Risks And Edge Cases
Only SQL statements supported by DataFusion and the metadata provider can be planned. `is_tag_scan` is always false, so any future tag-scan detection must be added here.

## Test Signals
Planner behavior is covered by integration tests for select, where, group by, order by, limit, invalid columns, unsupported DML/DDL, and multi-format object scans.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/sql/planner.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/test/error_handling_test.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/test/error_handling_test.rs

## Purpose
This file tests error handling across the query engine for invalid SQL, multi-statements, unsupported operations, invalid references, empty input, long SQL, and injection-like patterns.

## Important APIs, Types, And Functions
`create_test_input_with_sql` builds CSV `SelectObjectContentInput` values with `FileHeaderInfo::USE`. Tests use `get_global_db`, `Query`, `Context`, and `QueryError`.

## Control Flow
Each test creates a database in test mode, builds a query, executes it, and asserts either an expected error variant or graceful success/failure. Multi-statement tests specifically match `QueryError::MultiStatement`. Empty-query tests expect parser errors.

## State And Persistence Behavior
All tests run against in-memory fixture sessions through `get_global_db(..., true)`. No persistent state is mutated.

## Dependencies And Integration Points
The tests cover parser, dispatcher validation, metadata/planner resolution, and execution error propagation. They use `s3s` DTOs and the public crate API.

## Risks And Edge Cases
Several tests allow either success or error for invalid column references, long queries, and injection-like patterns, so they mainly assert graceful handling rather than strict semantics. They do not inspect S3 API error code mapping.

## Test Signals
Strong signal exists for syntax errors, multi-statement rejection, unsupported DML/DDL rejection, empty SQL parser errors, and complex invalid query failure.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/test/error_handling_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/test/integration_test.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/test/integration_test.rs

## Purpose
This file provides end-to-end tests for creating S3 Select DB instances and executing CSV, JSON, JSON-lines, and parquet queries, including scan ranges and concurrent execution.

## Important APIs, Types, And Functions
Fixture builders create CSV, JSON DOCUMENT, JSON LINES, and parquet `SelectObjectContentInput` values. Tests use `make_rustfsms`, `get_global_db`, `create_fresh_db`, `Query`, `Context`, and `QueryError`.

## Control Flow
Tests create test-mode databases, execute select queries, collect `QueryHandle` outputs into record batches, and assert success or expected row-count constraints. They also exercise staged state-machine planning and execution. Parquet scan-range tests mutate `request.scan_range` and verify row-group pruning outcomes.

## State And Persistence Behavior
All data comes from in-memory fixtures installed by `SessionCtxFactory` in test mode. Concurrent tests share the global component cache but create per-query contexts and sessions.

## Dependencies And Integration Points
The tests cover the full stack: crate root helpers, instance construction, dispatcher, parser, metadata provider, session fixture object stores, optimizer, physical planner, scheduler, output collection, `EcObjectStore` scan-range behavior in test mode, and parquet custom table provider.

## Risks And Edge Cases
Some aggregation tests accept failure due to lack of actual data, reducing strictness. Many tests assert success without checking exact values for CSV/JSON. Parquet row-count tests provide stronger correctness around scan-range pruning.

## Test Signals
Coverage includes DB creation, global/fresh DB creation, simple select, where, aggregation tolerance, invalid syntax, multi-statement errors, staged workflow, limit, order by, concurrent queries, JSON DOCUMENT, JSON LINES scan range, parquet simple select, tiny parquet scan range returning zero rows, full parquet scan range returning all rows, and CSV scan range returning rows.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/test/integration_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/test/mod.rs -->
# sources/object-store/rustfs/crates/s3select-query/src/test/mod.rs

## Purpose
This test module wires query crate test files into the Rust test harness.

## Important APIs, Types, And Functions
It declares `pub mod error_handling_test;` and `pub mod integration_test;`.

## Control Flow
When crate tests are compiled, both child modules are included.

## State And Persistence Behavior
No local state or persistence.

## Dependencies And Integration Points
This module connects Cargo test discovery with the error-handling and integration test suites.

## Risks And Edge Cases
New test files are ignored unless exported here.

## Test Signals
Its presence ensures both major test suites are compiled and run.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3select-query/src/test/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/Cargo.toml -->
# sources/object-store/rustfs/crates/scanner/Cargo.toml

## Purpose
This manifest defines the RustFS `rustfs-scanner` crate, which scans buckets/objects and manages lifecycle/data-usage related background scanning.

## Important APIs, Types, And Functions
Package metadata declares workspace versioning, crate name, description, keywords, categories, docs URL, and disabled doctests. Dependencies include RustFS config, ecstore, filemeta, notifications, objectlock, observability, policy, utils, workers, common/runtime crates, plus `async-trait`, `chrono`, `tokio`, `tracing`, `serde`, `serde_json`, `uuid`, and `snafu`.

## Control Flow
Cargo uses the dependency set to compile the scanner crate and its tests. The manifest links scanner code to storage, lifecycle, object-lock, notification, observability, and worker subsystems.

## State And Persistence Behavior
The manifest has no runtime state. It indicates that scanner runtime code can interact with persistent object metadata and lifecycle state through its dependencies.

## Dependencies And Integration Points
The crate is tightly integrated with RustFS object-store internals (`ecstore`, `filemeta`), policy/object-lock/lifecycle subsystems, notification and observability crates, and async runtime infrastructure.

## Risks And Edge Cases
Scanner depends on many internal crates, so version or API changes in storage metadata, lifecycle, or worker crates can break it. Disabled doctests mean examples are not automatically checked.

## Test Signals
The manifest points to the scanner crate test suite, including lifecycle integration tests in the crate tree, but no tests are defined in the manifest itself.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/scanner/Cargo.toml -->
