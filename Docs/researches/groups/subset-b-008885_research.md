# subset-b-008885 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_extract.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_extract.rs

Purpose: implements `JsonRef::extract` and shared `extract_json` traversal for MySQL/TiDB JSON path extraction. It returns `None` for no matches, a single owned `Json` for one deterministic match, or an auto-wrapped JSON array when multiple paths, wildcards, double-asterisk, or ranges can produce multiple matches.

Important APIs/types/functions: `JsonRef::extract`, `extract_json`, `RefEqualJsonWrapper`, and `append_if_ref_unique`. It depends on `PathExpression`, `PathLeg`, `ArraySelection`, `ArrayIndex`, `KeySelection`, `JsonType`, and binary accessors such as `array_get_elem`, `object_get_val`, `object_search_key`, and `array_get_index`.

Control flow: `extract` scans all path expressions, records whether multiple matches are possible, recursively calls `extract_json`, then chooses scalar versus array output. `extract_json` consumes one path leg at a time: array legs handle wildcard, index, range, and scalar-as-array-zero compatibility; key legs search objects; double-asterisk first tests the remainder at the current node, then recurses into children with the same full path to implement descendant matching. `append_if_ref_unique` de-duplicates by referenced byte slice pointer within one append operation.

State and persistence: no external persistence. It borrows immutable binary JSON slices and returns owned `Json` copies only at the API boundary. Deduplication state is transient `HashSet` state keyed by backing slice pointers.

Dependencies and integration points: central dependency for `json_length`, `json_keys`, `json_modify`, `json_remove`, and `BinaryModifier`. Correctness relies on binary layout helpers and on path flags computed in `path_expr.rs`.

Risks: recursive wildcard extraction can be expensive on deep or wide documents. Pointer-equality de-duplication avoids duplicate references, not structural equality, so identical values stored in different locations remain distinct. Scalar handling for array index zero is a MySQL compatibility edge that can surprise callers. Tests cover scalar extraction, object keys, wildcards, double-asterisk, repeated paths, ranges, right indexes, and missing paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_extract.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_keys.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_keys.rs

Purpose: implements `JSON_KEYS` behavior for a binary `JsonRef`, optionally scoped by one path expression.

Important APIs/types/functions: `JsonRef::keys` is public; private `json_keys` builds the result. It uses `PathExpression::contains_any_asterisk`, `JsonRef::extract`, `JsonType::Object`, `object_get_key`, `Json::from_str_val`, and `Json::from_array`.

Control flow: with no path, `json_keys(self)` returns an array of object keys or `None` for non-objects. With a path, the method rejects more than one expression and rejects wildcard/double-asterisk paths, extracts the target, and returns keys only when the target exists and is an object.

State and persistence: no persistent state. It creates a transient `Vec<Json>` sized to the object element count and copies key bytes into JSON string values.

Dependencies and integration points: relies on `json_extract.rs` for path resolution and binary object accessors for key ordering. The function is exposed through the `JsonRef` extension imported by the JSON module.

Risks: keys are decoded with `str::from_utf8`, so invalid key bytes propagate as errors. Ordering follows binary object order, which is normally sorted by construction. Path validation forbids wildcards because MySQL `JSON_KEYS` only accepts zero or one non-wildcard path. Tests cover non-object `None`, object keys, scoped object extraction, missing paths, arity errors, and wildcard rejection.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_keys.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_length.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_length.rs

Purpose: implements MySQL `JSON_LENGTH` over binary JSON.

Important APIs/types/functions: private `JsonRef::len` returns object/array element count or `1` for scalars; public `JsonRef::json_length` adds optional path behavior. It depends on `JsonType`, `get_elem_count`, `PathExpression`, and `JsonRef::extract`.

Control flow: without a path, the function always returns `Some(length)`. With exactly one wildcard path it returns `Ok(None)`. Otherwise it extracts using the provided path list and maps an existing target to that target's length.

State and persistence: no persistence and no mutation. All state is local and derived from the encoded JSON slice.

