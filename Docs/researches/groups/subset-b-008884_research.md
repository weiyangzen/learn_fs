# Research Group subset-b-008884

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/decimal.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/decimal.rs

## Purpose
`decimal.rs` implements TiKV's MySQL-compatible fixed precision decimal value, arithmetic, conversions, comparison, hashing, and binary encoders. It mirrors TiDB `MyDecimal` behavior while fitting values into a fixed nine-word base-1e9 buffer, so it is used anywhere pushed-down expression evaluation needs MySQL `DECIMAL` semantics instead of Rust floating point behavior.

## Important APIs, Types, and Functions
`Res<T>` is the local status wrapper for decimal operations. It carries a value plus `Ok`, `Truncated`, or `Overflow` status and can be converted through `EvalContext` so SQL mode decides whether the status becomes an error or warning.

`Decimal` is `#[repr(C)]`, asserted to be 40 bytes, and stores `int_cnt`, `frac_cnt`, `result_frac_cnt`, a sign flag, and `[u32; 9]` words. Each word stores up to 9 decimal digits. Public helpers include `zero`, `is_negative`, `prec_and_frac`, `frac_cnt`, `convert_to`, `round`, `shift`, `as_i64`, `as_i64_with_ctx`, `as_u64`, `from_f64`, `from_bytes`, `approximate_encoded_size`, `div`, and `is_zero`.

`RoundMode` supports `HalfEven`, `Truncate`, and a limited `Ceiling` path. Arithmetic is provided through trait implementations for `Add`, `Sub`, `Mul`, `Div`, `Rem`, and `Neg`, backed by `do_add`, `do_sub`, `do_mul`, and `do_div_mod_impl`. Bounds helpers `max_decimal` and `max_or_min_dec` synthesize maximum decimal values for a precision and scale.

The codec surface is split between comparable datum bytes and chunk bytes. `DecimalEncoder::write_decimal` writes precision, scale, and order-preserving bytes using sign inversion. `DecimalDecoder::read_decimal` reverses that format. `write_decimal_to_chunk` and `read_decimal_from_chunk` copy the raw 40-byte `Decimal` layout for vectorized/chunk execution. `DecimalDatumPayloadChunkEncoder` bridges datum payload bytes into chunk layout.

## Control Flow
Parsing starts in `from_bytes_with_word_buf`: trim whitespace, read optional sign, split integer and fractional digits, cap word counts with `fix_word_cnt_err`, fill integer words from right to left and fractional words from left to right, then optionally apply scientific notation with `shift`. Non-space trailing garbage marks the result as truncated; oversized integer/fractional parts produce `Overflow` or `Truncated` status while still returning a clipped value.

Addition and subtraction first align integer and fractional word counts. If signs match, addition propagates base-1e9 carries from the least significant word. If signs differ, subtraction calls `calc_sub_carry` to compare absolute values, possibly swaps operands, and then subtracts from the least significant aligned word while preserving the correct sign. Multiplication uses word-by-word long multiplication, then normalizes leading zero words and turns negative zero into zero. Division and modulo share `do_div_mod_impl`, which normalizes the divisor, estimates each quotient word, subtracts products from a temporary buffer, corrects overestimates, and either writes quotient words or reconstructs the remainder.

Rounding and shifting work at digit and word boundaries. `round_with_word_buf_len` decides target fractional words, clears discarded words, calls `handle_incr` to apply half-up/ceiling/truncate increment rules, and uses `handle_carry` to propagate a carry that may grow the integer part. `shift_with_word_buf_len` computes occupied digit bounds, handles huge shift overflow/truncation, performs small digit shifts inside words, then performs whole-word movement.

Encoding computes the requested integer and fractional byte widths from `(prec, frac)`. Negative values are masked with `u32::MAX`, and the first byte is XORed with `0x80` so lexicographic bytes remain comparable. Decoding reads the metadata, determines the sign mask from the first payload byte, rebuilds words, validates partial leading/trailing words, and restores zero normalization.

## State and Persistence Behavior
The decimal value is pure in-memory state; this file does not persist directly to disk. Its encoded bytes are persisted indirectly through TiKV datum storage and exchanged through coprocessor/chunk execution. The comparable codec is a logical storage format. The chunk codec is a raw memory-layout format guarded by `#[repr(C)]` and `const_assert_eq!(DECIMAL_STRUCT_SIZE, mem::size_of::<Decimal>())`, so it is intended for compatible TiDB/TiKV vectorized payloads rather than an independently portable wire format.

