# Research: subset-b-008882

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_uca/mod.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_uca/mod.rs

## Purpose
Implements Unicode Collation Algorithm based utf8mb4 collators for `utf8mb4_unicode_ci` and `utf8mb4_0900_ai_ci`. The file is a generic adapter over version-specific weight tables in `data_0400` and `data_0900`.

## Important APIs, Types, And Functions
`CollatorUtf8Mb4UnicodeCi` and `CollatorUtf8Mb40900AiCi` are type aliases over `CollatorUca<T>`. `UnicodeVersion` supplies `preprocess` and `char_weight`. `CollatorUca<T>` implements `Collator` with UTF-8 charset, `u128` weights, and case-insensitive semantics. The key methods are `write_sort_key`, `sort_compare`, and `sort_hash`.

## Control Flow
Each operation first applies version-specific preprocessing unless `sort_compare` is forced to no-pad. It then streams valid UTF-8 characters through `next_utf8_char`, obtains a packed `u128` collation weight, and processes 16-bit weight units from low to high. Sort-key writing serializes those units big-endian. Comparison lazily expands weights for both inputs, skips zero weights, and compares the first differing 16-bit unit. Invalid/truncated UTF-8 stops iteration and returns equality or the partial key/hash result.

## State And Persistence
The collator is stateless. `PhantomData<T>` binds the selected Unicode version at the type level. Persistent behavior is delegated to static data tables in the sibling modules.

## Dependencies And Integration Points
Depends on the parent collator framework, `CharsetUtf8mb4`, `BufferWriter`, `Hasher`, `Ordering`, and `next_utf8_char`. It is selected through the collation macros in `codec/collation/mod.rs`.

## Risks
Packed-weight ordering depends on the low-to-high 16-bit unpacking convention matching the generated tables. Invalid UTF-8 handling is permissive and can treat malformed tails as equal. Preprocessing controls padding behavior, so version-specific mistakes affect equality, hashing, and ordering together.

## Test Signals
No tests are local to this file. Coverage is expected through collation integration tests and generated data-table tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_uca/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/ascii.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/ascii.rs

## Purpose
Defines decoding behavior for binary and ASCII charsets. Binary is a pass-through; ASCII validates every byte.

## Important APIs, Types, And Functions
`EncodingBinary` implements `Encoding::decode` by cloning the input bytes. `EncodingAscii` implements `decode` by checking `u8::is_ascii` for every byte and returning `Error::cannot_convert_string` on the first non-ASCII byte.

## Control Flow
Binary decoding immediately returns `Bytes::from(data)`. ASCII decoding scans the full slice; if all bytes are ASCII it returns the original bytes, otherwise it formats a short escaped invalid-string preview through `format_invalid_char` and fails.

## State And Persistence
No state is stored. Both encoding structs are zero-sized strategy types.

## Dependencies And Integration Points
Depends on the shared `Encoding` trait and shared error formatter in `encoding/mod.rs`. It is exposed through `pub use ascii::*` and selected by `match_template_charset!` for `Binary` and `Ascii`.

## Risks
The failure message reports a preview of the whole input, not the exact invalid byte position. Binary intentionally skips validation, so callers must choose the correct strategy for user-visible charset conversion.

## Test Signals
No local unit tests. Behavior is simple enough that coverage likely comes from charset conversion paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/ascii.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/gb18030.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/gb18030.rs

## Purpose
Implements GB18030 charset conversion plus MySQL/TiDB-compatible case folding. It augments `encoding_rs::GB18030` with explicit mappings from `gb18030_data.rs` for standard-version differences and private-use code points.

## Important APIs, Types, And Functions
`EncodingGb18030` implements `Encoding`. `DECODE_MAP` maps encoded `u32` sequences to Unicode chars. `ENCODE_MAP` maps Unicode chars to the shortest explicit byte sequence. `decode`, `encode`, `lower`, and `upper` are the public trait methods.