Dependencies and integration points: consumes path parser flags and shared extraction logic. It participates as an attribute function in the JSON codec API.

Risks: the special wildcard `None` behavior is compatibility-sensitive. Multiple path expressions are passed through to `extract`; because `extract` may auto-wrap multiple matches as an array, length can become count of matched roots rather than length of an individual target. Tests cover scalars, arrays, objects, path selection, wildcard-to-None, and missing targets.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_length.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_memberof.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_memberof.rs

Purpose: implements MySQL 8 `MEMBER OF` semantics for binary JSON values.

Important APIs/types/functions: public `JsonRef::member_of` compares `self` with either each element of a JSON array or directly with a non-array right-hand JSON. It depends on `JsonType::Array`, `get_elem_count`, `array_get_elem`, and the `PartialOrd` implementation from JSON comparison code.

Control flow: if the right argument is an array, it loops through elements and returns true on `Ordering::Equal`; otherwise it compares the right value directly to `self`. Failure from element decoding propagates through `Result<bool>`.

State and persistence: no persistent state. The function only reads borrowed binary JSON and keeps loop counters locally.

Dependencies and integration points: integrates with `comparison.rs` ordering/equality semantics, so numeric, string, object, and array membership behavior is inherited from common JSON comparison code.

Risks: it unwraps `partial_cmp`, assuming JSON comparison always yields `Some`; NaN-like double values or future comparison changes could violate that. Array membership uses strict JSON equality, so a string containing object text is not the same as an object. Tests cover numeric/string distinctions, nested arrays, object equality versus containment, non-array direct comparison, and array-of-array membership.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_memberof.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_merge.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_merge.rs

Purpose: implements MySQL-compatible JSON merge and merge-patch operations over binary `Json`.

Important APIs/types/functions: `Json::merge`, `Json::merge_patch`, `MergeUnit`, `merge_binary_array`, and `merge_binary_object`. It uses `BTreeMap<String, Json>`, object/array binary accessors, `Json::from_ref_array`, `Json::from_object`, and recursive `Json::merge`.

Control flow: `merge` groups adjacent objects and merges them into a single object, pushes non-objects as merge units, returns a single result directly, or auto-wraps/concatenates into an array. Object merge inserts keys in a `BTreeMap`; duplicate keys merge old and new values recursively. `merge_patch` follows RFC-style patch semantics: non-object patch replaces the target; object patch starts from target object keys, removes keys whose patch value is JSON null, and recursively patches or inserts other keys.

State and persistence: no persistence. The methods allocate owned JSON values for merged objects and arrays. Temporary maps control key ordering and duplicate resolution.

Dependencies and integration points: depends on binary accessors, JSON constructors, and `Error::from` for UTF-8 key conversion. Used by higher-level SQL JSON merge functions.

Risks: `BTreeMap` sorts keys, so output order is deterministic but tied to lexicographic UTF-8 strings. Invalid key bytes error. Recursive duplicate-key merging can allocate heavily for large nested structures. Tests cover adjacent object merge, duplicate keys, scalar/object/array combinations, array concatenation, and nested multi-document merges; merge-patch has no visible local test in this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_merge.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_modify.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_modify.rs

Purpose: provides the public JSON modification entry point for `JSON_INSERT`, `JSON_REPLACE`, and `JSON_SET`.

Important APIs/types/functions: `ModifyType::{Insert, Replace, Set}` and `JsonRef::modify`. It uses `PathExpression`, `BinaryModifier`, and owned `Json` replacement values.

Control flow: the function first checks that path count equals value count, rejects any path containing wildcard/double-asterisk or range, copies `self` into `res`, and then applies each path/value pair sequentially. For each pair it constructs a fresh `BinaryModifier` over the current result and dispatches to `insert`, `replace`, or `set`.

State and persistence: no external persistence. Sequential modification means later operations see earlier changes. The original JSON is not mutated; each operation produces a new owned binary JSON.

Dependencies and integration points: delegates actual binary rewriting and insert/replace semantics to `modifier.rs`, while path validation comes from `path_expr.rs`.

