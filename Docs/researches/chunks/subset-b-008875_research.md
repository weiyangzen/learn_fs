# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_uca/data_0900.rs lines 3901-5250

## Scope

This chunk is a generated-data slice from `data_0900.rs`, inside the `UNICODE_CI_TABLE: [u64; 0x2CEA1]` used by the TiDB/TiKV `utf8mb4_0900_ai_ci` UCA collator. It contains no standalone functions or handwritten control flow; its behavior is realized when `Unicode0900::char_weight()` indexes the table and when `CollatorUca<data_0900::Unicode0900>` consumes the returned weight.

The selected lines cover 20,250 table entries. By table index, this is Unicode code point range `0xE05B..0x12F74`; the first entry is `0xE05BFBC1` at line 3901, and the last entry is `0xAF74FBC2` at line 5250. The chunk starts in the Basic Multilingual Plane private-use block, crosses BMP compatibility and Arabic presentation-form areas, crosses the BMP boundary at `0x10000`, and continues through many early supplementary-plane script blocks up to the start of the Egyptian Hieroglyphs area. The next lines after this chunk transition into ordinary explicit weights beginning around `0x12000..0x12543`, then fallback values again.

Because this is one chunk of a larger generated table, the final file-level report should reconcile it with earlier and later chunks of the same source file, especially the `Unicode0900` implementation at the file top, `map_long_rune()`, and the full table boundaries.

## Purpose

- Provide compile-time, allocation-free lookup data for converting Unicode scalar values into primary collation weights for `utf8mb4_0900_ai_ci`.
- Preserve MySQL/TiDB-compatible accent-insensitive and case-insensitive ordering by assigning equal or expanded primary weights to compatibility forms, presentation forms, fullwidth forms, ligatures, digits, symbols, and script-specific characters.
- Provide deterministic fallback-style weights for assigned or unassigned ranges not represented by UCA contractions/expansions in this generated table. Fallback entries in this chunk follow the same shape as the out-of-table formula in `char_weight()`: high 15 bits plus a `0xFBC0`/`0xFBC1`/`0xFBC2` plane marker.
- Encode multi-primary expansions compactly inside one `u64` entry when the expansion fits up to four 16-bit weights; larger special expansions are represented by `LONG_RUNE` elsewhere and resolved through `map_long_rune()`.
- Mark ignorable or unsupported entries with `0x0` or replacement-style `0xFFFD`, which causes downstream sort-key/comparison loops to skip or use replacement semantics.

## Important APIs, Types, And Functions

This chunk defines table elements only, but it is coupled to the following APIs:

- `Unicode0900` is the zero-sized marker type implementing `UnicodeVersion` for `utf8mb4_0900_ai_ci`.
- `UnicodeVersion::preprocess(s)` returns `s` unchanged for `Unicode0900`. Unlike the padded `Unicode0400` path, this collation does not trim right spaces in preprocessing.
- `UnicodeVersion::char_weight(ch) -> u128` casts the character to `usize`, indexes `UNICODE_CI_TABLE`, maps `LONG_RUNE` sentinels through `map_long_rune()`, and otherwise widens the table's `u64` to `u128`.
- `UNICODE_CI_TABLE` is indexed directly by Unicode scalar value. The index positions in this chunk therefore correspond to code points, not to dense ranges or compressed records.
- `LONG_RUNE: u64 = 0xFFFD` is a sentinel for selected code points whose collation expansion does not fit in the ordinary `u64` table cell. Two such sentinels in this chunk are at `0xFDFA` and `0xFDFB`; `map_long_rune()` maps both to long Arabic phrase ligature expansions.
- `CollatorUtf8Mb40900AiCi` is a type alias for `CollatorUca<data_0900::Unicode0900>`, so all `utf8mb4_0900_ai_ci` comparison, sort-key, and hash behavior uses this table.
- `CollatorUca::write_sort_key()` emits each nonzero 16-bit weight segment in little-endian segment order from the packed integer but writes each segment as big-endian bytes.
- `CollatorUca::sort_compare()` compares strings by reading UTF-8 chars, loading packed weights, and comparing successive low 16-bit segments until a difference or exhaustion.
- `CollatorUca::sort_hash()` hashes the same successive 16-bit weight segments used for comparison, rather than hashing raw UTF-8 bytes.

