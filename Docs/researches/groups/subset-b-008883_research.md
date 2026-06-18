# Research: subset-b-008883

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/logical_rows.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/logical_rows.rs

## Purpose
Defines the logical row indirection used by TiKV vectorized expression evaluation. `LogicalRows` represents either the identity row mapping for a batch or a borrowed slice of selected physical row indexes. This lets callers distinguish the common "all rows in physical order" case from a filtered/reordered selection without always materializing a `Vec<usize>`.

## Important APIs, Types, And Functions
- `BATCH_MAX_SIZE`: fixed batch cap of `1024`, documented as inherited from MonetDB/X100-style batch sizing rather than TiKV-specific benchmarks.
- `IDENTICAL_LOGICAL_ROWS`: compile-time initialized `[usize; BATCH_MAX_SIZE]` containing `0..BATCH_MAX_SIZE`.
- `LogicalRows<'a>`: `Identical { size }` for identity mappings and `Ref { logical_rows }` for borrowed index slices.
- `new_ident`, `from_slice`, `as_slice`, `get_idx`, `is_ident`, `len`, and `is_empty`: the core accessors used by evaluation code.
- `LogicalRowsIterator`: drives `IntoIterator` over either mapping mode.

## Control Flow
The identity path avoids dereferencing a slice in `get_idx` by returning the requested logical position. The borrowed path indexes into the supplied slice. `as_slice` bridges older call sites that still expect `&[usize]`; it returns a slice into `IDENTICAL_LOGICAL_ROWS` for identity mappings and panics if the requested identity size is at or above the static batch limit. Iteration repeatedly calls `len` and `get_idx`, increments its internal cursor, and ends after the logical row count.

## State And Persistence Behavior
There is no persistence or mutation beyond the iterator cursor. `LogicalRows` itself is `Copy` and only carries a size or borrowed slice. The static identity array is read-only process state and has no external serialization.

## Dependencies And Integration Points
This module is re-exported by `data_type/mod.rs` and underpins vectorized evaluation routines that accept logical row selections. It integrates with `VectorValue` encoding and evaluation paths indirectly because callers use logical rows to select physical vector indexes.

## Risks And Edge Cases
- `as_slice` is a compatibility escape hatch with a panic boundary for identity mappings whose size is not less than `BATCH_MAX_SIZE`; callers should prefer `get_idx` or iteration.
- `get_idx` does not bounds-check identity size against `idx` beyond normal slice behavior in the `Ref` case; callers must respect `len`.
- The batch size constant has a TODO noting lack of local benchmarking, so performance tuning may depend on assumptions from other systems.

## Test Signals
This file has no local tests. Coverage is likely indirect through vectorized evaluator tests that exercise filtered and identity logical row paths. Useful missing tests would cover `Identical` iteration, `Ref` iteration, empty mappings, and the `as_slice` panic boundary.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/logical_rows.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/mod.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/mod.rs

## Purpose
This is the central dynamic data-type facade for TiKV query evaluation. It declares concrete eval-type aliases, re-exports chunked vector storage implementations, and defines traits that connect concrete Rust values, borrowed references, scalar containers, and vector containers to TiDB `EvalType` metadata.

## Important APIs, Types, And Functions
- Module exports: chunked vectors for bytes, JSON, enum, set, sized scalar values, vector float32, bit vectors, `ScalarValue`, `ScalarValueRef`, `VectorValue`, and `VectorValueExt`.
- Type aliases: `Int = i64`, `Real = NotNan<f64>`, `Bytes = Vec<u8>`, and `BytesRef<'a> = &'a [u8]`.
- `match_template_evaltype!`: expands code over `Int`, `Real`, `Decimal`, `Bytes`, `DateTime`, `Duration`, `Json`, `Set`, `Enum`, and `VectorFloat32`.
- `AsMySqlBool`: converts concrete eval values and nullable references into MySQL truth values.
- `ChunkRef`, `ChunkedVec`, `Evaluable`, `EvaluableRet`, and `EvaluableRef`: generic contracts for vector storage, scalar borrowing, return-vector construction, and reference-to-owned conversion.
- `UnsafeRefInto`: intentionally unsafe lifetime widening helper used by aggregation macros.

