# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_uca/data_0900.rs lines 6542-7786

## Chunk Scope

This chunk is a contiguous slice of the generated `UNICODE_CI_TABLE` used by `Unicode0900`, the Unicode-version implementation behind TiDB/TiKV's `utf8mb4_0900_ai_ci` UCA collator. It covers source lines 6542-7786 inside the static array declaration that begins near the top of `data_0900.rs`.

Within the array, these lines contain 18,675 hexadecimal `u64` entries. Counting entries from the first element of `UNICODE_CI_TABLE`, the chunk maps approximately table indexes/codepoints `0x17B1A..=0x1C40C`. The first value in the assigned range is `0x8B1AFB00`; the last is `0xC40CFBC3`. The slice is almost entirely generated fallback-style collation weights: 4,070 values end in `FB00`, 14,456 values end in `FBC3`, and only 6 entries are literal zero values.

## Purpose

`data_0900.rs` provides the version-specific Unicode Collation Algorithm weight table for `utf8mb4_0900_ai_ci`. The file defines `Unicode0900`, implements `UnicodeVersion` for it, and supplies `UNICODE_CI_TABLE: [u64; 0x2CEA1]` as the fast direct lookup from Rust `char` codepoint to a packed primary-weight sequence.

The assigned chunk contributes a high-codepoint region of that lookup table. There are no independent functions or branches in this range; its purpose is data coverage. If a UTF-8 character's scalar value falls into this index interval, `Unicode0900::char_weight` returns the corresponding packed weight from this chunk unless the table value is the `LONG_RUNE` sentinel. Because `utf8mb4_0900_ai_ci` is accent-insensitive and case-insensitive in this implementation, these weights encode comparison equivalence and ordering at the collation layer rather than preserving raw Unicode codepoint order.

## Important APIs, Types, and Functions

The relevant public integration point is not declared in this chunk but consumes it directly:

- `pub struct Unicode0900 {}` marks the Unicode 9.0-style data provider for the generic UCA collator.
- `impl UnicodeVersion for Unicode0900` provides:
  - `preprocess(s: &[u8]) -> &[u8]`, which returns the input unchanged for this collation.
  - `char_weight(ch: char) -> u128`, which indexes `UNICODE_CI_TABLE` using `ch as usize`.
- `static UNICODE_CI_TABLE: [u64; 0x2CEA1]` is the generated table containing this chunk.
- `static LONG_RUNE: u64 = 0xFFFD` is a sentinel for table entries whose weight does not fit in the regular `u64` representation.
- `map_long_rune(r: usize) -> u128` supplies hand-listed extended `u128` weights for sentinel entries.

The table stores `u64` values, but `char_weight` returns `u128`. Regular table entries are widened directly to `u128`; sentinel entries are resolved through `map_long_rune`; codepoints beyond the table length are mapped by formula rather than table lookup.

## Control Flow

Runtime control flow involving this chunk is simple and performance-critical:

1. `CollatorUtf8Mb40900AiCi` aliases `CollatorUca<data_0900::Unicode0900>`.
2. `CollatorUca<T>::write_sort_key`, `sort_compare`, and `sort_hash` decode input bytes with `next_utf8_char`.
3. For each decoded `char`, the generic collator calls `T::char_weight`, so `Unicode0900::char_weight` receives the scalar value.
4. `Unicode0900::char_weight` checks whether the scalar value is beyond `UNICODE_CI_TABLE.len()`. If it is in range, the value at `UNICODE_CI_TABLE[r]` is returned as the packed weight unless it equals `LONG_RUNE`.
5. `CollatorUca` consumes the returned `u128` in 16-bit little-end chunks: it repeatedly uses `weight & 0xFFFF`, then shifts right by 16.

This chunk therefore feeds the inner loop of sorting, equality comparison, sort-key generation, and hashing for strings containing codepoints in the `0x17B1A..=0x1C40C` interval.

## Data Encoding Notes

Most values in this range are monotonic-looking generated weights with suffixes such as `FB00` or `FBC3`. The low 16-bit lane is significant because the generic collator serializes and compares the packed value by repeatedly masking `0xFFFF`. For example, a table value ending in `FB00` has `0xFB00` as the first emitted/compared weight lane; a value ending in `FBC3` has `0xFBC3` as the first lane. Higher 16-bit lanes then carry the generated primary ordering number.

The six zero entries matter because `CollatorUca` treats a zero character weight as ignorable: `write_sort_key` writes no lanes for it, `sort_hash` hashes no lanes for it, and `sort_compare` advances past zero weights while looking for the next non-zero weight. Any accidental nonzero-to-zero or zero-to-nonzero mutation in this chunk would change equality, sorting, and hash behavior for the affected codepoints.