## Data Shape In This Chunk

The slice begins with fallback entries for private-use code points:

- `0xE05B..0xF8FF` are almost entirely formula-shaped fallback values such as `0xE05BFBC1` and `0xF8FFFBC1`. These are the BMP Private Use Area. They preserve deterministic ordering by code point while separating the fallback namespace with the `FBC1` marker.
- `0xF900..0xFA6D` and `0xFA70..0xFAD9` contain explicit CJK Compatibility Ideograph weights. These map compatibility code points onto CJK primary weights such as `0x8C48FB41`, `0xCE26FB40`, and similar values, rather than treating them as unrelated private values.
- `0xFB00..0xFB06` include Latin ligature expansions such as repeated or paired letter weights. For example, entries like `0x1CE51CE5` encode multiple 16-bit primary weights in a single `u64` cell.
- `0xFB13..0xFB17` include Armenian ligature expansions.
- `0xFB1D..0xFB4F` contains Hebrew presentation forms, with a mixture of explicit base-letter weights, zero/ignored combining forms, and fallback gaps.
- `0xFB50..0xFDFF` contains Arabic presentation forms and Arabic ligature expansions. Many entries are multi-weight forms, and the two `LONG_RUNE` sentinels for `0xFDFA` and `0xFDFB` defer to `map_long_rune()` because those phrase ligatures exceed ordinary `u64` packing.
- `0xFE00..0xFE0F` and `0xFE20..0xFE2F` are zero in this table slice, making variation selectors and combining half marks ignorable for this primary-weight collation.
- `0xFE10..0xFE6F` contains vertical and small-form punctuation mappings, usually to punctuation weights or fallback values for gaps.
- `0xFE70..0xFEFE` contains Arabic presentation forms-B. Most assigned forms map to Arabic base/sequence weights; gaps and `0xFEFF` are zero or fallback.
- `0xFF00..0xFFEF` contains fullwidth and halfwidth forms. Fullwidth ASCII-like forms map back to ASCII/symbol primary weights, halfwidth Katakana/Hangul-like ranges map to script weights, and noncharacters/gaps use zeros or fallback entries.
- `0xFFF9..0xFFFB` are zero; `0xFFFC` has an explicit object-replacement style weight; `0xFFFD` is the replacement sentinel itself; `0xFFFE..0xFFFF` are fallback-shaped noncharacter weights.
- `0x10000..0x12F74` covers the start of supplementary-plane scripts. It interleaves explicit script weights with fallback-shaped values for unassigned gaps and zero entries for ignored marks. Notable ranges visible in the slice include Linear B, Aegean/ancient numeral blocks, Old Italic/Gothic-style script ranges, Deseret/Osage-like case-paired ranges, Brahmic supplementary scripts, and early historic scripts up through Egyptian Hieroglyphs-adjacent ranges.

The most important pattern is that fallback values in the BMP private-use range and supplementary-plane gaps are not produced at runtime by the out-of-table branch. They are physically present in the table because the table covers all code points up to `0x2CEA0`. The runtime out-of-table fallback is only for code points greater than the table length.

## Control Flow

At runtime, this chunk participates in a simple lookup pipeline:

1. A caller selects `CollatorUtf8Mb40900AiCi` through collation dispatch for `Collation::Utf8Mb40900AiCi`.
2. `CollatorUca` methods decode input bytes with `next_utf8_char()`.
3. For each decoded `char`, `Unicode0900::char_weight()` uses the scalar value as `UNICODE_CI_TABLE` index.
4. If the table entry is `0`, the downstream `while weight != 0` loops emit no sort-key words, compare no weight segment for that char, and hash no segment. This makes that code point primary-ignorable in this collation.
5. If the table entry is `LONG_RUNE` (`0xFFFD`), `map_long_rune()` returns a `u128` expansion. This matters in this chunk for `0xFDFA` and `0xFDFB`.
6. Otherwise the `u64` table value is widened to `u128`.
7. `write_sort_key()`, `sort_compare()`, and `sort_hash()` consume packed 16-bit segments from least significant to most significant until the packed weight becomes zero.