## Control Flow
`decode` walks the byte slice with a `base` cursor. It classifies each character as one, two, or four bytes according to GB18030 byte ranges, rejects incomplete or illegal sequences, then decodes through `DECODE_MAP` or falls back to `encoding_rs`. `encode` validates UTF-8, iterates chars, uses `ENCODE_MAP` for explicit overrides, and falls back to `encoding_rs` per character. `lower` and `upper` stream chars into `BytesWriter`, preserving or specially mapping selected code points before falling back to `unicode_to_lower`/`unicode_to_upper`.

## State And Persistence
The only state is process-local lazy static hash maps built from the static table. No persisted data or mutation after initialization.

## Dependencies And Integration Points
Uses `lazy_static`, `collections::HashMap`, `encoding_rs::GB18030`, `gb18030_data::GB18030_TO_UNICODE`, and byte writers from `data_type`. Exposed by `encoding/mod.rs` and selected for `Charset::Gb18030`.

## Risks
Manual sequence classification is security-sensitive: off-by-one errors could accept invalid byte strings or panic. The explicit table must remain synchronized with standards and TiDB. Per-character fallback encoding allocates temporary strings. Case-folding exceptions are large and easy to regress.

## Test Signals
Local tests cover encode/decode examples for common Chinese text, Euro sign, private-use mappings, emoji/four-byte sequences, GB18030-2005, and GB18030-2022 cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/gb18030.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/gb18030_data.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/gb18030_data.rs

## Purpose
Provides the explicit GB18030-to-Unicode override table consumed by `gb18030.rs`. It captures private-use and standard-version mappings that should not rely solely on `encoding_rs`.

## Important APIs, Types, And Functions
Exports one constant: `GB18030_TO_UNICODE: &[(u32, char)]`. Entries encode one-, two-, or four-byte GB18030 byte sequences as big-endian `u32` keys paired with Unicode `char` values.

## Control Flow
There is no executable control flow. At runtime, `gb18030.rs` iterates this slice to build `DECODE_MAP` directly and `ENCODE_MAP` by converting each `u32` key to big-endian bytes and trimming leading zero bytes.

## State And Persistence
Static read-only data compiled into the binary. It is not persisted or mutated. Its order is not semantically important for hash-map lookups, but duplicate Unicode chars or duplicate keys would affect map construction.

## Dependencies And Integration Points
Only integrated by `codec/collation/encoding/gb18030.rs`. Tests in that module exercise representative table regions, including PUA ranges, two-byte `0xFE**` mappings, and four-byte mappings.

## Risks
The table is large and hand/generated data quality is the main risk. Duplicate keys or chars silently collapse when collected into hash maps. Incorrect mappings would produce cross-component incompatibility with TiDB/MySQL and make stored text compare or round-trip incorrectly.

## Test Signals
No local tests in the data file. Indirect tests in `gb18030.rs` assert encode/decode behavior for selected mappings from this table.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/gb18030_data.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/gbk.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/gbk.rs

## Purpose
Implements GBK charset decode/encode and GBK-specific upper/lower transforms.

## Important APIs, Types, And Functions
`EncodingGbk` implements `Encoding::decode`, `encode`, `lower`, and `upper`. It delegates charset conversion to `encoding_rs::GBK` and case mapping to `unicode_letter` with MySQL worklog exceptions.

## Control Flow
`decode` calls `decode_without_bom_handling_and_without_replacement`, returning a UTF-8 byte vector on success and `cannot_convert_string` on invalid GBK. `encode` validates input as UTF-8 and uses `GBK.encode`. `lower` and `upper` iterate over Unicode chars, keep selected code points unchanged, otherwise apply `unicode_to_lower` or `unicode_to_upper`, then write UTF-8 bytes via `BytesWriter`.

## State And Persistence
No state is stored; all behavior is stateless conversion over input slices.

## Dependencies And Integration Points
Depends on `encoding_rs::GBK`, `BytesWriter`, `BytesGuard`, and shared Unicode case helpers. It is exported from `encoding/mod.rs` and selected by charset template macros.

## Risks
`GBK.encode` replacement behavior must be acceptable for callers because encode does not surface an error for unrepresentable chars. The hard-coded case exceptions must match TiDB/MySQL exactly.

