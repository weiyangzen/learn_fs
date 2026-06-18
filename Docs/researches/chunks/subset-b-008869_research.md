# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_uca/data_0400.rs lines 1-271

## Scope

This chunk covers the beginning of TiKV's generated UCA 4.0.0 collation data provider for MySQL-compatible `utf8mb4_unicode_ci` behavior. Lines 1-271 include:

- the source-generation note pointing at Unicode `allkeys-4.0.0.txt`;
- imports for the local `UnicodeVersion` trait and shared `trim_end_padding()` helper;
- the zero-sized `Unicode0400` marker type;
- the `UnicodeVersion` implementation used by `CollatorUtf8Mb4UnicodeCi`;
- `map_long_rune()`, the fallback table for a small set of code points whose primary-weight expansion does not fit in `u64`;
- the first 207 lines of the static `UNICODE_CI_TABLE: [u64; 0x10000]`.

The chunk stops in the middle of the generated table, around the CJK compatibility/radical-style ranges represented by packed values such as `0xE7FFFB40` through `0xE812...`. Later chunks for this same source file must cover the remainder of the static array and its closing syntax.

## Purpose

`data_0400.rs` supplies Unicode Collation Algorithm 4.0.0 primary weights for TiDB/TiKV's `utf8mb4_unicode_ci` collation. The surrounding module aliases `CollatorUtf8Mb4UnicodeCi = CollatorUca<data_0400::Unicode0400>`, so this file is the data backend used whenever SQL string comparison, sort-key generation, or hash generation is requested under that collation.

The important behavior in this chunk is not a dynamic algorithm with mutable state. It is a generated lookup provider:

- SQL trailing-space padding is handled before comparison by trimming ASCII space bytes.
- Each Unicode scalar value in the Basic Multilingual Plane is mapped by direct array index into `UNICODE_CI_TABLE`.
- Code points outside the BMP are treated as replacement-character weight `0xFFFD`.
- Selected BMP entries whose packed sort-weight expansion is too long for `u64` are marked with the sentinel `LONG_RUNE` and expanded by `map_long_rune()` into a `u128`.

The table values are packed sequences of 16-bit collation elements. The consumer (`CollatorUca`) repeatedly reads the low 16 bits, shifts right by 16, and compares, hashes, or writes those units in order.

## Important APIs, Types, And Functions

- `LONG_RUNE: u64 = 0xFFFD` is a sentinel stored in `UNICODE_CI_TABLE` for code points requiring the wider `u128` expansion path. It is also the fallback weight for unmapped/out-of-range characters, so its dual use is only safe because `char_weight()` calls `map_long_rune()` and that helper returns `0xFFFD` for non-special sentinel hits.
- `Unicode0400` is a zero-sized marker struct. It carries no runtime fields; its only purpose is to bind UCA 4.0.0 table behavior to the generic `CollatorUca<T>`.
- `impl UnicodeVersion for Unicode0400` provides the two hooks used by the generic UCA collator:
  - `preprocess(s: &[u8]) -> &[u8]` delegates to `trim_end_padding(s)`, implementing the padded semantics of `utf8mb4_unicode_ci`.
  - `char_weight(ch: char) -> u128` converts a scalar value to a packed collation weight.
- `char_weight()` first casts the character to `usize`, rejects values greater than `0xFFFF`, then indexes `UNICODE_CI_TABLE[r]`. If the `u64` value equals `LONG_RUNE`, it calls `map_long_rune(r)`; otherwise it widens the `u64` to `u128`.
- `map_long_rune(r: usize) -> u128` contains a match for a small number of BMP code points, including compatibility and Arabic presentation forms such as `0x321D`, `0x321E`, `0x327C`, `0x3307`, selected `0x331x`/`0x333x` entries, `0x337F`, `0x33AE`, `0x33AF`, and `0xFDFB`. These map to multi-element weight expansions that need more than 64 bits.
- `UNICODE_CI_TABLE: [u64; 0x10000]` is the main generated lookup table. In this chunk it begins at line 65 and continues past line 271. `#[rustfmt::skip]` preserves the generated dense layout and comment anchors such as `/* 0000 */`, `/* 00EF */`, and later offsets.

## Control Flow

The runtime path starts outside this file. `CollatorUtf8Mb4UnicodeCi` is a type alias for the generic UCA collator instantiated with `Unicode0400`. When the collation layer needs to compare or hash a string, `CollatorUca<Unicode0400>` calls `Unicode0400::preprocess()` unless the caller requests no-padding behavior. For this 4.0.0 collation, preprocessing only strips trailing byte `0x20` spaces, not tabs, non-breaking spaces, or multibyte Unicode whitespace.

For each valid UTF-8 character, `CollatorUca` calls `Unicode0400::char_weight(ch)`. The weight lookup is direct:

1. Convert `ch` to its scalar numeric value.
2. If it is above `0xFFFF`, return `0xFFFD`; this file does not provide per-character supplementary-plane weights for UCA 4.0.0.
3. Read `UNICODE_CI_TABLE[r]`.
4. If the read value is not `LONG_RUNE`, return it as `u128`.
5. If the read value is `LONG_RUNE`, dispatch to `map_long_rune(r)`, which returns either the special multi-16-bit expansion or the default `0xFFFD`.