`EvalContext` is the side-effect surface for warnings and errors. Conversion from `Res<T>` calls `handle_truncate`, `handle_truncate_err`, or `handle_overflow_err`, which means the same arithmetic result can be accepted, warned, or rejected depending on SQL flags.

## Dependencies and Integration Points
The module depends on `codec::prelude` buffer traits, `TEN_POW`, `EvalContext`, conversion traits (`ConvertTo`, `ToStringValue`), MySQL datatype definitions (`Real`, `Bytes`, `Json`, `JsonRef`, `JsonType`), `DEFAULT_DIV_FRAC_INCR`, and TiKV logging/error helpers. It integrates with JSON decimal conversion, integer/float/string casts, expression boolean evaluation through `AsMySqlBool`, datum encoding, and vectorized chunk payload conversion.

## Risks and Edge Cases
The arithmetic is dense and boundary-heavy: carries can grow integer precision, subtraction trims leading and trailing zero words before comparing, multiplication truncates differently depending on operand order, and division manually estimates quotient words. Any change to word count, rounding, or sign normalization can break MySQL compatibility.

`RoundMode::Ceiling` is explicitly incomplete in one digit path, and comments note several TiDB compatibility gaps in cast error handling. `from_f64` uses Rust's canonical float string, not the exact binary float value. `read_decimal_from_chunk` and `write_decimal_to_chunk` rely on raw struct layout and endianness assumptions. `read_decimal` performs validation, but malformed lengths or inconsistent precision/scale remain high-risk inputs because many later operations index `word_buf` by computed word counts.

## Test Signals
The embedded tests are broad: integer and float conversion, decimal to integer/float, shifting, rounding, string formatting, comparable codec, raw chunk codec including TiDB bytes, ordering, hashing, max/min synthesis, add/sub/mul/div/rem, negation, floor/ceil, byte conversion with `EvalContext` warning modes, and `Res::into_result_impl`. These tests directly cover the main compatibility and overflow/truncation surfaces.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/decimal.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/duration.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/duration.rs

## Purpose
`duration.rs` implements MySQL `TIME`/duration semantics for TiKV expression evaluation. It represents a duration as signed nanoseconds plus fractional seconds precision (FSP), parses MySQL-compatible duration strings and numeric values, formats values for SQL output and numeric casts, performs checked arithmetic, and provides datum/chunk codecs.

## Important APIs, Types, and Functions
The file defines duration constants for nanoseconds, microseconds, seconds, minutes, hours, days, allowed FSP widths, and MySQL's maximum time range of `838:59:59`. `check_hour_part`, `check_minute_part`, `check_second_part`, `check_nanos_part`, and `check_nanos` enforce component and total range limits.

`Duration` is `#[repr(C)]` with `nanos: i64` and `fsp: u8`. Public APIs include component readers (`hours`, `minutes`, `secs`, `subsec_micros`, `subsec_nanos`, `fsp`), FSP normalization (`minimize_fsp`, `maximize_fsp`, `round_frac`), unit conversions (`to_secs`, `to_secs_f64`, `to_millis`, `to_micros`, `to_nanos`), constructors (`zero`, `from_secs`, `from_millis`, `from_micros`, `from_nanos`, `new_from_parts`, `from_i64`), parsers (`parse`, `parse_consider_overflow`, `parse_exactly`), and checked arithmetic (`checked_add`, `checked_sub`).

Codec traits include `DurationEncoder::write_duration_to_chunk`, `DurationDatumPayloadChunkEncoder` for int and varint datum payloads, and `DurationDecoder` for int, varint, and chunk layouts. Conversion traits produce `f64` and `Decimal`; `Display`, ordering, hashing, and `AsMySqlBool` are implemented around the stored nanoseconds.

## Control Flow
Parsing is implemented in the nested `parser` module using `nom`. It trims input, captures an optional negative sign, then tries `day hh:mm:ss`, colon-delimited `hh:mm:ss`, and compact `hhmmss` forms. Fractional seconds are parsed after an optional dot, taking one extra digit when rounding is needed, and scaled to nanoseconds. If a compact parse leaves trailing data and the original string can match a datetime shape, the parser falls back to `DateTime::parse_datetime` and converts the time part to `Duration` for TiDB compatibility.