## Control Flow
Most behavior is macro-expanded over eval types. `AsMySqlBool` implementations encode MySQL truth rules: numeric zero is false, bytes parse through `ConvertTo<f64>`, JSON delegates to `JsonRef::is_zero`, vector-float values are true when non-empty, and nullable wrappers are false on `None`. `Evaluable` and `EvaluableRef` perform dynamic enum variant checks and panic on mismatches, with special conversions for `Enum` as `Int` or `Bytes`. `EvaluableRet` converts concrete chunked storage back to `VectorValue`.

## State And Persistence Behavior
This module owns no persistent state. It defines in-memory contracts for columnar execution. The key state invariant is in `ChunkedVec`: the null bitmap and value buffer must be mutated together so equality and stored representations remain coherent for null rows.

## Dependencies And Integration Points
It bridges `EvalType`, `FieldTypeAccessor`, MySQL codec types, collations, conversion traits, `EvalContext`, and vector/scalar containers. Aggregation code relies on `UnsafeRefInto`; vectorized expression code relies on `Evaluable` and `EvaluableRef`; codec paths rely on exported concrete types and `AsMySqlBool`.

## Risks And Edge Cases
- Many wrong-type paths intentionally panic rather than return `Result`, so framework-level dispatch must keep `EvalType` and container variants aligned.
- Unsafe lifetime transmute is explicitly documented as used by aggregation update macros; misuse outside that pattern could create dangling references.
- Enum coercions reinterpret enum numeric values as `i64` via pointer casting; this is performance-sensitive and depends on representation assumptions.
- `BytesRef` truth conversion can return conversion errors for malformed numeric strings.
- `Set` support exists at the type-trait layer but encoding/decoding support is incomplete elsewhere.

## Test Signals
Local tests cover byte-to-bool conversion, parse errors, infinities, and `Real` truth conversion including NaN rejection via `NotNan`. Broader trait coverage is indirect through scalar/vector tests and expression evaluation tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/scalar.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/scalar.rs

## Purpose
Defines dynamic single-value containers for all eval types. `ScalarValue` owns an optional value, while `ScalarValueRef` borrows an optional value from a scalar or vector. The file also implements binary datum encoding, sort-key encoding/comparison, typed accessors, and conversions between owned and borrowed representations.

## Important APIs, Types, And Functions
- `ScalarValue`: variants for `Int`, `Real`, `Decimal`, `Bytes`, `DateTime`, `Duration`, `Json`, `Enum`, `Set`, and `VectorFloat32`, each wrapping `Option`.
- `ScalarValueRef<'a>`: borrowed counterpart using references or specialized ref types such as `JsonRef`, `EnumRef`, `SetRef`, and `VectorFloat32Ref`.
- `eval_type`, `as_scalar_value_ref`, `is_none`, `is_some`, and `to_owned`.
- `encode` and `encode_sort_key`: write evaluable datum bytes according to `FieldType` and `EvalContext`.
- `cmp_sort_key`: compares two scalar refs with unsigned integer handling and collation-aware byte comparison.
- `compare_int`: switches signed vs unsigned ordering using `FieldType::is_unsigned`.
- `impl_from!` and `impl_as_ref!`: provide typed conversions and accessors.

## Control Flow
Owned values convert to borrowed refs by mapping `Option<T>` to `Option<&T>` or specialized refs. Encoding matches the variant, writes null flags for `None`, and otherwise delegates to `EvaluableDatumEncoder`. Integer encoding checks field unsignedness and emits either signed or unsigned datum form. Byte sort-key encoding first computes a collation sort key and then encodes that byte sequence. Sort-key comparison uses normal option ordering for most variants, a custom unsigned-aware path for integers, and collator-specific byte comparison for bytes.

## State And Persistence Behavior
`ScalarValue` owns in-memory values; `ScalarValueRef` borrows them. Persistence happens only through datum encoding into caller-provided byte buffers. There is no file or database state in this module.