Risks: parameter-count diagnostics use expected/found values that are easy to misread because expected is the value count. Rebuilding after every path can be expensive for many modifications. Wildcard/range rejection is required for MySQL behavior and must remain aligned with the parser flags. Tests cover root set, object and array edits, scalar auto-wrap, ignored inserts/replaces, missing parents, and wildcard errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_modify.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_remove.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_remove.rs

Purpose: implements MySQL `JSON_REMOVE` behavior over binary JSON.

Important APIs/types/functions: public `JsonRef::remove`, `BinaryModifier::remove`, and `PathExpression` validation helpers.

Control flow: it rejects paths that are the root, contain wildcard/double-asterisk, or contain ranges. Starting from an owned copy of `self`, it applies each removal sequentially through a new `BinaryModifier`. Missing paths are treated as no-ops by the modifier.

State and persistence: no persistent state. Like modification, each removal produces an owned `Json`, and subsequent removals operate on the previous output.

Dependencies and integration points: depends on `modifier.rs` for structural removal and `json_extract.rs` indirectly through the modifier. It is part of the JSON mutation API surface.

Risks: sequential path application means indexes can shift after earlier removals, matching MySQL semantics but requiring careful tests. Root removal is invalid. Wildcards and ranges are forbidden. Tests cover array element deletion, object member deletion, nested object deletion, no-op missing parents, and invalid wildcard paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_remove.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_type.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_type.rs

Purpose: implements MySQL `JSON_TYPE` string classification for binary JSON.

Important APIs/types/functions: `JsonRef::json_type` returns static byte-string constants such as `OBJECT`, `ARRAY`, `INTEGER`, `UNSIGNED INTEGER`, `DOUBLE`, `STRING`, `BOOLEAN`, `NULL`, `DATE`, `DATETIME`, `TIME`, `BLOB`, `BIT`, or `OPAQUE`.

Control flow: the method matches `JsonType`. Literal values distinguish booleans from null by `get_literal()`. Opaque values inspect `FieldTypeTp` and classify blob/string families as `BLOB`, bit as `BIT`, and unknown or unsupported types as `OPAQUE`. Timestamp maps to `DATETIME`.

State and persistence: no state beyond reading type code and opaque metadata from the borrowed JSON value.

Dependencies and integration points: depends on `FieldTypeTp`, `JsonType`, and opaque metadata accessors from `mod.rs`. Used by expression evaluation for SQL `JSON_TYPE`.

Risks: opaque classification depends on valid embedded field type. Any new JSON/opaque variants need this match updated to avoid generic `OPAQUE`. Tests cover standard object, array, signed/unsigned/double numeric boundaries, strings, booleans, and null; opaque/time classifications are not locally tested here.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_type.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_unquote.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_unquote.rs

Purpose: implements `JSON_UNQUOTE` and reusable JSON-string escape decoding.

Important APIs/types/functions: `JsonRef::unquote`, `unquote_string`, and private `decode_escaped_unicode`. It defines constants for escaped control characters and uses `ToStringValue`.

Control flow: JSON strings are decoded by scanning chars, treating backslash escapes specially, decoding `\u` followed by exactly four UTF-8 bytes of hex, and ignoring backslashes for unknown escape sequences. Date/datetime/timestamp/time/opaque values are rendered with JSON string formatting and stripped of surrounding quotes. Other JSON types return their normal JSON string representation.

State and persistence: no persistent state. It allocates a result `String` and advances an iterator over the source string.

Dependencies and integration points: used directly by JSON unquote expression behavior and by `path_expr.rs` to decode quoted object keys. Depends on serialization formatting for non-string and temporal values.

Risks: Unicode escape handling decodes one scalar value and does not combine surrogate pairs; invalid or short escapes error. The temporal/opaque branch asserts rendered output has quotes, so formatter behavior is an implicit invariant. Tests cover control escapes, unicode escapes, ignored unknown escapes, incomplete escapes, non-string values, and time/duration unquoting.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_unquote.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/mod.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/mod.rs

