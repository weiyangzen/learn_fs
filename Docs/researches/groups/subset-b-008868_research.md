# subset-b-008868 Research

Grouped research for the listed TiKV query common/datatype files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/storage/test_fixture.rs -->
# sources/storage-engines/tikv/components/tidb_query_common/src/storage/test_fixture.rs

## Purpose
Provides `FixtureStorage`, a test-only `Storage` implementation backed by an in-memory `BTreeMap<Vec<u8>, FixtureValue>`. It lets storage executor tests read deterministic key/value fixtures and inject per-key storage errors.

## APIs, Flow, And State
Important public pieces are `ErrorBuilder`, `FixtureValue`, `FixtureStorage::new`, conversions from byte-slice fixtures and `Vec<(Vec<u8>, Vec<u8>)>`, and the `Storage` trait methods `begin_scan`, `scan_next_entry`, `get_entry`, `collect_statistics`, and `met_uncacheable_data`. `begin_scan` creates a sorted map range from an `IntervalRange`, records direction and key-only flags, and stores an iterator with an erased lifetime. `scan_next_entry` advances from the front or back, clones returned keys/values, emits empty values for key-only scans, and calls the stored error builder for fixture errors. `get_entry` does point lookup by `PointRange`.

## Dependencies And Integration
Depends on the sibling storage range types, `OwnedKvPairEntry`, and the `Storage` trait. It integrates with unit tests and executor tests that need a simple source compatible with production storage APIs.

## Risks And Test Signals
The core risk is the unsafe transmute used to keep a `BTreeMap::Range` inside a self-referential storage object. It is acceptable only because the map is owned through `Arc` and results are cloned, but misuse around cloning or replacing `data` would be high risk. Tests cover point lookups, forward/backward scans, key-only mode, cloning mid-scan, and empty ranges.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/storage/test_fixture.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/util.rs -->
# sources/storage-engines/tikv/components/tidb_query_common/src/util.rs

## Purpose
Implements byte-prefix range helpers used by TiDB/TiKV coprocessor storage paths to detect point ranges and build exclusive prefix upper bounds.

## APIs, Flow, And State
`convert_to_prefix_next` mutates a key to the smallest lexicographically greater key representing the next prefix. Empty input becomes `[0]`; trailing `0xFF` bytes carry to zero; all-`0xFF` input appends a trailing zero after restoring the original bytes to `0xFF`. `is_prefix_next` checks whether `next` is exactly that transformation, including same-length carry cases and all-`0xFF` length-plus-one cases. `is_point` applies the check to a `kvproto::coprocessor::KeyRange` start/end pair.

## Dependencies And Integration
The file depends only on `kvproto::coprocessor::KeyRange`. It is used by query common storage/range logic to identify encoded point gets versus interval scans without decoding higher-level row keys.

## Risks And Test Signals
These helpers sit on range-boundary correctness, so off-by-one behavior could turn point reads into range scans or miss rows at prefix boundaries. Unit tests cover empty keys, normal increment, trailing carries, all-`0xFF` expansion, and many negative `is_prefix_next` examples.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_common/src/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/Cargo.toml -->
# sources/storage-engines/tikv/components/tidb_query_datatype/Cargo.toml

## Purpose
Defines the `tidb_query_datatype` Rust crate, which houses TiDB pushed-down query data types, codecs, collations, MySQL value representations, and related builders.

## APIs, Flow, And State
This manifest sets package metadata, Rust 2021 edition, unpublished status, Apache-2.0 licensing, and a Criterion benchmark target `bench_vector_distance`. It pulls in workspace crates such as `codec`, `kvproto`, `tidb_query_common`, `tipb`, `tikv_alloc`, and `tikv_util`, plus serialization, numeric, collation/encoding, regex, logging, and error crates. `criterion` is dev-only.

## Dependencies And Integration
The crate is part of TiKV's workspace and integrates with protobuf schemas (`tipb`, `kvproto`), storage/query common code, and codec primitives. The pinned TiKV fork of `encoding_rs` is an important charset dependency for collation/encoding behavior.

## Risks And Test Signals
The manifest's risks are dependency drift, pinned git dependency availability, and feature compatibility with workspace crates. Test signal is indirect: crate compilation, unit tests in codec/collation modules, and the Criterion benchmark target.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/benches/bench_vector_distance.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/benches/bench_vector_distance.rs

## Purpose
Provides Criterion microbenchmarks for vector distance and norm operations on `VectorFloat32Ref`, covering small 3-dimensional vectors and larger 784-dimensional vectors.