## Test Signals
No local tests; coverage is expected through charset conversion and string function tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/gbk.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/mod.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/mod.rs

## Purpose
Defines the encoding submodule boundary and shared invalid-character formatting for charset conversion errors.

## Important APIs, Types, And Functions
Declares modules `ascii`, `gb18030`, `gb18030_data`, `gbk`, `unicode_letter`, and `utf8`; re-exports all public encoding strategies except the raw data table. `format_invalid_char` returns a quoted preview with ASCII bytes as chars and non-ASCII as hex escapes.

## Control Flow
The formatter preallocates a small string, emits at most the first six bytes before appending ellipsis, then closes the quote. It is used by encoding implementations when constructing `Error::cannot_convert_string`.

## State And Persistence
No runtime state. The module is a compile-time organization point.

## Dependencies And Integration Points
Imports the parent `Encoding` trait, `Error`, `Result`, and byte aliases. Parent `collation/mod.rs` imports these concrete strategies for `match_template_charset!`.

## Risks
The preview loop uses `i > MAX_BYTES_TO_SHOW`, so it can include one byte more than the constant name suggests. Diagnostics are byte-oriented, not character-oriented. This is intentional but can be confusing for multibyte encodings.

## Test Signals
No local tests; indirectly covered by invalid charset conversion tests in concrete encodings.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/unicode_letter.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/unicode_letter.rs

## Purpose
Ports Go 1.21.3 Unicode case conversion logic so TiKV string functions match TiDB behavior.

## Important APIs, Types, And Functions
Constants identify upper, lower, and title case slots. `CASE_TABLE` stores sorted Unicode ranges and deltas. `to_case` performs range lookup and applies ordinary deltas or the `UPPER_LOWER` alternating-range rule. Public helpers are `unicode_to_upper`, `unicode_to_lower`, and `unicode_to_title`.

## Control Flow
ASCII is handled by direct arithmetic. Non-ASCII goes through binary search over `CASE_TABLE`; if a range matches, it applies the selected delta. For alternating upper/lower sequences, it clears or sets the low bit in the offset from the range start. If no range matches, the input char is returned unchanged.

## State And Persistence
Read-only static table only. No mutation or persisted state.

## Dependencies And Integration Points
Used by default `Encoding::lower`/`upper`, GBK, and GB18030. Its behavior is central to SQL `LOWER` and `UPPER` compatibility.

## Risks
The table is copied from a specific Go version, so future Unicode changes are intentionally not picked up unless regenerated. Invalid case indexes return replacement char internally. The `char::from_u32` return type forces callers to handle theoretically invalid mappings via `Option<char>`.

## Test Signals
Local `test_case` exercises ASCII, Latin-1, Turkish I, ligatures, Kelvin sign, and many table-driven mappings against expected case outputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/unicode_letter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/utf8.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/utf8.rs

## Purpose
Provides shared UTF-8-compatible decoding for `utf8mb4`, `utf8`, and `latin1` strategy types in this collation layer.

## Important APIs, Types, And Functions
`Utf8CompatibleEncoding` supplies a charset `NAME`. A blanket `Encoding` implementation validates with `str::from_utf8`. Concrete zero-sized types are `EncodingUtf8Mb4`, `EncodingUtf8`, and `EncodingLatin1`.

## Control Flow
`decode` tries to view the byte slice as UTF-8. On success it returns the same string bytes as owned `Bytes`; on failure it formats an invalid preview and returns `cannot_convert_string` with the concrete name.

## State And Persistence
Stateless strategy types only.

## Dependencies And Integration Points
Depends on shared `format_invalid_char`, `Error`, `Result`, and byte aliases from `encoding/mod.rs`. Selected by charset template macros in `collation/mod.rs`.

## Risks
`EncodingLatin1` being treated as UTF-8 compatible is a local compatibility choice; true Latin-1 byte decoding is not implemented here. Any caller expecting arbitrary `0x80..0xFF` Latin-1 bytes to decode will receive conversion errors.

