# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_uca/data_0900.rs lines 5251-6541

## Scope

This chunk is a middle slice of the generated `UNICODE_CI_TABLE` for the `utf8mb4_0900_ai_ci` collator. It covers table entries in `data_0900.rs` lines 5251-6541, roughly the zero-based Unicode scalar index span `0x12F75..=0x17B19` within `static UNICODE_CI_TABLE: [u64; 0x2CEA1]`.

The chunk contains only literal `u64` weight data. The executable behavior is defined by the surrounding `Unicode0900` implementation and the generic `CollatorUca<T>` code in `utf8mb4_uca/mod.rs`, which consume these entries during sort-key construction, string comparison, and collation-aware hashing.

## Purpose

- Provide precomputed primary collation weights for `utf8mb4_0900_ai_ci`, used by TiDB/TiKV-compatible UTF-8 string comparison.
- Keep runtime comparison fast by mapping each decoded Unicode scalar directly to one packed weight value instead of parsing Unicode Collation Algorithm data at runtime.
- Encode case-insensitive and accent-insensitive equivalence as identical packed weights; callers compare weight sequences rather than original bytes.
- Supply a dense data segment for codepoints around `U+12F75..U+17B19`. The literal values in this range include long runs of implicit/fallback-style weights such as `0xAF75FBC2` and `0x8B19FB00`, plus direct-looking primary values such as `0x4E13` through CJK-like ranges.

## Important APIs, Types, And Functions

- `Unicode0900` is the marker type for this generated data file. `CollatorUtf8Mb40900AiCi` is a type alias for `CollatorUca<data_0900::Unicode0900>`.
- `UnicodeVersion::char_weight(ch: char) -> u128` casts a Unicode scalar to `usize`, indexes `UNICODE_CI_TABLE`, maps the `LONG_RUNE` sentinel through `map_long_rune()`, and returns the weight as `u128`.
- `UNICODE_CI_TABLE` is the key artifact for this chunk. It is a `#[rustfmt::skip]` static `[u64; 0x2CEA1]`, and this chunk is a contiguous literal subsequence of that array.
- `LONG_RUNE: u64 = 0xFFFD` marks entries whose expansion does not fit in a single `u64`; those are resolved by `map_long_rune()`. This chunk is mostly ordinary literals, but the consumer must keep the sentinel contract intact for the table as a whole.
- `CollatorUca<T>::write_sort_key()` decodes UTF-8 with `next_utf8_char`, obtains each character weight, and writes each 16-bit lane of the packed weight in big-endian order.
- `CollatorUca<T>::sort_compare()` lazily decodes both inputs, compares the low 16-bit lanes of packed weights, and shifts each weight by 16 bits until a difference or end of weight sequence is found.
- `CollatorUca<T>::sort_hash()` hashes the same 16-bit lanes used for comparison, so equality under this collation produces equal hashes.

## Control Flow

At runtime, byte strings reach this table through the collation abstraction. Callers select `Collation::Utf8Mb40900AiCi`, the `match_template_collator!` macro resolves that to `CollatorUtf8Mb40900AiCi`, and the generic `CollatorUca<Unicode0900>` implementation handles compare, sort-key, or hash work.

The hot path decodes one UTF-8 scalar at a time. For a scalar whose numeric value falls inside the `UNICODE_CI_TABLE` range, `Unicode0900::char_weight()` reads the corresponding `u64` entry. If that scalar lands in the line 5251-6541 span, the returned weight comes from this chunk. If the scalar is beyond the table, the code synthesizes an implicit fallback weight from the scalar value. If the table entry is `LONG_RUNE`, `map_long_rune()` returns a wider packed expansion.

Packed weights are consumed as little-endian 16-bit lanes within the integer: comparison checks `(weight & 0xFFFF)`, then shifts right by 16 bits; sort-key writing emits the same lanes as big-endian `u16` values; hashing feeds the same lane sequence into the supplied hasher. A zero weight means the character is ignorable at this collation level and is skipped by compare/hash/sort-key generation.

