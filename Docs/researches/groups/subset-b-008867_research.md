# Research: subset-b-008867

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_first.rs -->
# sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_first.rs

Purpose: implements TiDB pushed-down `FIRST` aggregation for the batch aggregate executor. The parser validates a single child expression, verifies the output field type matches the child expression evaluation type, appends one output schema column and one RPN expression, then selects a typed `AggrFnFirst<T>` implementation for scalar, bytes-like, JSON, enum/set, and vector-float values.

Important APIs and control flow: `AggrFnDefinitionParserFirst` implements `AggrDefinitionParser::check_supported` and `parse_rpn`. `AggrFnFirst<T>` derives `AggrFunction`, whose generated `create_state` returns `AggrFnStateFirst<T>`. The state is `Empty` until the first logical row is observed, then becomes `Valued(Option<T::EvaluableType>)`, preserving `NULL` if the first row is null. `update_repeat` ignores repeat count after asserting it is nonzero; `update_vector` looks only at the first logical row and delegates to `update`.

State and persistence behavior: state is in-memory and per aggregate group; there is no durable persistence. `push_result` emits exactly one column and clones the captured owned value. The first value is never replaced, so correctness depends on caller row order matching TiDB aggregation semantics.

Dependencies and integration: uses `tidb_query_codegen::AggrFunction`, `tidb_query_datatype` evaluable refs and `VectorValue`, `tidb_query_expr::RpnExpression`, and `tipb::ExprType::First`. It integrates through `parser.rs` dispatch and the generic update macros in `lib.rs`.

Risks and test signals: unsupported or mismatched output types fail in parsing; mismatched runtime update types panic through the aggregate-state trait layer. A TODO notes cloning could be avoided. Tests cover empty output, first-null behavior, enum/set ownership, repeated update, vector logical-row ordering, and illegal return-type requests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_first.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_max_min.rs -->
# sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_max_min.rs

Purpose: implements `MAX` and `MIN` aggregation with shared generic machinery. `Extremum` binds an aggregate expression type and comparison direction; `Max` replaces stored values when current order is `Less`, and `Min` when it is `Greater`.

Important APIs and control flow: `AggrFnDefinitionParserExtremum<E>` validates one child, reads child eval type, unsigned integer flag, and output collation, checks the root output type, appends one schema column/expression, and selects a concrete implementation. General ordered types use `AggFnExtremum<T,E>`, ints use `AggFnExtremumForInt<E, IS_UNSIGNED>`, bytes use `AggFnExtremumForBytes<C,E>` with collation-specific `Collator`, and enum/set have dedicated string-comparison implementations.

State and persistence behavior: each state stores an optional owned extremum value and updates only for non-null inputs. Bytes, enum, set, and generic owned values are cloned into state; integer state stores copied `i64`. There is no persistence outside the aggregate state object.

Dependencies and integration: depends on `tidb_query_datatype` collation support, `FieldTypeFlag::UNSIGNED`, `match_template_collator`, `VectorValueExt`, and aggregate traits/macros from `lib.rs`. Parser dispatch in `parser.rs` maps `ExprType::Max` and `ExprType::Min` to this implementation.

Risks and test signals: correctness is sensitive to unsigned integer ordering, collation selection, and MySQL-specific enum/set string semantics. Several implementations use unsafe lifetime transmutes to reborrow owned values for comparison; this is localized but high-risk if data-type ownership contracts change. Tests cover max/min updates, null handling, vector updates, collations, signed/unsigned integer behavior, parser integration, and illegal output types.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_max_min.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_sum.rs -->
# sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_sum.rs

Purpose: implements `SUM` for numeric-like pushed-down aggregate inputs. It normalizes input expressions through TiDB-compatible cast insertion, then aggregates decimal or real values, with special enum/set paths that sum their numeric value/index.

Important APIs and control flow: `AggrFnDefinitionParserSum` validates a single child, takes the root field type, calls `util::rewrite_exp_for_sum_avg`, verifies the rewritten expression type equals the requested output type, appends one output column/expression, and returns `AggrFnSum<Decimal>`, `AggrFnSum<Real>`, `AggrFnSumForEnum`, or `AggrFnSumForSet`. `AggrFnStateSum<T>` stores `sum` and `has_value`, ignoring nulls and returning null until a non-null input is seen.