## APIs, Flow, And State
Each benchmark builds one or two `Vec<f32>` values, converts them through `VectorFloat32Ref::from_f32`, and benchmarks a single method inside `black_box`: `l1_distance`, `l2_squared_distance`, `l2_distance`, `inner_product`, `cosine_distance`, or `l2_norm`. `criterion_group!` registers all twelve benchmark functions and `criterion_main!` supplies the harness.

## Dependencies And Integration
Depends on `criterion` and `tidb_query_datatype::codec::mysql::VectorFloat32Ref`. It is wired by the crate manifest as `bench_vector_distance`.

## Risks And Test Signals
Benchmarks use identical input vectors, so they measure hot-path arithmetic and decoding-free vector reference overhead, not mismatched dimensions or error paths. They are performance signals, not correctness tests; correctness is implied by unwraps and by separate vector datatype tests elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/benches/bench_vector_distance.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/builder/field_type.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/builder/field_type.rs

## Purpose
Implements a fluent helper for constructing `tipb::FieldType` protobuf messages in tests and query datatype setup code.

## APIs, Flow, And State
`FieldTypeBuilder` wraps a `FieldType` and exposes chainable setters: `tp`, `flag`, `flen`, `decimal`, `collation`, and `charset`. Type, flag, length, decimal, and collation setters route through `FieldTypeAccessor` so enum/bit representations stay consistent with crate conventions. `charset` writes the protobuf string directly. `build` consumes the builder, and `From<FieldTypeBuilder> for FieldType` provides conversion ergonomics.

## Dependencies And Integration
Depends on `tipb::FieldType`, `FieldTypeAccessor`, `FieldTypeTp`, `FieldTypeFlag`, and `Collation`. It is re-exported by the builder module for callers needing compact schema construction.

## Risks And Test Signals
The builder is simple and has no persistence. Risk is mostly misuse: unset fields keep protobuf defaults, and `charset` bypasses accessor validation. Compile-time type checking and downstream field-type tests are the main signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/builder/field_type.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/builder/mod.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/builder/mod.rs

## Purpose
Defines the public builder namespace for query datatype helper constructors.

## APIs, Flow, And State
The module declares `field_type` and re-exports `FieldTypeBuilder`. There is no runtime control flow or stored state beyond Rust module resolution.

## Dependencies And Integration
Integrated by consumers importing `tidb_query_datatype::builder::FieldTypeBuilder`. It hides the concrete file layout and gives the crate a stable builder surface.

## Risks And Test Signals
Risk is minimal. Any missing or broken re-export is caught by compilation of callers and tests using the builder API.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/builder/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/batch/lazy_column.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/batch/lazy_column.rs

## Purpose
Defines `LazyBatchColumn`, a column container that can remain in raw datum bytes or be decoded into a typed `VectorValue` on demand. It reduces repeated serialization/deserialization in coprocessor batch execution.

## APIs, Flow, And State
The enum variants are `Raw(BufferVec)` and `Decoded(VectorValue)`. Constructors allocate raw or decoded storage, and accessors enforce the current state with panics on wrong-state use. `ensure_decoded` converts raw entries to typed values using `EvalType::try_from(field_type.tp())`, `RawDatumDecoder`, `EvalContext`, and `LogicalRows`. For referenced logical rows it builds a decode bitmap and fills unneeded physical positions with `None`; already-decoded columns are left unchanged. Encoding APIs either copy raw datum bytes, delegate to `VectorValue::encode`, or build chunk `Column` values for chunk output.

## Dependencies And Integration
Depends on `BufferVec`, `FieldType`, `EvalType`, `VectorValue`, `ChunkColumnEncoder`, `Column`, datum decoding, and `EvalContext`. It is used by `LazyBatchColumnVec` and batch executors as the bridge between storage datum format and TiDB chunk format.

## Risks And Test Signals
Risks include panics from wrong-state accessors, type/field mismatches during decode, and subtle physical versus logical row layout assumptions. Tests cover raw/decoded transitions, selective decode behavior, clone semantics, encoding, and benches compare `BufferVec` against vector-backed raw storage.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/batch/lazy_column.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/batch/lazy_column_vec.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/batch/lazy_column_vec.rs

## Purpose
Stores a batch of equal-length lazy columns plus optional common-handle keys exchanged between executors.

