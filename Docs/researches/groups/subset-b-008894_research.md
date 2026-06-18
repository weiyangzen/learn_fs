# Research Group subset-b-008894

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/impl_math.rs -->
# sources/storage-engines/tikv/components/tidb_query_expr/src/impl_math.rs

## Purpose
`impl_math.rs` implements TiDB/TiKV RPN scalar functions for SQL mathematical operations. It covers constants and checksums, logarithms, trigonometry, exponentiation, sign and square root, ceiling/floor/absolute value variants, MySQL-compatible random numbers, base conversion through `CONV`, rounding, and truncation for integer, unsigned integer, real, and decimal values.

## Important APIs, Types, and Functions
Functions are exported through `#[rpn_fn]` metadata and are wired from `tidb_query_expr/src/lib.rs` by `ScalarFuncSig` entries such as `Pi`, `Crc32`, `Log1Arg`, `CeilReal`, `FloorDecToInt`, `AbsInt`, `Sin`, `Pow`, `Rand`, `Conv`, `RoundWithFracReal`, and `TruncateDecimal`.

The file uses trait families to share generic RPN entry points while preserving SQL type-specific return types. `ceil<C: Ceil>` dispatches to implementations such as `CeilReal`, `CeilDecToDec`, `CeilIntToDec`, `CeilDecToInt`, and `CeilIntToInt`. `floor<T: Floor>` mirrors that with `FloorReal`, `FloorIntToDec`, `FloorDecToInt`, `FloorDecToDec`, and `FloorIntToInt`.

Key helpers include `f64_to_real`, which maps non-finite floating results to SQL `NULL`; `truncate_real`, which avoids changing values when decimal shifting overflows to infinity; `i64_to_usize`, a shared signed/unsigned magnitude helper used by string functions; and `IntWithSign`, which models signed base and signed numeric conversion for `CONV`. `MySqlRng` stores MySQL-compatible `RAND` state with `seed1` and `seed2`; a thread-local `MYSQL_RNG: RefCell<MySqlRng>` backs unseeded `RAND()`.

## Control Flow
Most functions are thin, type-specific RPN leaves: arguments are already decoded by the expression engine, operations run over TiDB wrapper types such as `Real` and `Decimal`, and return values are `Result<Option<T>>` so SQL `NULL` and evaluation errors are distinct.

Floating functions generally compute with Rust `f64`, then call `Real::new(...).ok()` or `f64_to_real`. Invalid mathematical domains such as logarithm of non-positive numbers, square root of negative values, and inverse trig outside range become `None`, while explicit overflows in `exp`, `cot`, `pow`, and `degrees` become `Error::overflow`.

Decimal ceiling, floor, rounding, and truncation delegate to `Decimal` APIs and convert codec results through `into_result(ctx)` when an `EvalContext` is needed for warning/error handling. Integer truncation selects a signed or unsigned path based on the mapped RHS field type in `lib.rs`: non-negative precision returns the original integer; sufficiently negative precision collapses to zero; intermediate negative precision divides and multiplies by a power of ten.

`CONV` trims input bytes as UTF-8 lossy text, validates source and target bases in the inclusive range 2..=36, extracts an optional sign and the maximal valid digit prefix, parses with `u64::from_str_radix`, clamps signed values where MySQL behavior requires it, and formats with uppercase digits in the target base. Invalid bases return `NULL`; strings without a valid digit prefix return `"0"`; numeric overflow returns a `BIGINT UNSIGNED` overflow error.

## State and Persistence Behavior
This file has no durable storage behavior. The only state is per-thread process memory in `MYSQL_RNG`. `rand()` advances the thread-local generator every call. `rand_with_seed_first_gen(seed)` constructs a temporary `MySqlRng` and returns only the first generated value, so it is deterministic for a given seed and does not mutate `MYSQL_RNG`.

## Dependencies and Integration Points
Dependencies include `tidb_query_codegen::rpn_fn`, `tidb_query_common::Result`, TiDB datatype wrappers from `tidb_query_datatype::codec::data_type`, `EvalContext`, MySQL decimal round modes, `file_system::calc_crc32_bytes`, `tikv_util::time::get_time`, and `num`/`num_traits` math helpers. Integration is through `lib.rs` scalar signature dispatch, plus `impl_string.rs` imports `i64_to_usize` for string-position logic.