State and persistence behavior: state is in-memory per group. Decimal addition flows through `Summable::add_assign`, allowing decimal errors to surface through `Result`; real addition is direct. Enum and set states use `Decimal` and convert `value.value()` before adding.

Dependencies and integration: relies on `Summable`, `EvalContext`, `RpnExpression`, `VectorValueExt`, `tipb::ExprType::Sum`, and generated `AggrFunction` impls. It shares type rewrite behavior with AVG and VARIANCE through `util.rs`.

Risks and test signals: `parse_rpn` treats unexpected post-rewrite types as `unreachable!`, so rewrite and eval-type mapping must remain aligned. The comment questions decimal truncation handling. Tests cover enum/set sums, byte-to-real integration through inserted casts, null skipping, and parser rejection of mismatched output type.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_sum.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_variance.rs -->
# sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_variance.rs

Purpose: implements population variance (`Variance`, `VarPop`) and sample variance (`VarSamp`) aggregates. The file uses a `VarianceType` strategy trait to choose expression matching and final denominator while sharing incremental variance accumulation.

Important APIs and control flow: `AggrFnDefinitionParserVariance<V>` validates one child, rewrites input like SUM/AVG, checks output type, and appends three output columns: unsigned count, sum, and variance. `AggrFnStateVariance<T,V>` updates count, sum, and accumulated variance using an online formula: after incrementing count and sum, it derives `t = count * input - sum` and adds `(t*t)/(count*(count-1))`. Enum/set variants convert values to `Decimal` before the same formula.

State and persistence behavior: state tracks `count`, `sum`, and accumulated variance in memory. `push_result` always emits count; sum and final variance are null when count is zero. Sample variance divides by `count - 1`, so callers must avoid requesting sample final variance for count 1 unless the surrounding SQL semantics handle it.

Dependencies and integration: shares `Summable` arithmetic, `rewrite_exp_for_sum_avg`, `FieldTypeBuilder`, aggregate update macros, and `tipb` expression kinds. Parser dispatch maps variance expression names to either `Population` or `Sample`.

Risks and test signals: `rewrite_exp_for_sum_avg(...).unwrap()` assumes casts always build; panic risk exists if cast construction changes. Decimal division and overflow/truncation errors propagate through `Result`. Tests cover enum/set variance, population and sample integration from string inputs through casts, output schema shape, and illegal output type.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_variance.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/lib.rs -->
# sources/storage-engines/tikv/components/tidb_query_aggr/src/lib.rs

Purpose: defines the aggregate-function framework for TiDB batch executors. It exposes parser entry points, declares aggregate modules, and provides the traits/macros that let concrete aggregate states be boxed while still receiving typed updates.

Important APIs and control flow: `AggrFunction` exposes `name` and `create_state`; `AggrFunctionState` is the object-safe state surface with typed update-partial supertraits for every supported eval reference and a `push_result` method. `ConcreteAggrFunctionState` is the simpler trait concrete states implement. Specialization provides a default "unmatched parameter type" panic implementation and a matching implementation that routes to `update_concrete_unsafe`, `update_repeat_unsafe`, and `update_vector_unsafe`.

State and persistence behavior: all aggregation state is per boxed state object and in memory. The module does not persist state; it defines how callers update rows, repeated rows, and vectors, then push results into `VectorValue` columns.

Dependencies and integration: uses nightly features (`specialization`, `proc_macro_hygiene`, `stmt_expr_attributes`) and `tidb_query_codegen::AggrFunction` in concrete modules. Macros `update!`, `update_vector!`, and `update_repeat!` are the call-site adapters for unsafe type erasure.

Risks and test signals: runtime type mismatch intentionally panics rather than returning `Result`, so parser/schema correctness is critical. Unsafe conversions are hidden behind macros and specialization; future eval type additions must update trait bounds and unmatched impls. Tests verify successful matching, repeated `push_result`, and panic behavior for wrong parameter/result targets.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/parser.rs -->
# sources/storage-engines/tikv/components/tidb_query_aggr/src/parser.rs