The table consumer then processes the packed weight from low-order 16-bit element to high-order element. In `write_sort_key()`, each 16-bit element is written big-endian to the sort-key buffer. In `sort_compare()`, the low 16-bit elements are compared one at a time, shifting the packed integer after equal elements. In `sort_hash()`, each low 16-bit element is fed into the hasher. Because all three operations consume the same packed representation, changing any value in this table affects ordering, grouping, distinctness, and hash joins/aggregations consistently for this collation.

## State And Persistence Behavior

This chunk has no mutable runtime state, heap allocation, locks, IO, or on-disk persistence. `Unicode0400` is zero-sized, and the table is a process-static read-only array embedded in the binary.

Persistence relevance is indirect but important:

- SQL indexes and MVCC keys may include encoded values whose order depends on collation sort keys. A table-value change can alter comparison semantics across persisted data.
- Hashing under this collation uses the same weight stream. A table change can affect hash partitioning, grouping, and equality checks.
- Trailing-space trimming is part of the collation contract. Removing or changing `preprocess()` would alter persisted index lookup semantics for strings such as `a` and `a `.
- The generated table source (`allkeys-4.0.0.txt`) is effectively a compatibility contract. Regenerating it from another Unicode version would not be a local refactor; it would change SQL-visible behavior.

## Dependencies And Integration Points

- `super::UnicodeVersion` is the trait consumed by `CollatorUca<T>` in `utf8mb4_uca/mod.rs`. The trait requires `Debug + Send + Sync + 'static`, which `Unicode0400` satisfies through the derived `Debug` and absence of fields.
- `trim_end_padding()` comes from the shared collation module and trims repeated trailing ASCII space bytes. Other padded collations use the same helper, so this file participates in the common MySQL padding convention.
- `CollatorUca` integrates this data with `next_utf8_char()`. Invalid UTF-8 stops processing in the generic collator; this table only receives valid Rust `char` values.
- `CollatorUtf8Mb4UnicodeCi` is re-exported by the collation module and selected through the broader `Collation` dispatch macros/types used by TiDB query datatype code.
- The generated table is paired with `data_0900.rs` in the same module, but they intentionally differ: this file is UCA 4.0.0 and padded, while `data_0900.rs` backs the newer `utf8mb4_0900_ai_ci` no-padding collation.
- The table values depend on the Unicode public data file referenced in the header. There is no local parser or generator in this chunk; the Rust source already contains the generated output.

## Risks And Edge Cases

- The sentinel value `0xFFFD` is overloaded as both "long rune marker" in the `u64` table and replacement/default weight. This works only because `map_long_rune()` lists every intentionally long code point and returns `0xFFFD` otherwise. A generated table entry that legitimately needs the single weight `0xFFFD` is indistinguishable from the sentinel path but still resolves back to `0xFFFD`.
- Any edit to a numeric literal can silently change SQL ordering. The dense generated layout makes review difficult; changes should be generated and validated against Unicode/MySQL expected collation outputs rather than hand-edited.
- `char_weight()` returns `0xFFFD` for all supplementary-plane code points. That may be intentional for this compatibility implementation, but it means distinct non-BMP characters collapse to the same primary weight in this collator.
- `UNICODE_CI_TABLE` has a compile-time length of `0x10000`. Missing or extra generated entries will fail compilation, but misplaced entries with the right count will compile and produce incorrect collation behavior.
- The packed weight representation assumes consumers read 16-bit chunks from least-significant to most-significant bits. Repacking values in high-to-low order would reverse multi-element comparison behavior.
- Zero weights in the table are skipped by the generic loops because they mean "no weight". That is expected for ignorable characters and unmapped control ranges, but an accidental zero can cause characters to disappear from comparisons, hashes, and sort keys.
- Long expansions are capped at `u128`, so `map_long_rune()` can represent at most eight 16-bit elements. Future generation logic would need a different representation if a collation expansion exceeded that bound.
- The table is marked `#[rustfmt::skip]`; formatting tools should not normalize it. Reflowing the table can make generated offset comments less useful during review.

## Test Signals

- Existing collation comparison tests in `collator/mod.rs` include `Collation::Utf8Mb4UnicodeCi` and assert representative behavior: `a` equals `a ` under padded comparison, case-insensitive comparison equates `a`/`A`, accent-insensitive comparison equates `cAfe`/`cafe`-style inputs, and German sharp-s compares equal to `ss` for this collation.
- Targeted regression tests for this chunk should cover:
  - trailing-space trimming through `Unicode0400::preprocess()`;
  - direct ASCII weights (`A` and `a` should map to the same primary weight in this case-insensitive table);
  - non-BMP inputs returning `0xFFFD`;
  - `LONG_RUNE` entries such as `U+321D`, `U+337F`, `U+33AE`, `U+33AF`, and `U+FDFB` returning their specific `u128` expansions rather than plain `0xFFFD`;
  - a BMP table entry that is zero, confirming the generic collator skips zero-weight characters consistently in sort keys and hashes.
- Because this is generated data, high-value validation is differential: compare sort keys and ordering against known MySQL `utf8mb4_unicode_ci` behavior or the expected UCA 4.0.0 allkeys-derived fixture set.
- Build-time validation already checks the array length and Rust literal syntax. It does not verify semantic alignment with Unicode data, MySQL compatibility, or the long-rune sentinel list.
