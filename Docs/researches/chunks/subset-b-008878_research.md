# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_uca/data_0900.rs lines 7787-9117

## Chunk Scope

This chunk is a contiguous slice of the generated `UNICODE_CI_TABLE` inside `data_0900.rs`, the Unicode data provider for the `utf8mb4_0900_ai_ci` UCA collator. It contains only literal table data, not executable function bodies.

Counting from the first element of `UNICODE_CI_TABLE`, this span covers 19,965 entries, approximately Unicode scalar/table indexes `U+1C40D..=U+21209`. The first literal is `0xC40DFBC3`; the last literal is `0x9209FB84`. The chunk continues the generated fallback-style run from the previous chunk, then transitions into more mixed weights, including zeros, direct compact weights, repeated primary weights, `FB40`/`FB84`/`FBC3` suffix patterns, and three `LONG_RUNE` sentinels for `U+1F19C`, `U+1F1A8`, and `U+1F1A9`.

## Purpose

`data_0900.rs` provides the static Unicode Collation Algorithm lookup data for TiDB/TiKV-compatible `utf8mb4_0900_ai_ci` comparisons. The surrounding `Unicode0900` implementation maps each decoded Rust `char` to a packed collation weight by indexing `UNICODE_CI_TABLE`.

This assigned range contributes the lookup values for high Unicode scalars around `U+1C40D..=U+21209`. For strings containing characters in this range, these constants determine case-insensitive/accent-insensitive ordering, equality, sort-key bytes, and collation-aware hash input. There is no local parsing, allocation, or branching in the chunk; its significance is positional data correctness.

## Important APIs, Types, and Functions

- `Unicode0900` is the marker type implemented in this file for the 0900 UCA data.
- `UnicodeVersion::preprocess(s)` returns `s` unchanged for this collation, so table lookup sees the original UTF-8 decoded scalars.
- `UnicodeVersion::char_weight(ch)` casts `ch` to `usize`, indexes `UNICODE_CI_TABLE`, expands `LONG_RUNE` through `map_long_rune`, and returns a `u128` packed weight.
- `UNICODE_CI_TABLE: [u64; 0x2CEA1]` is the generated dense lookup table containing this chunk.
- `LONG_RUNE: u64 = 0xFFFD` marks entries whose weight expansion does not fit a normal `u64`. This chunk has three such entries, all resolved by `map_long_rune`.
- `CollatorUtf8Mb40900AiCi` aliases `CollatorUca<data_0900::Unicode0900>`, which is the runtime collator that consumes this table.
- `CollatorUca<T>::write_sort_key`, `sort_compare`, and `sort_hash` all consume returned weights as repeated 16-bit lanes using `weight & 0xFFFF` followed by `weight >>= 16`.

## Control Flow

Runtime control flow reaches this chunk through the collation framework:

1. A caller selects `utf8mb4_0900_ai_ci`, which resolves to `CollatorUtf8Mb40900AiCi`.
2. `CollatorUca<Unicode0900>` decodes input bytes one UTF-8 scalar at a time with `next_utf8_char`.
3. For each scalar, `Unicode0900::char_weight` indexes `UNICODE_CI_TABLE`.
4. If the scalar value is in this chunk's index interval, the returned weight is one of these literals unless it is the `0xFFFD` sentinel.
5. If the value is `LONG_RUNE`, `map_long_rune` returns the corresponding wider `u128` expansion. In this span that applies to `U+1F19C`, `U+1F1A8`, and `U+1F1A9`.
6. The generic collator compares, serializes, or hashes the resulting 16-bit weight lanes.

Zero weights are significant in this flow. This chunk contains 182 `0x0` entries; `write_sort_key` emits no bytes for them, `sort_hash` hashes nothing for them, and `sort_compare` skips them while searching for the next nonzero weight. Changing a zero to nonzero, or the reverse, changes equality and ordering semantics.

## State and Persistence Behavior