## Risks and Edge Cases
The highest-risk behavior is compatibility with MySQL/TiDB numeric semantics rather than algorithmic complexity. Floating operations must consistently choose between `NULL` and overflow errors for `NaN` or infinite results. `Real::new(f64::INFINITY).unwrap()` appears in tests for some paths, so behavior depends on the local `Real` wrapper allowing infinity while rejecting `NaN` in other paths.

`CONV` is subtle because negative bases mean signed interpretation, positive bases mean unsigned interpretation, and signed overflow is clamped rather than always errored. The target-base sign flag also affects whether a negative sign is emitted or the value is formatted through two's-complement representation.

Rounding and truncation for very large positive/negative precisions clamp to `i32` or `i8` ranges. `round_with_frac_int` uses floating arithmetic to round integers at negative precisions, which is compact but can be precision-sensitive for very large integers. `RAND()` state is thread-local, so parallel evaluation can produce per-thread sequences.

## Test Signals
Inline tests are broad. They cover pi, crc32, logarithm domains, all ceiling/floor variants, absolute value overflow on `i64::MIN`, sign, sqrt, radians/degrees, exp overflow, trig functions, cot and pow overflow, seeded and unseeded random generation, inverse trig domains, `CONV` valid/invalid/error cases, round/truncate variants for signed, unsigned, real, and decimal inputs, fractional rounding, and direct `MySqlRng` seed behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/impl_math.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/impl_miscellaneous.rs -->
# sources/storage-engines/tikv/components/tidb_query_expr/src/impl_miscellaneous.rs

## Purpose
`impl_miscellaneous.rs` implements miscellaneous TiDB scalar functions that do not fit arithmetic, string, or comparison modules. It provides `ANY_VALUE` for multiple data families, IPv4/IPv6 conversion and predicate functions, and UUID generation, version extraction, and timestamp extraction.

## Important APIs, Types, and Functions
The generic `any_value<T>` returns the first variadic argument for scalar types implementing `Evaluable + EvaluableRet`. Specialized variants handle owned outputs for borrowed data: `any_value_json`, `any_value_vector_float32`, and `any_value_bytes`.

Network functions include `inet_aton`, `inet_ntoa`, `inet6_aton`, `inet6_ntoa`, `is_ipv4`, `is_ipv4_compat`, `is_ipv4_mapped`, and `is_ipv6`. Constants `IPV4_LENGTH`, `IPV6_LENGTH`, `PREFIX_COMPAT`, and `PREFIX_MAPPED` encode byte-length and IPv4-in-IPv6 prefix checks.

UUID functions are `uuid`, `uuid_version`, and `uuid_timestamp`. `uuid` creates an RFC 4122 version-1 UUID using random node bytes with the multicast bit set. `uuid_version` parses any UUID string accepted by the `uuid` crate and returns the version number. `uuid_timestamp` returns a decimal UNIX timestamp, with microsecond precision, for UUID versions that contain a timestamp.

## Control Flow
`ANY_VALUE` functions are simple variadic RPN functions: an empty argument list returns `NULL`; otherwise the first argument is cloned or copied into the result, preserving `NULL` if the first argument is `NULL`.

`inet_aton` manually parses a lossy UTF-8 string as MySQL IPv4 notation. It accepts one to four dot-separated decimal components, rejects empty strings, trailing dots, too many dots, non-digits, and octets above 255, and left-shifts shorter forms according to MySQL rules before returning a 32-bit address as `i64`. `inet_ntoa` does the reverse only when the input can be converted to `u32`.

`inet6_aton` first tries `Ipv6Addr::from_str`, then falls back to `Ipv4Addr::from_str`, returning raw octets. `inet6_ntoa` formats raw 16-byte values as IPv6 and raw 4-byte values as IPv4; all other lengths return `NULL`. `is_ipv4` and `is_ipv6` require valid UTF-8 text before parsing with standard library address parsers. `is_ipv4_compat` and `is_ipv4_mapped` operate on raw 16-byte addresses and compare fixed prefixes.

`uuid_timestamp` parses the string, obtains the embedded timestamp if present, converts seconds and nanoseconds into microseconds since the UNIX epoch, shifts a `Decimal` by -6, and truncates to six decimal places.

## State and Persistence Behavior
The module has no persistence. `uuid` uses `rand::thread_rng()` for a transient node id and the `uuid` crate's current timestamp source. All network and UUID parsing functions are pure with respect to repository and storage state.