## Test Signals
No local tests; validation is indirect through charset conversion behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/encoding/utf8.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/mod.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/mod.rs

## Purpose
Defines the core collation and encoding contracts, compile-time dispatch macros, and `SortKey` wrapper used to compare/hash values according to SQL collation semantics.

## Important APIs, Types, And Functions
Macros: `match_template_collator!`, `match_template_multiple_collators!`, and `match_template_charset!`. Traits: `Charset`, `Collator`, and `Encoding`. `SortKey<T, C>` wraps byte-like data with a collator marker and implements `Hash`, `Eq`, `Ord`, `Clone`, and `Deref`.

## Control Flow
Template macros map enum-like tags to concrete collator/encoding types. `SortKey::new`, `new_ref`, and option mapping functions validate charset bytes before transmuting or wrapping. Ordering and equality call `C::sort_compare`; hashing calls `C::sort_hash`; owned sort-key bytes can be generated through `Collator::sort_key`.

## State And Persistence
`SortKey` stores only the original byte container and `PhantomData<C>`. It does not cache computed sort keys. Unsafe reference mapping relies on `repr(transparent)` and identical layout with the wrapped value.

## Dependencies And Integration Points
Integrates charset modules, collator implementations, encoding strategies, `codec::prelude::BufferWriter`, `num::Unsigned`, byte data types, and generated collation enums. It is the central API used by expression evaluation, comparison, hash aggregation, and sorting code.

## Risks
`new_unchecked` and unsafe transmute helpers can panic later if invalid bytes are compared or hashed. `Hash`/`Ord` unwrap collator results, so validation must happen before use. Macro mappings must stay synchronized with collation IDs.

## Test Signals
No local tests. Behavior is exercised through individual collators, charset validation, and SQL comparison tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/convert.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/convert.rs

## Purpose
Implements MySQL/TiDB-compatible scalar conversions among integers, floats, decimals, strings/bytes, datetime/duration, JSON, enum, and field-type-constrained output values.

## Important APIs, Types, And Functions
Traits: `ToInt`, `ToStringValue`, `ConvertTo<T>`, and `ConvertFrom<T>`. Bound helpers: `integer_unsigned_upper_bound`, `integer_signed_upper_bound`, `integer_signed_lower_bound`. Conversion helpers include `truncate_binary`, `truncate_f64`, `get_valid_utf8_prefix`, `bytes_to_int_without_context`, `bytes_to_uint_without_context`, `produce_dec_with_specified_tp`, `produce_float_with_specified_tp`, `produce_str_with_specified_tp`, `pad_zero_for_binary_type`, `get_valid_int_prefix(_helper)`, and `get_valid_float_prefix(_helper)`.

## Control Flow
Generic `ConvertTo` routes through `ToInt`, `ConvertTo<f64>`, or `ToStringValue`. Numeric conversions clamp to type bounds and route warnings/errors through `EvalContext`. String-to-int first keeps the valid UTF-8 prefix, trims, extracts a numeric prefix, rounds float-like input to integer strings without losing decimal precision, parses, and clamps overflow. String-to-float extracts a valid float prefix and maps parse infinities to min/max with truncation handling. Field-type producers enforce `flen`, `decimal`, unsigned flags, multi-byte character truncation, binary zero padding, and statement-mode warning behavior.

## State And Persistence
No persistent state. All mutable effects are warnings/errors recorded in `EvalContext`.

## Dependencies And Integration Points
Depends on protobuf `FieldType`, field accessors, `FieldTypeTp`, `Collation`, MySQL decimal/time/json/vector data types, charset constants, `EvalContext`, flags, and result wrappers. Used broadly by expression evaluation and cast functions.

## Risks
Compatibility rules are subtle: signed/unsigned overflow, truncate-as-warning, invalid UTF-8 prefixes, exponent rounding, and binary padding all affect SQL-visible results. Some functions panic for unsupported field types. Float rounding differs between signed and unsigned paths (`round_ties_even` vs `round`). `ToStringValue` uses specialization and has FIXME notes for missing TiDB produce-string steps.

