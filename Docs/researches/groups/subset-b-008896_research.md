# subset-b-008896 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/impl_time.rs -->
# sources/storage-engines/tikv/components/tidb_query_expr/src/impl_time.rs

## Purpose

`impl_time.rs` implements TiDB/TiKV pushed-down scalar time, date, duration, interval, Unix timestamp, and parsing functions for the RPN expression engine. The functions are annotated with `#[rpn_fn]`, so `tidb_query_codegen` generates `*_fn_meta()` entries consumed by the crate-level dispatcher in `lib.rs`. The implementation is deliberately close to MySQL/TiDB semantics: it propagates SQL `NULL`, records warnings through `EvalContext`, respects SQL modes such as `NO_ZERO_DATE`, clamps MySQL `TIME` ranges, honors return field fractional-second precision, and converts invalid or overflowed values to either warnings plus `NULL` or hard errors depending on the context configuration.

This file has no storage-layer persistence. Its stateful behavior is evaluation-local: it reads `EvalContext` for timezone, SQL mode, statement flags, and warning/overflow policy; it reads `RpnFnCallExtra.ret_field_type` for return precision; and for interval functions it builds immutable per-expression metadata from the protobuf `Expr` tree.

## Important APIs, types, and functions

The basic date/time extractors and formatters include `date_format`, `date`, `sysdate_with_fsp`, `sysdate_without_fsp`, `week_with_mode`, `week_without_mode`, `week_day`, `day_of_week`, `day_of_year`, `week_of_year`, `year_week_with_mode`, `year_week_without_mode`, `to_days`, `to_seconds`, `month`, `month_name`, `hour`, `minute`, `second`, `time_to_sec`, `micro_second`, `year`, `day_of_month`, `day_name`, `period_add`, `period_diff`, `last_day`, and `quarter`. Most reject invalid zero dates by routing `Error::incorrect_datetime_value` through `ctx.handle_invalid_time_error`. `year` and `day_of_month` are special because a full zero date can return `0` unless `NO_ZERO_DATE` is active.

The time arithmetic surface includes `add_string_and_duration`, `sub_string_and_duration`, `date_diff`, `null_time_diff`, `add_datetime_and_duration`, `add_datetime_and_string`, `add_date_and_string`, `sub_duration_and_duration`, `sub_datetime_and_duration`, `sub_datetime_and_string`, `sub_duration_and_string`, `add_duration_and_duration`, `add_duration_and_string`, and the four `*_time_diff` variants. These functions parse `BytesRef` operands as `Duration` or `DateTime` as MySQL would, use checked arithmetic helpers from `tidb_query_datatype::codec::mysql`, and convert overflow to the configured invalid-time or overflow behavior. The `add_time_*_null` functions intentionally return `NULL` for unsupported `ADDTIME` result combinations registered in `lib.rs`.

`make_date` and `make_time` construct values from numeric parts. `make_date` applies MySQL's two-digit year conversion (`0..69` maps to `2000..2069`, `70..99` maps to `1970..1999`) and computes day-of-year against the proleptic calendar. `make_time` inspects argument field metadata through captured `args` to decide whether the hour argument is signed, validates minute/second ranges, clamps overflow to the MySQL maximum `838:59:59`, and uses `extra.ret_field_type.get_decimal()` as the result FSP.

The `ADDDATE`/`SUBDATE` interval family is centered on `AddSubDateMeta`, `build_add_sub_date_meta`, `AddSubDateConvertToTime`, `add_date`, `sub_date`, and the `add_sub_date_time_*` helpers. `build_add_sub_date_meta` validates the three-argument expression shape, extracts the interval unit literal from child 2, records whether the unit is a clock unit, and captures signedness/FSP details from the interval child field type. `AddSubDateConvertToTime` converts string, integer, real, decimal, and datetime operands into `Time`, changing the time type to `DateTime` for clock units and timestamps. The public generic wrappers cover all combinations of time operand type, interval operand type, and return type used by TiDB signatures, for example `add_date_time_string_interval_any_as_string`, `sub_date_time_datetime_interval_any_as_datetime`, and `add_date_time_duration_interval_any_as_duration`.

