# subset-b-008887 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/table.rs -->
## sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/table.rs

### Purpose
This file implements TiDB table and index key/value codec helpers for TiKV query components. It defines the raw key layout constants for table prefixes, record keys, index keys, extra system column IDs, and index value metadata flags. It also provides row encoding/decoding, row cutting for column pruning, index key cutting, table range validation, and the `RowHandle` abstraction used by executors such as index lookup.

### Important APIs, types, and functions
The table prefix shape is `t{table_id}_{r|i}` with comparable-encoded signed IDs. `extract_table_prefix`, `check_table_ranges`, `check_record_key`, `check_index_key`, and `decode_table_id` validate and decode this layout. `encode_row_key`, `encode_common_handle`, `encode_column_key`, and `encode_index_seek_key` construct raw TiDB keys for table rows, common handles, row columns, and index seeks.

`flatten` and private `unflatten` bridge logical datum types with storage encodings: durations become nanoseconds, time-like values become packed integers, floats round through `f32`, and unsupported enum/set/bit unflattening is rejected in this path. `encode_row`, `decode_col_value`, and `decode_row` implement row value conversion around `Datum` streams and `ColumnInfo`.

`RowColMeta` and `RowColsDict` are lightweight views over encoded row bytes. `cut_row` dispatches row v1/v2 handling: v1 scans datum pairs and records offsets; v2 uses `row::v2::RowSlice` plus `V1CompatibleEncoder` to emit v1-compatible column datums for requested columns. `cut_idx_key` maps requested index column IDs to encoded datum slices and optionally decodes a trailing int handle.

`RowHandle` abstracts lookup handles. `IntHandle` extracts one decoded integer handle column, builds row keys, emits prefix-next point range ends, and detects consecutive handles. `CommonHandle` consumes `LazyBatchColumnVec` extra common-handle keys, appends raw common-handle bytes to record prefixes, and returns a point range end by appending `0`.

### Control flow
Validation first checks fixed bytes and lengths, then decodes table IDs or handles. Row encoding interleaves `col_id, value` pairs and uses a single `Null` datum for empty rows. Row decoding decodes the whole datum stream, validates even pair counts, then only materializes requested columns. Row cutting avoids full materialization by recording offsets into the source buffer or by converting row v2 selected columns into a v1-compatible buffer.

Index key decoding skips `PREFIX_LEN + ID_LEN`, decodes one datum per `ColumnInfo`, and unflattens according to column type. `cut_idx_key` similarly skips the prefix and index ID, splits fixed index datums, then treats remaining bytes as an optional int handle.

### State and persistence behavior
The module does not persist data itself. State is carried in byte buffers, offset maps, and `EvalContext` warnings/errors during type conversion. `RowColsDict` owns encoded bytes and offset metadata, so callers can hold borrowed column slices safely as long as the dict lives. `CommonHandle::from_lazy_batch_column_vec` mutates the batch by taking extra handle keys, which is a one-shot transfer.

### Dependencies and integration points
The codec depends on `codec::prelude` numeric encoding, `Datum` encoding, `ColumnInfo`/`FieldType`, row v2 codecs, `EvalContext`, and `LazyBatchColumnVec`. Executors use `RowHandle` for table lookup planning. Table scans and coprocessor range checks use key validation helpers. TiDB compatibility is encoded through special negative column IDs, row v1/v2 compatibility, common-handle support, and collation/restored-data flags defined elsewhere.

### Risks and edge cases
`FieldTypeTp::Enum`, `Set`, and `Bit` are not supported by `unflatten`, despite related eval paths existing elsewhere. `decode_index_key` assumes the key is long enough to skip prefix and index ID; callers must supply valid index keys. `cut_row` notes that mismatched `col_ids` and `cols` give undefined results. `IntHandle::is_next_of` can overflow on `i64::MAX + 1` in debug builds if called with max previous handle. Common-handle point range end by appending `0` is a prefix range, not a consecutive-key optimization.

### Test signals
Tests cover row and index key round trips, row encode/decode/cut behavior, empty rows, table prefix extraction, table range validation, table ID decoding, key type checks, `IntHandle` extraction and type validation, point range end generation, and common-handle extraction/error cases. The tests also cover row v1 cut behavior and lazy batch column decoding assumptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/table.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/def/eval_type.rs -->
## sources/storage-engines/tikv/components/tidb_query_datatype/src/def/eval_type.rs