Purpose: central parser dispatch for aggregate protobuf definitions. It turns a `tipb::Expr` aggregate node into a typed aggregate function plus the RPN child expression and output schema entries required by executors.

Important APIs and control flow: `AggrDefinitionParser` provides `check_supported`, default `parse`, and overridable `parse_rpn`. The default `parse` takes the first child, builds an `RpnExpression` with `RpnExpressionBuilder::build_from_expr_tree`, then passes root and expression to the concrete parser. `map_pb_sig_to_aggr_func_parser` maps supported `ExprType` values to parser structs for count, sum, avg, first, bit ops, max/min, and variance variants. `AllAggrDefinitionParser` is the public catch-all.

State and persistence behavior: no persistent state. It mutates the consumed protobuf expression by taking children and lets concrete parsers append to caller-owned `out_schema` and `out_exp` vectors.

Dependencies and integration: integrates aggregate implementation modules with `tidb_query_expr` RPN building and `tipb` expression metadata. It is the gateway used by executors before creating aggregate states.

Risks and test signals: default `parse` unwraps the first child, relying on prior `check_supported` to enforce arity. `AllAggrDefinitionParser::parse` unwraps parser dispatch, so unsupported aggregate types must be filtered before parsing. Concrete module tests exercise parser integration and blacklisted/mismatched expressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/parser.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/summable.rs -->
# sources/storage-engines/tikv/components/tidb_query_aggr/src/summable.rs

Purpose: defines arithmetic required by SUM, AVG, and VARIANCE over supported aggregate numeric types. It abstracts zero construction, addition, subtraction, multiplication, division, and conversion from `usize`.

Important APIs and control flow: `Summable` extends `Evaluable` and `EvaluableRet`. `Decimal` implementation delegates arithmetic to TiDB decimal operators and converts codec errors into query `Result`; `Real` implementation uses floating-point arithmetic over `Real`.

State and persistence behavior: stateless helper trait. Aggregate states own the concrete `Decimal` or `Real` values and call these methods during updates/finalization.

Dependencies and integration: used by `impl_sum.rs`, `impl_variance.rs`, and AVG implementation outside this subset. It depends on `EvalContext` only for `add_assign`, though the current implementations do not use context.

Risks and test signals: decimal division calls `.unwrap()` before conversion, which can panic if decimal division returns no value. The TODO in decimal add asks whether truncation should be a warning. Coverage is indirect through aggregate tests rather than unit tests in this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/summable.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/util.rs -->
# sources/storage-engines/tikv/components/tidb_query_aggr/src/util.rs

Purpose: shared aggregate parser utilities for arity validation and expression rewriting. It centralizes child-expression support checks and cast insertion for numeric and bit-operation aggregate families.

Important APIs and control flow: `check_aggr_exp_supported_one_child` requires exactly one child and delegates child expression validation to `RpnExpressionBuilder::check_expr_tree_supported`. `rewrite_exp_for_sum_avg` inspects the RPN return type and appends a cast node when SUM/AVG/VARIANCE require decimal or real output: ints become decimal except MySQL BIT becomes double; non numeric-ish values become double. `rewrite_exp_for_bit_op` casts non-int inputs to `LongLong`.

State and persistence behavior: no state is kept. The functions mutate `RpnExpression` by pushing cast nodes.

Dependencies and integration: uses `FieldTypeAccessor`, `FieldTypeBuilder`, `FieldTypeTp`, `EvalType`, and `get_cast_fn_rpn_node` from query expression code. It is called by aggregate parsers before schema and implementation selection.

Risks and test signals: rewrite correctness must match TiDB type inference (`typeInfer4Sum`, `typeInfer4Avg`) or parser output schemas will reject requests. Cast insertion relies on `exp.is_last_constant()` and original field type metadata. Tests are indirect through SUM, variance, and bit-op integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_aggr/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_codegen/Cargo.toml -->
# sources/storage-engines/tikv/components/tidb_query_codegen/Cargo.toml

Purpose: declares `tidb_query_codegen`, a non-published Rust 2021 procedural macro crate used by TiDB query components.

Important APIs and control flow: marks the library as `proc-macro = true`. Dependencies include `darling` for derive/attribute parsing, `syn` with full AST support, `quote` and `proc-macro2` for generated tokens, and `heck` for identifier case conversion.