`Duration::new_from_parts` validates components, folds hours, minutes, seconds, and fractional nanoseconds into one signed count, then calls `checked_round` to round according to FSP and enforce the global range. `from_secs`, `from_millis`, `from_micros`, and `from_nanos` all validate FSP first, convert to nanoseconds with checked multiplication where needed, and round to requested FSP. `from_i64` interprets numeric `HHMMSS` values, with a datetime parse fallback for large positive values that look like datetime literals.

Formatting routes through `format(sep)`: `Display` uses `:` separators, while `to_numeric_string` omits separators for numeric casts. Fractional output is truncated to the stored FSP after prior rounding. Checked addition/subtraction use Rust checked integer arithmetic, reapply the MySQL max range, and preserve the maximum FSP of the operands.

## State and Persistence Behavior
`Duration` has no persistence of its own. Datum storage carries nanoseconds as signed int or varint payloads; chunk storage writes the nanosecond count as little-endian `i64`. FSP is not stored in the chunk payload, so decoders reconstruct it from `FieldType.decimal()` or the caller-supplied FSP. `EvalContext` records warning/error behavior for truncated parses and overflow handling, including an `overflow_as_null` path in `parse_consider_overflow`.

## Dependencies and Integration Points
The module depends on `tipb::FieldType`, `FieldTypeAccessor`, `codec::prelude`, `TEN_POW`, `Decimal`, `check_fsp`, `DEFAULT_FSP`, `MIN_FSP`, `MAX_FSP`, `Time`/`TimeType` for datetime fallback, conversion traits, MySQL error codes, and `EvalContext`. It integrates with scalar casts from strings and numbers to time, vectorized chunk codecs, JSON/time conversion through shared datatype traits, and boolean evaluation.

## Risks and Edge Cases
The most subtle risk is compatibility parsing. Inputs like `2011-11-11`, `1234abc`, compact numbers, datetime-like strings, and strings with partial trailing garbage intentionally follow TiDB/MySQL quirks. Small changes to fallback conditions or truncation warnings can alter SQL results. FSP rounding can roll seconds, minutes, or hours forward, including negative values. Chunk decoding depends on external FSP because only nanoseconds are stored. Numeric `from_i64` has a special large positive datetime fallback but negative large values do not mirror that path.

## Test Signals
Tests cover component accessors, microsecond rounding, overflow-as-warning parsing, a large matrix of duration string formats and datetime fallback cases, overflow-as-null handling, numeric string and `Decimal`/`f64` conversion, `round_frac`, chunk codec round trips, checked addition/subtraction overflow, and `from_i64`. Benchmarks cover parser, component access, decimal conversion, rounding, codec, and arithmetic hot paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/duration.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/enums.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/enums.rs

## Purpose
`enums.rs` implements TiKV's MySQL `ENUM` value wrapper and codecs. It keeps the SQL-visible enum name together with the numeric enum index, while comparison, hashing, boolean conversion, and integer casts use the numeric value as MySQL does.

## Important APIs, Types, and Functions
`Enum` owns `name: Vec<u8>` and `value: u64`. `Enum::new` forces the name to empty when `value == 0`, since MySQL enum value zero represents the empty invalid value. Accessors expose `value`, `value_ref`, `name`, and `as_ref`. `Enum::get_value_name` maps a 1-based enum value to `FieldType.elems[value - 1]`, or empty bytes for zero.

`EnumRef<'a>` borrows `name` and `value`, supports `new`, `to_owned`, `is_empty`, `value`, `value_ref`, `name`, `as_str`, and `len`. It implements `Display`, `ToInt`, and `ToStringValue`.

`EnumEncoder` writes either comparable uint datum bytes (`write_enum_uint`) or chunk bytes (`write_enum_to_chunk`, little-endian `u64` followed by raw name bytes). `EnumDatumPayloadChunkEncoder` converts compact-bytes, fixed uint, or varuint datum payloads into chunk layout using `FieldType.elems`. `EnumDecoder` reads the same datum forms or chunk form and reconstructs `Enum`.