### Purpose
This file defines `EvalType`, the reduced set of runtime value categories used by TiKV expression and vectorized query execution. It maps TiDB/MySQL field types into execution categories such as `Int`, `Real`, `Decimal`, `Bytes`, `DateTime`, `Duration`, `Json`, `Enum`, `Set`, and `VectorFloat32`.

### Important APIs, types, and functions
`EvalType` is a copyable enum with a debug-backed `Display` implementation. `into_certain_field_type_tp_for_test` maps each eval type to one representative `FieldTypeTp`, primarily for tests that need a concrete protobuf field type. `TryFrom<FieldTypeTp> for EvalType` is the production conversion surface. Integer-like MySQL types, including `Bit` and `Year`, map to `Int`; `Float` and `Double` map to `Real`; all date/time/timestamp field types map to `DateTime`; string and blob families plus `Null` map to `Bytes`; TiDB vector float32 maps to `VectorFloat32`.

### Control flow
Conversion is a single match over `FieldTypeTp`. Unsupported or not-yet-encoded types return `DataTypeError::UnsupportedType`; currently `Unspecified`, `NewDate`, `Set`, and `Geometry` fall into the error path even though `EvalType::Set` exists.

### State and persistence behavior
There is no mutable state or persistence. This module is pure type classification.

### Dependencies and integration points
The conversion depends on `FieldTypeTp` and `DataTypeError`. It is used by expression builders, aggregation executors, vector column allocation, and support checks to choose typed execution paths.

### Risks and edge cases
The existence of `EvalType::Set` but rejection of `FieldTypeTp::Set` is intentional per the TODO, but it can surprise new call sites. Timestamp is intentionally collapsed into `DateTime`, so any logic needing timestamp-specific timezone behavior must use field metadata elsewhere.

### Test signals
The test matrix exercises every major `FieldTypeTp` and verifies supported mappings versus unsupported errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/def/eval_type.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/def/field_type.rs -->
## sources/storage-engines/tikv/components/tidb_query_datatype/src/def/field_type.rs

### Purpose
This file provides Rust-side definitions and accessors for TiDB field metadata stored in protobuf `FieldType` and `ColumnInfo`. It centralizes MySQL/TiDB type codes, collation codes, charset parsing, field flags, and helper predicates used throughout expression evaluation, codecs, and executors.

### Important APIs, types, and functions
`FieldTypeTp` mirrors parser MySQL type constants, including TiDB-specific `TiDbVectorFloat32`. `from_i32`, `from_u8`, and `to_u8` convert between protobuf/raw numeric forms and enum values. `Collation` maps TiDB collation IDs, including legacy positive IDs and newer negative padding-aware IDs, into a smaller enum. `Collation::from_i32` treats unknown nonnegative codes as `Utf8Mb4BinNoPadding` for compatibility but rejects unknown negative codes. `Charset::from_name` parses known charset names.

`FieldTypeFlag` defines bitflags for not-null, unsigned, binary, parse-to-json, boolean literal, and enum/set-as-int behavior. `FieldTypeAccessor` abstracts over `tipb::FieldType` and `tipb::ColumnInfo`, exposing `tp`, `flag`, `flen`, `decimal`, and `collation` getters/setters plus semantic helpers like `is_hybrid`, `is_blob_like`, `is_char_like`, `is_varchar_like`, `is_string_like`, `is_binary_string_like`, `is_non_binary_string_like`, `is_unsigned`, `is_bool`, and `need_restored_data`.

### Control flow
Accessor implementations translate between differing protobuf field names: `FieldType` uses `tp`, `flag`, `flen`, `decimal`, and `collate`; `ColumnInfo` uses flattened `tp`, `flag`, `column_len`, `decimal`, and `collation`. Predicate helpers build on the accessors, so executor and codec code can work with either protobuf type.

### State and persistence behavior
The module mutates protobuf structs in-place through setter methods but maintains no global state. Flag conversion uses truncating bitflag parsing, so unknown flags are ignored by the accessor layer.

### Dependencies and integration points
The code depends on `tipb::{FieldType, ColumnInfo}` and local `DataTypeError`. It is used by row codecs, expression type inference, collation-aware comparison and aggregation, table scan schema construction, and index restored-data decisions.

### Risks and edge cases
`FieldTypeTp::from_i32` and `from_u8` use `unsafe transmute` after numeric range checks. This is concise but depends on the enum discriminants remaining exactly aligned with TiDB constants. `to_u8` always returns `Some`, even for values represented by negative or large `i32` after cast; current variants fit the intended byte space. `need_restored_data` has nuanced collation logic and is a compatibility-sensitive area, especially for varstrings and newer UTF8MB4 0900 collations.