State and persistence behavior: no runtime state; build-time macro crate configuration only.

Dependencies and integration: consumed by aggregate and expression crates through `#[derive(AggrFunction)]` and `#[rpn_fn]`. Workspace-managed dependencies reduce version drift for shared crates.

Risks and test signals: uses nightly-only features in source, so compiler/toolchain compatibility matters. Macro expansion failures surface at compile time in downstream crates.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_codegen/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_codegen/src/aggr_function.rs -->
# sources/storage-engines/tikv/components/tidb_query_codegen/src/aggr_function.rs

Purpose: implements the derive macro backend for aggregate function structs. It generates the boilerplate `crate::AggrFunction` implementation from a `#[aggr_function(state = expr)]` attribute.

Important APIs and control flow: `AggrFunctionStateExpr` parses `state = <expr>`. `AggrFunctionOpts` captures the deriving type's ident, generics, and forwarded `aggr_function` attributes. `generate_tokens` parses the first attribute, turns the struct name into the `name()` string, preserves generics/where clauses, and emits `create_state` returning `Box::new(state_expr)`.

State and persistence behavior: no runtime state beyond generated aggregate state creation. The supplied state expression controls actual aggregate state initialization.

Dependencies and integration: uses `darling::FromDeriveInput`, `syn`, and `quote`. Concrete aggregate structs in `tidb_query_aggr` derive this macro.

Risks and test signals: missing or malformed `#[aggr_function]` attributes panic during macro expansion. It assumes the target crate has `crate::AggrFunction` and `crate::AggrFunctionState` in scope. Coverage is mainly compile-time through downstream aggregate modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_codegen/src/aggr_function.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_codegen/src/lib.rs -->
# sources/storage-engines/tikv/components/tidb_query_codegen/src/lib.rs

Purpose: exports procedural macros for TiDB query components: `AggrFunction` derive and `rpn_fn` attribute. It is the public proc-macro entry point for code generation used by aggregate and scalar expression implementations.

Important APIs and control flow: `aggr_function_derive` parses a `DeriveInput`, converts it through `AggrFunctionOpts::from_derive_input`, and returns generated tokens or panics on validation error. `rpn_fn` passes attribute and function tokens to `rpn_function::transform`, returning either generated tokens or a compile-error token stream.

State and persistence behavior: compile-time only; it emits Rust code and keeps no runtime state.

Dependencies and integration: enables nightly proc-macro diagnostics, iterator ordering, and a higher recursion limit for large generated expressions. It depends on internal `aggr_function` and `rpn_function` modules.

Risks and test signals: derive path panics rather than emitting structured compile errors, whereas `rpn_fn` returns compile errors. Any public macro behavior change has broad downstream compile impact.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_codegen/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_codegen/src/rpn_function.rs -->
# sources/storage-engines/tikv/components/tidb_query_codegen/src/rpn_function.rs

Purpose: implements the `#[rpn_fn]` attribute macro that converts plain Rust scalar functions into TiDB RPN evaluator metadata, validators, evaluators, and vectorized row loops.

Important APIs and control flow: `transform` parses attributes and an `ItemFn`, rejects explicit lifetimes, and selects `VargsRpnFn`, `RawVargsRpnFn`, or `NormalRpnFn`. `RpnFnAttr` parses flags such as `varg`, `raw_varg`, `nullable`, `writer`, argument bounds, metadata hooks, extra validator, and captures. Type parsers recognize `Option<&T>`, `Option<JsonRef>`, `BytesRef`, enum/set refs, and writer guard returns. `ValidatorFnGenerator` emits return-type, arity, argument-type, and custom validation. Normal functions generate a dispatch trait, default unreachable impl, real impl over an argument type list, evaluator struct, and `_fn_meta` constructor. Vararg paths generate row loops using thread-local buffers; raw varargs pass `ScalarValueRef` slices.

State and persistence behavior: generated evaluators are stateless apart from metadata boxed behind `Any`, thread-local temporary argument buffers, writer buffers, and per-call chunked result vectors. No durable state is kept.

Dependencies and integration: relies on `syn`, `quote`, `heck`, `tidb_query_expr` function traits, `tidb_query_datatype` evaluable traits, and `tipb::Expr` validation. Generated `RpnFnMeta` values are consumed by the expression framework to validate and execute pushed-down functions.

