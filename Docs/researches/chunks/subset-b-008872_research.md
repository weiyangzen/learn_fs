# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_uca/data_0900.rs lines 1-1526

## Scope And Purpose

This chunk is the opening section of TiKV's generated Unicode Collation Algorithm data for the `utf8mb4_0900_ai_ci` collation. It defines the `Unicode0900` marker type, implements the `UnicodeVersion` trait used by the shared UCA collator, handles long packed weight sequences that do not fit in the main `u64` table, and starts the large `UNICODE_CI_TABLE` lookup array.

The file header says the table was created from Unicode UCA allkeys data. Despite the `0900` name, this source comment points at `https://www.unicode.org/Public/UCA/4.0.0/allkeys-4.0.0.txt`; that mismatch is worth preserving as provenance context because collation behavior must match TiDB/MySQL compatibility, not just the label in the Rust type.

The requested line range ends at line 1526 inside the `UNICODE_CI_TABLE` initializer. The array itself continues later in the file, so this chunk should be merged with subsequent chunks before drawing final conclusions about the complete codepoint coverage.

## Important APIs, Types, And Data

`Unicode0900` is a zero-sized marker struct with `Debug` derived. It is not constructed directly in this file; it is used as the type parameter behind `CollatorUtf8Mb40900AiCi = CollatorUca<data_0900::Unicode0900>` in the sibling `utf8mb4_uca/mod.rs`.

`impl UnicodeVersion for Unicode0900` provides two trait methods:

- `preprocess(s: &[u8]) -> &[u8]` returns the original input slice unchanged. For this collation version there is no right-space trimming or byte normalization at the data-version layer. The shared `CollatorUca` decides when to call preprocessing for sort keys, comparison, and hashing.
- `char_weight(ch: char) -> u128` converts a Unicode scalar value into its primary collation weight sequence. It indexes the static table when the codepoint is covered, maps table sentinel values through `map_long_rune`, and synthesizes a fallback implicit weight for codepoints outside the generated table.

`LONG_RUNE` is the sentinel value `0xFFFD`. In ordinary Unicode terms `U+FFFD` is the replacement character, but in this generated table it also marks entries whose full weight sequence must be retrieved from `map_long_rune`. The explicit `map_long_rune(0xFFFD)` arm preserves the replacement character's actual weight, preventing that codepoint from being lost to the sentinel convention.

`map_long_rune(r: usize) -> u128` covers long weight sequences that cannot be represented safely in the `u64` table. In this chunk it has explicit arms for circled/squared CJK compatibility forms, Arabic ligatures, the replacement character, and a few enclosed/symbol codepoints such as `0x1F19C`, `0x1F1A8`, and `0x1F1A9`. The default branch returns `0xFFFD`, which means any accidental sentinel not covered by the match degrades to the replacement weight instead of panicking.

`UNICODE_CI_TABLE: [u64; 0x2CEA1]` begins at line 70 and is marked `#[rustfmt::skip]` to keep the generated layout stable. This chunk contains the array declaration and the first 1,457 lines of literal data. A quick scan over lines 1-1526 found about 21,881 hex literals in this chunk, including 652 zero weights, 23 `0xFFFD` sentinels, and roughly 1,374 literals with `FBC*` implicit-weight markers.

## Control Flow

The runtime path for this data is simple and performance-oriented:

1. `CollatorUca<Unicode0900>` receives a decoded `char` from the shared UTF-8 traversal code.
2. `Unicode0900::char_weight` casts the char to `usize`.
3. If the value is beyond the generated table length, `char_weight` synthesizes an implicit two-part weight using high and low bits of the codepoint plus `0xFBC0`.
4. Otherwise it reads `UNICODE_CI_TABLE[r]`.
5. If the table value equals `LONG_RUNE`, it calls `map_long_rune(r)` and returns that `u128`.
6. Non-sentinel table entries are widened from `u64` to `u128` and returned directly.

The shared `CollatorUca` then consumes the returned `u128` as a sequence of 16-bit weights from least significant to most significant chunks. This is why multi-element weights are packed as concatenated 16-bit units and why `u128` is required for long contractions/expansions.

One boundary detail deserves attention: the range check uses `if r > UNICODE_CI_TABLE.len()` and then indexes `UNICODE_CI_TABLE[r]`. If `r == UNICODE_CI_TABLE.len()`, the code would attempt an out-of-bounds access. The practical risk depends on whether a valid Rust `char` can equal exactly `0x2CEA1`; it can, because that value is below the Unicode maximum. If no later code changes this check, this is a latent panic boundary that tests should cover explicitly.

## Table Content In This Chunk

The first table rows cover ASCII/control ranges and Latin letters. Many upper- and lowercase Latin letters share the same weight, which encodes case-insensitive behavior at this collation layer. Zero entries appear for ignored/control codepoints and cause the shared UCA loops to skip them because a zero weight produces no sort-key words and is treated as exhausted during comparison.

Early rows include packed multi-weight expansions such as combined Latin/diacritic sequences and compatibility mappings. Values like `0x1C4106261C3E` show multiple 16-bit weights packed into one table cell. Values ending in or containing `FBC0`, `FB40`, `FB41`, and related ranges represent implicit or generated collation positions for codepoints whose primary weights are derived rather than assigned as compact alphabetic weights.