### Test signals
Tests cover type numeric conversion, invalid ranges, u8 round trips, collation aliasing and rejection, charset parsing, and `need_restored_data` outcomes for binary, general, unicode, 0900, GBK, and GB18030 collations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/def/field_type.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/def/mod.rs -->
## sources/storage-engines/tikv/components/tidb_query_datatype/src/def/mod.rs

### Purpose
This module is the public facade for datatype definitions. It declares the `eval_type` and `field_type` submodules, re-exports their primary types, and defines shared MySQL/TiDB width constants.

### Important APIs, types, and functions
Exports include `EvalType`, `Charset`, `Collation`, `FieldTypeAccessor`, `FieldTypeFlag`, and `FieldTypeTp`. Constants include `UNSPECIFIED_LENGTH`, `MAX_BLOB_WIDTH`, `MAX_DECIMAL_WIDTH`, and `MAX_REAL_WIDTH`.

### Control flow
There is no runtime control flow; this is module organization and shared constant declaration.

### State and persistence behavior
The module has no state. Constants are compile-time values used by builders, codecs, and expression code.

### Dependencies and integration points
Consumers import this module through `tidb_query_datatype::{...}` or the crate prelude. It ties together the field metadata and eval type conversion modules for the rest of the query stack.

### Risks and edge cases
`MAX_BLOB_WIDTH` is an `i32` while neighboring constants are `isize`, with a FIXME noting the mismatch. New datatype definitions must be re-exported here if they are intended as public API.

### Test signals
There are no direct tests in this facade; coverage is supplied by `eval_type.rs`, `field_type.rs`, and downstream users.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/def/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/error.rs -->
## sources/storage-engines/tikv/components/tidb_query_datatype/src/error.rs

### Purpose
This file defines datatype-definition errors that are separate from runtime codec/expression errors.

### Important APIs, types, and functions
`DataTypeError` is a `thiserror::Error` enum with `UnsupportedType { name }`, `UnsupportedCollation { code }`, and `UnsupportedCharset { name }`. Display messages are stable and human-readable.

### Control flow
No control flow exists beyond enum construction by callers such as `EvalType::try_from`, `Collation::from_i32`, and `Charset::from_name`.

### State and persistence behavior
The enum owns only the unsupported value details. There is no persistence or global state.

### Dependencies and integration points
It depends on `thiserror` and is re-exported from `tidb_query_datatype`. It is used where field metadata cannot be translated into supported TiKV execution semantics.

### Risks and edge cases
The error type is intentionally narrow. Callers needing richer context, such as source expression or column ID, must wrap or augment it at a higher layer.

### Test signals
Indirect tests in field and eval type modules assert that unsupported cases produce errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/expr/ctx.rs -->
## sources/storage-engines/tikv/components/tidb_query_datatype/src/expr/ctx.rs

### Purpose
This file defines evaluation configuration, SQL execution flags, warning accumulation, and per-evaluation context for TiKV query expressions and codecs.

### Important APIs, types, and functions
`SqlMode` models strict modes, zero date handling, invalid dates, and division-by-zero behavior. `Flag` models DAG request execution flags such as `IGNORE_TRUNCATE`, `TRUNCATE_AS_WARNING`, statement kind flags, `OVERFLOW_AS_WARNING`, `DIVIDED_BY_ZERO_AS_WARNING`, and `IN_LOAD_DATA_STMT`.

`EvalConfig` stores timezone, flags, maximum warning count, SQL mode, paging/max-keys options, division precision increment, and test marker. `from_request` builds it from `tipb::DagRequest`, preferring timezone name over offset. Setter methods update individual config fields, and `new_eval_warnings` creates a bounded warning buffer.

`EvalWarnings` tracks total warning count separately from stored warning details. `append_warning` increments the total and stores up to the configured limit. `merge` combines warning counts and truncates stored details to the receiver capacity.

`EvalContext` combines shared `Arc<EvalConfig>` with mutable warnings. It handles truncation, overflow, division by zero, invalid time errors, string-to-int overflow fallback, warning draining, and unsigned clipping policy.

### Control flow
Error handling methods convert runtime errors to success, warning, or error depending on flags and SQL mode. Truncation is ignored, warned, or returned as an error. Overflow is warned only under `OVERFLOW_AS_WARNING`. Division by zero is statement-sensitive and strict-mode-sensitive. Invalid time errors become hard errors only for strict insert/update/delete paths.

