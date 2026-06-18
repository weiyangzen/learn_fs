# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_uca/data_0900.rs lines 11602-12337

## Scope

This chunk is the final segment of `UNICODE_CI_TABLE` in `data_0900.rs`, covering 11,019 direct table entries from Unicode scalar index `U+2A396` through `U+2CEA0`. It ends with the closing `];` of the static array. The values are overwhelmingly generated fallback-style collation weights such as `0xA396FB85` through `0xCEA0FB85`, with a small transition near `0xA6D7..0xA6FF` to `...FBC5` before returning to `...FB85`.

## Purpose

`data_0900.rs` supplies the weight data for TiKV's MySQL-compatible `utf8mb4_0900_ai_ci` collation implementation. The surrounding module exposes this through `Unicode0900`, which implements `UnicodeVersion` for `CollatorUca<data_0900::Unicode0900>`. This chunk specifically preserves table coverage for high Unicode code points at the end of the generated table, so `char_weight` can return a deterministic UCA-style primary weight by direct indexing instead of taking the out-of-table fallback path.

These entries matter for sorting, equality, hashing, and sort-key generation for UTF-8 strings containing code points in this high range. Even if most entries correspond to unassigned or rarely used scalar values, changing them can alter distributed SQL ordering semantics, index key ordering, hash grouping, and comparison compatibility with TiDB/MySQL expectations.

## Important APIs, Types, And Data

- `Unicode0900`: zero-sized marker type implementing `UnicodeVersion`.
- `UnicodeVersion::preprocess`: for 0900 returns the input byte slice unchanged, matching the no-padding behavior documented for `utf8mb4_0900_ai_ci`.
- `UnicodeVersion::char_weight`: converts a `char` to `usize`, indexes `UNICODE_CI_TABLE`, resolves `LONG_RUNE` sentinels via `map_long_rune`, and returns the weight as `u128`.
- `UNICODE_CI_TABLE: [u64; 0x2CEA1]`: generated case-insensitive/accent-insensitive collation weight table indexed by Unicode scalar value. This chunk is the tail of that array.
- `LONG_RUNE: u64 = 0xFFFD`: sentinel for table entries that need a longer `u128` expansion from `map_long_rune`; this chunk does not contain sentinel entries.
- `CollatorUtf8Mb40900AiCi = CollatorUca<data_0900::Unicode0900>` in `utf8mb4_uca/mod.rs`: the public collator binding that consumes this data.

## Control Flow

There is no executable control flow inside the chunk itself; it is literal static data. Runtime flow is:

1. Higher-level collation dispatch selects `CollatorUtf8Mb40900AiCi` for `Collation::Utf8Mb40900AiCi`.
2. `CollatorUca<Unicode0900>` reads UTF-8 bytes with `next_utf8_char`.
3. Each decoded `char` is passed to `Unicode0900::char_weight`.
4. If the scalar value is within `UNICODE_CI_TABLE`, the weight at that index is returned. For this chunk, values from `U+2A396` to `U+2CEA0` resolve here.
5. `write_sort_key`, `sort_compare`, and `sort_hash` consume the returned `u128` by comparing or emitting 16-bit weight units from least significant to most significant until the weight becomes zero.

If a scalar is greater than the table length check, `char_weight` constructs a fallback weight from the scalar value using the `0xFBC0` base and high-bit low-plane payload. This chunk reduces reliance on that fallback for the final covered table range.

## State And Persistence Behavior

The chunk contributes immutable process-static state. It has no mutation, no allocation, no I/O, and no persistence side effects. Persistence impact is indirect: collation weights influence encoded sort keys, comparison results, grouping/hash behavior, and index/order compatibility. Any table value change can become externally visible in query results or persisted key ordering produced by code paths that materialize sort keys.

## Dependencies And Integration Points

- Depends on Rust static array indexing and `char as usize` alignment with the generated table's scalar-value order.
- Consumed by `utf8mb4_uca/mod.rs` through the `UnicodeVersion` trait.
- Integrated into generic collation dispatch in `codec/collation/mod.rs` through `match_template_collator`, including scalar and vector data-type comparison paths.
- Used by `SortKey<T, C>` ordering, hashing, and equality wrappers, and by string comparison in `codec/data_type/scalar.rs`.
- The table data is generated from Unicode collation input noted in the file header, so regeneration tooling or upstream UCA changes are the expected source of legitimate edits.

## Risks

- Off-by-one table edits are high risk. Since the table is positional and indexed directly by scalar value, inserting, deleting, or reflowing numeric entries without preserving count shifts every later code point's weight.
- The bounds check uses `if r > UNICODE_CI_TABLE.len()`, so `r == len` would attempt an out-of-bounds index. This chunk ends at index `0x2CEA0`, matching the declared array length `0x2CEA1`; callers with `char` value exactly `0x2CEA1` would exercise that edge unless other chunks or later fixes handle it.
- The repetitive `...FB85` and `...FBC5` pattern looks mechanical; manual review can easily miss a single corrupted hex literal.
- Because `sort_compare` consumes packed 16-bit units from the low end of the returned weight, byte/word ordering inside each literal is semantically significant.
- The file header says it was created from a UCA 4.0.0 URL despite this module naming `0900`; this may be a stale generator comment or compatibility artifact and is worth verifying before any regeneration.

## Test Signals

Useful validation signals include:

- Unit tests around `CollatorUtf8Mb40900AiCi::char_weight` for representative boundary code points in this chunk: `U+2A396`, the `...FBC5` transition around `U+2A6D7..U+2A6FF`, `U+2A700`, and `U+2CEA0`.
- A regression test comparing `sort_compare`, `write_sort_key`, and `sort_hash` consistency for strings containing those boundary scalars.
- A table integrity check confirming `UNICODE_CI_TABLE.len() == 0x2CEA1` and that generated chunks preserve exact entry count.
- Cross-checks against TiDB/MySQL expected ordering for `utf8mb4_0900_ai_ci` where fixtures include high Unicode scalar values.