## Dependencies And Integration Points
Integrates with `tipb::FieldType`, `EvalContext`, `EvaluableDatumEncoder`, collator dispatch, `EvalType`, and MySQL concrete types. It is used by expression evaluation, vector element access, result encoding, and sorting code that needs dynamic scalar handling.

## Risks And Edge Cases
- `Enum` and `Set` scalar encoding are explicitly `unimplemented!`, so routing those values through generic encode paths can panic.
- `From<Option<f64>>` and `From<f64>` map NaN to `None` because `Real::new` rejects NaN; callers must not confuse this with SQL NULL semantics unless intended.
- Wrong-type conversions from `ScalarValue` into `Option<T>` panic with the dynamic eval type in the message.
- `cmp_sort_key` panics for cross-type comparisons and depends on correct `FieldType` collation/unsigned metadata.
- Accessor panic messages for enum/set mention `Int`, which may make diagnosis less precise.

## Test Signals
This file has no local test module. It is exercised indirectly by `VectorValue::get_scalar_ref`, codec encode tests, collated sorting, and expression evaluation tests. Missing direct tests include scalar encode for all supported types, unsigned integer comparison, collation sort-key behavior, and confirmation that enum/set encode panics are not hit by supported paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/scalar.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/vector.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/vector.rs

## Purpose
Defines `VectorValue`, the dynamic column container used by vectorized query execution. It wraps per-type chunked vector storage and provides uniform APIs for capacity management, append/truncate, scalar element access, MySQL truth evaluation, binary datum encoding, and type-specific push/extract helpers.

## Important APIs, Types, And Functions
- `VectorValue`: variants for every eval type, backed by matching `ChunkedVec*` storage.
- Constructors and metadata: `with_capacity`, `from_scalar`, `clone_empty`, `eval_type`, `len`, `is_empty`, `capacity`.
- Mutation: `truncate`, `clear`, `append`, explicit `push_*` methods, and generic `VectorValueExt<T>::push`.
- Access: `get_scalar_ref` and `to_*_vec` extraction methods.
- Encoding sizing: `maximum_encoded_size` and `maximum_encoded_size_chunk`.
- Encoding: `encode` and `encode_sort_key`.

## Control Flow
Construction dispatches on `EvalType` or `ScalarValue` variants. `from_scalar` fills a typed chunked vector with repeated nulls or cloned scalar values. `append` macro-dispatches on the left-hand variant and panics if the right-hand vector has a different eval type. Boolean evaluation iterates all rows and calls `AsMySqlBool` for each nullable element. Encoding retrieves the row element, writes a null datum for missing values, or delegates to `EvaluableDatumEncoder`; bytes sort-key encoding runs through the configured collator first.

## State And Persistence Behavior
The container owns in-memory column state through chunked vectors. Null state is maintained by the chunk implementations through their `ChunkedVec` contract. Persistence only occurs when encoded datum bytes are appended to caller buffers.

## Dependencies And Integration Points
This module sits between vectorized executors and low-level chunked storage modules. It uses `ScalarValueRef` for dynamic row access, `FieldTypeAccessor` and `EvalContext` for encoding, `DECIMAL_STRUCT_SIZE` and concrete MySQL type encoders for size estimates, and collation dispatch for sort keys.

## Risks And Edge Cases
- `Set` maximum-size and encoding paths are `unimplemented!`; generic code must avoid set vectors until support exists.
- Type mismatches in `append`, `push_*`, and `to_*_vec` panic rather than returning errors.
- `maximum_encoded_size` for decimal iterates selected rows and uses approximate sizes, with a FIXME noting a maximum-size-only approach would avoid iteration.
- Chunk-format sizing for variable-width values depends on offset overhead assumptions and selected logical rows.
- `eval_as_mysql_bools` asserts output capacity and then writes by index, so callers must provide a large enough buffer.

## Test Signals
Local tests cover basic capacity/length behavior, cloning, null/value pushes, truncation, enum/set empty vector construction, append semantics, and conversion from `ChunkedVecSized`. Encoding and size-estimate behavior are tested indirectly by codec and executor tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/vector.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/datum.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/datum.rs