## State And Persistence Behavior

This chunk has no mutable state, allocation, I/O, or persistence. It contributes read-only process memory compiled into the TiKV/TiDB query datatype component.

Its behavior still affects persisted and distributed results indirectly wherever collation order is materialized or compared: encoded sort keys, index/range ordering decisions, SQL comparison results, grouping/equality under case-insensitive collation, and hash-based operators that use `sort_hash()`. Changing any literal in this chunk can change comparison order or equality for the affected Unicode scalar range and may break compatibility with existing TiDB/MySQL collation semantics.

## Dependencies And Integration Points

- `data_0900.rs` implements the local `UnicodeVersion` trait from `utf8mb4_uca/mod.rs`.
- `CollatorUtf8Mb40900AiCi` is registered through `match_template_collator!` in `codec/collation/mod.rs` for `Collation::Utf8Mb40900AiCi`.
- The collation module integrates with `SortKey<T, C>`, scalar value comparison (`ScalarValueRef::cmp_sort_key`), byte/string expression evaluation, and any code path that compares or hashes SQL string values with a field collation.
- UTF-8 decoding depends on `next_utf8_char` from the surrounding collator module. Invalid UTF-8 terminates the UCA compare/sort-key loops rather than consulting this table for replacement characters.
- The table is generated from Unicode Collation Algorithm source data, according to the file header. Its generated format must remain consistent with `CollatorUca`'s packed-16-bit-lane interpretation.

## Risks And Edge Cases

- The table is dense generated data with no semantic names per entry. Manual edits are high risk because a one-value shift or missing literal would remap all following scalar weights.
- `Unicode0900::char_weight()` uses the scalar value as an array index. The surrounding bounds check is `r > UNICODE_CI_TABLE.len()` rather than `r >= UNICODE_CI_TABLE.len()`, so a valid scalar exactly equal to `0x2CEA1` would attempt an out-of-bounds table read instead of using the fallback formula.
- Values in this chunk include implicit-weight patterns with suffixes such as `FBC2` and `FB00`. Those must remain ordered relative to direct primary weights; otherwise rare-script and CJK ordering can drift from MySQL-compatible `utf8mb4_0900_ai_ci`.
- Packed multi-lane weights are limited by the `u64` table format unless routed through `LONG_RUNE` and `map_long_rune()`. Adding an expansion that does not fit in `u64` requires using the sentinel path, not just inserting a truncated literal.
- Because `sort_compare()`, `write_sort_key()`, and `sort_hash()` all interpret the same integer lanes, any malformed literal can create inconsistent ordering or equality across SQL compare, grouping, and index-key behavior.
- The file header says the data was created from a Unicode UCA 4.0.0 URL despite the type name `Unicode0900` and collation name `utf8mb4_0900_ai_ci`. That may be intentional generator history, but it is a documentation/versioning risk when regenerating or auditing the table.

## Test Signals

- Collation conformance tests should include `utf8mb4_0900_ai_ci` strings containing Unicode scalars from this chunk's index span, especially boundary scalars around `U+12F75`, transition points where the literal pattern changes, and `U+17B19`.
- Sort-key tests should assert that `write_sort_key()` emits the same 16-bit weight sequence that `sort_compare()` uses for representative literals from this chunk.
- Hash/equality tests should verify that strings comparing equal under `utf8mb4_0900_ai_ci` also produce equal `sort_hash()` output.
- Boundary tests should cover scalars immediately before the table, inside this chunk, at the table end, exactly at `UNICODE_CI_TABLE.len()`, and beyond the table to exercise direct lookup versus fallback behavior.
- Regeneration tests or golden fixtures should diff the generated `UNICODE_CI_TABLE` against the authoritative collation source so accidental line wrapping, dropped literals, or shifted entries are detected.
