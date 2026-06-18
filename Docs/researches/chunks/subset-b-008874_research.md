# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_uca/data_0900.rs lines 2769-3900

## Scope

This chunk is a generated-data segment inside `UNICODE_CI_TABLE`, the dense `u64` lookup table used by `Unicode0900` for TiKV's `utf8mb4_0900_ai_ci` collation implementation. The selected lines contain only array initializer literals; there are no local Rust functions, branches, type definitions, or comments in the selected range.

Within the full initializer, 40,455 table entries appear before this chunk. Because table lookup uses the Unicode codepoint as a zero-based array index, this chunk covers table indexes/codepoint slots `0x9E07` through `0xE05A` and contributes 16,980 entries. The first selected value is `0x9E07FB41`, and the last selected value is `0xE05AFBC1`.

The data shape changes several times inside the range:

- Lines 2769-2798 continue a generated implicit-weight-like sequence for CJK codepoint slots around `U+9E07..U+9FD5`, mostly values ending in `FB41`.
- Lines 2799-2802 transition to values ending in `FBC1` through `U+9FFF`, followed by ordinary compact primary weights such as `0x3DBF`, `0x3DC0`, and onward.
- The middle of the chunk contains many direct `u16`-sized primary weights, some generated fallback-style `...FBC1` values, and 41 zero-weight entries.
- Lines 3758-3894 contain a dense run of 2,048 `0xFFFD` entries corresponding to surrogate codepoint slots `U+D800..U+DFFF`.
- Lines 3894-3900 leave the surrogate run and begin private-use-area-style generated fallback weights, starting at `0xE000FBC1` and continuing through `0xE05AFBC1`.

## Purpose

- Provide precomputed collation weights for Unicode codepoint slots covered by `U+9E07..U+E05A` under TiKV's `utf8mb4_0900_ai_ci` path.
- Keep the hot path for string comparison, hashing, and sort-key generation as a direct array lookup in `Unicode0900::char_weight(ch)`.
- Preserve TiDB/MySQL-compatible ordering for characters in this range, including CJK ideograph slots, Yi/Vai/Lisu/Bamum-style BMP blocks represented by compact primary weights, unassigned or ignorable slots represented by zero weights, surrogate slots, and the beginning of the private-use area.
- Encode most table values as packed 16-bit sort-key units in a `u64`; `Unicode0900::char_weight` widens the value to `u128` so the shared UCA collator can consume one or more 16-bit weights.

This is generated collation data, not hand-authored algorithmic logic. Correctness depends on the literals remaining aligned with their table indexes and matching the UCA/TiDB collation data used to generate the file.

## Important APIs, Types, And Functions

- `Unicode0900` is the marker type implementing `UnicodeVersion` for the `data_0900.rs` table. The selected literals are private data backing that implementation.
- `UNICODE_CI_TABLE: [u64; 0x2CEA1]` is the dense codepoint-to-weight array. This chunk is a contiguous section of that initializer.
- `Unicode0900::preprocess(s: &[u8]) -> &[u8]` returns input unchanged. Unlike the older Unicode 4.0 data provider, this version does not trim padding in preprocessing; `utf8mb4_0900_ai_ci` is wired as a no-padding collation in this module.
- `Unicode0900::char_weight(ch: char) -> u128` casts the Rust `char` to `usize`, indexes `UNICODE_CI_TABLE`, treats `LONG_RUNE` specially, and returns the selected `u64` weight as `u128` for normal entries.
- `LONG_RUNE: u64 = 0xFFFD` is the sentinel for table entries whose real weight may require a wider `u128` mapping through `map_long_rune(r)`. This chunk contains many `0xFFFD` entries for surrogate slots; because Rust `char` cannot represent surrogate codepoints, those slots are effectively unreachable through normal UTF-8 decoding, but their presence still preserves dense index alignment.
- `map_long_rune(r: usize) -> u128` is the fallback for real long-weight sentinel entries. If a reachable codepoint in this chunk were accidentally changed to `0xFFFD` without a matching `map_long_rune` arm, lookup would return the default replacement-character-style weight.
- `CollatorUtf8Mb40900AiCi` is a type alias to `CollatorUca<data_0900::Unicode0900>`. TiKV's collation dispatch selects this alias for `Collation::Utf8Mb40900AiCi`.
- `CollatorUca<T>` implements `Collator` with `Weight = u128`. Its `write_sort_key`, `sort_compare`, and `sort_hash` methods repeatedly consume the low 16 bits of each packed weight and shift right by 16 until the weight becomes zero.

## Control Flow

There is no executable control flow in lines 2769-3900 themselves. Runtime reaches the data through the generic UCA collator:

1. An expression, key comparison, hash operation, or sort-key request is dispatched for collation `Utf8Mb40900AiCi`.
2. `match_template_collator!` maps that collation to `CollatorUtf8Mb40900AiCi`, which is `CollatorUca<Unicode0900>`.
3. `CollatorUca` iterates the input bytes with `next_utf8_char`.
4. For each decoded `char`, `Unicode0900::char_weight` uses `ch as usize` as the table index.
5. If the index falls in `0x9E07..=0xE05A`, one of the selected literals is read.
6. For non-`LONG_RUNE` values, the `u64` literal is widened to `u128` and returned.
7. `write_sort_key` writes each low-to-high 16-bit unit as big-endian `u16`; `sort_compare` compares those units; `sort_hash` hashes those units.

The packed numeric representation is easy to misread. A literal such as `0x9E07FB41` is consumed as sort-key unit `0xFB41` first, then `0x9E07`. Compact values such as `0x3DBF` emit or compare a single unit. A value of `0` produces no sort-key units and is skipped by the UCA loops.

