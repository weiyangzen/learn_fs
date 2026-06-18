# Research: subset-b-008886

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/mod.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/mod.rs

## Purpose
This module is the central MySQL `DATE`, `DATETIME`, and `TIMESTAMP` implementation for TiKV expression evaluation. It defines the packed `Time(u64)` bitfield, `TimeType`, parsing from strings and numeric values, MySQL-compatible validation rules, timestamp/time-zone conversion, date arithmetic, formatting, conversion to other scalar types, and codec helpers for datum payloads and chunk storage.

## Important APIs, Types, and Functions
`Time` stores year, month, day, hour, minute, second, microsecond, fractional-second precision, and type in one `u64`. `TimeType` maps to and from `FieldTypeTp::{Date, DateTime, Timestamp}`. Public constructors include `parse`, `parse_without_type`, `parse_datetime`, `parse_date`, `parse_timestamp`, `parse_from_i64`, `parse_from_real`, `parse_from_decimal`, their default-type variants, `from_packed_u64`, `from_duration`, `from_local_time`, `from_unixtime`, `from_year`, `from_days`, and `zero`. Public behavior methods include `round_frac`, `normalized`, `checked_add`, `checked_sub`, `add_sec_nanos`, `add_months`, `date_diff`, `ordinal`, `weekday`, `date_format`, `to_numeric_string`, `get_daynr`, and `timestamp_diff`.

The private `parser` module implements MySQL/TiDB permissive date parsing, including digit-only inputs, punctuation-heavy separated inputs, fractional seconds with optional rounding, two-digit year adjustment, real/decimal string parsing, and ISO8601 timezone suffixes such as `Z`, `+0800`, `-08`, and `+08:30`. The private `date_format_parser` module implements `str_to_date` behavior for tokens such as `%Y`, `%y`, `%m`, `%d`, `%H`, `%h`, `%p`, `%f`, `%j`, `%r`, `%T`, `%#`, `%.`, and `%@`.

## Control Flow and Validation
Parsing starts by trimming input, splitting components and optional time-zone offset, inferring a type when no explicit type is supplied, building a seven-part array, applying fractional rounding and component carry, then calling `Time::from_slice`. `Time::new` delegates to `TimeArgs::check`, which selects date/datetime/timestamp validation. Zero dates and zero-in-date values are routed through `handle_zero_date`, `handle_zero_in_date`, and `handle_invalid_date`, which interpret `EvalContext` SQL modes and flags such as strict mode, `NO_ZERO_DATE`, `NO_ZERO_IN_DATE`, `INVALID_DATES`, and `IGNORE_TRUNCATE`.

For `Timestamp`, validation creates a chrono value in `ctx.cfg.tz`, then ensures the Unix timestamp is in `[0, 2^31 - 1]`. For packed conversion, `to_packed_u64` converts timestamps to UTC before packing, and `from_packed_u64` converts packed UTC timestamp fields back into the evaluation time zone. Date arithmetic normalizes invalid-but-allowed dates where needed, uses chrono checked operations for second/nanosecond additions, and clamps month addition to the target month length.

## State and Persistence Behavior
The module has no external persistence. Its persistent representation is the in-memory and encoded `Time(u64)` layout. Datum/chunk persistence is exposed through `TimeEncoder`, `TimeDatumPayloadChunkEncoder`, and `TimeDecoder`: chunk encoding writes the raw little-endian bitfield, while datum payload decoders read packed unsigned integers or varints according to a `FieldType`. Comparisons, hashing, and equality explicitly clear the precision/type low bits, so ordering is based on date-time components rather than field type or FSP.

## Dependencies and Integration Points
The module depends heavily on `chrono` and the local `Tz` wrapper for local/named/fixed time-zone handling. It integrates with TiKV codec traits from `codec::prelude`, field metadata via `FieldType` and `FieldTypeAccessor`, MySQL scalar types `Decimal`, `Duration`, and `Real`, interval units from `interval`, week behavior from `weekmode`, and extension methods from `extension` for week/day names and day suffixes. `EvalContext` is the key integration point for SQL mode, warnings, flags, and time-zone configuration.