## Dependencies and Integration Points
The file depends on standard `Ipv4Addr`/`Ipv6Addr`, `TryFrom`/`TryInto`, `FromStr`, `rand::Rng`, `uuid::Uuid`, TiDB data types including `Decimal`, `Json`, `VectorFloat32`, `DateTime`, and MySQL `RoundMode`. Integration occurs through `lib.rs` scalar signature mapping for `DecimalAnyValue`, `DurationAnyValue`, `IntAnyValue`, `JsonAnyValue`, `VectorFloat32AnyValue`, `InetAton`, `IsIPv6`, `Uuid`, and related signatures.

## Risks and Edge Cases
`inet_aton` intentionally implements MySQL's permissive short IPv4 forms, so changes to parsing must preserve one-, two-, and three-component semantics. It uses `String::from_utf8_lossy`, while `is_ipv4` and `is_ipv6` reject invalid UTF-8 by returning `0`; this difference is deliberate but easy to overlook.

IPv6 formatting relies on Rust standard library canonical formatting. Tests already note a Rust library formatting issue for IPv4-compatible IPv6 display, so exact output can depend on standard library behavior. `uuid_timestamp` only works for UUID versions with embedded timestamps; unsupported versions return `NULL`. It unwraps after an explicit parse error check, so the code is safe under the local control flow but brittle if refactored carelessly.

## Test Signals
Tests cover all `ANY_VALUE` families, including empty and multi-argument cases; IPv4 parsing and formatting, including invalid dotted forms; IPv6 and IPv4 octet conversion; IPv4-compatible and IPv4-mapped prefix checks; IPv4/IPv6 string predicates; UUID shape and version 1 generation; UUID version extraction for versions 1, 3, 4, 5, 6, and 7; and timestamp extraction for timestamped versus non-timestamped UUIDs.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/impl_miscellaneous.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/impl_op.rs -->
# sources/storage-engines/tikv/components/tidb_query_expr/src/impl_op.rs

## Purpose
`impl_op.rs` implements SQL logical, null, truthiness, unary, and bitwise operators for the RPN expression engine. It is the operator layer for three-valued boolean logic, `IS NULL`, `IS TRUE`, `IS FALSE`, unary negation, unary not, bit operations, and left/right shifts.

## Important APIs, Types, and Functions
Logical functions are `logical_and`, `logical_or`, and `logical_xor`. Unary predicates and operators include `unary_not_int`, `unary_not_real`, `unary_not_decimal`, `unary_not_json`, `unary_minus_uint`, `unary_minus_int`, `unary_minus_real`, and `unary_minus_decimal`.

Null checks are factored through `is_null_ref<'a, T: EvaluableRef<'a>>` with typed RPN wrappers `is_null<T>`, `is_null_bytes`, `is_null_json`, and `is_null_vector_float32`. Bitwise functions include `bit_and`, `bit_or`, `bit_xor`, `bit_neg`, `left_shift`, and `right_shift`.

`KeepNull` is a compile-time policy trait with `KeepNullOn` and `KeepNullOff`. It parameterizes `int_is_true`, `real_is_true`, `decimal_is_true`, `int_is_false`, `real_is_false`, and `decimal_is_false` so `IS TRUE` style signatures can either preserve `NULL` or collapse `NULL` to false depending on the TiDB scalar signature.

## Control Flow
The logical functions encode SQL three-valued logic directly. `logical_and` returns `0` if either side is explicit zero, returns `NULL` if no zero exists but at least one side is `NULL`, and otherwise returns `1`. `logical_or` returns `1` for any nonzero input, `0` only when both are zero, and `NULL` for `NULL OR false` or `NULL OR NULL`. `logical_xor` requires both operands to be non-null and returns whether exactly one operand is logically nonzero.

Unary not maps zero to `1` and nonzero to `0` for int, real, and decimal inputs. JSON unary not compares only against JSON numeric zero. Unary minus for signed integers checks `i64::MIN` overflow; unary minus for unsigned values interprets the input bits as `u64`, allows exactly `i64::MAX + 1` to become `i64::MIN`, and errors above that boundary.

`IS NULL` always returns a non-null integer result. Truthiness helpers use `KeepNull`: with `KeepNullOff`, `NULL` becomes `Some(0)`; with `KeepNullOn`, `NULL` remains `None`. Bit operations propagate `NULL` unless all required operands are present. Shifts cast the left operand to `u64`, treat shift counts whose `u64` representation is >= 64 as zero, and otherwise use wrapping shift operations before returning the bits as `i64`.