Unix timestamp support is implemented by `from_unixtime_1_arg`, `from_unixtime_2_arg`, `eval_from_unixtime`, `unix_timestamp_int`, `unix_timestamp_decimal`, `get_micro_timestamp`, `unix_timestamp_to_mysql_unix_timestamp`, and `find_zone_transition`. `eval_from_unixtime` accepts `Decimal` timestamps in the MySQL-supported range `0..=32536771199.999999`, splits integral and fractional parts, converts the fractional part to nanoseconds, and delegates to `DateTime::from_unixtime`. `get_micro_timestamp` builds a local `chrono` naive datetime, asks the configured TiDB timezone for the earliest mapped instant, and uses `find_zone_transition` for nonexistent local times at DST transitions. `unix_timestamp_to_mysql_unix_timestamp` returns `0` outside MySQL's supported timestamp range and truncates decimal output to the requested FSP.

`timestamp_diff` uses `build_timestamp_diff_meta` to parse and validate the interval unit literal before evaluation. Runtime evaluation rejects invalid zero endpoints and delegates to `DateTime::timestamp_diff`.

`str_to_date_date`, `str_to_date_datetime`, and `str_to_date_duration` call `Time::parse_from_string_with_format`, translate parse failure into truncation warnings plus `NULL`, enforce `NO_ZERO_DATE` for date/datetime return paths, and set the final type/FSP according to the signature and `RpnFnCallExtra`.

## Control flow and error handling

Most public functions follow the same RPN scalar pattern: accept nullable `Option` operands when the SQL function is nullable, return `Ok(None)` for `NULL` inputs, convert bytes with `from_utf8` or `std::str::from_utf8`, perform datatype parsing or arithmetic, and route domain errors through `EvalContext`. This is important because the same Rust error can be a warning plus `NULL` or a hard evaluation error depending on SQL mode and statement flags.

String plus/minus duration has a two-stage parse flow: first try exact `Duration`, then try `DateTime`, then issue an invalid datetime warning and return `NULL`. Datetime plus/minus string is stricter: parse the string as a `Duration`, return `NULL` on parse failure, then perform checked datetime arithmetic. Duration time-diff has additional clamping logic for results beyond MySQL `TIME` bounds but still representable within `i64` nanoseconds.

Interval add/sub wrappers use metadata captured at expression-build time rather than reparsing the interval unit for every row. Runtime control flow is: convert the time operand, convert the interval operand into an interval string using metadata signedness/decimal information, parse it into either an `Interval` or `Duration`, call the selected operation (`add_date`, `sub_date`, `Duration::checked_add`, or `Duration::checked_sub`), normalize FSP or string representation, and return the requested type. This structure is the main integration point between protobuf planning metadata and vectorized row evaluation.

Timezone conversion for `UNIX_TIMESTAMP` has a notable DST branch. If a local datetime maps to multiple instants, MySQL-compatible behavior selects the earliest. If it maps to no instant, the code binary-searches for the timezone transition within a 24-hour window and returns the transition instant. This creates a dependency on `chrono`, `chrono_tz`, and the configured `Tz`.

## State and persistence behavior

The file does not read or write durable state. All mutable state is scoped to evaluation:

- `EvalContext` accumulates warnings and provides SQL mode, timezone, and error policy.
- `RpnFnCallExtra` supplies return field metadata such as FSP.
- Generated `rpn_fn` metadata stores `AddSubDateMeta` or `IntervalUnit` as boxed per-expression metadata.
- Writer functions use `BytesWriter` and return `BytesGuard`, so string results are produced into the vectorized evaluation arena rather than persisted.

## Dependencies and integration points