Packed expansions are therefore ordered by low 16-bit segments first. For a table value like `0x1CE51CE5`, the comparison/sort-key path observes `0x1CE5`, then `0x1CE5`. For a fallback value like `0xE05BFBC1`, the observed sequence is `0xFBC1`, then `0xE05B`. This matches the fallback construction used for out-of-table code points and keeps fallback classes grouped by the `FBC*` marker before comparing the code-point payload.

## State And Persistence Behavior

- The chunk is immutable static process data. It has no mutable state, heap allocation, file I/O, RocksDB writes, raft state, or persistence side effects.
- Its behavior is nevertheless part of TiKV's persisted SQL semantics. Sort keys generated from this table may be written into indexes, used for key ordering, or used by query executors for grouping, ordering, comparison, and hash semantics.
- Changing any value in this range can change comparison order or equality for `utf8mb4_0900_ai_ci`. That can invalidate existing index order assumptions, cause different query results, or create TiDB/TiKV incompatibility with MySQL collation behavior.
- Zero entries are semantically meaningful. Turning a zero into a nonzero weight makes a previously ignorable code point participate in ordering and hashing; turning a nonzero into zero collapses distinctions.
- `LONG_RUNE` sentinel entries depend on `map_long_rune()` staying synchronized with the table. If a sentinel is introduced in this chunk without a matching `map_long_rune()` arm, it will resolve to replacement `0xFFFD` rather than the intended long expansion.
- The table is compiled into the binary. There is no runtime version negotiation, data-file loading, or migration layer for table changes.

## Dependencies And Integration Points

- `data_0900.rs` depends on `super::UnicodeVersion` from `utf8mb4_uca/mod.rs`.
- The generated table comments claim creation from a Unicode UCA allkeys file. The merge report should verify generation provenance across the whole file because the path says `data_0900.rs` while the header references `UCA/4.0.0/allkeys-4.0.0.txt`.
- `utf8mb4_uca/mod.rs` defines the generic `CollatorUca<T>` implementation that consumes these entries.
- `codec/collation/mod.rs` dispatches `Collation::Utf8Mb40900AiCi` to `CollatorUtf8Mb40900AiCi`.
- `codec/data_type/scalar.rs` and other expression/evaluation paths call `sort_compare()` through collation-aware scalar comparison.
- The table relies on `next_utf8_char()` to decode valid UTF-8 scalar values. Invalid trailing byte sequences stop the loop with equality or truncation behavior determined by `CollatorUca`; the table is not involved if decoding fails.
- The sort-key path depends on `BufferWriter::write_u16_be()` and on the chosen packed-weight segment order.
- Hashing depends on Rust's `Hasher` and hashes the same 16-bit segments as comparison. The collation module explicitly warns that `sort_hash(str) != hash(sort_key(str))`.
- Compatibility-form entries integrate with broader SQL behavior: fullwidth ASCII, Arabic presentation forms, Hebrew forms, ligatures, and CJK compatibility ideographs must compare consistently with their base forms under this accent/case-insensitive collation.

## Risks And Edge Cases