## Control Flow
Datum decode reads the numeric enum value, looks up the corresponding name from the protobuf field type, and constructs an owned `Enum`. Datum-to-chunk conversion follows the same path but writes the chunk layout directly. Chunk decode reads an eight-byte little-endian value and treats all remaining bytes in the reader as the enum name. Display returns an empty string for value zero and UTF-8-lossy text for nonzero names.

## State and Persistence Behavior
`Enum` itself is in-memory. Persisted datum payloads store only the numeric enum value; the name is derived from schema metadata (`FieldType.elems`) at decode time. Chunk payloads store both value and name bytes for execution. This means schema metadata is part of correct interpretation for datum reads, and chunk decoding consumes the remaining buffer as a name.

## Dependencies and Integration Points
The file depends on `codec::prelude` number codecs, `tipb::FieldType`, `FieldTypeTp`, `ToInt`, `ToStringValue`, and `EvalContext`. It integrates with table schema field metadata, scalar casts to integer/string, vectorized chunk execution, ordering, hashing, and boolean evaluation.

## Risks and Edge Cases
`Enum::get_value_name` indexes `elems[value - 1]` without an explicit bounds check, so invalid stored enum values or mismatched schema metadata can panic. Equality, ordering, and hashing ignore the name, so two enums with the same value but different names compare equal. `read_enum_from_chunk` consumes all remaining bytes as the name, so callers must frame chunk data correctly. UTF-8 validation only occurs through `EnumRef::as_str`; display and string conversion are lossy.

## Test Signals
Tests cover display/string conversion, UTF-8 string access, zero-value emptiness, fixed uint/varuint/compact-bytes datum decoding, chunk encoding, and datum-payload-to-chunk conversion for all supported payload forms.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/enums.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/binary.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/binary.rs

## Purpose
`json/binary.rs` provides low-level navigation over TiKV/TiDB binary JSON buffers. It lets `JsonRef` read array elements, object keys and values, object key positions, value-entry payloads, literal values, raw pointer identity, and encoded length without materializing a new JSON document.

## Important APIs, Types, and Functions
All APIs are implemented on `JsonRef<'a>`. `array_get_index` converts JSON path array indexes from either left or right into a zero-based element index. `array_get_elem` reads the value entry for an array element. `object_get_key` reads a key entry and returns the raw key slice. `object_get_val` reads the value entry corresponding to an object key. `object_search_key` performs binary search over sorted object keys. `val_entry_get` decodes a value-entry type plus offset or inline literal and returns the referenced `JsonRef`. `as_ptr`, `as_literal`, and `binary_len` expose internal pointer, literal conversion, and encoded byte length.

## Control Flow
Array and object reads use layout constants from `constants.rs`. Arrays start with a header followed by value entries; objects start with a header, key entries, value entries, key bytes, and value bytes. `object_search_key` assumes keys are sorted and performs a standard lower-bound binary search using `object_get_key`.

`val_entry_get` first converts the one-byte type code into `JsonType`, reads the following little-endian `u32`, and then interprets it either as inline literal data or as an offset into `self.value()`. Fixed-width numbers, time, datetime, and duration use known byte lengths. Strings and opaque values read a varint length. Nested arrays/objects read their embedded data size from the nested header.

## State and Persistence Behavior
The module is read-only and returns borrowed slices into the original binary JSON value. It does not allocate except where errors format messages through string conversion. There is no persistence side effect, but the functions define how persisted binary JSON bytes are navigated by higher-level JSON operations.

## Dependencies and Integration Points
It depends on `codec::number::NumberCodec`, `JsonRef`, `JsonType`, binary layout constants, path expression `ArrayIndex`, `ToStringValue`, and the shared codec `Result`. It is used by JSON extraction, comparison, containment, depth, merge/modify helpers, and any scalar function that needs random access to binary JSON arrays or objects.

## Risks and Edge Cases
Most functions index directly into `self.value()` with computed offsets and lengths. They assume the `JsonRef` points to well-formed binary JSON. Corrupt value entries, unsorted object keys, invalid offsets, invalid varint lengths, or mismatched element counts can panic or return errors depending on where decoding fails. `object_get_key` has no `Result` return and will panic on malformed key offsets. `array_get_index` carefully returns `None` for right indexes beyond the array length.

## Test Signals
Tests verify type detection for common JSON literals, array element access across scalar, time, duration, nested array, string, boolean, and object values, and object key/value access for similarly mixed objects.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/binary.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/comparison.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/comparison.rs