## APIs, Flow, And State
`LazyBatchColumnVec` wraps `Vec<LazyBatchColumn>` and `Option<Vec<Vec<u8>>>` for `extra_common_handle_keys`. It constructs from lazy columns or decoded `VectorValue`s, clones empty columns with preserved schema, exposes column and row counts, push/swap-remove adapters, equal-length assertion, maximum encoded-size estimates, row-wise binary encoding, and column-wise chunk encoding. It can truncate all columns to the shortest length and offers slice/index access for single and range indexing. Extra common handle keys are lazily allocated, queried, retrieved by row, or taken.

## Dependencies And Integration
Depends on `LazyBatchColumn`, `VectorValue`, `FieldType`, `EvalContext`, and codec `Result`. Batch executors use it as the shared row-batch container between scans, selections, expressions, and output encoders.

## Risks And Test Signals
The struct assumes equal column lengths but only enforces that when callers invoke `assert_columns_equal_length` or `truncate_into_equal_length`. Output offsets and schema indexes must align. Extra handle keys are not automatically length-checked against rows. Coverage is mostly through users and lazy column tests rather than direct tests in this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/batch/lazy_column_vec.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/batch/mod.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/batch/mod.rs

## Purpose
Defines the public batch codec module surface for lazy batch column containers.

## APIs, Flow, And State
The module declares `lazy_column` and `lazy_column_vec`, then re-exports `LazyBatchColumn` and `LazyBatchColumnVec`. It has no runtime control flow or persistence.

## Dependencies And Integration
Acts as the import boundary for batch executors and query code that need lazy column storage without referencing internal file names.

## Risks And Test Signals
Risk is limited to accidental API exposure changes. Compilation of downstream batch executor code is the main signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/batch/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/chunk/chunk.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/chunk/chunk.rs

## Purpose
Implements `Chunk`, a compact columnar row container compatible with TiDB chunk encoding. It supports appending datums, iterating rows, and encoding/decoding chunks for tests.

## APIs, Flow, And State
`Chunk` owns `Vec<Column>`. `new` builds one `Column` per `FieldType`; `reset` clears reusable buffers; `num_cols`, `num_rows`, `append_datum`, `get_row`, and `iter` expose row/column operations. `decode_for_test` reconstructs columns from encoded bytes. `ChunkEncoder::write_chunk` serializes each column. `Row` is a lightweight `(chunk, index)` view with `get_datum`, and `RowIterator` walks row indexes until `num_rows`.

## Dependencies And Integration
Depends on `Column`, `ChunkColumnEncoder`, `FieldTypeAccessor`, `Datum`, and codec buffer writer traits. It integrates with lazy batch chunk encoding and TiDB coprocessor response formats.

## Risks And Test Signals
`num_rows` trusts the first column length, so callers must keep columns aligned. `append_datum` indexes columns directly and can panic on bad indexes. Tests cover appending multiple datum types, constructing chunks from lazy raw columns, chunk encode/decode round trips, and benches for raw-datum to chunk encoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/chunk/chunk.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/chunk/column.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/chunk/column.rs

## Purpose
Implements the low-level columnar storage unit used by `Chunk`. `Column` stores null metadata, fixed or variable width payload data, and type-specific encode/decode routines for TiDB datum and chunk formats.

## APIs, Flow, And State
`Column` state includes `length`, `null_cnt`, `null_bitmap`, `var_offsets`, `data`, and `fixed_len`. `new` maps field types to fixed widths or variable layout. `from_raw_datums` decodes selected raw datum rows based on `EvalType`; `from_vector_value` converts typed vectors to chunk columns. `get_datum` reconstructs `Datum` values by field type. Append APIs cover nulls, signed/unsigned ints, bit, float/double, bytes, time, duration, decimal, JSON, vector-float32, and enum. Variable columns maintain a leading zero offset and append one offset per row; fixed columns resize data after writes. `ChunkColumnEncoder::write_chunk_column` writes length, null count, optional bitmap, optional offsets, and payload bytes.

## Dependencies And Integration
Depends on TiKV codec buffer traits, number codecs, MySQL datatype encoders/decoders, `VectorValue`, `EvalContext`, `FieldTypeAccessor`, `FieldTypeFlag`, and datum flags. It is the conversion point between row datum encoding, vectorized evaluation values, and chunk response bytes.

## Risks And Test Signals
Risks concentrate in datum flag handling, unsigned casts, bit field length handling, unimplemented Set and over-64-bit Bit paths, null bitmap correctness, and var-offset consistency. Tests cover each scalar family, chunk round trips, and raw/lazy conversion paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/chunk/column.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/chunk/mod.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/chunk/mod.rs

## Purpose
Defines the public chunk codec module surface.