## Risks and Edge Cases
The bitfield layout makes pre-validation mandatory because oversized component values would otherwise wrap in narrow fields. Time-zone parsing and DST behavior are sensitive: `chrono_datetime` chooses the earliest local result and treats nonexistent/ambiguous local times as truncation. Timestamp range is MySQL/TiDB-specific and capped at 2038-style signed 32-bit seconds. Zero date handling changes substantially with SQL mode and warnings. `checked_add`/`checked_sub` return `TimeType::Timestamp` even when operating on non-timestamp inputs, which is intentional in this implementation but should be watched when refactoring. `round_components` returns `None` when carrying through zero month/day, causing callers to reset or fail depending on the entry point.

## Test Signals
The test module is broad. It covers integer/real/decimal parsing, zero-date mode behavior, valid and invalid date/datetime/timestamp strings, ISO8601 timezone offsets, invalid-date SQL modes, codec round trips for datetime and timestamp, comparisons, duration and local-time construction, fractional rounding, normalization of invalid dates, DST-aware add/subtract, weekday/date formatting/numeric string conversions, conversion to decimal and f64, month addition, second/nanosecond addition, day number conversion, and `timestamp_diff` units. The tests are strong signals for compatibility with TiDB/MySQL edge behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/tz.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/tz.rs

## Purpose
This file defines TiKV's unified time-zone wrapper for MySQL time handling. `Tz` abstracts over fixed offsets, IANA named zones from `chrono_tz`, and the host local time zone so the rest of the MySQL time module can operate through chrono's `TimeZone` trait.

## Important APIs, Types, and Functions
`Tz` has variants `Offset(FixedOffset)`, `Name(chrono_tz::Tz)`, and `Local(Local)`. Constructors are `from_offset(secs)`, `from_tz_name(name)`, `utc()`, and `local()`. `from_tz_name("system")` maps to local time. `get_chrono_tz` returns the named zone only when the variant is `Name`, which lets callers distinguish IANA zones from fixed/local zones.

`TzOffset` mirrors the selected zone result as `Local(FixedOffset)`, `Fixed(FixedOffset)`, or `NonFixed(<chrono_tz::Tz as TimeZone>::Offset)`. It implements chrono `Offset` by returning a fixed offset via `fix`.

## Control Flow and State
The `TimeZone for Tz` implementation delegates every chrono offset lookup and local/UTC construction method to the wrapped variant, then wraps the returned offset in the corresponding `TzOffset`. This preserves whether the source was local, fixed, or named while still allowing chrono `Date` and `DateTime` values to be produced with `Tz` as the zone type. Formatting uses debug-style output for fixed and named zones because those chrono types do not expose the desired `Display`.

## Dependencies and Integration Points
This module depends on `chrono` and `chrono_tz`. It is re-exported by `time/mod.rs` and used by `EvalConfig`/`EvalContext` consumers to parse, validate, pack, unpack, and display timestamp values. It is also used in tests to force UTC, fixed offsets, and named DST-aware zones such as `America/New_York`.

## Risks and Edge Cases
`from_offset` casts `i64` to `i32` before `FixedOffset::east_opt`, so callers should pass chrono-valid second offsets. `Local` depends on host environment settings, which can make behavior less reproducible than named or fixed zones. Named zones can produce ambiguous or nonexistent local times at DST boundaries; callers in `mod.rs` generally choose `earliest()` and convert failures to truncation.

## Test Signals
This file has no local tests, but it is exercised indirectly by the time module's timestamp parsing, timezone suffix conversion, local-time construction, packed timestamp codec, and DST arithmetic tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/tz.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/weekmode.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/weekmode.rs

## Purpose
This small file defines MySQL week-mode flags used by date formatting and week/year-week calculations.