## Purpose
`json/comparison.rs` implements ordering and equality for binary JSON values. It follows TiDB/MySQL JSON precedence rules across JSON types and provides type-specific comparisons for numbers, literals, strings, arrays, objects, opaque bytes, dates/datetimes/timestamps, and times.

## Important APIs, Types, and Functions
Helper functions include `compare`, `compare_i64_u64`, and `compare_f64_with_epsilon`. `JsonRef::get_precedence` maps each `JsonType` to constants from `constants.rs`, treating JSON null and booleans as separate precedence categories inside `Literal`. `JsonRef::as_f64` converts numeric and literal JSON values for mixed numeric comparison.

The file implements `Eq`, `Ord`, `PartialEq`, and `PartialOrd` for both `JsonRef<'_>` and owned `Json`. Owned comparisons delegate to `as_ref()`.

## Control Flow
`JsonRef::partial_cmp` first compares type precedence. If precedence differs, the value with the greater precedence constant sorts greater. If precedence matches, it dispatches by left-hand type. Signed and unsigned integers use exact mixed comparison that handles negative signed values. Float comparisons use epsilon equality. Literals compare decoded literal values, with JSON null equal to JSON null by precedence. Strings and opaque values compare decoded byte slices. Arrays compare lexicographically element by element and then by length. Objects compare raw binary value bytes. Date/datetime/timestamp values compare decoded `Time`; time values compare decoded `Duration`.

Several branches return `None` if decoding string, opaque, time, or array elements fails. The `Ord` implementations unwrap `partial_cmp`, so callers using total-order APIs assume valid comparable JSON.

## State and Persistence Behavior
Comparison is read-only. It traverses borrowed binary JSON buffers and may decode nested values but does not persist or mutate state. Its results affect SQL comparison predicates, sorting, hashing contexts that rely on equality, and JSON containment.

## Dependencies and Integration Points
The module depends on `Json`, `JsonRef`, `JsonType`, binary constants, `ToStringValue`, and the shared `Result`. It integrates with `binary.rs` for array traversal, typed getters from `json/mod.rs`, `Time`/`Duration` comparison, and `json_contains.rs`, which calls `partial_cmp(...).unwrap()` for scalar containment.

## Risks and Edge Cases
Numeric comparison between large integers and floats can be lossy because mixed float paths cast integers to `f64` and use `f64::EPSILON`. `Ord::cmp` and owned `PartialEq` unwrap `partial_cmp`; malformed JSON that makes comparison return `None` can panic. Object ordering is raw binary byte ordering rather than semantic key/value traversal beyond what the binary representation guarantees. Type precedence constants are negative values, so changing their order changes SQL-visible comparison behavior.

## Test Signals
Tests cover mixed numeric comparison among `i64`, `u64`, and `f64`; comparisons within same JSON type; comparisons across different JSON type precedence categories; and date/datetime/timestamp/time ordering using parsed `Time` and `Duration` values.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/comparison.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/constants.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/constants.rs

## Purpose
`json/constants.rs` centralizes byte-size, literal-value, and comparison-precedence constants for TiKV's binary JSON implementation. These constants are shared by JSON encoders, decoders, binary navigation, comparison, and semantic helpers.

## Important APIs, Types, and Functions
The file exports literal codes `JSON_LITERAL_NIL`, `JSON_LITERAL_TRUE`, and `JSON_LITERAL_FALSE`. Binary layout constants include fixed widths such as `TYPE_LEN`, `LITERAL_LEN`, `U16_LEN`, `U32_LEN`, `NUMBER_LEN`, `TIME_LEN`, `DURATION_LEN`, `HEADER_LEN`, `KEY_OFFSET_LEN`, `KEY_LEN_LEN`, `KEY_ENTRY_LEN`, `VALUE_ENTRY_LEN`, `ELEMENT_COUNT_LEN`, and `SIZE_LEN`.

Comparison precedence constants include `PRECEDENCE_BLOB`, `PRECEDENCE_BIT`, `PRECEDENCE_OPAQUE`, `PRECEDENCE_DATETIME`, `PRECEDENCE_TIME`, `PRECEDENCE_DATE`, `PRECEDENCE_BOOLEAN`, `PRECEDENCE_ARRAY`, `PRECEDENCE_OBJECT`, `PRECEDENCE_STRING`, `PRECEDENCE_NUMBER`, and `PRECEDENCE_NULL`.

