# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_uca/data_0900.rs lines 1527-2768

## Scope

This chunk is a middle segment of the generated `UNICODE_CI_TABLE` static used by `Unicode0900`, the Unicode Collation Algorithm data provider behind TiKV's `utf8mb4_0900_ai_ci` collator. It contains only literal `u64` weight entries, with no local functions, branches, or type definitions in the selected lines.

Within the full table, 21,826 hexadecimal entries appear before this chunk, and this chunk contributes another 18,630 entries. Because table indexing is zero-based, the selected range approximately covers table indexes `0x5542` through `0x9DF3`. The first value in the range is `0xD541FB40`; the last value is `0x9E06FB41`. The immediately surrounding lines show this range continues a monotonic generated sequence from `0xD4BAFB40` before the chunk and into `0x9E7F.../0x9E80...` style values after the chunk.

## Purpose

- Provide precomputed primary collation weights for a contiguous Unicode codepoint interval in the `Unicode0900` table.
- Let `Unicode0900::char_weight(ch)` perform direct array lookup for most codepoints instead of parsing UCA text or computing implicit weights at runtime.
- Preserve MySQL/TiDB-compatible `utf8mb4_0900_ai_ci` ordering for strings evaluated inside TiKV expression, key, comparison, hash, and sort-key code paths.
- Encode each table entry as packed 16-bit sort-key units inside a `u64`, later widened to `u128` by `Unicode0900::char_weight`.

The chunk appears to be generated data derived from the Unicode Collation Algorithm source referenced at the top of the file. Its values are not meaningful as hand-maintained Rust logic; their correctness comes from matching the expected UCA/MySQL collation data.

## Important APIs, Types, And Functions

- `Unicode0900` is the marker type implementing `UnicodeVersion` for this file. The selected table segment is private module data consumed by that implementation.
- `UNICODE_CI_TABLE: [u64; 0x2CEA1]` is the dense codepoint-to-weight table. This chunk is part of that array initializer and therefore participates in compile-time construction of the static.
- `UnicodeVersion::char_weight(ch: char) -> u128` is the public contract consumed by generic UCA collation code. For in-range codepoints it indexes `UNICODE_CI_TABLE[ch as usize]`, checks for the `LONG_RUNE` sentinel, and returns the table value as `u128`.
- `LONG_RUNE: u64 = 0xFFFD` marks table entries whose weights cannot fit in the normal `u64` representation. This chunk contains regular generated weights, not the surrounding `map_long_rune` match arms.
- `map_long_rune(r: usize) -> u128` handles rare multi-unit weights listed before the table. The selected chunk is relevant because a mistaken `0xFFFD` value in this range would divert lookup to that match and likely return replacement-character weight for unlisted cases.
- `CollatorUtf8Mb40900AiCi` is a type alias to `CollatorUca<data_0900::Unicode0900>`, so all `utf8mb4_0900_ai_ci` compare, hash, and sort-key calls eventually consume entries from this table for codepoints in the covered interval.
- `CollatorUca<T>` reads packed weights by repeatedly taking the low 16 bits and shifting right by 16. That determines the byte order emitted by `write_sort_key`, the comparison order in `sort_compare`, and the pieces fed to `sort_hash`.

## Control Flow

There is no executable control flow inside lines 1527-2768. Runtime flow reaches this chunk through direct indexing:

1. A caller asks the collation layer to compare, hash, or write a sort key for a UTF-8 string under collation `Utf8Mb40900AiCi`.
2. The collation dispatch maps that collation to `CollatorUtf8Mb40900AiCi`, which is `CollatorUca<Unicode0900>`.
3. `CollatorUca` iterates the input with `next_utf8_char`.
4. For each decoded `char`, `Unicode0900::char_weight` casts it to `usize` and looks up `UNICODE_CI_TABLE[r]` if the codepoint is within the table bound.
5. For codepoints whose index falls in this chunk, one of these literal `u64` values is returned as a `u128`.
6. The caller consumes the packed 16-bit units from low to high until the shifted weight becomes zero.

The values in this chunk are mostly sequential implicit-weight-looking entries with suffixes `FB40` and `FB41`. For example, the range starts around `0xD541FB40` and later transitions into `0x....FB41` values. Because `CollatorUca` consumes low 16 bits first, the low unit `0xFB40` or `0xFB41` is compared/emitted before the higher 16-bit unit such as `0xD541` or `0x9E06`.

## State And Persistence Behavior