## Important APIs, Types, and Functions
`WeekMode` is a `bitflags` type with `BEHAVIOR_MONDAY_FIRST`, `BEHAVIOR_YEAR`, and `BEHAVIOR_FIRST_WEEKDAY`. `to_normalized` applies MySQL normalization: when Monday-first is not set, `BEHAVIOR_FIRST_WEEKDAY` is toggled. This mirrors the behavior used by TiDB/MySQL week calculations where mode bits are not interpreted independently.

## Control Flow and State
There is no persisted state. `to_normalized` copies the flag value, conditionally XORs the first-weekday bit, and returns the adjusted flag set.

## Dependencies and Integration Points
The only direct dependency is `bitflags`. The type is re-exported by `time/mod.rs` and used by time extension/date-format logic for `%U`, `%u`, `%V`, `%v`, `%X`, and `%x` formatting, plus public week/year-week APIs defined in the time extension module.

## Risks and Edge Cases
The main risk is semantic compatibility: changing the normalization rule would alter MySQL-compatible week numbering. Since the file itself has no tests, coverage is indirect through date-format and week calculation tests in the time module and extension module.

## Test Signals
No local test module exists. `time/mod.rs` date-format tests exercise week-related format tokens using `WeekMode::from_bits_truncate` values.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/time/weekmode.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/vector.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/vector.rs

## Purpose
This file implements TiKV's MySQL vector-float32 scalar representation and codec helpers. It stores vectors as raw little-endian `f32` bytes to avoid alignment requirements when data originates from protobuf or row buffers.

## Important APIs, Types, and Functions
`VectorFloat32` owns a `Vec<u8>` and validates through `VectorFloat32Ref::new`. `VectorFloat32Ref<'a>` borrows the byte slice and exposes `len`, `is_empty`, `encoded_len`, `to_owned`, `from_f32`, distance functions, formatting, and ordering. Supported metrics are `l2_squared_distance`, `l2_distance`, `inner_product`, `cosine_distance`, `l1_distance`, and `l2_norm`.

`VectorFloat32Encoder` writes a `u32` little-endian element count followed by raw bytes. `VectorFloat32Decoder` reads that format and validates the resulting slice. `VectorFloat32DatumPayloadChunkEncoder` copies datum payload bytes directly because the chunk format matches the binary format.

## Control Flow and State
Validation checks that byte length is a multiple of four and rejects NaN or infinite values by reading each element with `read_unaligned`. Ordering is lexicographic by float values, then by length. Distance operations first enforce equal dimensions through `check_dims`, then loop over elements using an unsafe unchecked accessor. `l2_norm` intentionally accumulates in `f64` to align with pgvector behavior, while the other metrics accumulate intermediate values in `f32` and return `f64`.

## Dependencies and Integration Points
The module depends on `codec::prelude` for buffer reader/writer traits and number encoding, `bytemuck::cast_slice` for `f32` to byte-slice views, and local `crate::codec::Result`. It integrates with MySQL datum handling through the `FieldTypeTp::TiDbVectorFloat32` path in row v2 compatibility and datum payload/chunk encoders.

## Risks and Edge Cases
The implementation only supports little-endian targets for encode/decode. Borrowed slices can be unaligned by design, so all float reads use `read_unaligned`; this is correct but concentrates safety around index bounds. `index` and debug bounds in `index_unchecked` use `idx > self.len()` instead of `idx >= self.len()`, so direct calls with `idx == len` would read past the logical end; current loops use `0..len`, but this is a risk for future changes. Cosine distance returns `NaN` on zero-norm division and clamps non-NaN similarity to `[-1, 1]`.

## Test Signals
Tests cover NaN/infinity rejection, string formatting, invalid byte length, lexicographic comparison, binary encoding layout, decoding with remaining bytes, empty-vector decoding, and error preservation when decoding incomplete data.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/vector.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/overflow.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/overflow.rs