No `LONG_RUNE` value was observed in the sampled summary for this chunk. If a future generator changes that, the consuming path would jump to `map_long_rune`; missing cases in that function fall back to `0xFFFD`, collapsing all unlisted long runes to the replacement-character weight.

## State and Persistence Behavior

This file has no mutable state and performs no persistence. Its state is compile-time static data embedded into the binary. The important persistence contract is behavioral rather than storage-oriented: once compiled, this table fixes deterministic collation order, sort-key bytes, and hash input for all affected characters.

Because the array is a large static (`[u64; 0x2CEA1]`) and this chunk alone accounts for thousands of entries, it also contributes to binary size and resident read-only data. Runtime lookup is O(1) array indexing with no allocation.

## Dependencies

Direct dependencies visible from the file/module context are:

- `super::UnicodeVersion`, the trait that `Unicode0900` implements.
- `utf8mb4_uca::mod.rs`, which defines `CollatorUca<T>` and aliases `CollatorUtf8Mb40900AiCi` to `CollatorUca<data_0900::Unicode0900>`.
- The collation framework's `Collator` trait, `CharsetUtf8mb4`, `BufferWriter`, `next_utf8_char`, `Result`, `Ordering`, and `Hasher` imports reached through `use super::*` in `utf8mb4_uca::mod.rs`.
- Generated Unicode/UCA source data noted in the file comment. The comment says the file was created from Unicode `allkeys-4.0.0.txt`, despite the Rust type and collation alias naming the 0900 collation. That mismatch is worth preserving as a documentation/test signal rather than assuming either side is authoritative.

This chunk has no external crate calls and no procedural logic of its own.

## Integration Points

The chunk integrates with the rest of TiDB/TiKV collation behavior through the `utf8mb4_0900_ai_ci` path:

- SQL string comparisons using this collation eventually call `CollatorUtf8Mb40900AiCi::sort_compare`.
- Index or execution code needing sortable byte sequences calls `write_sort_key`, which emits big-endian `u16` lanes derived from the packed weights.
- Hash-based comparison/grouping paths call `sort_hash`, hashing the same 16-bit lane sequence used by comparison.
- Equality and ordering semantics for any character in the chunk's table interval are therefore shared across sort keys, comparison, and hashing as long as the table values remain aligned.

Because the table is generated and table-indexed by Unicode scalar value, source-line movement is not semantically important; entry order is. Insertions, deletions, or formatting that change the number/order of hex literals before this chunk would remap every later codepoint to the wrong weight.

## Risks and Edge Cases

- Off-by-one table edits are high impact. The array is positional: deleting or adding one literal in this chunk shifts all subsequent codepoint weights.
- The `char_weight` bounds check uses `if r > UNICODE_CI_TABLE.len()`, not `>=`. A `char` with scalar value exactly equal to `UNICODE_CI_TABLE.len()` would try to index one past the array. This chunk does not introduce that branch, but it is relevant to the table contract.
- Zero-weight entries are semantically ignorable. Any generator change around the six zeros in this slice can alter equality/hashing for rare codepoints in ways that are hard to detect with ordinary ASCII or BMP tests.
- Packed-weight lane order is subtle. `CollatorUca` consumes least-significant 16-bit lanes first, so manually interpreting the hex constants as ordinary big-endian sort keys would be misleading.
- The file is generated and large. Manual edits are risky; regeneration should include full golden comparison tests against expected MySQL/TiDB collation behavior.
- The comment/source-version mismatch (`allkeys-4.0.0.txt` in a 0900 data file) could confuse future maintenance or generator auditing.

## Test Signals

Useful validation signals for this chunk are mostly integration/golden tests rather than unit tests against the raw constants:

- `utf8mb4_0900_ai_ci` comparison tests that include codepoints from `0x17B1A..=0x1C40C`, especially characters mapped to zero and representative `FB00`/`FBC3` suffix values.
- Sort-key golden tests verifying the exact emitted `u16` lane sequence for selected codepoints in this range.
- Hash/compare consistency tests: strings that compare equal under `sort_compare` should produce the same `sort_hash` contribution.
- Table-shape tests checking `UNICODE_CI_TABLE.len() == 0x2CEA1` and guarding against accidental entry-count drift.
- Fuzz or property tests around high Unicode scalar values near the table boundary and this chunk's boundaries, because the table lookup is positional and the out-of-range fallback is formula-based.

No dedicated tests were found in this chunk because it is static generated data. The main signal for correctness is that existing collation tests continue to match MySQL-compatible ordering and equality semantics after any regeneration.