## Test Signals
Extensive local tests cover int/uint conversions, overflows, truncation, JSON casts, float parsing, valid-prefix extraction, binary truncation, float truncation, string production for UTF-8/GBK/GB18030/ASCII and invalid UTF-8, and decimal field-type production.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/convert.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/bit_vec.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/bit_vec.rs

## Purpose
Provides a compact boolean vector used as null/validity bitmaps in chunked column vectors.

## Important APIs, Types, And Functions
`BitVec` stores `Vec<u64>` plus logical `length`. Methods include `with_capacity`, `push`, `replace`, `len`, `is_empty`, `truncate`, `capacity`, `append`, and `get`. `BitAndIterator` streams the row-wise AND of multiple bitmaps.

## Control Flow
Bits are appended at `length & 63`, extending `data` by one word as needed. `replace` and `get` assert index bounds and use masks. `append` pushes every bit from the source then truncates the source to zero. `BitAndIterator` validates equal lengths, computes one 64-bit AND word every 64 rows, then shifts out booleans one by one.

## State And Persistence
In-memory only. `length` can be smaller than physical capacity. Truncation discards full trailing words but does not clear unused bits in the last retained word.

## Dependencies And Integration Points
Used by all `ChunkedVec*` implementations as validity/null bitmaps and by `ChunkRef::get_bit_vec` consumers.

## Risks
Bounds violations panic. `append` is O(n) over bits rather than word-level merging. `BitAndIterator` indexes `data[idx]` and assumes every bitmap has enough storage for its logical length; malformed `BitVec` construction would panic.

## Test Signals
Local tests cover capacity, length, push combinations, boundary alignment, replace combinations, append, truncate, and bitwise-AND iteration.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/bit_vec.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_bytes.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_bytes.rs

## Purpose
Stores `Option<Bytes>` column data compactly for vectorized evaluation.

## Important APIs, Types, And Functions
`ChunkedVecBytes` stores contiguous `data`, validity `bitmap`, logical `length`, and `var_offset` with a leading zero. Public helpers include `push_data_ref`, `push_ref`, `get`, and `into_writer`. Writer types `BytesWriter`, `PartialBytesWriter`, and `BytesGuard` support staged construction.

## Control Flow
Non-null pushes set the bitmap, append bytes, then call `finish_append` to push the new end offset and increment length. Null pushes only set bitmap false and duplicate the current offset. `get` slices `data[var_offset[idx]..var_offset[idx + 1]]` when valid. `append` drains another chunk's data and bitmap, offsets the other `var_offset` entries by the current data length, then resets the other chunk.

## State And Persistence
All state is in memory. Writers consume and return the chunk through guard types, preventing accidental partial ownership leaks in normal use.

## Dependencies And Integration Points
Implements `ChunkedVec<Bytes>` and `ChunkRef<BytesRef>`, uses `BitVec`, and exports byte writer utilities used by encoding lower/upper implementations.

## Risks
Offset invariants are critical; manual mutation could panic or slice incorrectly. `capacity` is approximate. Partial writer must be finished to record a row. `UnsafeRefInto` extends lifetimes for evaluator plumbing and must only be used while storage outlives refs.

## Test Signals
Local tests cover slice/vector construction, get basics, truncate, append/drain behavior, writer APIs including partial writes, plus benches for append and iteration.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_bytes.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_common.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_common.rs

## Purpose
Provides a macro with common `ChunkedVec` boilerplate for concrete column vector implementations.

## Important APIs, Types, And Functions
`impl_chunked_vec_common!($ty)` expands `from_slice`, `from_vec`, `push`, and `is_empty` methods for a `ChunkedVec<$ty>` implementation.

## Control Flow
`from_slice` allocates with slice length capacity and clones each optional element through `push`. `from_vec` consumes the vector and pushes each element. `push` dispatches `Some` to `push_data` and `None` to `push_null`. `is_empty` delegates to `len`.

## State And Persistence
No state of its own. It standardizes mutation behavior across chunked vectors.