Risks and test signals: code generation uses specialization, unsafe transmutes to extend row-local references to static within bounded buffers, null-bit-vector fast paths, and metadata downcasts. Attribute combinations have explicit validation, but generated code assumes caller contracts for lifetimes, argument ordering, and output row count. Tests compare generated token streams for normal, generic, capture, and non-null enum cases and verify type parsing/lifetime helpers.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_codegen/src/rpn_function.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/Cargo.toml -->
# sources/storage-engines/tikv/components/tidb_query_common/Cargo.toml

Purpose: declares the shared `tidb_query_common` crate for TiDB pushed-down executor utilities.

Important APIs and control flow: package metadata marks it non-published and Rust 2021. Dependencies cover errors (`anyhow`, `thiserror`, `error_code`), async traits/futures, protobufs, metrics, tracker integration, logging wrappers, API version support, and scheduling/runtime helpers.

State and persistence behavior: no runtime state in the manifest. It defines build-time dependency boundaries for error handling, statistics, storage abstraction, and metrics modules.

Dependencies and integration: used by query expression, aggregate, and executor crates for `Result`, storage traits, execution summaries, and metrics. Dev dependency `byteorder` supports storage range tests.

Risks and test signals: workspace dependency versions and nightly prometheus feature choices affect downstream compatibility. Manifest itself is validated by Cargo builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/error.rs -->
# sources/storage-engines/tikv/components/tidb_query_common/src/error.rs

Purpose: defines the common error model for query evaluation and storage access. It separates evaluation failures from storage failures while presenting a single `tidb_query_common::Result`.

Important APIs and control flow: `EvaluateError` contains deadline, invalid charset, custom codec-compatible, and generic variants, with MySQL/TiDB-style numeric `code()`. It implements conversions from boxed errors, deadline errors, UTF-8/JSON errors, and `Infallible`. `StorageError` wraps `anyhow::Error`; `ErrorInner` distinguishes storage and evaluate sources; `Error` boxes `ErrorInner`. A default generic `From<T: Into<EvaluateError>> for Error` maps convertible failures to evaluation errors.

State and persistence behavior: stateless error values only. Error codes are computed from variants and integrated with `error_code::ErrorCodeExt`.

Dependencies and integration: used throughout aggregate, expression, and storage scanner code as `Result<T>`. `other_err!` constructs `EvaluateError::Other` values through this module.

Risks and test signals: generic specialization for `From<T>` relies on nightly min specialization and can overlap if new conversions are added. `EvaluateError::Custom` is a compatibility layer, so richer error typing may be hidden. Tests are indirect through consumers that assert failures or error codes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/execute_stats.rs -->
# sources/storage-engines/tikv/components/tidb_query_common/src/execute_stats.rs

Purpose: provides lightweight execution statistics for pushed-down executors and `EXPLAIN ANALYZE` support.

Important APIs and control flow: `ExecSummary` tracks processed time, produced rows, and iteration count, deriving add/add-assign for accumulation. `ExecSummaryCollector` abstracts enabled/disabled collection. `ExecSummaryCollectorEnabled` records coarse start time on iteration start, accumulates elapsed nanoseconds and produced row counts on finish, and moves counts into a target slot on collect. `ExecSummaryCollectorDisabled` compiles the same call pattern into no-ops. `ExecuteStats` bundles per-executor summaries with scanned rows per range.

State and persistence behavior: collectors keep in-memory counters until `collect`, where enabled collection drains by `mem::take`. `ExecuteStats::clear` resets summaries and scanned rows.

Dependencies and integration: depends on `tikv_util::time` and `derive_more`. Executors use these collectors around `next_batch` calls and merge storage scanned-row output.

Risks and test signals: target indexing is unchecked beyond slice indexing, so executor output index bookkeeping must be correct. `usize` counters can theoretically saturate/wrap only through extremely large workloads. Coverage is likely through executor tests rather than this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/execute_stats.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/lib.rs -->
# sources/storage-engines/tikv/components/tidb_query_common/src/lib.rs