## Control Flow
There is no executable control flow. The constants are consumed by other modules to compute offsets, lengths, and ordering categories. `HEADER_LEN` is derived from element-count and size lengths; key and value entry lengths are derived from their component widths.

## State and Persistence Behavior
The constants define the persisted binary JSON layout contract. Changing any length constant changes how JSON bytes are encoded and decoded. Changing precedence constants changes SQL-visible comparison behavior. The file itself holds no mutable state.

## Dependencies and Integration Points
This file has no imports. It is used by `binary.rs`, `jcodec.rs`, `comparison.rs`, and any other JSON module that needs binary layout or precedence definitions. The constants align TiKV's Rust implementation with TiDB's binary JSON format.

## Risks and Edge Cases
The major risk is drift from TiDB/MySQL binary JSON layout or precedence. Because many callers perform unchecked slicing based on these values, an incorrect size constant can cascade into panics or corrupt reads. There are no local tests, so coverage is indirect through JSON codec, navigation, comparison, containment, and depth tests.

## Test Signals
No tests live in this file. Effective test signals are the downstream tests in `binary.rs`, `jcodec.rs`, `comparison.rs`, `json_contains.rs`, and `json_depth.rs`, all of which rely on these constants for correct offsets and ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/constants.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/jcodec.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/jcodec.rs

## Purpose
`json/jcodec.rs` implements binary JSON encoding and decoding for TiKV MySQL JSON values. It writes owned or borrowed JSON documents into TiDB-compatible binary layout and reads that layout back into owned `Json` values. It also provides a simple datum-payload-to-chunk bridge for JSON.

## Important APIs, Types, and Functions
`JsonRef::encoded_len` returns the number of bytes a value contributes to the value area; literals are encoded inline in value entries and contribute zero appended bytes.

`JsonEncoder` provides `write_json`, `write_json_obj_from_keys_values`, `write_json_obj`, `write_json_ref_array`, `write_json_array`, `write_value_entry`, and scalar writers for literal, i64, u64, f64, string, and opaque values. Object and array writers build headers, entry tables, and value sections. `JsonDatumPayloadChunkEncoder::write_json_to_chunk_by_datum_payload` copies a JSON datum payload directly into chunk output. `JsonDecoder::read_json` reconstructs owned `Json` by reading the type byte and then the type-specific payload length.

## Control Flow
Top-level encoding writes the one-byte `JsonType` first, then writes the value bytes. Object encoding sorts key/value entries by key when given unsorted `Vec<(&[u8], JsonRef)>`; `BTreeMap` object encoding relies on map order. It computes key-entry length, value-entry length, key/value payload length, and total size, writes element count and size, writes key entries with offsets and lengths, writes value entries with either inline literal bytes or offsets, then appends keys and non-literal values.

Array encoding computes the value-entry table and appended value size, writes header and value entries, then appends non-literal values. `write_value_entry` writes literal values inline padded to four bytes, while all other types store a little-endian offset and advance the mutable value offset.

Decoding reads the type byte and then determines payload length by type: arrays/objects read their embedded size from the header, strings and opaque values read varint lengths, fixed-width numerics read eight bytes, literals read one byte, date/datetime/timestamp read eight bytes, and time reads twelve bytes.

## State and Persistence Behavior
The encoder defines persisted binary JSON bytes. It does not maintain mutable state beyond the output buffer and local offset counters. The chunk encoder preserves JSON datum payload bytes exactly, so JSON chunk values use the same binary representation as datum payloads.

## Dependencies and Integration Points
The module depends on `codec::prelude` buffer traits, `NumberCodec`, `BTreeMap`, `FieldTypeTp`, `Json`, `JsonRef`, `JsonType`, binary constants, and shared codec errors. It integrates with constructors and typed getters in `json/mod.rs`, navigation in `binary.rs`, comparison and JSON scalar functions, and vectorized chunk execution.

## Risks and Edge Cases
Object key lengths are cast to `u16` and offsets/sizes to `u32`; oversized JSON objects or keys could truncate if not rejected earlier. Decoding arrays/objects reads size from `value[ELEMENT_COUNT_LEN..]` after the type byte, so malformed or too-short buffers can panic before `read_bytes` returns an EOF error. Literal inline encoding assumes `v.value()[0]` exists. Opaque decoding assumes the first payload byte is a MySQL type code before the varint length. Correctness depends on matching `constants.rs` layout exactly.