## Dependencies And Integration Points
Invoked by bytes, JSON, enum, set, sized, and vector-float chunk implementations. Assumes each target type has `with_capacity`, `push_data`, `push_null`, and `len` methods from its `ChunkedVec` implementation.

## Risks
The macro clones slice elements, which can be expensive for large variable-length values. It also hides repeated behavior, so bugs in semantics are replicated across all chunked vector types.

## Test Signals
No local tests; all consumer modules exercise generated methods through their own `from_slice`, `from_vec`, and `push` tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_common.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_enum.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_enum.rs

## Purpose
Stores `Option<Enum>` values by splitting enum numeric values from display names while preserving borrowed `EnumRef` access.

## Important APIs, Types, And Functions
`ChunkedVecEnum` contains `values: ChunkedVecSized<Int>` and `names: ChunkedVecBytes`. Public accessors are `get`, `as_vec_int`, and `as_vec_bytes`. It implements `ChunkedVec<Enum>`, `PartialEq`, `ChunkRef<EnumRef>`, `From<Vec<Option<Enum>>>`, and `UnsafeRefInto`.

## Control Flow
`push_data` writes the enum's 1-based value as `i64` and the name bytes. `push_null` writes null to both child vectors. `get` reads the numeric reference and name, then constructs `EnumRef` using `retain_lifetime_transmute` for matching lifetimes. `append`, `truncate`, and `to_vec` delegate to both children in lockstep.

## State And Persistence
In-memory owned child vectors. Both child vectors duplicate null bitmaps; this is explicitly accepted to satisfy borrowing/lifetime constraints.

## Dependencies And Integration Points
Composes `ChunkedVecSized<Int>` and `ChunkedVecBytes`, integrates with evaluator `ChunkRef`, and exposes child vectors for consumers that need numeric or byte representations.

## Risks
The two child vectors must remain length/null aligned; any future direct mutation can corrupt representation. Unsafe lifetime retention is sound only while the chunk owns both children. Duplicated bitmaps waste memory.

## Test Signals
Local tests cover basics, truncation, append/drain behavior, and borrowed `EnumRef` equality.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_enum.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_json.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_json.rs

## Purpose
Stores `Option<Json>` values compactly in contiguous bytes for vectorized execution.

## Important APIs, Types, And Functions
`ChunkedVecJson` stores `data`, `bitmap`, `length`, and `var_offset`. It implements `get`, `ChunkedVec<Json>`, `ChunkRef<JsonRef>`, `From<Vec<Option<Json>>>`, and `UnsafeRefInto`.

## Control Flow
For non-null JSON, `push_data` sets bitmap true, writes one byte of `JsonType`, appends raw JSON value bytes, records end offset, and increments length. Nulls record the current offset with bitmap false. `get` checks bitmap, converts the first stored byte to `JsonType`, and returns `JsonRef` over the payload. `append` drains another chunk and offsets variable positions.

## State And Persistence
In-memory only. The first byte of every non-null row is type metadata; payload interpretation is delegated to JSON codecs.

## Dependencies And Integration Points
Depends on `Json`, `JsonRef`, `JsonType`, `BitVec`, and common chunk macros. Used by expression columns carrying JSON values.

## Risks
`JsonType::try_from(...).unwrap()` panics if stored bytes are corrupt. Offset invariants are critical. `UnsafeRefInto` must not outlive the backing vector.

## Test Signals
Local tests cover slice construction, basics, truncation, append/drain, string and numeric JSON examples.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_json.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_set.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_set.rs

## Purpose
Stores `Option<Set>` values as set-value bitmaps plus shared set-name data.

## Important APIs, Types, And Functions
`ChunkedVecSet` stores `data: Arc<BufferVec>`, validity `bitmap`, and per-row `value: Vec<u64>`. It implements `get`, `ChunkedVec<Set>`, `PartialEq`, `ChunkRef<SetRef>`, `From<Vec<Option<Set>>>`, and `UnsafeRefInto`.