Purpose: crate root for common TiDB query utilities. It enables min specialization and exposes modules for macros, errors, execution stats, metrics, storage, and utility helpers.

Important APIs and control flow: exports `macros`, `error`, `execute_stats`, `metrics`, `storage`, and `util`, and re-exports `Error` and `Result` from `error.rs` for convenient downstream use.

State and persistence behavior: no runtime state; module wiring only.

Dependencies and integration: downstream query crates import `tidb_query_common::{Result, Error}` and use exported modules for storage scans, metrics recording, and stats.

Risks and test signals: the crate requires nightly `min_specialization`, matching the specialized conversion/update patterns used by query components. Any module visibility changes are broad API changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/macros.rs -->
# sources/storage-engines/tikv/components/tidb_query_common/src/macros.rs

Purpose: defines the `other_err!` macro used to construct location-tagged evaluation errors.

Important APIs and control flow: `other_err!($msg)` and `other_err!($fmt, args...)` expand to `tidb_query_common::error::Error::from(EvaluateError::Other(format!(...)))`, prefixing messages with `file!()` and `line!()`.

State and persistence behavior: no state. It creates formatted error values at call sites.

Dependencies and integration: imported with `#[macro_use]` from `tidb_query_common`; aggregate parsers and other query modules use it for unsupported or mismatched request errors.

Risks and test signals: macro pattern only accepts a token-tree first argument and one-or-more format args for the formatted variant, so unusual `format!` forms may not match. File/line inclusion aids diagnostics but can make exact error-string assertions brittle.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/macros.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/metrics.rs -->
# sources/storage-engines/tikv/components/tidb_query_common/src/metrics.rs

Purpose: defines coprocessor executor metrics and tracker updates for pushed-down query execution.

Important APIs and control flow: `make_auto_flush_static_metric!` declares `ExecutorName` labels and a local counter type. `COPR_EXECUTOR_COUNT` registers `tikv_coprocessor_executor_count`; `EXECUTOR_COUNT_METRICS` exposes an auto-flushing local metric. `record_executor_work` skips zero work, asserts supported batch executor labels in debug builds, and saturating-adds work counts into the TLS tracker. `record_coprocessor_executor_iterations` similarly records iteration counts.

State and persistence behavior: metrics are held in Prometheus counters and thread-local tracker fields, not durable storage. Saturating additions prevent overflow panics.

Dependencies and integration: depends on `prometheus`, `prometheus_static_metric`, and `tracker::with_tls_tracker`. Executors call these hooks to update observability data.

Risks and test signals: `record_executor_work` only maps a subset of labels; unsupported labels no-op outside debug assertions. Metric registration unwraps at initialization, so duplicate registration or registry failures panic. Coverage is usually integration/metrics based.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/storage/mod.rs -->
# sources/storage-engines/tikv/components/tidb_query_common/src/storage/mod.rs

Purpose: defines the storage abstraction consumed by table/index scan executors and related region lookup interfaces.

Important APIs and control flow: `Storage` exposes range scan lifecycle (`begin_scan`, `scan_next_entry`), point get (`get_entry`), key-only/commit-ts flags, cacheability, and statistics collection. Convenience methods convert `OwnedKvPairEntry` to `(Vec<u8>, Vec<u8>)`. A blanket `Storage` impl for `Box<T>` forwards calls. `FindRegionResult` reports local region lookup success or nearest next region start. `RegionStorageAccessor` asynchronously finds regions and obtains local storage for index lookup. `StubAccessor` is a non-instantiating placeholder returning `None` as an optional accessor.

State and persistence behavior: the trait allows implementations to own scan cursors and statistics, but this module stores no data itself. `OwnedKvPairEntry` can carry optional commit timestamp.

Dependencies and integration: uses `kvproto` key ranges/regions, Raft state roles, `async_trait`, and range types from `range.rs`. `scanner.rs` builds on this trait for multi-range scanning.

Risks and test signals: trait methods take owned `IntervalRange`/`PointRange`, causing allocation/copy TODOs. `StubAccessor` methods are `unimplemented!`, safe only when never instantiated. Correct cacheability depends on storage implementations returning `Some(false)` for cache-safe scans.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/storage/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/storage/range.rs -->
# sources/storage-engines/tikv/components/tidb_query_common/src/storage/range.rs