## State and Persistence Behavior
This module is stateless and has no durable persistence. All behavior is local to one scalar evaluation and its decoded input values.

## Dependencies and Integration Points
Dependencies are intentionally small: `tidb_query_codegen::rpn_fn`, `tidb_query_common::Result`, and TiDB codec data types plus `Error` for overflow. Integration is through `lib.rs`, which maps scalar signatures such as `LogicalAnd`, `UnaryMinusInt`, `IntIsNull`, `DecimalIsTrueWithNull`, `BitAndSig`, `LeftShift`, and `RightShift` to this module. `UnaryMinusInt` is selected through `map_unary_minus_int_func` so signed and unsigned field types route to the correct implementation.

## Risks and Edge Cases
The highest-risk area is SQL compatibility around `NULL` and truthiness. `IS TRUE` and `IS TRUE WITH NULL` look similar but differ by `KeepNull`, so signature mapping mistakes would produce visible SQL behavior changes. Shift operations intentionally cast signed operands to unsigned bits; negative shift counts therefore become huge `u64` counts and return zero. That matches the tested behavior but is non-obvious.

Unsigned unary minus is another compatibility-sensitive branch because the same physical `i64` value may represent an unsigned MySQL value. Overflow text uses the unsigned magnitude for unsigned values and the signed magnitude for signed values. JSON unary not only treats JSON numeric zero as false; arrays containing zero are true.

## Test Signals
Tests cover logical truth tables with nulls, unary not for int/real/decimal/json, signed and unsigned unary minus overflow boundaries, null predicates across int, real, decimal, bytes, time, duration, and JSON values, bit and/or/xor/negation, `IS TRUE` and `IS FALSE` with and without null preservation, and left/right shifts for positive, negative, zero, large, and null operands.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/impl_op.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/impl_other.rs -->
# sources/storage-engines/tikv/components/tidb_query_expr/src/impl_other.rs

## Purpose
`impl_other.rs` is a small catch-all module for scalar functionality not assigned to the larger expression implementation files. In the current source it implements only SQL `BIT_COUNT`.

## Important APIs, Types, and Functions
The single exported RPN function is `bit_count(arg: &Int) -> Result<Option<Int>>`. It calls Rust's `count_ones()` on the `i64` value and converts the resulting `u32` count to the TiDB integer return type.

## Control Flow
The expression engine handles nullable argument propagation around the non-null `&Int` function signature. For non-null input, `bit_count` computes the population count of the raw two's-complement 64-bit representation and returns it as `Some(Int)`.

## State and Persistence Behavior
This module is pure and stateless. It has no persistence, allocation-heavy state, or external side effects.

## Dependencies and Integration Points
Dependencies are limited to `tidb_query_codegen::rpn_fn`, `tidb_query_common::Result`, and TiDB codec data type aliases. `lib.rs` maps `ScalarFuncSig::BitCount` to `bit_count_fn_meta()`.

## Risks and Edge Cases
The important edge case is negative input. Because `count_ones()` operates on the two's-complement representation of `i64`, `-1` has 64 set bits and `i64::MIN` has 1 set bit. That matches MySQL-style unsigned bit interpretation, but replacing it with arithmetic absolute-value logic would be wrong.

## Test Signals
The inline test covers positive values, zero, several negative values, `i64::MAX`, `i64::MIN`, and `NULL` propagation through the RPN evaluator.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/impl_other.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/impl_regexp.rs -->
# sources/storage-engines/tikv/components/tidb_query_expr/src/impl_regexp.rs

## Purpose
`impl_regexp.rs` implements TiDB regular expression scalar functions for UTF-8 strings: `REGEXP`/`REGEXP_LIKE`, `REGEXP_SUBSTR`, `REGEXP_INSTR`, and `REGEXP_REPLACE`. It handles MySQL match-type flags, collation-driven default case sensitivity, constant-expression precompilation, character-position semantics, and capture substitution in replacements.

## Important APIs, Types, and Functions
Constants such as `PATTERN_IDX`, `LIKE_MATCH_IDX`, `SUBSTR_MATCH_IDX`, `INSTR_MATCH_IDX`, and `REPLACE_MATCH_IDX` describe argument positions for raw variadic RPN functions. `invalid_pos_error`, `is_valid_match_type`, `get_match_type`, `build_regexp`, `build_regexp_from_args`, and `init_regexp_data` are the shared regex construction path.