- The selected lines define immutable process static data. They allocate no runtime state and perform no mutation.
- There is no direct RocksDB, raft, disk, or network persistence in the chunk.
- Persistence impact is indirect: collation weights affect encoded sort keys, comparison ordering, hash grouping, expression evaluation, and any persisted/indexed data whose order or equality semantics are produced under `utf8mb4_0900_ai_ci`.
- Because this table is compiled into TiKV binaries, changing a value changes deterministic collation behavior across upgrades. Mixed-version clusters or TiDB/TiKV version skew can observe inconsistent string ordering if the table diverges from the expected TiDB/MySQL collation data.
- The dense array layout is itself part of the runtime contract. Inserting, deleting, or rewrapping values incorrectly shifts subsequent codepoint mappings even if all hex literals remain valid Rust.

## Dependencies And Integration Points

- Depends on the local `UnicodeVersion` trait from `utf8mb4_uca/mod.rs`; `Unicode0900` supplies the data implementation for that trait.
- Integrated by `CollatorUca<T>`, which implements the shared `Collator` trait for UCA-based utf8mb4 collations.
- Exposed through `CollatorUtf8Mb40900AiCi`, selected from `Collation::Utf8Mb40900AiCi` in the wider collation dispatch.
- Works alongside `data_0400.rs`, which provides older `utf8mb4_unicode_ci` UCA data through the same generic `CollatorUca` machinery.
- Uses `next_utf8_char`, `BufferWriter`, `Hasher`, and the broader collation module's compare/hash/sort-key API indirectly through `CollatorUca`.
- Tied to TiDB field type collation IDs: `Utf8Mb40900AiCi = -255` selects this path, while `Utf8Mb40900Bin = -309` uses binary no-padding behavior instead of this UCA table.
- The file header says the data was created from Unicode UCA allkeys data. Regeneration should be treated as a data pipeline concern, not as manual editing of this chunk.

## Risks And Edge Cases

- Off-by-one risk: `Unicode0900::char_weight` uses the codepoint as an array index. Any shifted initializer entry changes the weight for every subsequent codepoint in the table.
- Boundary risk: this chunk starts and ends in the middle of a large static initializer. A malformed comma, missing value, or extra value can compile only if the total array length still matches, but semantic mapping would be corrupted.
- Compatibility risk: `utf8mb4_0900_ai_ci` must match TiDB/MySQL expectations. A single changed literal can affect `ORDER BY`, range comparisons, hash aggregation/grouping, joins, and expression results for affected characters.
- Packed-weight ordering is non-obvious. Although literals look high-to-low in hex, `CollatorUca` consumes low 16-bit units first. Manual review must account for the little-endian logical packing into the integer.
- Sentinel collision risk: `0xFFFD` is not just a normal replacement-character-looking value here; it triggers `map_long_rune`. Introducing it accidentally in the table changes control flow.
- Incomplete Unicode range risk: for codepoints above `UNICODE_CI_TABLE.len()`, `Unicode0900::char_weight` computes a fallback implicit weight instead of using this table. This chunk only covers a subset of in-table codepoints and should not be used to infer behavior for supplementary ranges outside the static.
- Generated-data drift risk: the file comment references a Unicode source path, but consumers depend on MySQL/TiDB collation compatibility. Regeneration must be validated against the exact collation version expected by TiDB, not merely against any newer Unicode release.
- Memory and binary-size risk: this large static is compiled into the binary. The chunk is data-heavy but lookup-fast; replacing it with a compressed representation would need benchmark and correctness validation.

## Test Signals

- There are no unit tests in the selected lines; the best signals are collation tests that exercise `Utf8Mb40900AiCi` comparisons, hashes, and sort-key generation for characters whose codepoints map into this approximate index range.
- A focused regression test can compare selected codepoints around the chunk boundaries, including indexes near `0x5542` and `0x9DF3`, against known TiDB/MySQL `utf8mb4_0900_ai_ci` sort order.
- Sort-key tests should verify the low 16-bit units are emitted in the expected order for representative values such as entries ending in `FB40` and `FB41`.
- Hash tests should verify strings that compare equal under accent-insensitive/case-insensitive UCA behavior hash through the same weight sequence.
- Table-integrity tests could assert `UNICODE_CI_TABLE.len() == 0x2CEA1`, verify generated checksums, and spot-check first/last values for each generated chunk to catch accidental shifts.
- Cross-version compatibility tests should compare TiKV results with TiDB/MySQL for `ORDER BY`, equality, and range predicates involving characters covered by this chunk.