Purpose: defines the binary JSON module, public JSON value/reference types, constructors, conversion hooks, creation functions, and module exports for MySQL/TiDB binary JSON.

Important APIs/types/functions: `JsonType`, `JsonRef<'a>`, `Json`, `json_array`, `json_object`, constructors such as `from_string`, `from_i64`, `from_ref_array`, `from_object`, `from_time`, `from_duration`, accessors such as `get_u64`, `get_i64`, `get_double`, `get_elem_count`, `get_literal`, `get_str`, `get_opaque_type`, `get_time`, `get_duration`, `Json::as_ref`, and re-exports for codecs, path parsing, and `ModifyType`.

Control flow: construction methods write MySQL binary JSON payloads through encoder helpers and store a `JsonType` plus bytes. `JsonRef` offers zero-copy access to typed slices with assertions guarding expected type. SQL creation helpers convert `Datum` values into JSON arrays or key/value objects, rejecting odd object arity and null member names. Conversion implementations cast JSON to float and Rust/MySQL values into JSON.

State and persistence: owned state is `Json { type_code, value: Vec<u8> }`; borrowed state is `JsonRef { type_code, value: &[u8] }`. No disk persistence. Binary bytes are the durable in-memory representation passed across codec boundaries.

Dependencies and integration points: imports binary, comparison, codec, modifier, path, serde, and JSON function submodules. Integrates with datum conversion, time/duration codecs, decimal/real conversion, `EvalContext` warning behavior, and `AsMySqlBool`.

Risks: many accessors assert type rather than returning typed errors, so callers must check `JsonType`. `AsMySqlBool` is marked TODO and currently always false. Float/decimal JSON conversion intentionally loses DECIMAL typing. Tests cover array/object creation and JSON-to-float conversion/truncation behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/modifier.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/modifier.rs

Purpose: performs low-level binary JSON rewriting for insert, replace, set, and remove operations.

Important APIs/types/functions: `BinaryModifier<'a>`, `new`, `set`, `replace`, `insert`, `remove`, private `do_insert`, `do_remove`, `rebuild`, and recursive `rebuild_to`. It tracks `old: JsonRef`, `to_be_modified_ptr: *const u8`, and `new_value: Option<Json>`.

Control flow: public operations locate target or parent nodes with `extract_json`, record the backing pointer of the node to replace, prepare a new owned JSON value when needed, and call `rebuild`. Insert can append to arrays, auto-wrap scalar parents into arrays for array index insertions, or insert object keys. Remove rebuilds arrays without the selected index or objects without the selected key. `rebuild_to` walks the original binary tree, copies headers and keys, recursively rewrites child value entries, and updates value type/offset metadata.

State and persistence: state is transient and pointer-based. It never mutates the input buffer; it emits a new `Json` with rebuilt bytes.

Dependencies and integration points: used by `json_modify.rs` and `json_remove.rs`; relies heavily on binary layout constants, `NumberCodec`, value-entry decoding, and pointer identity from `JsonRef`.

Risks: raw pointer identity is central; any future representation that moves buffers during traversal would break it. Offset and inline-literal rewriting is delicate. Multiple matches use only the first match. Rebuild cost is proportional to document size even for small edits. Behavior is tested indirectly through modify/remove tests rather than direct modifier unit tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/modifier.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs

Purpose: parses MySQL JSON path expressions into reusable typed path legs and flags.

Important APIs/types/functions: `ArrayIndex::{Left, Right}`, `ArraySelection::{Asterisk, Index, Range}`, `KeySelection::{Asterisk, Key}`, `PathLeg`, `PathExpression`, flags `PATH_EXPRESSION_CONTAINS_ASTERISK`, `PATH_EXPRESSION_CONTAINS_DOUBLE_ASTERISK`, `PATH_EXPRESSION_CONTAINS_RANGE`, and `parse_json_path_expr`.

Control flow: nom parsers recognize `$`, dot member selection, quoted/unquoted keys, array indexes including `last` and `last - n`, ranges `start to end`, wildcards, and double-asterisk. Parsing accumulates flags from produced legs, rejects trailing unconsumed input, and rejects a final double-asterisk. Range parsing validates obvious reversed ranges for same-side indexes.