## APIs, Flow, And State
The module declares `chunk` and `column`, re-exports `Chunk`, `ChunkEncoder`, `RowIterator`, `ChunkColumnEncoder`, and `Column`, and also re-exports codec `Error` and `Result`. There is no runtime state.

## Dependencies And Integration
Provides a stable import path for batch encoders, tests, and query datatype code needing chunk containers or chunk serialization helpers.

## Risks And Test Signals
Risk is limited to re-export churn. Downstream compile failures and chunk module tests signal issues.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/chunk/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/charset.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/charset.rs

## Purpose
Implements charset adapters used by collators to validate and decode character units from byte strings.

## APIs, Flow, And State
`CharsetBinary` treats each byte as a character, always validates, and decodes one byte at a time. `CharsetUtf8mb4` validates with `str::from_utf8` and decodes a Unicode scalar using `core::str::next_code_point`, returning the character and byte length. `CharsetGbk` and `CharsetGb18030` are aliases of `CharsetUtf8mb4` because TiKV stores those character data as UTF-8 internally for this layer.

## Dependencies And Integration
Depends on the collation `Charset` trait and crate-level `Charset` enum. Collator implementations bind to these charset types to define valid input and character weight input types.

## Risks And Test Signals
The UTF-8 decoder uses unsafe `from_u32_unchecked` after `next_code_point`; correctness depends on the standard library iterator. GBK/GB18030 aliases are an integration assumption that storage uses UTF-8 bytes, not original encoded bytes. Collator tests indirectly cover decoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/charset.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/binary.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/binary.rs

## Purpose
Implements the raw binary collation without padding semantics.

## APIs, Flow, And State
`CollatorBinary` uses `CharsetBinary`, byte weights, case-sensitive behavior, raw byte sort keys, direct byte-slice comparison, and raw byte hashing. It does not trim trailing spaces and ignores `force_no_pad` because binary collation is already no-padding here.

## Dependencies And Integration
Implements the shared `Collator` trait and is selected by `match_template_collator!` for `Collation::Binary`. It underpins binary string comparisons, sort keys, and hash semantics.

## Risks And Test Signals
The implementation is intentionally simple; risk is semantic mismatch with SQL padding expectations if used for a padded collation. Shared collation tests compare ordering, sort key, and hash equality behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/binary.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/gb18030_collation.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/gb18030_collation.rs

## Purpose
Implements `gb18030_bin` and `gb18030_chinese_ci` collators using generated Unicode-to-GB18030 weight tables.

## APIs, Flow, And State
`CollatorGb18030Bin` and `CollatorGb18030ChineseCi` implement `Collator` with `CharsetGb18030` and `u32` weights. `char_weight` indexes included four-byte tables by Unicode scalar. Sort-key writers trim padding, decode UTF-8, and emit big-endian one-, two-, or four-byte weights. The binary variant maps invalid UTF-8 bytes to `?`; the Chinese case-insensitive variant truncates on invalid sequences. `sort_compare` and `sort_hash` mirror those invalid-sequence policies and compare/hash weights directly.

## Dependencies And Integration
Depends on shared collation helpers, buffer writer/reader traits, and included data files `gb18030_bin.data` and `gb18030_chinese_ci.data`. It is selected through the collation macro for GB18030 collations.

## Risks And Test Signals
Risks include large table correctness, byte-order compatibility with TiDB/MySQL sort keys, and invalid UTF-8 policy differences between bin and Chinese CI variants. Tests verify representative weights; shared collator tests verify compare, hash, and sort key output.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/gb18030_collation.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/gbk_collation.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/gbk_collation.rs

## Purpose
Implements `gbk_bin` and `gbk_chinese_ci` collators using generated BMP-sized GBK weight tables.

## APIs, Flow, And State
The private `GbkCollator` trait supplies case-insensitive status, invalid-rune truncation policy, and a weight table. A blanket `Collator` implementation decodes UTF-8 characters, maps them to `u16` weights, writes variable-width sort keys, compares weight streams, and hashes weights after trimming padding. `CollatorGbkBin` is case-sensitive and substitutes `?` for invalid UTF-8. `CollatorGbkChineseCi` is case-insensitive and truncates comparison/hash/sort-key generation at invalid UTF-8.

## Dependencies And Integration
Depends on `CharsetGbk`, shared collation helpers, `BufferWriter`, `Hasher`, and included data files `gbk_bin.data` and `gbk_chinese_ci.data`. Integrated through `match_template_collator!`.