## Purpose
Implements the legacy dynamic `Datum` representation and the original datum byte codec used for TiDB-compatible key/value encoding. It covers datum variants, comparison/coercion rules, conversion to primitive/MySQL types, arithmetic helpers, JSON conversion, encoding/decoding, size estimation, datum splitting, and skip helpers.

## Important APIs, Types, And Functions
- Datum flags: null, bytes, compact bytes, signed/unsigned integers, float, decimal, duration, varint forms, JSON, vector-float32, and max marker.
- `Datum`: variants for null, signed/unsigned integers, float, duration, bytes, decimal, time, JSON, vector-float32, enum, set, min, and max.
- Accessors: `as_int`, `as_real`, `as_decimal`, `as_string`, `as_time`, `as_duration`, `as_json`.
- Comparison: `cmp`, typed comparison helpers, `cmp_f64`, enum/set compare stubs.
- Conversion: `into_bool`, `to_string`, `into_string`, `into_f64`, `into_i64`, `into_arith`, `into_dec`, `cast_as_json`, `into_json`, `to_json_path_expr`.
- Arithmetic: `coerce`, `checked_div`, `checked_add`, `checked_minus`, `checked_mul`, `checked_rem`, and `checked_int_div`.
- Codecs: `DatumDecoder::read_datum`, `decode`, `DatumEncoder::write_datum`, `encode`, `encode_key`, `encode_value`, `encode_to`, `split_datum`, and `skip_n`.

## Control Flow
Comparison first handles JSON cross-type ordering specially, then dispatches by the right-hand datum variant. Numeric comparisons coerce as needed across signed, unsigned, float, decimal, string, time, and duration forms. Encoding iterates a datum slice, writes one flag per datum, and chooses comparable fixed-width encodings for keys versus compact/varint encodings for values. Decoding reads a flag and consumes the corresponding payload. `split_datum` computes the encoded length for the leading datum based on flag-specific payload rules, including JSON and vector-float32 reference decoders. Arithmetic helpers perform checked operations and convert divide-by-zero cases to `Datum::Null` for division/remainder semantics.

## State And Persistence Behavior
`Datum` owns in-memory values. Its persistent behavior is the encoded byte stream shared with TiDB: comparable encodings preserve sort order for key encoding, while value encoding uses compact forms. `Min` is special-cased so it must be the last datum when encoded, and `Max` uses its own flag.

## Dependencies And Integration Points
This file depends on the standalone `codec` crate for number and byte encodings, MySQL decimal/time/duration/JSON/vector-float32 codecs, `EvalContext` for warning/error and conversion behavior, TiKV byte-slice helpers, and conversion traits. It is used by row/table/index codec layers and remains a compatibility bridge alongside newer `ScalarValue`/`VectorValue` APIs.

## Risks And Edge Cases
- Several comments note differences or uncertainty versus TiDB behavior, especially decimal/time coercion and comparison.
- `Datum::VectorFloat32` comparison is not implemented, and enum/set encoding and size estimation are `unimplemented!`.
- `Datum::Min` uses `BYTES_FLAG` for backward compatibility and sets a guard requiring it to be the last datum.
- Float comparison returns an invalid-type error for unordered NaN cases.
- Some conversions use default `EvalContext`, which may not preserve caller-specific SQL mode or warning behavior.
- Decimal multiplication unwraps the decimal result and may panic if the decimal operation returns `None`.
- `split_datum` must exactly match all encoding formats; mistakes here affect key prefix parsing and skip logic.

## Test Signals
Local tests are extensive. They verify key/value round-trip encoding for primitive, decimal, JSON, duration, and vector-float32 data; cross-type comparison and encoded comparable ordering; MySQL boolean conversion; datum splitting for key/value buffers; coercion; JSON casts; JSON conversion; and primitive conversions to f64/i64. Gaps remain around enum/set and vector-float32 comparison/encoding edge cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/datum.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/datum_codec.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/datum_codec.rs

## Purpose
Provides the newer unified trait-based datum codec for evaluable types. It separates payload decoding/encoding from flag-and-payload encoding, then exposes typed raw datum decoders for vectorized storage paths.

