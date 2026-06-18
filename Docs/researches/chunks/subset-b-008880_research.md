# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_uca/data_0900.rs lines 10360-11601

## Scope

This chunk is a contiguous data-only slice of `static UNICODE_CI_TABLE: [u64; 0x2CEA1]` in `data_0900.rs`. The requested lines cover 18,630 table literals, starting after 154,380 preceding entries, so they correspond to Unicode scalar indexes approximately `U+25B0C..=U+2A3D1`.

The slice contains no standalone Rust functions or type definitions. Its behavior is defined by the surrounding `Unicode0900` implementation and by `CollatorUca<T>` in `utf8mb4_uca/mod.rs`, which read these literals as packed Unicode Collation Algorithm weights for TiDB/TiKV's `utf8mb4_0900_ai_ci` collation.

## Purpose

- Provide precomputed case-insensitive, accent-insensitive collation weights for Unicode codepoints in the `U+25B0C..=U+2A3D1` range.
- Keep runtime comparison fast by allowing `Unicode0900::char_weight()` to map a decoded `char` directly to a packed integer weight through array indexing.
- Preserve MySQL/TiDB-compatible ordering for a high Unicode range dominated by generated implicit-weight patterns. In this chunk, values progress through long monotonic runs such as `0xDAD0FB84..` and later `0xA3xxFB85`, where the low 16-bit lane is compared first and the higher lane refines ordering within that bucket.
- Contribute to the generated `utf8mb4_0900_ai_ci` data set without adding runtime parsing of UCA source files.

## Important APIs, Types, And Functions

- `Unicode0900` is the marker type implemented in this file for the `utf8mb4_0900_ai_ci` data set.
- `UnicodeVersion::char_weight(ch: char) -> u128` is the public table access path. It casts `ch` to a `usize`, indexes `UNICODE_CI_TABLE`, resolves `LONG_RUNE` sentinel entries through `map_long_rune()`, and returns the result as `u128`.
- `UNICODE_CI_TABLE` is the main artifact. This chunk is only a literal segment of that static table; changing its length or shifting an entry changes the weight of every following codepoint.
- `CollatorUtf8Mb40900AiCi` is a type alias for `CollatorUca<data_0900::Unicode0900>`, so all consumers of `Collation::Utf8Mb40900AiCi` eventually use this table for character weights.
- `CollatorUca<T>::write_sort_key()`, `sort_compare()`, and `sort_hash()` consume the packed weights by repeatedly reading the low 16 bits and shifting right by 16 bits.

## Control Flow

At runtime, SQL string operations choose a concrete collator from the `Collation` enum. For `Collation::Utf8Mb40900AiCi`, the `match_template_collator!` registration maps to `CollatorUtf8Mb40900AiCi`, which is `CollatorUca<Unicode0900>`.

The collator decodes input bytes with `next_utf8_char()`. For each decoded scalar, `Unicode0900::char_weight()` looks up `UNICODE_CI_TABLE[ch as usize]`. If the scalar falls in this chunk's index range, the returned value is one of these line 10360-11601 literals. `sort_compare()` then compares the low 16-bit lane first, shifts both packed weights, and continues lane by lane until it finds a difference or exhausts one weight. `write_sort_key()` emits the same lane sequence as big-endian `u16` values, and `sort_hash()` hashes the same lanes.

The chunk itself does not branch, allocate, or perform I/O. It is a passive lookup segment whose control-flow impact comes from the exact integer returned for a codepoint.

## State And Persistence Behavior

This range is immutable compiled data. There is no in-memory mutation, persistent storage, serialization logic, or external resource access in the chunk.

The values still affect persistent and distributed behavior indirectly. Index ordering, range bounds, grouping, equality, hash joins/aggregations, and encoded sort keys can all depend on these weights when strings contain characters from `U+25B0C..=U+2A3D1` under `utf8mb4_0900_ai_ci`. Any literal change can therefore alter query results or compatibility with preexisting TiDB/MySQL collation semantics.

## Dependencies And Integration Points

- Depends on the `UnicodeVersion` trait from `utf8mb4_uca/mod.rs`.
- Integrated through `CollatorUtf8Mb40900AiCi`, which is exported by the collator module and registered for `Collation::Utf8Mb40900AiCi`.
- Uses the generic UTF-8 decoding helper `next_utf8_char()` before table lookup. Invalid UTF-8 prevents a scalar lookup rather than causing this table to map replacement characters.
- Shares packed-weight interpretation with `data_0400.rs` and the generic `CollatorUca<T>` implementation: table values are read as sequences of 16-bit collation lanes packed into an integer.
- The file header indicates generated UCA source data; regeneration tooling must preserve this table's exact length, entry order, and sentinel conventions.

## Risks And Edge Cases

- This is dense generated data. A dropped, inserted, or reordered literal would silently remap subsequent Unicode scalar values to the wrong weights.
- Manual edits are hard to review because the values are numeric and mostly monotonic; validation needs generated golden data or behavioral fixtures rather than visual inspection.
- The packed format means the low 16 bits are semantically first during comparison. Values with suffixes like `FB84` and `FB85` are not arbitrary constants; they define primary ordering buckets consumed by `sort_compare()`, `write_sort_key()`, and `sort_hash()`.
- `Unicode0900::char_weight()` uses an array index after a bounds check. The surrounding check is `r > UNICODE_CI_TABLE.len()`, so an exact `r == UNICODE_CI_TABLE.len()` would be an out-of-bounds lookup instead of using the fallback formula.
- Wide expansions must use the `LONG_RUNE` sentinel plus `map_long_rune()`. This chunk's values fit the normal `u64` table shape, but future generated changes in the same scalar range must not truncate multi-lane weights into a plain `u64`.
- Because comparison, sort-key emission, and hashing all share this table, a malformed literal can create broad SQL-visible inconsistencies for ordering and equality.

## Test Signals

- Golden collation tests should include representative characters from this chunk's scalar span, especially near `U+25B0C`, the line 11601 boundary around `U+2A3D1`, and any transition from `...FB84` to `...FB85` implicit-weight buckets.
- Sort-key tests should verify that `write_sort_key()` emits the same 16-bit lane sequence that `sort_compare()` uses for selected codepoints in this range.
- Equality/hash tests should confirm that strings comparing equal under `utf8mb4_0900_ai_ci` also produce identical `sort_hash()` output.
- Regression tests should diff regenerated `UNICODE_CI_TABLE` output against an authoritative fixture so line wrapping or literal shifts in this generated region are caught.
- Boundary tests around the full table end and fallback path should cover scalars inside this chunk, immediately after it, exactly at `UNICODE_CI_TABLE.len()`, and above the table range.