### State and persistence behavior
`EvalConfig` is shared immutably through `Arc`. `EvalContext` owns mutable warnings for a single evaluation path. `take_warnings` atomically replaces the current warning buffer with an empty buffer using the same configured capacity. No durable persistence occurs.

### Dependencies and integration points
The module depends on `tipb::DagRequest`, timezone support in `codec::mysql::Tz`, codec `Error`/`Result`, and `DEFAULT_DIV_FRAC_INCR`. It is used by datum codecs, expression evaluation, aggregate executors, table/index decoders, and executor result warning propagation.

### Risks and edge cases
Warning detail storage is capped while `warning_cnt` keeps growing, so consumers must read both fields. `from_request` silently leaves UTC if neither timezone name nor offset is present. Division-by-zero semantics are subtle: in non-write statements it records a warning. `overflow_from_cast_str_as_int` returns `u64::MAX as i64` for positive overflow, which is `-1` by two's-complement cast and is presumably part of TiDB-compatible cast behavior that should not be casually changed.

### Test signals
Tests cover truncation handling modes, warning count capping, division-by-zero combinations across flags and strict mode, and invalid-time strict write behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/expr/ctx.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/expr/mod.rs -->
## sources/storage-engines/tikv/components/tidb_query_datatype/src/expr/mod.rs

### Purpose
This facade exposes expression evaluation context types and re-exports codec `Error`/`Result` for expression-facing users.

### Important APIs, types, and functions
It declares `mod ctx`, publicly re-exports everything from `ctx`, and re-exports `crate::codec::{Error, Result}`.

### Control flow
There is no runtime control flow.

### State and persistence behavior
No state is stored here. Stateful behavior lives in `ctx.rs`.

### Dependencies and integration points
This module lets other crates import `tidb_query_datatype::expr::{EvalContext, EvalConfig, Error, Result}` from one place. It is used by expression builders, codec conversions, and executors.

### Risks and edge cases
The module couples expression errors to codec errors by re-exporting the codec error type. That keeps old APIs simple but means expression and codec error domains are not cleanly separated.

### Test signals
There are no direct tests; coverage comes from `ctx.rs` and downstream expression/executor tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/expr/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/lib.rs -->
## sources/storage-engines/tikv/components/tidb_query_datatype/src/lib.rs

### Purpose
This is the crate root for `tidb_query_datatype`, which houses shared datatype, codec, builder, and expression context code used by TiKV query crates.

### Important APIs, types, and functions
The crate enables several nightly features (`proc_macro_hygiene`, `min_specialization`, `test`, `str_internals`, `core_intrinsics`, and `bool_to_result`) and imports project macros from `num_derive`, `static_assertions`, `tikv_util`, and `bitflags`. Public modules are `builder`, `def`, `error`, `codec`, and `expr`. The crate prelude currently re-exports `FieldTypeAccessor`, and the root re-exports `def::*` and `error::*`.

### Control flow
There is no runtime control flow; this file controls compilation, macro availability, module visibility, and public exports.

### State and persistence behavior
No state is stored here.

### Dependencies and integration points
This root is consumed by query expression, aggregation, and executor crates. Its exported APIs are the shared vocabulary for field metadata, eval type conversion, row codecs, MySQL datatypes, and evaluation contexts.

### Risks and edge cases
The crate depends on nightly/internal features, so compiler upgrades can affect it. Macro imports are crate-wide and can hide where helper macros originate. Public re-exports mean changes to `def` or `error` can become semver-visible inside the workspace.

### Test signals
The root conditionally imports the `test` crate for test builds. Behavioral coverage is in the public modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/Cargo.toml -->
## sources/storage-engines/tikv/components/tidb_query_executors/Cargo.toml

### Purpose
This manifest defines the `tidb_query_executors` crate, described as a vector query engine for TiDB pushed-down executors.

### Important APIs, types, and functions
The package is version `0.0.1`, edition `2021`, unpublished, and Apache-2.0 licensed. Runtime dependencies include async support, workspace codec/collections/kvproto/tipb/txn types, `tidb_query_aggr`, `tidb_query_common`, `tidb_query_datatype`, `tidb_query_expr`, metrics/logging utilities, `match-template`, `protobuf`, `smallvec`, and `fail`.

### Control flow
No runtime control flow exists in the manifest, but feature and dependency choices determine available executor implementations and test utilities.