## Important APIs, Types, And Functions
- `DatumPayloadDecoder`: reads typed payloads after the datum flag, wrapping codec errors as `Error::InvalidDataType`.
- `DatumPayloadEncoder`: writes payloads for integers, floats, decimals, compact bytes, JSON, vector-float32, and enum numeric values.
- `DatumFlagAndPayloadEncoder`: writes complete datum flag plus payload for null, integer, float, decimal, bytes, duration, datetime, JSON, vector-float32, and enum-as-uint.
- `EvaluableDatumEncoder`: semantically named encoder for eval values, mapping eval types to datum encodings.
- `ColumnIdDatumEncoder`: writes column IDs as var-int datum values.
- Typed decoders: `decode_int_datum`, `decode_real_datum`, `decode_decimal_datum`, `decode_bytes_datum`, `decode_date_time_datum`, `decode_duration_datum`, `decode_json_datum`, `decode_vector_float32_datum`, and `decode_enum_datum`.
- `RawDatumDecoder<T>`: generic trait implemented for `&[u8]` for supported eval types.

## Control Flow
Decoder helpers first check for an empty buffer, then strip the leading flag and validate that the flag is legal for the requested eval type. They accept both index and record encodings where TiDB uses different flags, for example bytes as comparable or compact bytes, datetime as `UINT` or `VAR_UINT`, and duration as duration or var-int. Encoding methods write the flag and delegate payload layout to lower-level codec traits. `decode_real_datum` also truncates double precision to float precision when the field type is `Float`, and wraps valid non-NaN results in `Real`.

## State And Persistence Behavior
This file has no in-memory state. Its persistence contract is exact datum byte compatibility across record/index encodings. All methods operate on caller-provided buffers or byte slices.

## Dependencies And Integration Points
It integrates `tipb::FieldType`, `FieldTypeAccessor`, `FieldTypeTp`, `EvalContext`, legacy datum flag constants, and MySQL encoders/decoders for decimal, duration, enum, JSON, time, and vector-float32. `ScalarValueRef` and `VectorValue` encoding paths call `EvaluableDatumEncoder`; table/row decoding can use `RawDatumDecoder`.

## Risks And Edge Cases
- Set decoding is `unimplemented!`; any generic set raw-decoder use will panic.
- Unsupported flags return detailed `InvalidDataType` errors, so callers must pass the correct field type and source encoding kind.
- Decimal encoding derives precision/fraction from the value, with a FIXME asking whether field type should provide them.
- Real decoding maps NaN to `None` through `Real::new(v).ok()`, which can blur invalid data and null semantics.
- Date/time and duration decoding require field metadata to unflatten packed values correctly.

## Test Signals
There is no local test module. Coverage is indirect through `ScalarValueRef`/`VectorValue` encoding and table/row codec decoding tests. Missing direct tests should enumerate accepted flags for each eval type and verify rejection messages for unsupported flags, especially record-vs-index encodings.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/datum_codec.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/error.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/error.rs

## Purpose
Defines the codec-layer error type and MySQL-compatible error codes used by TiKV query datatype encoding, decoding, conversion, and evaluation routines. It also maps these errors into protobuf and common evaluation error forms.

## Important APIs, Types, And Functions
- Error code constants for unknown errors, truncation, bad values, division by zero, data too long, regexp errors, timezone errors, zlib corruption, conversion failures, and overflow.
- `Error` enum: `InvalidDataType`, `Encoding`, `ColumnOffset`, `UnknownSignature`, `Eval`, `CorruptedData`, and boxed `Other`.
- Constructors: `overflow`, `truncated_wrong_val`, `truncated`, `m_bigger_than_d`, cast overflow helpers, timezone/division/data-too-long/conversion/datetime/zlib/parameter/regexp helpers.
- Inspectors: `code`, `is_overflow`, `is_truncated`, and `unexpected_eof`.
- Conversions into `tipb::Error`, `EvaluateError`, and from UTF-8, serde, parse-float, TiKV codec, IO, regexp, external codec, and datatype schema errors.
- `Result<T>` alias and `ErrorCodeExt` implementation.