Purpose: represents point and interval key ranges for the legacy DAG scan path.

Important APIs and control flow: `Range` wraps either `PointRange` or `IntervalRange`. `Range::from_pb_range` turns a protobuf `KeyRange` into a point range when point ranges are accepted and `crate::util::is_point` says the start/end describe one key; otherwise it creates a lower-inclusive/upper-exclusive interval. Debug impls print keys through `log_wrappers::Value::key`. Conversions from byte vectors, strings, and string slices simplify tests and callers.

State and persistence behavior: value types own their key bytes. There is no persistence or cursor state.

Dependencies and integration: used by `RangesIterator` and `RangesScanner`, and by storage implementations receiving scan requests.

Risks and test signals: comments mark this module for removal after DAG v2. String/slice conversions are labeled "Maybe abuse" and are best suited to tests or simple call sites. Point detection depends on external `util::is_point`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/storage/range.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/storage/ranges_iter.rs -->
# sources/storage-engines/tikv/components/tidb_query_common/src/storage/ranges_iter.rs

Purpose: provides a small state machine over user key ranges for scanners. It tells callers whether to start a new range, continue the current interval, or stop.

Important APIs and control flow: `IterStatus` has `Drained`, `NewRange(Range)`, and `Continue`. `RangesIterator` owns an `IntoIter<Range>` and an `in_range` flag. `next` returns `Continue` while a range is active; otherwise it pops the next range or returns drained. `notify_drained` clears the active flag. `is_drained` checks whether no further ranges remain.

State and persistence behavior: in-memory iteration state only. Multiple `notify_drained` calls are idempotent.

Dependencies and integration: `scanner.rs` uses it to coordinate storage `begin_scan`, point gets, and interval `scan_next_entry` calls.

Risks and test signals: `is_drained` ignores `in_range`, so it means "no queued ranges after the current one" rather than "all scanning is complete"; scanner uses that nuance for scanned-range boundary calculations. Tests cover empty/nonempty iteration, continuation, and repeated drain notifications.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/storage/ranges_iter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/storage/scanner.rs -->
# sources/storage-engines/tikv/components/tidb_query_common/src/storage/scanner.rs

Purpose: implements `RangesScanner`, an async scanner over multiple point and interval ranges backed by an abstract `Storage`. It handles scan direction, key-only reads, optional commit timestamps, scanned row accounting, scanned physical range reporting, cacheability checks, and cooperative rescheduling.

Important APIs and control flow: `RangesScannerOptions` carries storage, ranges, scan flags, range-awareness, and commit-ts loading. `RangesScanner::new` initializes the `RangesIterator`, stats buffers, scanned-range buffers, and `RescheduleChecker`. `next` delegates to `next_opt(true)`. `next_opt` loops over `IterStatus`: point ranges call `get_entry` and drain immediately; new intervals call `begin_scan` then `scan_next_entry`; continues call `scan_next_entry`; drained updates scanned range and returns `None`. Non-null rows increment the last range count, trigger reschedule checks, convert `(key,value,commit_ts)` through `KvFormat::make_kv_pair`, and return. Empty reads notify range drained and continue.

State and persistence behavior: state includes the storage cursor, range iterator, per-range scanned row counts, current/working scanned range boundaries, and reschedule counters. `collect_storage_stats` delegates to storage; `collect_scanned_rows_per_range` drains row counts into a destination then seeds a new zero bucket; `take_scanned_range` returns and advances working boundaries for streaming partial retry. No durable persistence is performed.

Dependencies and integration: depends on `api_version::KvFormat` to shape returned kv entries, `yatp::task::future::reschedule` for coroutine fairness, storage/range traits from this crate, and `tikv_util::time`. Executors use it as the common multi-range scan primitive.

Risks and test signals: scanned range correctness assumes ordered ranges; comments warn unordered ranges make streaming retry ranges unsound. `take_scanned_range` asserts range awareness is enabled. Rescheduling checks every 32 scanned keys or on new range when elapsed time exceeds 1 ms. Tests cover forward/backward scans, key-only mode, scanned-row collection, forward/backward scanned range reporting, empty ranges, point ranges, and `next_opt(false)` behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/storage/scanner.rs -->
