# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_uca/data_0400.rs lines 272-479

## Scope

This chunk covers lines 272-479 of the generated Unicode Collation Algorithm 4.0.0 data table used by TiKV's `utf8mb4_unicode_ci` collation. The range sits inside `static UNICODE_CI_TABLE: [u64; 0x10000]`, not inside executable Rust logic. Each row contains many comma-separated `u64` weights and ends with a comment such as `/* 6870 */`, `/* A017 */`, or `/* C592 */` that marks the first Unicode scalar value represented by that row.

The visible table rows span entries beginning around U+6870 and continuing through U+C602. In Unicode block terms, this chunk covers a large middle/tail slice of CJK unified ideographs, the transition through U+9FA5 into Yi syllable/radical weights, and the beginning/middle of Hangul syllable weights through U+C602. The next and previous chunks own adjacent table rows.

## Purpose

- Provide precomputed UCA 4.0.0 primary collation weights for BMP code points used by `utf8mb4_unicode_ci`.
- Keep collation comparisons fast by making `Unicode0400::char_weight()` a direct array lookup for code points at or below U+FFFF.
- Encode one or more 16-bit collation elements inside each `u64`; consumers later peel the value from least significant 16-bit units upward.
- Preserve MySQL-compatible case-insensitive Unicode ordering for database string comparison, sort keys, hashes, indexes, and SQL operators implemented through TiDB/TiKV expression evaluation.
- Cover high-volume CJK and Hangul ranges where table accuracy matters because many characters are not algorithmically derived in this implementation.

## Important APIs, Types, And Functions

- `UNICODE_CI_TABLE: [u64; 0x10000]` is the central data structure. This chunk contributes rows of `u64` literals to that static array.
- `Unicode0400::char_weight(ch: char) -> u128` indexes this table by `ch as usize`, returning the stored `u64` as `u128` for normal BMP entries.
- `LONG_RUNE` and `map_long_rune()` are defined before this table for entries that cannot fit in `u64`; this chunk does not define those functions, but `char_weight()` checks the sentinel before returning table values.
- `CollatorUtf8Mb4UnicodeCi` is an alias for `CollatorUca<data_0400::Unicode0400>`, so these constants directly back the public `utf8mb4_unicode_ci` collator.
- `CollatorUca<T>::write_sort_key()`, `sort_compare()`, and `sort_hash()` consume the returned weight by repeatedly using `weight & 0xFFFF` and `weight >>= 16`.

The dominant value patterns are generated weights such as `0xE870FB40` through the CJK rows and `0xAC00FBC1` through the Hangul rows. These values are data, not addresses or bit flags in local code. Their low 16-bit suffixes, commonly `0xFB40` or `0xFBC1` in this chunk, are part of the packed collation-element representation consumed by the generic UCA collator.

## Control Flow

There is no branch or loop defined in this chunk. The runtime control flow that reaches it is:

1. A caller asks the collation layer to compare, hash, or build a sort key for UTF-8 bytes under `utf8mb4_unicode_ci`.
2. `CollatorUca<Unicode0400>` optionally trims trailing pad bytes through `Unicode0400::preprocess()`.
3. The collator decodes the next UTF-8 scalar with `next_utf8_char()`.
4. `Unicode0400::char_weight()` casts that scalar to an index and reads `UNICODE_CI_TABLE[index]`.
5. The collator compares or writes the packed 16-bit weight sequence by walking the returned integer until it becomes zero.

For values in this chunk, the lookup path is the normal table path. Characters above U+FFFF bypass the table and return replacement weight `0xFFFD`; characters whose table slot is `LONG_RUNE` are expanded through `map_long_rune()`, but this chunk is mostly direct `u64` entries.

## State And Persistence Behavior

This chunk defines immutable process-global data. It has no mutable state, no synchronization, no IO, and no persistence side effects. Its persistence impact is indirect: the weights determine stable ordering and equality semantics for strings stored in or compared by TiKV/TiDB. Changes to any literal here can alter index ordering, range scans, grouping, joins, distinctness, hash behavior, and compatibility with persisted data ordered under `utf8mb4_unicode_ci`.

Because the table is `static`, memory is initialized as part of the compiled binary. The table is never regenerated at runtime. Any update to Unicode/UCA compatibility requires source regeneration or manual literal changes followed by recompilation.

## Dependencies And Integration Points

- Generated from Unicode's `allkeys-4.0.0.txt`, as documented at the top of `data_0400.rs`.
- Depends on the local `UnicodeVersion` trait contract in `utf8mb4_uca/mod.rs`.
- Integrated through `CollatorUtf8Mb4UnicodeCi`, which exposes these weights to the common `Collator` trait.
- The common collation API in `codec/collation/mod.rs` defines `char_weight`, `write_sort_key`, `sort_compare`, and `sort_hash`; those methods are what make this static table observable to the rest of TiDB/TiKV expression and codec code.
- The table layout depends on Rust array indexing matching Unicode scalar numeric values for BMP entries. Row comments are only human anchors; correctness comes from literal order.

## Risks And Edge Cases

- Off-by-one insertion or deletion in this generated array would shift every following code point's weight while still compiling if the final count is repaired elsewhere. That would be a severe silent collation regression.
- The line comments are not checked by the compiler. A stale marker such as `/* 6870 */` would mislead maintainers even if the array order changed.
- Packed multi-element weights rely on the low-to-high 16-bit consumption order in `CollatorUca`; changing encoding without changing the consumer would invert or corrupt ordering.
- CJK, Yi, and Hangul ranges are large and easy to treat as mechanical, but these are high-impact ranges for real user data. Small literal mistakes could break equality or ordering for specific characters.
- The `u64` table format cannot store every UCA expansion. The file handles exceptional long runes through the sentinel path outside this chunk; future generated data must preserve that split.
- Invalid UTF-8 handling is outside this table. The caller stops comparison/hash processing when `next_utf8_char()` fails, so malformed input behavior depends on the surrounding collator, not on these literals.

## Test Signals

- Unit or integration tests for `utf8mb4_unicode_ci` should compare known CJK, Yi, and Hangul ordering cases against MySQL/TiDB expected sort order.
- Sort-key tests should verify that representative characters from this chunk write the expected sequence of big-endian `u16` weight elements.
- Hash/equality tests should include values whose weights share suffix patterns such as `0xFB40` and `0xFBC1`, proving the packed weight loop consumes all elements.
- Regression tests should include boundary characters near row transitions: around U+6870, U+9FA5/U+A000, U+A4CF/U+AC00, and U+C602.
- A generation-time or build-time table validation would be useful: assert `UNICODE_CI_TABLE.len() == 0x10000`, verify selected code-point-to-weight fixtures from `allkeys-4.0.0.txt`, and detect unintended row shifts.