## Control Flow
Most constructors format a MySQL-style message and wrap it in `Error::Eval` with the appropriate code. `code` returns the embedded eval code or `ERR_UNKNOWN` for structural errors. Conversion into `tipb::Error` copies the numeric code and rendered message. Conversion into `EvaluateError` preserves custom eval code/message but degrades non-eval errors into generic `Other` strings. `ErrorCodeExt` maps variants to TiKV error-code categories.

## State And Persistence Behavior
No mutable or persistent state. The persistence-facing behavior is serialized error propagation into `tipb::Error` and stable numeric MySQL/TiDB error codes.

## Dependencies And Integration Points
Used by nearly every codec submodule via `crate::codec::Result` and constructors. It integrates with `thiserror`, `error_code`, `tipb`, `tidb_query_common::error::EvaluateError`, regex/serde/codec error types, and scalar function signatures.

## Risks And Edge Cases
- Non-`Eval` variants collapse to `ERR_UNKNOWN` when converted to `tipb::Error`, so some structural failures may lose specific MySQL-style codes.
- Several external errors are boxed into `Other`, preserving text but not structured fields.
- `is_truncated` only checks `ERR_TRUNCATE_WRONG_VALUE`, not the `WARN_DATA_TRUNCATED` warning code returned by `truncated`.
- Error message compatibility matters because clients may compare TiDB/MySQL error strings.

## Test Signals
No local tests in this file. Indirect coverage comes from conversion, codec, regexp, time, and expression tests that assert error handling. Direct unit tests would be useful for code mappings, `tipb::Error` conversion, and warning-vs-error truncation distinctions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mod.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mod.rs

## Purpose
Declares the public codec module tree and shared codec-level helpers. It exposes the main submodules for batch, chunk, collation, conversion, data types, datums, MySQL types, row/table codecs, overflow helpers, and common error/result exports.

## Important APIs, Types, And Functions
- `invalid_type!` macro: local shortcut for creating `Error::InvalidDataType` from a literal or formatted message.
- Public modules: `batch`, `chunk`, `collation`, `convert`, `data_type`, `datum`, `datum_codec`, `error`, `mysql`, `row`, and `table`.
- Private module: `overflow`, with selected public re-exports.
- Public re-exports: `Datum`, `Error`, `Result`, `div_i64`, `div_i64_with_u64`, and `div_u64_with_i64`.
- `TEN_POW`: shared powers-of-ten table from `10^0` through `10^9`.

## Control Flow
The file is mostly declarative. The macro expands at call sites to construct invalid-data errors. Module visibility controls which codec subsystems are part of the crate API, and re-exports provide stable short paths for common datum/error/overflow items.

## State And Persistence Behavior
No runtime state or persistence. The powers-of-ten table is a static constant used by numeric/time/decimal logic elsewhere in the codec package.

## Dependencies And Integration Points
This is the integration root for all codec users in `tidb_query_datatype`. Other modules import `crate::codec::{Error, Result, Datum}` or call `invalid_type!`. Row/table/index codec layers are exposed here for higher-level query components.

## Risks And Edge Cases
- `invalid_type!` is defined in this module and relied on by child modules; macro visibility/order matters.
- Public module exports form a compatibility surface for downstream crates.
- The TODO about replacing the old failure-style boxed error shortcut signals historical error handling that may still leak through `box_err!` uses.

## Test Signals
No local tests. Module-level correctness is covered by successful compilation and downstream tests for the exposed submodules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/binary_literal.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/binary_literal.rs

## Purpose
Implements MySQL bit and hexadecimal literal handling. `BinaryLiteral` stores raw bytes and provides parsing, formatting, ordering, bit-string rendering, and unsigned-integer conversion with TiDB/MySQL truncation behavior.