## Control Flow
`push_data` sets bitmap true and pushes the set bitmask. `push_null` sets bitmap false and pushes zero. `get` returns `SetRef::new(&data, value[idx])` for non-null rows. `append` drains row values and bitmap from another vector but keeps the receiver's shared `data`.

## State And Persistence
In-memory row data plus an `Arc` to the set element names. The name buffer is not populated by the public API here; tests set it directly.

## Dependencies And Integration Points
Uses `tikv_util::buffer_vec::BufferVec`, `Arc`, `BitVec`, and evaluator `ChunkRef`. Integrates with MySQL SET scalar types.

## Risks
Appending vectors with different `data` dictionaries can produce wrong names because only row bitmasks are appended. Comments note missing setter support and future refactor needs. Bitmap and value vector must stay aligned.

## Test Signals
Local tests cover basics, truncation, append behavior, and equality over data, bitmap, and values.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_set.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_sized.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_sized.rs

## Purpose
Stores nullable fixed-size/primitive evaluation values compactly using a data vector plus validity bitmap.

## Important APIs, Types, And Functions
`ChunkedVecSized<T>` stores `data: Vec<T>`, `bitmap: BitVec`, and `PhantomData<T>`. It implements private `get`, `ChunkedVec<T>`, `ChunkRef<&T>`, `From<Vec<Option<T>>>`, and `UnsafeRefInto`.

## Control Flow
Non-null rows push the value and set bitmap true. Null rows set bitmap false and push `std::mem::zeroed()` as placeholder storage. `get` returns `Some(&data[idx])` only when the bitmap is true. `truncate` trims data and bitmap. `append` drains both data and bitmap from the source vector.

## State And Persistence
In-memory only. Null rows still occupy a `T` slot to preserve O(1) indexed access.

## Dependencies And Integration Points
Used for primitive/evaluable types such as `Int`, `Real`, `Decimal`, `DateTime`, and `Duration`, and as a child vector for enums. Requires `T: Clone` for owned chunk operations and `T: Evaluable + EvaluableRet` for borrowed chunk access.

## Risks
`std::mem::zeroed()` is unsafe for arbitrary `T`; the trait implementation allows any `T: Clone`, so correctness relies on only using types where zeroed is valid. Bounds violations panic. Unsafe lifetime extension is used for evaluator plumbing.

## Test Signals
Local tests cover construction for decimal, real, duration, datetime, and int values; basics; truncation; append; plus append/iterate benches.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_sized.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_vector_float32.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_vector_float32.rs

## Purpose
Stores nullable `VectorFloat32` values compactly as contiguous encoded bytes for vector-search related evaluation paths.

## Important APIs, Types, And Functions
`ChunkedVecVectorFloat32` stores `data`, `bitmap`, `length`, and `var_offset`. It implements `get`, `ChunkedVec<VectorFloat32>`, `ChunkRef<VectorFloat32Ref>`, `From<Vec<Option<VectorFloat32>>>`, and `UnsafeRefInto`.

## Control Flow
`push_data` marks the row valid, encodes `VectorFloat32Ref` into `data` using `write_vector_float32`, records the end offset, and increments length. `push_null` records a false bitmap and duplicate offset. `get` slices the row bytes, decodes a `VectorFloat32Ref` with `read_vector_float32_ref`, then unsafely extends the reference lifetime for return. `append`, `truncate`, and `to_vec` mirror other variable-length chunk vectors.

## State And Persistence
In-memory encoded vector bytes. Decoding borrows from `data`, so returned refs are tied to chunk storage despite unsafe lifetime adjustment.

## Dependencies And Integration Points
Depends on `VectorFloat32`, `VectorFloat32Ref`, MySQL vector encoder/decoder traits, `BitVec`, and chunk traits. Integrates vector data into the same nullable column abstraction as scalar types.

## Risks
`unwrap()` on encode/decode can panic if serialization fails or data is corrupt. Unsafe lifetime widening must not outlive backing storage. No local tests were present in the file, so regressions may rely on higher-level vector tests.

## Test Signals
No local unit tests. Expected coverage should come from vector codec and expression/chunk tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/chunked_vec_vector_float32.rs -->