The implementation depends heavily on `tidb_query_datatype::codec::mysql::{Time, Duration, Interval, IntervalUnit, WeekMode, Tz}` and associated conversion traits. It also uses `tidb_query_datatype::expr::{EvalContext, SqlMode}`, `FieldTypeAccessor`, `FieldTypeFlag`, `Decimal`, `Real`, `BytesRef`, `BytesWriter`, and `DateTime` aliases from the datatype codec. The `#[rpn_fn]` macro generates function metadata exported through this crate and selected by `lib.rs` for `tipb::ScalarFuncSig` variants.

The file integrates with `RpnExpressionBuilder` via metadata mappers (`build_add_sub_date_meta`, `build_timestamp_diff_meta`) and with vectorized execution through generated RPN stack adapters. Tests use `RpnFnScalarEvaluator`, `ExprDefBuilder`, and `LazyBatchColumnVec` to exercise both direct scalar evaluation and full expression-tree build/eval paths.

## Risks and edge cases

The highest-risk areas are MySQL compatibility and boundary behavior. Zero dates and incomplete dates are accepted by some functions and rejected by others. This is intentional but easy to regress if helpers are consolidated without preserving per-function SQL-mode semantics. Timezone behavior around DST gaps/overlaps is another sensitive path because it relies on `chrono_tz` mapping and a bounded binary search. Decimal timestamp conversion must preserve truncation and overflow behavior exactly, especially when multiplying fractional seconds to nanoseconds.

The interval family has a broad generic surface. A mismatch between a `ScalarFuncSig` mapping in `lib.rs`, its field types, and the generic wrapper selected here can produce wrong parsing rules or wrong return types. `make_time` depends on captured argument field signedness and return FSP; bugs here can appear only for unsigned hour operands or invalid FSP. Duration arithmetic intentionally clamps some out-of-range diffs to MySQL `TIME` extrema but treats i64 overflow as invalid; that distinction should remain explicit.

## Test signals

The in-file test module is broad. It covers formatting tokens, date extraction, all week modes, zero-date behavior, `TO_DAYS`/`TO_SECONDS`, string/duration addition and subtraction, `DATE_DIFF`, null-only signatures, date/datetime/duration arithmetic, `FROM_DAYS`, `MAKEDATE`, `MAKETIME`, month/day names and warning codes, period math, `LAST_DAY`, duration `TIMEDIFF` clamping, `QUARTER`, the large `ADDDATE`/`SUBDATE` signature matrix, `FROM_UNIXTIME`, `UNIX_TIMESTAMP` with offsets and named timezones, `TIMESTAMPDIFF`, and many `STR_TO_DATE` parsing patterns and failure cases. The tests are strong regression indicators for MySQL compatibility, but there is less explicit property coverage for arbitrary timezone databases, decimal edge overflow beyond listed cases, and future changes to interval-unit parsing.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/impl_time.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/impl_vec.rs -->
# sources/storage-engines/tikv/components/tidb_query_expr/src/impl_vec.rs

## Purpose

`impl_vec.rs` implements TiDB vector scalar functions for the RPN expression engine. It provides text conversion, dimension counting, L1/L2 distances, negative inner product, cosine distance, and L2 norm for `VectorFloat32` values. Each function is annotated with `#[rpn_fn]`, so the codegen layer emits metadata consumed by `lib.rs` for `ScalarFuncSig::Vec*` dispatch.

## Important APIs, types, and functions

The core functions are small wrappers around `VectorFloat32Ref` methods:

- `vec_as_text(a, writer)` converts a vector to its textual representation and writes it through `BytesWriter`.
- `vec_dims(arg)` returns `arg.len()` as TiDB `Int`.
- `vec_l1_distance(a, b)` calls `a.l1_distance(b)?`.
- `vec_l2_distance(a, b)` calls `a.l2_distance(b)?`.
- `vec_negative_inner_product(a, b)` calls `a.inner_product(b)?` and negates the result.
- `vec_cosine_distance(a, b)` calls `a.cosine_distance(b)?`.
- `vec_l2_norm(a)` calls `a.l2_norm()`.

Distance and norm results are wrapped with `Real::new(...).ok()`. The comment explains the reason: TiKV does not support NaN as a SQL `Real`, so NaN converts to `NULL`. Infinite values are accepted when `Real::new` permits them, which is covered by tests with very large components.