## Important APIs, Types, And Functions
- `BinaryLiteral(Vec<u8>)`: internal byte-backed representation for bit and hex literals.
- `trim_leading_zero_bytes`: normalizes byte slices for comparison and integer conversion while preserving a single zero byte for all-zero inputs.
- Free `to_uint(ctx, bytes)`: converts big-endian bytes to `u64`, reporting truncation through `EvalContext` when more than 8 significant bytes remain.
- `BinaryLiteral::from_u64`: creates a big-endian literal with requested byte width or trimmed width.
- `from_hex_str`: parses `x'...'`, `X'...'`, and `0x...` forms.
- `from_bit_str`: parses `b'...'`, `B'...'`, and `0b...` forms into bytes, padding to byte boundaries.
- `to_bit_string`: renders `b'...'`, optionally trimming leading zero bits.
- `to_uint`, `Display`, `Eq`, `Ord`, `PartialEq`, and `PartialOrd`.

## Control Flow
Hex parsing validates the prefix, strips quote wrappers for `x'...'`, rejects odd-length quoted hex, and pads odd-length `0x...` input with a leading zero before decoding. Bit parsing validates the prefix, pads the bit stream to a byte boundary, then converts each 8-bit group with `usize::from_str_radix`. Integer conversion trims leading zero bytes, returns zero for empty input, signals truncation for more than eight significant bytes, and otherwise folds bytes in big-endian order. Ordering trims leading zeros, compares significant lengths, then compares bytes lexicographically.

## State And Persistence Behavior
No external persistence. The type owns bytes in memory. Its externally visible persistence form is string formatting (`0x...` or `b'...'`) and numeric conversion.

## Dependencies And Integration Points
Used by MySQL literal parsing and expression evaluation paths. It depends on the crate codec `Result`/`Error`, `EvalContext` for truncation handling, and the `hex` crate for decoding/encoding.

## Risks And Edge Cases
- `from_hex_str` accepts lowercase `0x` but not uppercase `0X`, matching the local tests but worth checking against parser expectations.
- Quoted hex literals must have an even number of digits; unquoted `0x...` odd lengths are padded.
- `from_bit_str` error messages for invalid prefixes mention hexadecimal format in one branch, which is misleading.
- `to_uint` returns `u64::MAX` after calling `handle_truncate_err`; depending on SQL mode, that call may produce an error instead.
- Formatting an empty literal displays as an empty string, while bit-string rendering displays `b''`.

## Test Signals
Local tests cover zero trimming, `from_u64` sizing, display formatting, hex parsing and invalid forms, bit parsing and invalid forms, bit-string rendering with and without trimming, unsigned conversion/truncation, and ordering with leading zeros.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/binary_literal.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/charset.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/charset.rs

## Purpose
Defines charset name constants and the set of multi-byte charsets recognized by the MySQL codec layer.

## Important APIs, Types, And Functions
- Charset constants: `CHARSET_BIN`, `CHARSET_UTF8`, `CHARSET_UTF8MB4`, `CHARSET_ASCII`, `CHARSET_LATIN1`, `CHARSET_GBK`, and `CHARSET_GB18030`.
- `MULTI_BYTES_CHARSETS`: lazy static `HashSet<&'static str>` containing `utf8`, `utf8mb4`, `gbk`, and `gb18030`.

## Control Flow
There is no dynamic control flow beyond lazy initialization of the hash set. Callers can test whether a charset is multi-byte using membership in `MULTI_BYTES_CHARSETS`.

## State And Persistence Behavior
The only state is process-local lazy static initialization. There is no serialization or persistent storage.

## Dependencies And Integration Points
Depends on `lazy_static` and `std::collections::HashSet`. Charset constants are used by string conversion, field metadata handling, and validation paths that need MySQL-compatible charset names or need to distinguish single-byte from multi-byte charsets.

## Risks And Edge Cases
- Adding a new multi-byte charset requires updating `MULTI_BYTES_CHARSETS`; the comment explicitly calls this out.
- Constants are stringly typed, so callers must normalize charset names before membership checks if inputs may vary in case or aliases.
- Rust treats `utf8mb4` equivalently to UTF-8 at the string level, but MySQL length and validation semantics may require additional checks elsewhere.

## Test Signals
No local tests. Coverage is indirect through conversion and charset validation tests. A small direct test could assert multi-byte membership and exclude binary/ascii/latin1.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/charset.rs -->