## Purpose
This file provides checked division helpers for mixed signed and unsigned integer arithmetic where MySQL/TiDB semantics require division-by-zero and unsigned overflow errors instead of Rust panics or wrapping behavior.

## Important APIs, Types, and Functions
`div_i64(a, b)` returns signed division or `Error::division_by_zero`; it detects the `i64::MIN / -1` overflow through `overflowing_div`. `div_u64_with_i64(a, b)` divides an unsigned numerator by a signed denominator, returning unsigned results and raising overflow when a negative divisor would imply an out-of-range unsigned result. `div_i64_with_u64(a, b)` handles a signed numerator and unsigned divisor similarly.

## Control Flow and State
Each function first rejects a zero divisor. The signed/signed function delegates overflow detection to Rust's intrinsic checked flag. The mixed functions branch on the signed operand's negativity: negative combinations either return `0` when the absolute magnitude is below the divisor or raise `UNSIGNED BIGINT` overflow when the result would not fit MySQL unsigned semantics.

## Dependencies and Integration Points
The module depends only on `crate::codec::{Error, Result}`. It is a utility for codec/expression arithmetic paths that need consistent TiDB/MySQL error codes, especially `ERR_DIVISION_BY_ZERO` and `ERR_DATA_OUT_OF_RANGE`.

## Risks and Edge Cases
The exact overflow thresholds are subtle around `i64::MIN`, because negating it overflows and the code uses `overflowing_neg().0` before casting to `u64`. Current behavior is intentional and tested, but future simplification could easily change edge semantics. Error messages identify `"UNSIGNED BIGINT"` for overflow, so callers may depend on that type string.

## Test Signals
The test matrix covers signed overflow, positive and negative signed division, mixed signed/unsigned boundary cases, and division by zero for all three helpers with expected codec error codes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/overflow.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/mod.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/mod.rs

## Purpose
This is the row codec module entry point. It currently exposes only the v2 row codec submodule.

## Important APIs, Types, and Functions
The file contains `pub mod v2;`, making `crate::codec::row::v2` available to downstream code. There are no local functions or types.

## Control Flow and State
There is no runtime control flow and no state. The file is purely a module declaration.

## Dependencies and Integration Points
It integrates the v2 row codec with the surrounding `codec` namespace. Consumers reach row-slice decoding, v1 compatibility, and test row encoders through this module tree.

## Risks and Edge Cases
The main risk is accidental module visibility changes. Removing or renaming this declaration would break all `codec::row::v2` imports. There are no direct tests for this file beyond compilation of downstream modules.

## Test Signals
Coverage is compile-time: all tests in `row/v2` depend on this module path being available.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/v2/compat_v1.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/v2/compat_v1.rs

## Purpose
This file converts row-format-v2 encoded column values into v1 datum-compatible encodings. It is the bridge for code that decodes or transports row v2 data through older datum APIs.

## Important APIs, Types, and Functions
`decode_v2_u64` reads 1, 2, 4, or 8 byte little-endian unsigned integer payloads, matching TiDB's compact row v2 integer encoding. The private `decode_v2_i64` does the signed equivalent through sign-extending casts from 1, 2, 4, or 8 byte payloads. `V1CompatibleEncoder` extends `DatumFlagAndPayloadEncoder` with helpers for v2 signed/unsigned integers, duration, and the central `write_v2_as_datum(src, ft)`.

`write_v2_as_datum` maps `FieldTypeTp` to v1 datum flags and payload encodings. Integer-like fields choose signed or unsigned by field flag. Float/double, decimal, JSON, and vector payloads are copied after writing the corresponding datum flag. String/blob/geometry fields use compact bytes. Date/time/enum/bit/set use unsigned integer datum encoding. Year uses signed integer encoding. Duration intentionally uses `DURATION_FLAG` instead of TiDB's varint choice because the fixed payload is faster in TiKV.