## Control flow and error handling

There is no complex control flow. The binary distance functions delegate dimension checks and numeric computation to the vector datatype implementation. A mismatched vector length propagates as an error from the datatype method. Nullable behavior is mostly provided by the generated `rpn_fn` adapter: tests show that `NULL` vector operands produce `NULL` results for distance functions without entering the body with invalid references.

The writer function `vec_as_text` writes `Some(Bytes::from(a.to_string()))` to the output arena and returns a `BytesGuard`. Numeric functions return `Result<Option<Real>>` or `Result<Option<Int>>`, matching SQL nullability.

## State and persistence behavior

The file has no persistent state and no mutable global state. All behavior is pure with respect to vector inputs except for writing text results into the provided `BytesWriter`. Errors and nulls are returned directly through the RPN evaluation result path.

## Dependencies and integration points

The file depends on `tidb_query_codegen::rpn_fn`, `tidb_query_common::Result`, and `tidb_query_datatype::codec::data_type::*` for `VectorFloat32Ref`, `VectorFloat32`, `Bytes`, `BytesWriter`, `BytesGuard`, `Int`, and `Real`. It integrates with the crate-level dispatcher in `lib.rs`, which maps `ScalarFuncSig::VecAsTextSig`, `VecDimsSig`, `VecL1DistanceSig`, `VecL2DistanceSig`, `VecNegativeInnerProductSig`, `VecCosineDistanceSig`, and `VecL2NormSig` to the generated metadata functions.

## Risks and edge cases

The main correctness risks are numeric edge cases and consistency with TiDB's vector semantics. NaN is intentionally translated to `NULL`, notably for cosine distance involving zero vectors or overflow patterns. Dimension mismatch must continue to be an error rather than `NULL`. Very large `f32` values can produce infinities, and the tests show expected infinite `Real` values for L1/L2 distance and negative inner product. Since the implementation delegates to datatype methods, future changes in vector distance definitions will flow through here.

## Test signals

Tests cover dimensions for empty and non-empty vectors, L2 norm, L1/L2 distance, negative inner product, cosine distance, null operands, dimension mismatch errors, NaN-to-NULL behavior, and overflow to infinity. The cases are ported from pgvector expected output, giving a useful compatibility signal for common vector database semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/impl_vec.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/lib.rs -->
# sources/storage-engines/tikv/components/tidb_query_expr/src/lib.rs

## Purpose

`lib.rs` is the root of the `tidb_query_expr` crate. It declares the expression implementation modules, re-exports public expression types, imports all generated RPN function metadata, and implements the central mapping from TiDB protobuf scalar function signatures (`tipb::ScalarFuncSig`) to executable `RpnFnMeta`. This is the crate-level dispatch table that lets pushed-down TiDB expressions run inside TiKV's coprocessor/vectorized query engine.

The crate documentation states the broader role: scanning and understanding TiDB rows, running pushed-down executors, returning execution results through the TiKV coprocessor interface, and exporting standalone UDF-like scalar functions.

## Important APIs, types, and functions

Module declarations expose `types` and implementation modules including arithmetic, cast, compare, control, encryption, JSON, LIKE, math, miscellaneous, op, regexp, string, time, and vector functions. `pub use self::types::*` makes RPN expression types available to downstream crates.

The helper mappers select specialized `RpnFnMeta` values based on field metadata:

- `map_to_binary_fn_sig` and `map_from_binary_fn_sig` choose charset-specialized binary conversion functions.
- `map_string_compare_sig`, `map_compare_in_string_sig`, `map_regexp_*`, `map_locate_*_utf8_sig`, `map_strcmp_sig`, `map_find_in_set_sig`, `map_ord_sig`, and `map_field_string_sig` choose collation-specialized string functions.
- `map_like_sig` selects both collation and charset behavior for SQL `LIKE`, using target/pattern charset compatibility to avoid incorrect `_` matching when TiDB has not pushed complete collation information.
- `map_int_sig` and `map_rhs_int_sig` inspect child `FieldTypeFlag::UNSIGNED` flags and select signed/unsigned arithmetic, comparison, division, modulo, and truncation implementations.
- `map_unary_minus_int_func`, `map_upper_utf8_sig`, and `map_lower_utf8_sig` validate arity and choose metadata based on signedness or charset.