## State And Persistence Behavior

- The selected lines define immutable compiled-in static data. They allocate no mutable runtime state.
- There is no direct disk, RocksDB, raft, or network persistence in this chunk.
- Persistence impact is indirect but important: collation order and equality feed persisted key order, query comparison results, hash grouping, joins, range predicates, and generated sort keys wherever TiKV evaluates `utf8mb4_0900_ai_ci` semantics.
- The initializer layout is part of the behavioral contract. Adding, removing, or shifting a single literal changes the weight for that codepoint and every subsequent codepoint in the table, even if the Rust array still compiles.
- The surrogate-slot `0xFFFD` run is not normally reachable from valid UTF-8 because Rust `char` excludes `U+D800..U+DFFF`. It still matters as padding in a dense array indexed by codepoint value; deleting it would corrupt the mapping for private-use and later codepoints.
- Zero weights in this range cause `CollatorUca` to skip the character's primary weight contribution. Any change between `0` and nonzero can change equality, ordering, and hashing for affected codepoints.

## Dependencies And Integration Points

- Depends on the local `UnicodeVersion` trait from `utf8mb4_uca/mod.rs`.
- Integrated by `CollatorUca<T>`, which provides the shared UCA implementation for `write_sort_key`, `sort_compare`, and `sort_hash`.
- Selected through `CollatorUtf8Mb40900AiCi` for `Collation::Utf8Mb40900AiCi` in the broader collation dispatch.
- Shares module structure with `data_0400.rs`, which provides the older `utf8mb4_unicode_ci` table through the same generic collator.
- Uses `next_utf8_char` indirectly for UTF-8 decoding; invalid UTF-8 stops the UCA iteration rather than producing table lookups for arbitrary bytes.
- Uses `BufferWriter` for sort-key emission and `Hasher` for collation-aware hash input through the generic `Collator` trait.
- Tied to TiDB field type metadata: `Utf8Mb40900AiCi = -255` maps SQL collation metadata to this runtime path, while `Utf8Mb40900Bin` takes a binary no-padding path instead.
- Test and expression integration points include comparison expression code and LIKE/collation tests that dispatch through `Collation::Utf8Mb40900AiCi`.

## Risks And Edge Cases

- Off-by-one edits are the dominant risk. Since the table is dense and indexed by codepoint, any inserted or removed value silently remaps later codepoints if the total array length is repaired elsewhere.
- The chunk begins and ends inside a giant initializer, so syntax-only validation is insufficient. A comma or wrapping mistake can be caught by the compiler, but semantic drift requires table checksums or spot checks.
- `0xFFFD` is overloaded as a sentinel, not merely a replacement-character-looking weight. For valid `char` values, introducing `0xFFFD` must be paired with a correct `map_long_rune` case or the fallback branch returns a generic `0xFFFD` weight.
- The surrogate run is table-alignment data for codepoint slots that valid Rust strings cannot contain. A future compaction scheme must preserve equivalent index translation instead of assuming unreachable slots can be dropped for free.
- The `FBC1` suffix values in this chunk are generated fallback/implicit-style weights. They compare by low 16-bit unit first, so their primary ordering comes from the suffix before the higher codepoint-derived unit.
- Compatibility risk is high: a single changed literal can alter `ORDER BY`, range scans, grouping, joins, and equality comparisons for strings containing affected characters.
- Generated-data drift is possible if the regeneration source or MySQL/TiDB compatibility target changes. The file header references Unicode allkeys data, but consumers need the exact collation behavior expected by TiDB for `utf8mb4_0900_ai_ci`.
- Boundary behavior above the table is handled by `Unicode0900::char_weight` using an implicit fallback formula for codepoints greater than the table length. This chunk should not be extrapolated to supplementary-plane codepoints outside the table.
- The table-bound check in `char_weight` is sensitive because it uses the codepoint as an index. Any change to `UNICODE_CI_TABLE.len()` must be reviewed with boundary tests around the final in-table and first out-of-table codepoints.
- Memory and binary-size tradeoffs are intentional: this chunk favors direct lookup speed over compressed data representation. Compression would need careful benchmarking and equivalence tests.

## Test Signals

- There are no tests in the selected lines; they are static data only.
- Existing collation tests that exercise `Collation::Utf8Mb40900AiCi` compare, hash, sort-key, and LIKE paths are the relevant regression signals.
- Focused table-integrity tests should verify `UNICODE_CI_TABLE.len() == 0x2CEA1`, plus first/last values for this chunk: index `0x9E07 -> 0x9E07FB41` and index `0xE05A -> 0xE05AFBC1`.
- Boundary spot checks should cover the previous chunk boundary around `U+9E06/U+9E07`, the transition near `U+9FD5..U+A000`, zero-weight entries around the first zero in this chunk, the surrogate range `U+D800..U+DFFF` as unreachable/alignment data, and the private-use transition at `U+E000`.
- Sort-key tests should verify packed-unit order for representative multi-unit values such as `0x9E07FB41` and `0xE000FBC1`.
- Hash tests should verify that strings comparing equal under `utf8mb4_0900_ai_ci` feed identical weight-unit sequences into `sort_hash`.
- Cross-system compatibility tests should compare TiKV results against TiDB/MySQL for `ORDER BY`, equality, and range predicates involving codepoints from the covered interval.
- A generated checksum or per-block snapshot test would be the strongest signal for this chunk, because visual review of thousands of hex literals is unreliable.