The public RPN functions are `regexp_like<C: Collator>`, `regexp_substr<C: Collator>`, `regexp_instr<C: Collator>`, and `regexp_replace<C: Collator>`. They are generic over the TiDB collation implementation so case-insensitive collations can inject the `i` flag by default.

Replacement support is modeled by `ReplaceInstruction`, with `SubstitutionNum(usize)` and `Literal(Vec<u8>)`. `ReplaceMetaData` stores an optional precompiled `Regex` and optional parsed replacement instructions. `init_regexp_replace_data` precomputes both when the expression tree has constant pattern and replacement children. `init_replace_instructions` parses backslash escapes and one-digit capture substitutions.

## Control Flow
During expression build, metadata mappers inspect `tipb::Expr` children. If the pattern and optional match type are constant bytes/string expressions, `init_regexp_data` compiles a `regex::Regex` once and stores it in function metadata. If not, evaluation calls `build_regexp_from_args` per row. `regexp_replace` similarly pre-parses constant replacement expressions into instructions.

`get_match_type` starts with `i` when the collation is case-insensitive, accepts only `i`, `c`, `m`, and `s`, and applies flags left-to-right with `c` removing `i`. `build_regexp` rejects empty patterns, converts bytes to UTF-8, prepends inline Rust regex flags such as `(?ims)`, and maps regex compilation failures to `Error::regexp_error`.

`regexp_like` converts the expression bytes to UTF-8 and returns whether the regex matches. `regexp_substr` optionally trims the input by 1-based character position, normalizes occurrence values below 1 to 1, and returns the selected match as bytes. `regexp_instr` follows the same position and occurrence logic, validates return option 0 or 1, and returns a 1-based character offset for match start or end, or 0 if not found.

`regexp_replace` optionally preserves the prefix before the 1-based character position, treats occurrence 0 as replace all and negative occurrence as 1, then iterates captures. For every match it appends the unmatched slice and then executes replacement instructions. `\0` references the full match and `\1` through `\9` reference capture groups; missing capture numbers are regexp errors. A trailing backslash in the replacement is ignored by the parser.

## State and Persistence Behavior
There is no durable state. The only retained state is expression metadata containing compiled regexes and parsed replacement instructions. That metadata is tied to the built RPN expression and avoids repeated compilation for constant patterns or replacements. Dynamic patterns and match types allocate and compile during evaluation.

## Dependencies and Integration Points
The module depends on the Rust `regex` crate, `HashSet`, `Cow`, TiDB `Collator` and datatype traits, `tipb::Expr`/`ExprType`, and `tidb_query_codegen::rpn_fn` support for raw variadic functions and metadata mappers. `lib.rs` maps `RegexpSig`, `RegexpUtf8Sig`, and `RegexpLikeSig` through `map_regexp_like_sig`, and maps substring, instr, and replace signatures through their respective mapper functions.

## Risks and Edge Cases
Regex behavior is compatibility-sensitive. TiDB's documented support here is UTF-8 only, so invalid input or pattern bytes become UTF-8 errors. Empty patterns are explicitly rejected. The Rust `regex` crate is not MySQL ICU regex, so flags and unsupported constructs must be checked against TiDB compatibility expectations.

Position arguments are character indexes, not byte indexes. The code uses `char_indices().nth(pos - 1)` and later slices by byte offsets, so it handles multi-byte UTF-8 correctly as long as the input was valid UTF-8. `pos == 1` on an empty string is valid, while other out-of-range or non-positive positions are errors.

Replacement parsing supports only one digit after a backslash as a substitution number. Sequences such as `\12` mean capture 1 followed by literal `2`, matching the tests. Missing capture groups raise an error during replacement, not during metadata initialization. `get_match_type` stores flags in a `HashSet`, so flag ordering in the inline regex prefix is not stable, but for the supported flags order should not change semantics.

## Test Signals
Tests build full RPN expressions through `ExprDefBuilder` and `RpnExpressionBuilder`, not just direct function calls. They cover regexp like matches, invalid patterns, empty patterns, case flags, multiline and dot-matches-newline flags, rightmost `i`/`c` behavior, invalid match types, null propagation, substring and instr character positions over ASCII and multi-byte UTF-8, occurrence and return-option behavior, replacement from constants and column refs, replace-all versus specific occurrence, capture references including `\0`, out-of-range capture errors, trailing backslash handling, and long real-world URL-like strings.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_expr/src/impl_regexp.rs -->