## Control Flow and State
The conversion is stateless and writes directly into the destination buffer. Invalid compact integer widths and unsupported field types return `Error::InvalidDataType`. Null field type writes only `NIL_FLAG`.

## Dependencies and Integration Points
The file depends on `codec::number::NumberCodec`, `BufferWriter`, field metadata traits, and datum codec helpers. It integrates with `encoder_for_test` in tests and with `RawDatumDecoder` to prove that converted bytes decode as the expected high-level scalar values. It also recognizes `FieldTypeTp::TiDbVectorFloat32`, linking row compatibility to vector datum support.

## Risks and Edge Cases
Correctness depends on field metadata matching the v2 payload bytes. A mismatched type can copy arbitrary payload bytes under a misleading datum flag. Compact integer widths outside 1, 2, 4, or 8 bytes are rejected. The duration behavior intentionally differs from TiDB, so cross-component assumptions about exact v1 bytes should account for the TiKV-specific `DURATION_FLAG` choice.

## Test Signals
Tests encode values through the v2 test encoder, convert with `V1CompatibleEncoder`, and decode with `RawDatumDecoder`. Covered types include signed and unsigned integers, real numbers including infinities, decimals, bytes including non-ASCII data, date/datetime/timestamp, JSON, and duration.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/v2/compat_v1.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/v2/encoder_for_test.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/v2/encoder_for_test.rs

## Purpose
This test-only module builds row-format-v2 byte buffers for unit tests. It is intentionally straightforward and mirrors the TiDB row v2 layout: version, flags, non-null/null counts, sorted column IDs, offsets, values, and optional checksum bytes.

## Important APIs, Types, and Functions
`Column` carries a column id, `ScalarValue`, and `FieldType`, with builders for type, unsigned flag, and decimal precision. `Column::encode_for_checksum` serializes supported column values into the TiDB checksum input format. `ChecksumHandler` abstracts checksum calculation and metadata. `Crc32RowChecksumHandler` implements it with `crc32fast` and `ChecksumHeader`.

`RowEncoder` extends `NumberEncoder` with `write_row`, `write_row_with_checksum`, and `write_row_impl`. It sorts non-null columns and null IDs, chooses small or big format, writes IDs and offsets at the selected width, writes scalar values, and appends checksum header/value and optional extra checksum. `ScalarValueEncoder` writes compact v2 payloads for signed/unsigned integers, decimals, reals, bytes, datetime, duration, and JSON. `prepare_cols_for_test` supplies a representative row for checksum tests.

## Control Flow and State
`write_row_impl` scans input columns to determine whether any ID exceeds 255, separates null from non-null values, sorts by column ID, encodes non-null payloads while collecting end offsets, upgrades to big format if value bytes exceed `u16::MAX`, then emits the full row. Checksums are calculated before row encoding over sorted non-null columns. The checksum handler stores a reusable buffer and crc32 hasher state.

## Dependencies and Integration Points
The module depends on `codec::prelude`, `tipb::FieldType`, field accessor traits, `ScalarValue`, MySQL decimal/json/duration encoders, `EvalContext`, and `crc32fast`. It is used by row v2 tests and by v1 compatibility tests to create authoritative v2 payloads without relying on production TiDB encoders.

## Risks and Edge Cases
This module is test-only, so production safety risk is low, but its byte expectations influence codec compatibility tests. Unsupported scalar/type combinations return errors in checksum encoding and `write_value` uses `unreachable!()` for unsupported or null values after the caller has filtered nulls. IDs are cast to `u8` or `u32` based on the selected format, so invalid negative IDs would produce nonsensical bytes if introduced by a test.

## Test Signals
Tests assert exact encoded bytes for unsigned integer rows, mixed-type small rows, big rows with IDs above 255, and checksum rows with header version bits and optional extra checksum. They also verify checksum calculation against independently fed crc32 bytes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/v2/encoder_for_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/v2/mod.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/v2/mod.rs

## Purpose
This file defines the row v2 module boundary, version byte, row flags, and public re-exports.