## Test Signals
`test_json_binary` round-trips null, boolean, signed and unsigned integers, double, UTF-8 string, and nested object/array JSON values by writing with `write_json`, reading with `read_json`, and comparing string output.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/jcodec.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_contains.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_contains.rs

## Purpose
`json/json_contains.rs` implements MySQL `JSON_CONTAINS` semantics for binary JSON values. It answers whether a source JSON document contains a target JSON document using recursive object, array, and scalar rules compatible with TiDB.

## Important APIs, Types, and Functions
The file adds `JsonRef::json_contains(&self, target: JsonRef<'_>) -> Result<bool>`. It relies on `JsonType`, binary object/array accessors (`get_elem_count`, `object_get_key`, `object_get_val`, `object_search_key`, `array_get_elem`), and JSON comparison from `comparison.rs`.

## Control Flow
If the source is an object and the target is also an object, every target key must exist in the source object and the corresponding source value must recursively contain the target value. Empty target objects are therefore contained by any object. If the source is an array and target is an array, each target element must be contained somewhere in the source array. If the source is an array and target is not an array, any source element containing the target is sufficient. For scalar source values, containment is equality according to JSON partial comparison. All other object/non-object mismatches return false.

## State and Persistence Behavior
The function is read-only and recursively traverses borrowed binary JSON. It does not allocate persistent state or mutate the document. Its behavior is used by SQL predicate evaluation.

## Dependencies and Integration Points
The module depends on `JsonRef`, `JsonType`, shared `Result`, binary navigation from `binary.rs`, and comparison from `comparison.rs`. It integrates with MySQL JSON search functions in the expression layer and with object key sorting assumptions from the binary JSON encoder because `object_search_key` is binary search.

## Risks and Edge Cases
The scalar branch calls `self.partial_cmp(&target).unwrap()`, so malformed or non-comparable JSON that yields `None` can panic. Array containment is recursive and can revisit many nested values, so deeply nested or large arrays can be expensive. Object containment depends on sorted object keys; if a binary JSON object is malformed or unsorted, key search can return false even when bytes contain the key. Duplicate target array elements are checked independently and do not consume source elements.

## Test Signals
Tests cover object subset containment, empty objects, scalar/object mismatches, arrays containing scalars and arrays, nested arrays and objects, numeric/string distinctions, object-in-array containment, negative cases, and a large integer comparison edge.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_contains.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_depth.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_depth.rs

## Purpose
`json/json_depth.rs` implements JSON document depth calculation. It provides the behavior behind MySQL/TiDB JSON depth functions by recursively counting the maximum nesting level of arrays and objects.

## Important APIs, Types, and Functions
The public API is `JsonRef::depth(&self) -> Result<i64>`. The private recursive helper `depth_json(j: &JsonRef<'_>) -> Result<i64>` handles traversal. It uses `JsonType`, `get_elem_count`, `object_get_val`, and `array_get_elem`.

## Control Flow
For scalar JSON values, `depth_json` returns `0 + 1`, so scalars have depth 1. For objects, it iterates every value, recursively computes child depth, tracks the maximum, and returns `max_depth + 1`. Arrays follow the same pattern over elements. Empty arrays and objects have no children, so their max child depth remains zero and their depth is 1.

## State and Persistence Behavior
The calculation is read-only and keeps only stack-local recursion state. It does not persist or mutate anything. Returned depth is an `i64`, but traversal depth is bounded in practice by the binary JSON input and call stack.

## Dependencies and Integration Points
The module depends on `JsonRef`, `JsonType`, shared `Result`, and binary JSON navigation helpers. It integrates with scalar JSON functions and inherits binary layout assumptions from `binary.rs`.

## Risks and Edge Cases
Deeply nested JSON can cause deep recursion and potential stack pressure. Malformed binary JSON can make `object_get_val` or `array_get_elem` return errors or panic through lower-level slicing. Empty containers intentionally return depth 1, which matches MySQL semantics but can surprise callers expecting zero for empty documents.

## Test Signals
Tests cover null, booleans, numbers, strings, empty arrays/objects, flat arrays/objects, mixed arrays with objects, and deeply nested object/array structures up to depth 6.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_depth.rs -->