### State and persistence behavior
The manifest has no runtime state.

### Dependencies and integration points
This crate sits above datatype, expression, common storage interfaces, and aggregation crates. Dev dependencies `anyhow`, `tidb_query_codegen`, and `tipb_helper` support executor tests and expression construction.

### Risks and edge cases
The manifest does not declare crate-local features, so optional behavior is mostly controlled by code cfgs and workspace dependency versions. Executor code relies on workspace versions of core TiKV crates, making API drift in those crates a direct integration risk.

### Test signals
The dev dependencies align with the test modules in executor files that use `tipb_helper`, mock storage, and generated query function support.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/fast_hash_aggr_executor.rs -->
## sources/storage-engines/tikv/components/tidb_query_executors/src/fast_hash_aggr_executor.rs

### Purpose
This file implements `BatchFastHashAggregationExecutor`, a vectorized hash aggregation executor optimized for exactly one group-by expression. It hashes typed group keys directly instead of using the slower general multi-key aggregation path.

### Important APIs, types, and functions
`BatchFastHashAggregationExecutor<Src>` wraps generic `AggregationExecutor<Src, FastHashAggregationImpl>` and delegates the `BatchExecutor` API. `check_supported` rejects multi-column group-by, unsupported group-by eval types, unsupported RPN expressions, and unsupported aggregate definitions.

`new` builds a single RPN group-by expression from tipb expressions and delegates to `new_impl`. `new_impl` derives the group-by field type and eval type, then creates a typed `Groups` hash map. `Groups` stores `HashMap<Option<T>, usize>` variants for int, real, bytes, duration, decimal, datetime, enum, and vector float32 keys, where the value is an offset into the aggregate state vector.

`FastHashAggregationImpl` owns aggregate states, typed groups, the group-by expression, output group-by field type, and per-input-row state offsets. It implements `AggregationExecutorImpl`.

### Control flow
For each input batch, `process_batch_input` evaluates the group-by expression over source columns. Scalar group results route through `handle_scalar_group_each_row`, creating one state group and assigning every logical row to offset 0. Vector results route through `calc_groups_each_row`, which maps each logical row value into a hash key, reuses existing state offsets, or appends new aggregate states for new groups. Bytes grouping is collation-aware: it transmutes the group map to use `SortKey<Bytes, Collator>` under the selected collation and stores sort keys as grouping identities.

After group offsets are computed, `HashAggregationHelper::update_each_row_states_by_offset` evaluates aggregate arguments and updates states. Results are only emitted after the source is drained. `iterate_available_groups` takes the group map, calls the result iteratee over each group's state slice, and builds a decoded group-by output column.

### State and persistence behavior
State is in-memory only. Aggregate states are append-only until final output; group maps point into the `states` vector. `states_offset_each_logical_row` is cleared and reused each batch. `iterate_available_groups` consumes groups with `mem::take`, so output is a terminal phase for this implementation.

### Dependencies and integration points
The executor depends on `tidb_query_aggr` for aggregate function definitions/states, `tidb_query_expr` for RPN evaluation, datatype vector/field/collation APIs, `AggregationExecutor` shared machinery, and `HashAggregationHelper` for updating states. Metrics record work under `batch_fast_hash_aggr`.

### Risks and edge cases
The executor assumes exactly one group-by expression and no partial output before drain, so memory grows with group cardinality and aggregate state size. Bytes grouping uses unsafe transmute to reinterpret the hash map key type for collation sort keys; this depends on identical representation expectations and is a sensitive maintenance area. Scalar group handling panics if a supposedly constant expression produces a different value on later batches. Support checking excludes `EvalType::Enum`, but implementation and tests include enum grouping through direct test construction, so production support and internal capability differ.

### Test signals
Tests compare fast and slow hash aggregation on integration cases, constant group-by, collation grouping, no-row input, no aggregate functions, and enum column grouping. They validate output schemas, group counts, warning propagation through mock executors, and undefined row order handling by sorting before assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/fast_hash_aggr_executor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/index_lookup_executor.rs -->
## sources/storage-engines/tikv/components/tidb_query_executors/src/index_lookup_executor.rs

### Purpose
This file implements the batch index lookup executor. It consumes index-scan results from a source executor, extracts row handles, groups table row lookups by local region, performs table scans for locally available leader regions, and returns rows from the table side while preserving unresolved index rows as intermediate results for fallback.