State and persistence: output state is an owned `PathExpression` with a `Vec<PathLeg>` plus bit flags. No persistent state.

Dependencies and integration points: quoted key parsing reuses `json_unquote::unquote_string`; JSON function modules use flags for validation and `extract_json` uses legs for traversal. Nom errors are converted into MySQL-style position messages.

Risks: parser accepts some MySQL-compatible whitespace forms but key grammar must stay aligned with TiDB/MySQL expectations. Quoted keys reject control characters and invalid unicode escapes. Position reporting depends on remaining-input length. Tests are broad: flags, valid paths with unicode keys, `last`, ranges, double-asterisk, invalid syntax, overflow indexes, reversed ranges, asterisk detection, and range detection.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/path_expr.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/serde.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/serde.rs

Purpose: bridges binary `Json`/`JsonRef` with Serde JSON parsing and MySQL-style string formatting.

Important APIs/types/functions: `MySqlFormatter`, `write_mysql_finite_float`, `ToStringValue for JsonRef/Json`, `Serialize for JsonRef`, `FromStr for Json`, `JsonVisitor`, and `Deserialize for Json`.

Control flow: formatter emits spaces after commas/colons and removes `+` from exponent notation. Serialization matches `JsonType`, reads binary payloads, and serializes objects/arrays recursively. Opaque values become a `base64:typeN:...` string. Temporal values are rendered as strings with maximized fsp. Deserialization visits serde values and constructs binary JSON; unsigned integers below `i64::MAX` are stored as signed, larger values as unsigned.

State and persistence: no persistence. Serialization allocates a `Vec<u8>` writer and creates strings; deserialization constructs owned `Json` bytes.

Dependencies and integration points: depends on serde, serde_json, base64, `ToStringValue`, binary accessors, time/duration formatting, and `FieldTypeTp`. `Json::from_str` and `Display` flow through this module.

Risks: `object_get_key` is unwrapped as UTF-8 during serialization, so invalid key bytes can panic. Serde parsing chooses f64 for numbers outside integer ranges. Opaque encoding is string-based and must remain compatible with TiDB. Tests cover parsing, illegal JSON, numeric boundary storage, MySQL-style formatting, and opaque base64 rendering.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/serde.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/mod.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/mod.rs

Purpose: top-level MySQL codec module facade and fractional-second precision helper.

Important APIs/types/functions: constants `UNSPECIFIED_FSP`, `MAX_FSP`, `MIN_FSP`, `DEFAULT_FSP`, `DEFAULT_DIV_FRAC_INCR`; function `check_fsp`; public submodules and re-exports for decimal, duration, enum, JSON, set, time, and vector types/codecs.

Control flow: `check_fsp` maps unspecified precision to the default, validates the inclusive range 0..=6, and returns a `u8` precision or invalid-type error.

State and persistence: no state. It is a module boundary and pure validation helper.

Dependencies and integration points: used throughout MySQL time/duration/JSON conversion code to normalize fsp. The re-export list is the public import surface for consumers of `codec::mysql`.

Risks: changes to re-exports can break many downstream imports. FSP validation is tiny but central to temporal correctness. No local tests in this file; coverage is indirect through time/duration/JSON temporal tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/set.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/set.rs

Purpose: represents MySQL `SET` values as a bitmap plus shared string table.

Important APIs/types/functions: owned `Set`, borrowed `SetRef<'a>`, constructors `Set::new` and `SetRef::new`, `value`, `as_ref`, `to_owned`, `is_set`, `is_empty`, `Display`, ordering/equality, and `AsMySqlBool`.

Control flow: display iterates all labels in `BufferVec`, appending comma-separated labels whose bit is set in `value`. Equality and ordering compare only the numeric bitmap. `AsMySqlBool` returns true when any bit is set.

State and persistence: `Set` owns `Arc<BufferVec>` plus `u64` bitmap; `SetRef` borrows the buffer. There is no persistence. TiDB guarantees no more than 64 set members, matching the bitmap width.