- This chunk is generated and dense. Manual edits are high risk because a single shifted or deleted literal changes the table index for every later code point.
- The table index range is implicit. Rust checks the declared array length, but it does not verify that each value is assigned to the intended Unicode code point. Generator tests or golden comparison tests are needed.
- The `char_weight()` bounds check uses `if r > UNICODE_CI_TABLE.len()`. Since valid indexes are `0..len-1`, `r == UNICODE_CI_TABLE.len()` would index out of bounds. This chunk does not introduce the bug, but the full-file report should inspect whether any valid Unicode scalar can equal `0x2CEA1` and trigger it. `0x2CEA1` is below Unicode max, so this is a real edge to test unless unreachable by table-generation assumptions elsewhere.
- The packed fallback values are intentionally two 16-bit segments with `FBC1`/`FBC2` as the first comparison segment. Reversing packing order or changing the sort-key extraction order would reorder every fallback code point in this chunk.
- `0xFFFD` has dual meaning: it is both the replacement-character weight/sentinel value and the `LONG_RUNE` marker. Correctness relies on `map_long_rune()` containing arms for sentinel entries that should be long expansions, and returning replacement for the literal replacement character.
- `0xFDFA` and `0xFDFB` are long Arabic phrase ligatures. If `map_long_rune()` changes or loses those arms, equality/order for those characters changes materially.
- Zero entries for variation selectors, marks, and some gaps can collapse strings that differ only by those code points. That is expected for primary-weight `ai_ci` behavior but should be covered by compatibility tests against upstream MySQL/TiDB expectations.
- Compatibility ideographs and presentation forms have many explicit equivalence-style mappings. Incorrect values can make visually or semantically equivalent compatibility characters sort differently from their canonical forms.
- Supplementary-plane ranges combine assigned script weights, unassigned fallback weights, and zero marks. Unicode version upgrades can reclassify previously unassigned code points, requiring table regeneration rather than local patching.
- Because `write_sort_key()` emits 16-bit segments until the packed integer becomes zero, a table entry cannot encode an interior zero weight segment. This generated representation assumes primary-weight sequences do not require meaningful zero segments.
- The table is `#[rustfmt::skip]`; formatting tools will not normalize it. Review must rely on generation diffs, scripts, or targeted table-index checks rather than normal code readability.

## Test Signals

- Unit or integration tests should compare `CollatorUtf8Mb40900AiCi::sort_compare()`, `write_sort_key()`, and `sort_hash()` against golden cases for:
  - BMP private-use fallback ordering, for example neighboring code points around `0xE05B` and `0xF8FF`;
  - CJK Compatibility Ideographs around `0xF900`;
  - Latin ligatures `0xFB00..0xFB06`;
  - Hebrew presentation forms around `0xFB1D..0xFB4F`;
  - Arabic presentation forms and long ligatures `0xFDFA`/`0xFDFB`;
  - variation selectors `0xFE00..0xFE0F` as primary-ignorable;
  - fullwidth ASCII forms around `0xFF01..0xFF5E`;
  - replacement/noncharacter boundary values `0xFFFC..0xFFFF`;
  - the BMP-to-supplementary boundary at `0xFFFF`/`0x10000`;
  - supplementary fallback gaps such as `0x12544..0x12F74`.
- Add a direct test for `Unicode0900::char_weight()` at `r == UNICODE_CI_TABLE.len()` or the corresponding scalar value if valid, because the current `>` bounds check appears off by one.
- Golden sort-key tests should assert the segment order for a fallback value: `0xE05BFBC1` should emit segments `0xFBC1`, then `0xE05B`.
- Golden expansion tests should assert that packed ligature weights emit multiple 16-bit segments and that long-rune ligatures use `map_long_rune()` rather than literal `0xFFFD`.
- Regeneration tests should verify table length, selected boundary values, and checksums for generated ranges so accidental line-level edits are detected.

## Unresolved Cross-Chunk References

- The table's beginning and end are outside this chunk. The merge lane should combine all chunks to describe the full `UNICODE_CI_TABLE` coverage, including whether the declared length `0x2CEA1` is intended to include or exclude index `0x2CEA1`.
- `map_long_rune()` is near the file top and should be reconciled with all `LONG_RUNE` sentinels across the full table, not only `0xFDFA` and `0xFDFB`.
- The generator that produced this file is not in this chunk. The final report should identify whether generation is reproducible in the repository and whether `data_0900.rs` intentionally derives from the header's UCA 4.0.0 URL.
- Tests for `utf8mb4_0900_ai_ci` may live outside this module. The merge lane should connect this table to collation conformance tests across TiKV/TiDB compatibility suites.