## Important APIs, Types, and Functions
`CODEC_VERSION` is `128`. The comment explains that v1 used the first byte as a datum type, so v2 starts at 128 for compatibility. Internal `Flags` has `BIG` and `WITH_CHECKSUM` bits. The module declares `compat_v1` and `row_slice`, re-exports their public APIs, and exposes `encoder_for_test`.

## Control Flow and State
There is no runtime logic beyond bitflag construction in downstream modules. The constants and flags define the byte-level contract used by `RowSlice::from_bytes` and `RowEncoder::write_row_impl`.

## Dependencies and Integration Points
The only direct dependency is `bitflags`. This module integrates row v2 decoding, v1 conversion, and test encoding under `crate::codec::row::v2`. The version and flags are shared by production row slicing and test buffer generation.

## Risks and Edge Cases
Changing `CODEC_VERSION` or flag bit assignments would break wire compatibility. `Flags` is private, which keeps external callers from depending on bit details directly, but row v2 sibling modules depend on the exact layout.

## Test Signals
There are no local tests. All `row/v2/row_slice.rs`, `compat_v1.rs`, and `encoder_for_test.rs` tests validate this module's version and flag definitions indirectly.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/v2/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/v2/row_slice.rs -->
# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/v2/row_slice.rs

## Purpose
This file implements zero-copy decoding and lookup for TiDB/TiKV row-format-v2 byte slices. It parses the row header, ID arrays, offset arrays, value region, and optional checksum without materializing per-column values.

## Important APIs, Types, and Functions
`RowSlice<'a>` has `Small` and `Big` variants. Small rows store non-null IDs and null IDs as `u8` and offsets as `u16`; big rows store IDs and offsets as `u32`. Both variants retain the original bytes, the values slice, and optional `Checksum`. `RowSlice::from_bytes` parses a row, `search_in_non_null_ids` binary-searches sorted non-null IDs and returns a value byte range, `search_in_null_ids` checks null IDs, `get` returns an optional value slice for a column, `values` and `origin` expose raw slices, and `get_checksum` returns parsed checksum metadata.

`Checksum` stores a header, primary crc32 value, and optional extra checksum value. `LeBytes<'a, T>` is a little-endian unaligned view over integer arrays with `get`, `get_unchecked`, and a bounded `binary_search`.

## Control Flow and State
`from_bytes` asserts the first byte is `CODEC_VERSION`, reads flags, counts, and typed little-endian arrays. If `WITH_CHECKSUM` is set, it calls `cut_checksum_bytes` using the last non-null offset to split trailing checksum bytes away from the values region, then parses a 5-byte or 9-byte checksum trailer. Lookups validate the requested column ID against the row width, binary-search the appropriate ID array, derive the start offset from the previous offset or zero, and return a slice from `values`.

## Dependencies and Integration Points
The module depends on `codec::prelude` for reading primitives, `num_traits::PrimInt` for generic little-endian arrays, local codec errors, and row v2 constants/flags. It integrates with `encoder_for_test` for test fixtures and with higher-level datum decoders that consume the returned raw value payload.

## Risks and Edge Cases
The implementation is only compiled for little-endian targets. `from_bytes` uses `assert_eq!` for the version byte and checksum length assertions, so malformed data can panic instead of returning a codec error. `cut_checksum_bytes` unwraps the last offset when checksum is present and non-null count is nonzero, so corrupted offset arrays can also panic. The custom binary search limits steps to 20 to avoid pathological corrupted rows, but it still relies on sorted ID arrays from the encoder/TiDB contract. `LeBytes` uses unaligned unsafe reads; bounds are checked in safe `get`, while internal search uses calculated indices.

## Test Signals
Tests cover little-endian array reading, big and small non-null lookup, null lookup with IDs inside and outside width ranges, checksum decoding with and without extra checksum for both small and big rows, and benchmarks for lookup and parsing performance.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/v2/row_slice.rs -->