## Risks And Test Signals
Risks are table-generation correctness, invalid-character policy, and the assumption that stored GBK text arrives as UTF-8. Shared collation tests cover Chinese ordering, invalid runes, padding, sort keys, and hash equality.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/gbk_collation.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/latin1_bin.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/latin1_bin.rs

## Purpose
Implements `latin1_bin` collation with SQL padding behavior.

## APIs, Flow, And State
`CollatorLatin1Bin` uses `CharsetBinary`, byte weights, and case-sensitive semantics. `write_sort_key` trims trailing padding spaces before writing bytes. `sort_compare` trims trailing spaces unless `force_no_pad` is set, then uses byte comparison. `sort_hash` hashes the trimmed bytes so equal padded values hash equally.

## Dependencies And Integration
Depends on `bstr` trimming helpers, shared `PADDING_SPACE`, `BufferWriter`, and the `Collator` trait. It is selected through the collation macro for `Collation::Latin1Bin`.

## Risks And Test Signals
Main risk is padding semantics: only ASCII space is trimmed, while other trailing bytes remain significant. Dedicated tests in the collator module cover equal padded values and non-space trailing bytes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/latin1_bin.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/mod.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/mod.rs

## Purpose
Collects concrete collator implementations, re-exports them, and provides shared helpers and cross-collation tests.

## APIs, Flow, And State
The module declares binary, UTF8, GBK, GB18030, latin1, and UCA collator modules. It re-exports their public collator types. Shared helpers include `PADDING_SPACE`, `trim_end_padding`, and `next_utf8_char`, a small UTF-8 decoder that returns `(char, remaining_bytes)` or `None`. Tests iterate over multiple `Collation` enum values through `match_template_collator!`, checking compare results, sort hashes, and sort-key bytes for ASCII, accents, Unicode, Chinese text, invalid bytes, no-padding variants, and GB18030/GBK behavior.

## Dependencies And Integration
Depends on the collation trait layer, charset module, TiKV codec prelude, and concrete collator modules. This is the central module consumed by scalar/vector comparisons and sort-key generation.

## Risks And Test Signals
Risks include helper semantics shared by many collators, especially padding and invalid UTF-8 handling. The test matrix is a strong signal because it verifies comparison and hash agreement for equal values and exact sort-key bytes across collations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_binary.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_binary.rs

## Purpose
Implements UTF-8 binary collations with and without padding behavior.

## APIs, Flow, And State
`CollatorUtf8Mb4Bin` trims trailing padding spaces for sort keys, comparisons, and hashes unless `force_no_pad` is requested for comparison. `CollatorUtf8Mb4BinNoPadding` writes, compares, and hashes raw bytes without trimming. Both use `CharsetUtf8mb4`, Unicode scalar numeric weights, and case-sensitive semantics, but their sort operations are byte-based rather than weight-stream based.

## Dependencies And Integration
Depends on shared collation helpers and the `Collator` trait. `Utf8Mb4Bin`, `Utf8Mb4BinNoPadding`, and `Utf8Mb40900Bin` selection flows through `match_template_collator!`, with 0900 binary mapped to the no-padding implementation.

## Risks And Test Signals
Padding behavior is the key risk: the two types intentionally diverge for strings differing only by trailing spaces. Shared tests cover this distinction in compare, hash, and sort-key expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_binary.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_general_ci.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_general_ci.rs

## Purpose
Implements `utf8mb4_general_ci`, a case-insensitive UTF-8 collation using static Unicode-plane weight tables.

## APIs, Flow, And State
`CollatorUtf8Mb4GeneralCi` uses `CharsetUtf8mb4` and `u16` weights. `char_weight` maps code points above BMP to replacement weight `0xFFFD`; BMP code points consult a sparse plane table and fall back to the code point when no plane override exists. `write_sort_key` trims padding, decodes UTF-8 with `next_utf8_char`, writes big-endian weights, and stops at invalid bytes. `sort_compare` compares decoded weight streams and returns equality on invalid UTF-8. `sort_hash` hashes the same weights after padding trim.

## Dependencies And Integration
Depends on shared collation helpers, buffer writer traits, and the `Collator` trait. It is selected through `match_template_collator!` and used by string comparison, hashing, and sort-key paths for `utf8mb4_general_ci`.

## Risks And Test Signals
Risks are static table correctness, incomplete Unicode equivalence relative to newer UCA collations, and invalid UTF-8 truncation/equality behavior. Shared tests cover case folding, accent examples, non-BMP fallback, padding, exact sort keys, and hash consistency for equal comparisons.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_general_ci.rs -->