### Important APIs, types, and functions
`BatchIndexLookUpExecutor<S, Src, Builder, F>` is the main executor. It stores source executor state, config, output table schema, force-fallback flag, adaptive table lookup batch size, optional table task builder, table scan parameters, current phase, intermediate results, channel indices, and table scan summary. `BuildIndexLookUpExecutorOptions` carries construction inputs from planner code. `build_index_lookup_executor` rejects keep-order requests, extracts index handle offsets/types from source schema, builds `TableScanParams`, and optionally creates an `AccessorTableTaskIterBuilder`.

`IndexLookUpPhase` has `IndexScan`, `TableLookUp`, and `Done` states. `IndexScanState` buffers index batches and row count. `TableLookUpState` carries an optional table task iterator and optional active table scan executor.

`TableTaskIterBuilder` constructs a `TableTaskIterator` from buffered index results. `AccessorTableTaskIterBuilder` binds table ID, region accessor, and `IndexLayout`. `AccessorTableTaskIterator` decodes handle columns, extracts `RowHandle`s, sorts handles, finds regions, builds key ranges, tracks fallback rows, and produces `TableTask`s. `TableTask` converts storage plus raw key ranges into a `BatchTableScanExecutor`.

### Control flow
In `IndexScan` phase, `on_phase_index_scan` pulls from the source executor. It returns an empty output batch carrying source drain status or warnings while buffering non-empty index results. If `force_no_index_lookup` is active, non-empty source results go straight to `intermediate_results`, and the executor finishes when the source drains. Otherwise, once the source drains or buffered row count reaches the adaptive threshold, it doubles the threshold up to `BATCH_MAX_SIZE` and transitions to `TableLookUp`.

`step_to_table_lookup` creates an `EvalContext`, builds a table task iterator from buffered results, and merges any handle decoding warnings. In `TableLookUp`, the executor either continues an active table scan or asks the iterator for the next task. Drained table scans are released after their summary is collected, and their drain status is converted back to `Remain` because more table tasks or source batches may remain. When the iterator is exhausted, unresolved rows are appended to `intermediate_results`; the executor either loops back to `IndexScan` or enters `Done` if the source is drained.

`AccessorTableTaskIterator::new` ensures handle columns are decoded, extracts handles through `RowHandle::from_lazy_batch_column_vec`, and sorts `(result_index, logical_row_index)` by handle value. `next_task` finds the region for the next handle, scans forward while subsequent handles stay before the same region end, coalesces consecutive int handles into larger ranges, clamps range ends to region end when necessary, obtains local region storage, and advances the cursor. Failed region lookup, follower role, storage acquisition failure, or region-end decode failure mark rows as left for fallback.

### State and persistence behavior
All state is in-memory for a single executor invocation. Buffered index batches are moved between phase states and `intermediate_results`. `finish_table_task_iter` transfers unresolved rows out of the iterator. `table_scan_exec_summary` accumulates stats for inner table scans and is drained into outer `ExecuteStats`. No data is persisted; storage reads are delegated to region storage accessors and table scan executors.

### Dependencies and integration points
The executor depends on `BatchExecutor`, `BatchTableScanExecutor`, `RegionStorageAccessor`, `Storage`, `FindRegionResult`, `StateRole`, `txn_types::Key`, table codec `RowHandle`, `EvalConfig`/`EvalContext`, `LazyBatchColumnVec`, `tipb::IndexLookUp` and `TableScan`, and table scan field-type conversion helpers. It integrates with intermediate result channels so unresolved rows can be reconciled by higher-level DAG execution.

### Risks and edge cases
Keep-order is unsupported. Paging and max-keys-read force fallback because buffering complicates early-stop semantics. Missing table task builders also force fallback, currently including common-handle cases per TODO. Errors in `find_region_by_handle_index` and storage acquisition are swallowed into fallback rows rather than emitted, while storage scan errors from active table scans are returned. Range construction must compare raw keys converted to MVCC comparable keys against region ends, and incorrect end clamping could skip or over-read rows. The executor is not cacheable because it reads regions outside the source region.

### Test signals
Tests cover iterator construction and handle sorting, region/task generation, consecutive range coalescing, follower/not-found/storage-error fallback rows, exhausted iterators, table scan executor construction, index scan phase buffering and adaptive threshold growth, table lookup phase task execution and summary collection, forced fallback for paging/max-keys/missing builder, intermediate result channel behavior, intermediate schema routing, and table scan summary accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_executors/src/index_lookup_executor.rs -->