`map_expr_node_to_rpn_func(expr)` is the large `ScalarFuncSig` match. It maps every supported pushed-down scalar signature to generated metadata, including the time functions from `impl_time.rs` and vector functions from `impl_vec.rs`. Unsupported signatures return an `other_err!("ScalarFunction ... is not supported in batch mode")`.

## Control flow and dispatch behavior

The dispatch path is: read the protobuf `Expr`, inspect `expr.get_sig()`, inspect child field types or return field type where needed, choose a generated `RpnFnMeta`, and return it to expression building. Some signatures map directly to a metadata function. Others go through helper mappers so runtime evaluation gets a monomorphized implementation matching unsigned integer combinations, charset/collation, return type, interval metadata, or argument count.

The match is organized by implementation module. It covers arithmetic, casts including vector casts, comparison and `IN`, control flow, encryption, JSON, vector functions, LIKE/regexp, math, miscellaneous functions, boolean/bit ops, string functions, and time functions. The time section wires many `ADDDATE`/`SUBDATE` variants to generic metadata functions with concrete type parameters, which must align exactly with TiDB planner signatures.

## State and persistence behavior

`lib.rs` does not store persistent state. It is a pure mapping layer from protobuf expression metadata to function metadata. The selected `RpnFnMeta` may carry function-specific metadata mappers that later build boxed metadata, but this file itself only chooses the function. Errors are returned as `tidb_query_common::Result`.

## Dependencies and integration points

This file depends on TiDB/TiKV datatype metadata (`Charset`, `Collation`, `FieldTypeAccessor`, `FieldTypeFlag`, collator templates, and datatype aliases), `tipb::{Expr, FieldType, ScalarFuncSig}`, and the generated metadata functions from every `impl_*` module. It is tightly coupled to:

- `RpnExpressionBuilder`, which calls this mapper when converting protobuf expression trees to RPN nodes.
- `tipb` signature definitions generated from TiDB protobufs.
- `tidb_query_codegen::rpn_fn`, which creates the `*_fn_meta()` functions referenced here.
- `tidb_query_datatype` field flags, charset, collation, and eval type semantics.

## Risks and edge cases

This file is a high-blast-radius compatibility table. Adding a new scalar function requires both an implementation and a correct mapping here. Incorrect signedness mapping can silently change overflow or comparison behavior. Incorrect collation mapping can produce wrong string comparisons, `LIKE`, regexp, `FIELD`, `FIND_IN_SET`, or `ORD` results. The `map_like_sig` compatibility branch is especially sensitive because it compensates for incomplete collation pushdown from TiDB.

The time and vector entries show how new function families are integrated. The vector mappings are direct and low-risk, but they require `ScalarFuncSig` names to stay synchronized. The time `ADDDATE`/`SUBDATE` mappings are riskier because many signatures share generic wrappers with type parameters; a single wrong type parameter can parse inputs using the wrong conversion trait or return a wrong SQL type.

## Test signals

This file has no local test module in the read content, so coverage is mostly indirect. Every implementation module's `RpnFnScalarEvaluator` tests relies on this dispatch mapping when evaluating by `ScalarFuncSig`. The `impl_time.rs` tests also build real protobuf expression trees for interval and timestamp-diff cases, giving stronger coverage for metadata mappers and dispatch alignment. `impl_vec.rs` tests cover the direct vector signature mappings through scalar evaluation. Remaining risk is for signatures not exercised by nearby module tests and for newly added `tipb::ScalarFuncSig` variants that fall into the unsupported default.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/types/expr.rs -->
# sources/storage-engines/tikv/components/tidb_query_expr/src/types/expr.rs

## Purpose