The chunk has no mutable state, persistence, I/O, or runtime allocation. Its data is compiled into read-only process memory as part of the large static table.

The persistence contract is behavioral: once built into TiKV/TiDB components, these constants define deterministic collation behavior for the affected codepoints. A changed literal can alter persisted/indexed sort-key compatibility, range comparison results, grouping behavior, or hash-based equality for SQL values using `utf8mb4_0900_ai_ci`.

## Dependencies

- Depends directly on the local `UnicodeVersion` trait from `utf8mb4_uca/mod.rs`.
- Is consumed by `CollatorUca<T>`, which depends on the broader collation module's `Collator`, `CharsetUtf8mb4`, `BufferWriter`, `next_utf8_char`, `Ordering`, `Hasher`, and `Result` plumbing.
- Integrates through the `CollatorUtf8Mb40900AiCi` type alias for MySQL/TiDB-compatible `utf8mb4_0900_ai_ci` behavior.
- The file header identifies generated Unicode/UCA source data. The comment mentions `allkeys-4.0.0.txt` while the type/collation name is `0900`, which is a maintenance signal for anyone regenerating or auditing this table.

This chunk has no external crate calls and no module-level imports of its own beyond the surrounding file context.

## Integration Points

The data participates in every runtime path that uses this collation:

- SQL string comparison calls `sort_compare`, which lazily compares packed weight lanes.
- Sort-key generation calls `write_sort_key`, which writes the same lane sequence as big-endian `u16` values.
- Collation-aware hashing calls `sort_hash`, which hashes the same lane sequence used by comparison.
- Equality, ordering, grouping, and range behavior remain consistent only if this table's positional mapping and packed-lane interpretation are preserved.

Because the array is indexed by Unicode scalar value, source formatting is secondary; entry count and order are the contract. Adding, removing, or shifting one literal in or before this chunk remaps all later codepoints to the wrong weights.

## Risks and Edge Cases

- Manual edits are high risk. This is generated dense data with no symbolic labels per codepoint.
- The three `LONG_RUNE` sentinels in this chunk depend on exact `map_long_rune` cases. If a sentinel is added without a corresponding match arm, the fallback arm returns `0xFFFD`, collapsing the intended expansion.
- The 182 zero-weight entries are ignorable at this collation level; accidental changes can make previously ignored characters affect sort keys and hashes.
- The dominant generated suffix runs (`FBC3`, `FB84`, and `FB40`) encode implicit ordering. Reordering or truncating these values can break rare-script and CJK-extension ordering relative to MySQL-compatible results.
- `Unicode0900::char_weight` uses `if r > UNICODE_CI_TABLE.len()` before indexing. A scalar exactly equal to the table length would not take the fallback path. This is outside the local data chunk but relevant to table-boundary tests.
- Packed weights are consumed least-significant 16-bit lane first. Reading a hex literal as a big-endian byte string gives the wrong mental model for compare/hash behavior.

## Test Signals

- Golden comparison tests for `utf8mb4_0900_ai_ci` should include representative scalars from `U+1C40D..=U+21209`, especially the chunk boundaries and transitions from `FBC3`-style values into direct compact weights and `FB84`-style values.
- Add focused coverage for `U+1F19C`, `U+1F1A8`, and `U+1F1A9` to prove the `LONG_RUNE` path returns the intended `u128` expansions.
- Include zero-weight representatives from this range to verify they are skipped consistently by `sort_compare`, `write_sort_key`, and `sort_hash`.
- Sort-key golden tests should assert the exact emitted `u16` lane sequence for selected literals rather than comparing raw `u64` hex text.
- Regeneration checks should validate `UNICODE_CI_TABLE.len() == 0x2CEA1`, preserve total element count, and diff generated constants against the authoritative source to catch shifted entries.
- Boundary/property tests around the table end and out-of-range fallback should include the known `r == UNICODE_CI_TABLE.len()` edge case.