Dependencies and integration points: uses `tikv_util::buffer_vec::BufferVec` for compact label storage and integrates with codec boolean conversion.

Risks: `is_set` shifts `1 << idx`; callers must keep indexes below 64. Equality ignores label table identity, so two sets with the same bitmap but different labels compare equal. Display uses lossy UTF-8 conversion. Tests cover string rendering, bit membership, and empty checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/set.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/extension.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/extension.rs

Purpose: adds MySQL/TiDB date and weekday helper methods to `chrono::Weekday` and internal `Time`.

Important APIs/types/functions: `WeekdayExtension::{name, name_abbr}`, `DateTimeExtension::{days, calc_year_week, calc_year_week_by_week_mode, week, year_week, abbr_day_of_month, day_number, second_number}`, plus private `calc_day_number`, `calc_days_in_year`, and `calc_weekday`.

Control flow: weekday methods map enum variants to full or abbreviated English names. Week calculations implement TiDB/MySQL week-mode behavior by deriving day numbers, first weekday, year-boundary adjustments, and week numbering. `week` returns 0 for zero month/day. `year_week` forces year behavior. Day/second number helpers compute days or seconds since MySQL's zero date baseline.

State and persistence: no persistent state. All calculations are pure over a `Time` value and `WeekMode`.

Dependencies and integration points: depends on `chrono::Weekday`, internal `Time`, and `weekmode::WeekMode`. Used by SQL date formatting/extraction functions.

Risks: week numbering has many boundary conditions around January, ISO-like modes, Sunday/Monday starts, zero dates, and leap years. Private helpers are not directly tested in this file, so coverage is likely indirect through time function tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/extension.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/interval.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/interval.rs

Purpose: parses MySQL interval literals and converts scalar expression values into normalized interval strings for date/time arithmetic and duration extraction.

Important APIs/types/functions: `IntervalUnit`, `IntervalUnit::from_str`, `is_valid_for_timestamp`, `is_clock_unit`, internal `TimeIndex`, `Interval`, `Interval::parse_from_str`, `extract_duration`, `negate`, accessors, and trait `ConvertToIntervalStr` for `BytesRef`, `i64`, `Real`, and `Decimal`. Static regex/map state includes `ONE_TO_SIX_DIGIT_REGEX`, `NUMERIC_REGEX`, `INTERVAL_REGEX`, and `INTERVAL_STR_INDEX_MAP`.

Control flow: simple units parse an integer part, optional fractional part, rounding behavior, overflow checks, and convert into months, seconds, nanoseconds, and fsp. Compound units use regex numeric extraction, right-align matched numeric fields into a canonical year/month/day/hour/minute/second/microsecond array, validate field count, apply sign, and checked arithmetic. `extract_duration` reuses parsing in strict duration mode and maps month units to 30-day durations where allowed. Conversion implementations normalize different SQL value types before parsing; strings use truncation warnings, `SECOND` strings parse as decimals, reals honor requested decimal formatting, and decimals transform decimal points into unit-specific separators for compound units.

State and persistence: no persistent state beyond lazily initialized regexes/maps. Each `Interval` stores normalized `month`, `sec`, `nano`, and `fsp`.

Dependencies and integration points: depends on duration constants/limits, `Decimal`, `Real`, `BytesRef`, `EvalContext` warning/error policy, `RoundMode`, `lazy_static`, and `regex`. It is consumed by temporal expression evaluation for `INTERVAL` arithmetic and duration conversion.

Risks: MySQL interval grammar is compatibility-heavy; regex extraction tolerates separators by position rather than strict token grammar. Overflow handling differs between normal parse mode, which may return `Ok(None)` after context handling, and duration mode, which returns errors. Fractional parsing truncates to six digits and some simple non-second units round the integer value while also reporting invalid fractional usage. Tests are extensive for unit classification, value-to-string conversion, simple and compound parsing, invalid/overflow cases, and duration extraction.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/interval.rs -->
