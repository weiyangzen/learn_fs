# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_uca/data_0400.rs lines 480-610

## Scope

This chunk covers the tail of the generated `UNICODE_CI_TABLE` for the UCA 4.0.0-backed `utf8mb4_unicode_ci` collator. The source file declares `Unicode0400`, implements `UnicodeVersion` for it, and stores a 65,536-entry BMP lookup table generated from Unicode's `allkeys-4.0.0.txt`. Lines 480-610 are table data only: they start at the entry labeled `/* C603 */` and run through the final `0xFFFF` table slot and closing `];`.

The covered range maps BMP code points roughly from U+C603 through U+FFFF. It includes the end of the Hangul syllable/private-use-style implicit range, CJK compatibility ideographs, alphabetic and Arabic presentation forms, halfwidth/fullwidth forms, and the terminal special/noncharacter slots.

## Purpose

The table gives each BMP Unicode scalar a compact collation weight for case-insensitive Unicode comparison. `Unicode0400::char_weight` indexes `UNICODE_CI_TABLE[ch as usize]`; `CollatorUca<Unicode0400>` then consumes the returned `u128` in 16-bit chunks, lowest chunk first, when building sort keys, comparing strings, or hashing collation keys.

Most values in this chunk are generated constants, not hand-authored logic. Patterns in the data still matter:

- Sequential values such as `0xC603FBC1` encode implicit weights for a run of code points and preserve stable ordering for characters without explicit UCA primary mappings.
- Values ending in `FB40` or `FB41` in the CJK compatibility area map compatibility ideographs back into the same primary-weight space used by corresponding unified ideographs.
- Multi-primary packed values such as `0xEB90EB9`, `0x131F131D`, or longer Arabic packed sequences represent compatibility decomposition for ligatures/presentation forms.
- `0` entries are ignorable or unassigned table entries in this collation implementation.
- `0xFFFD` appears as the replacement-character weight and also as the fallback for unsupported/non-BMP input in `char_weight`.

## Important APIs and Types

- `Unicode0400`: marker type for the Unicode 4.0.0 collation table.
- `UnicodeVersion`: trait implemented by `Unicode0400`; exposes `preprocess` and `char_weight`.
- `Unicode0400::preprocess`: trims right-padding spaces through `trim_end_padding`, matching the padded behavior of MySQL `utf8mb4_unicode_ci`.
- `Unicode0400::char_weight`: converts a `char` to a table index, rejects non-BMP scalars with `0xFFFD`, and expands rare `LONG_RUNE` sentinels through `map_long_rune`.
- `UNICODE_CI_TABLE`: `[u64; 0x10000]` static table. This chunk is the final slice of that table.
- `CollatorUtf8Mb4UnicodeCi`: type alias in `utf8mb4_uca/mod.rs` that wires this data into `CollatorUca<data_0400::Unicode0400>`.

The chunk itself defines no public functions, structs, or methods; its API impact is entirely through table entries read by `Unicode0400::char_weight`.

## Control Flow

Runtime control flow is outside this chunk but depends directly on these entries:

1. `CollatorUca<Unicode0400>` receives UTF-8 bytes and, unless forced otherwise, applies `Unicode0400::preprocess` to trim trailing ASCII spaces.
2. `next_utf8_char` decodes the next valid UTF-8 scalar.
3. `Unicode0400::char_weight` indexes this table when the scalar is in the BMP.
4. `write_sort_key`, `sort_compare`, and `sort_hash` split each packed weight into 16-bit collation elements by repeatedly reading `weight & 0xFFFF` and shifting right by 16.
5. Zero-weight entries contribute no sort-key elements and are skipped by comparison/hash loops.

Because packed weights are consumed least-significant word first, the order of 16-bit groups inside each hex literal is semantically significant. Reversing or normalizing these constants without understanding the packing would change comparison results.

## State and Persistence

There is no mutable state, allocation, I/O, or persistence in this chunk. `UNICODE_CI_TABLE` is compile-time static read-only data embedded in the TiDB query datatype crate. Collation behavior is deterministic for a fixed binary and does not depend on runtime configuration beyond the selected `Collation` enum/type alias.

## Dependencies and Integration Points

This generated data integrates with:

- `trim_end_padding` in `collator/mod.rs`, which supplies MySQL-style padding behavior for `utf8mb4_unicode_ci`.
- `next_utf8_char` in `collator/mod.rs`, which determines whether a byte sequence reaches the table lookup or is ignored as invalid/truncated UTF-8.
- `CollatorUca` in `utf8mb4_uca/mod.rs`, which uses table weights for sort-key writing, comparison, and hash consistency.
- `Collation::Utf8Mb4UnicodeCi` dispatch through the broader collation module, making these constants part of SQL comparison, grouping, ordering, and key encoding behavior for that collation.

The file header states the table was generated from Unicode UCA 4.0.0 `allkeys-4.0.0.txt`, so compatibility with MySQL/TiDB collation semantics depends on keeping the generated values and packing format aligned with that source.

## Risks

- **Generated-data drift:** manual edits to any value in this chunk can silently change SQL comparison, ordering, grouping, or hash equality for affected Unicode code points.
- **Packing mistakes:** values may encode multiple 16-bit collation elements in one integer. Consumers emit low 16-bit chunks first, so apparent hex order is not display order.
- **Zero-weight behavior:** changing `0` entries to nonzero values, or vice versa, changes whether characters are ignored by comparison and hashing.
- **Compatibility-form sensitivity:** the U+F900..U+FFFF area contains many compatibility and presentation forms. Small mistakes can break equivalence for CJK compatibility ideographs, ligatures, Arabic presentation forms, and fullwidth ASCII forms.
- **BMP-only table boundary:** non-BMP characters never index this table and currently fall back to replacement weight `0xFFFD`; any Unicode-version upgrade must coordinate table shape, fallback behavior, and long-rune handling.

## Test Signals

The nearby collation tests in `collator/mod.rs` exercise the public behavior that depends on this table rather than asserting individual constants. Useful signals include:

- `Utf8Mb4UnicodeCi` treats `a` and `A ` as equal after case folding and right-padding trim.
- Accent/case examples such as `cAfe` versus `café` compare equal under Unicode CI behavior.
- German sharp-s behavior, such as `ß` versus `ss`, validates multi-element packed weights.
- Sort-key, compare, and hash paths should remain consistent because they all consume the same packed table weights in 16-bit chunks.

For this exact chunk, stronger regression tests would target code points near U+C603, CJK compatibility ideographs around U+F900, ligatures around U+FB00, Arabic presentation forms around U+FB50/U+FDxx/U+FExx, fullwidth ASCII around U+FF01-U+FF5E, and terminal values U+FFFD-U+FFFF.