`types/expr.rs` defines the in-memory Reverse Polish Notation expression representation used by `tidb_query_expr`. It provides node variants for function calls, constants, and column references, plus a thin `RpnExpression` wrapper around a vector of nodes. Expression evaluation itself lives elsewhere (`expr_eval`), but this file defines the core shape that builders, evaluators, and tests share.

## Important APIs, types, and functions

`RpnExpressionNode` has three variants:

- `FnCall { func_meta, args_len, field_type, metadata }` represents a scalar function invocation. `func_meta` is the generated/executable `RpnFnMeta`, `args_len` describes stack arity, `field_type` stores the return type, and `metadata: Box<dyn Any + Send>` stores function-specific metadata such as parsed interval units.
- `Constant { value, field_type }` stores a scalar value and its TiDB field type.
- `ColumnRef { offset }` references a column by schema/evaluation offset.

Test-only helpers expose internals for assertions: `field_type`, `expr_tp`, `fn_call_func`, and `constant_value`. `expr_tp` maps stored `ScalarValue` eval types back to protobuf `ExprType`, including newer `VectorFloat32` as `TiDbVectorFloat32`.

`RpnExpression(Vec<RpnExpressionNode>)` implements `Deref<Target = Vec<RpnExpressionNode>>`, `DerefMut`, `From<Vec<RpnExpressionNode>>`, `AsRef<[RpnExpressionNode]>`, and `AsMut<[RpnExpressionNode]>`. Its public methods are:

- `ret_field_type(schema)` returns the field type of the expression result, using the last RPN node and consulting the external schema for a trailing `ColumnRef`.
- `into_inner()` unwraps the vector.
- `is_last_constant()` checks whether the final node is a constant.

## Control flow and behavior

The file contains simple pattern matching. RPN expressions are expected to be non-empty when asking for return type or last-constant status; both methods assert that invariant. `ret_field_type` uses the final node because RPN evaluation leaves the expression result at the top of the stack, so the final node determines result type for function calls/constants or identifies the result column for column references.

The test-only `expr_tp` helper maps constants by their `ScalarValue::eval_type()`. Function calls always report `ExprType::ScalarFunc`; column refs report `ExprType::ColumnRef`.

## State and persistence behavior

There is no persistence. The state is an owned vector of expression nodes. Per-function metadata is type-erased with `Any + Send`, which allows the builder to attach arbitrary immutable metadata while keeping the node enum uniform. That type erasure means consumers must downcast consistently with the selected `RpnFnMeta`; the safety of that contract is established by builder/codegen conventions rather than the Rust type system in this file.

## Dependencies and integration points

The file depends on `tidb_query_datatype::codec::data_type::ScalarValue`, `tipb::FieldType`, and `super::super::function::RpnFnMeta`. It is used by expression builders that translate protobuf `Expr` trees to RPN, by evaluators that execute RPN nodes over row batches, and by tests that inspect generated RPN structure.

The comments explicitly point to `RpnExpressionBuilder` as the preferred construction path and to the `expr_eval` file for evaluation. `lib.rs` supplies the function metadata that becomes `RpnExpressionNode::FnCall.func_meta`.

## Risks and edge cases

The main invariant risk is empty expressions: `ret_field_type` and `is_last_constant` panic if called on an empty expression. Another risk is schema mismatch for `ColumnRef`; `ret_field_type` indexes `schema[*offset]` directly and will panic if the offset is out of range. The type-erased `metadata` field is flexible but can hide mismatches until runtime if a function is paired with metadata of the wrong concrete type.

Because `Deref` and `DerefMut` expose the inner vector, callers can mutate the expression freely and potentially break builder invariants. That is convenient for internal code but should be treated as a trusted-module API rather than a defensive abstraction.

## Test signals

This file's helper methods are compiled only under `#[cfg(test)]`, so direct tests elsewhere can assert field types, protobuf expression types, function metadata identity, and constant values. There is no local test module in the file. Coverage comes indirectly from expression builder/evaluator tests across the crate, especially tests that build protobuf expressions and then evaluate or inspect RPN nodes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/types/expr.rs -->