The middle of this chunk includes large contiguous ranges of symbol, compatibility, CJK-related, and generated implicit-weight entries. Around lines 850-980 the table transitions through dense symbol weights, CJK/radical-like implicit sequences, and sentinel-backed long sequences. Several `0xFFFD` table entries in this area correspond to explicit `map_long_rune` arms such as CJK compatibility abbreviations and ligature-like expansions.

The end of this chunk, lines 1450-1526, is a long monotonic run of values such as `0xD0BEFB40` through `0xD540FB40`. This is characteristic generated implicit-weight data: adjacent codepoints receive adjacent packed weights. The chunk stops in the middle of that contiguous run, so the next chunk is necessary to know where this generated range ends.

## State And Persistence Behavior

This file has no mutable runtime state, heap allocation, I/O, or persistence behavior. All state is compile-time static data embedded in the binary. `UNICODE_CI_TABLE` is a private immutable static array, and `LONG_RUNE` is a private immutable static sentinel.

The persistent behavior is semantic rather than storage-based: changing any literal in this table changes TiKV's comparison, sort key, hash, grouping, uniqueness, and range-scan behavior for `utf8mb4_0900_ai_ci` strings. Because collation keys may influence encoded keys, query results, and distributed execution consistency, table changes must be treated as compatibility-affecting data migrations even though the Rust code path is pure.

## Dependencies And Integration Points

This chunk depends directly on the sibling `UnicodeVersion` trait from `utf8mb4_uca/mod.rs`. That module provides `CollatorUca<T>`, which implements the repository-wide `Collator` trait for UTF-8 UCA collations.

The integration chain is:

- `codec/collation/mod.rs` maps the `Utf8Mb40900AiCi` collation enum variant to `CollatorUtf8Mb40900AiCi`.
- `utf8mb4_uca/mod.rs` aliases `CollatorUtf8Mb40900AiCi` to `CollatorUca<Unicode0900>`.
- `CollatorUca` calls `Unicode0900::preprocess` and `Unicode0900::char_weight` while writing sort keys, comparing byte strings, and hashing.
- UTF-8 decoding is handled by shared charset/collation helpers; this data file only maps a valid Rust `char` to packed weights.

The table is private to the module, so external code cannot inspect or patch it directly. Any behavioral testing must go through the collator APIs or through higher-level TiDB expression/evaluation paths that choose this collation.

## Risks And Edge Cases

The most concrete code risk in this chunk is the table-length check. `r > UNICODE_CI_TABLE.len()` should likely be `r >= UNICODE_CI_TABLE.len()` if the intent is to fall back for every out-of-table codepoint. As written, a codepoint exactly equal to the array length can index one past the end.

The sentinel design is compact but fragile. `0xFFFD` means "look in `map_long_rune`" in the table, while `map_long_rune(0xFFFD)` returns the replacement character weight. A generated table update must keep every sentinel-backed entry synchronized with `map_long_rune`; otherwise the default branch silently maps the character to replacement semantics.

Packed weights depend on the shared UCA consumer reading 16-bit lanes from least significant to most significant bits. Any generator change that reverses packing order, emits too many 16-bit lanes for `u128`, or emits a `u64` table value whose intended sequence needs more than four lanes would alter ordering.

Zero weights are semantically meaningful. They make ignored codepoints disappear from sort keys and comparisons, so accidental zero generation can cause distinct strings to compare equal. Conversely, changing a zero to a nonzero weight can change equality/grouping semantics.

The generated table is large and easy to modify incorrectly by hand. `#[rustfmt::skip]` protects layout, but it also means formatting tools will not normalize or reveal suspicious alignment changes. Review should focus on generator provenance and high-level diff validation rather than individual manual literals.

The source comment's UCA version reference should be reconciled with the `0900` type/SQL collation name. If the file is intentionally generated for MySQL 8.0 `utf8mb4_0900_ai_ci` compatibility from an adapted source, the generation process should document that outside the generated data blob.

## Test Signals

Useful tests for this chunk should exercise the public collation behavior rather than private table internals:

- Direct `CollatorUtf8Mb40900AiCi::char_weight` checks for ASCII case folding, representative Latin accents, ignored zero-weight characters, CJK/symbol implicit ranges, `U+FFFD`, and every explicit `map_long_rune` codepoint in lines 37-63.
- A regression test for the boundary codepoint `char::from_u32(0x2CEA1)` to catch the `r == UNICODE_CI_TABLE.len()` panic path.
- Sort-key and comparison tests verifying that multi-lane packed weights are emitted in the intended order, especially values with more than one 16-bit unit and long `u128` expansions.
- Hash-consistency tests through `CollatorUca::sort_hash`, ensuring strings that compare equal under `utf8mb4_0900_ai_ci` hash identically.
- Compatibility fixtures against TiDB/MySQL expected ordering for representative strings across Latin, combining marks, punctuation, compatibility symbols, Arabic ligatures, CJK compatibility forms, and supplementary-plane codepoints.

Because this chunk is generated data, the strongest validation signal is a generator-level golden test: regenerate `data_0900.rs` from the authoritative source and compare the full file, then run targeted runtime collation fixtures over changed ranges.
