# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_uca/data_0900.rs lines 9118-10359

## Scope

This chunk covers lines 9118 through 10359 of
`sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/utf8mb4_uca/data_0900.rs`.
The visible source is a contiguous segment of the generated `UNICODE_CI_TABLE`
static lookup array used by the `Unicode0900` implementation of the
`UnicodeVersion` trait. The chunk contains 18,630 hexadecimal `u64` table
entries. Within the complete table, this segment starts after 135,691 earlier
entries, so it corresponds to Unicode scalar table indexes `0x2120B` through
`0x25AD0`. The first visible value is `0x920AFB84` and the last visible value is
`0xDACFFB84`.

## Purpose

The chunk supplies precomputed case-insensitive collation weights for a large
range of Unicode code points used by TiDB/TiKV UTF-8 collation logic. The
surrounding file declares `Unicode0900`, implements `UnicodeVersion` for it, and
backs `Unicode0900::char_weight(ch)` with the `UNICODE_CI_TABLE` array. This
chunk is therefore not executable logic by itself, but it is part of the
runtime data path for `utf8mb4_0900_ai_ci` comparisons, sort-key generation, and
hashing.

The values in this range are overwhelmingly monotonic generated weights with a
constant low suffix `FB84`. The high-order portion increments in lockstep from
`0x920A` through `0xDACF`, which indicates that these characters retain a stable
individual primary order instead of folding into earlier Latin, Greek, kana, or
other multi-character equivalence weights visible elsewhere in the same table.
Given the table index range, the covered code points are in the CJK Extension B
area (`U+20000..U+2A6DF`), specifically the subrange `U+2120B..U+25AD0`.

## Important APIs, Types, And Data

- `Unicode0900` is the marker type for this table-backed Unicode version.
- `UnicodeVersion` defines `preprocess(s: &[u8]) -> &[u8]` and
  `char_weight(ch: char) -> u128`; `Unicode0900` implements both.
- `UNICODE_CI_TABLE: [u64; 0x2CEA1]` is the generated lookup table containing
  this chunk. The array is annotated with `#[rustfmt::skip]` so formatting does
  not disturb the generated layout.
- `LONG_RUNE: u64 = 0xFFFD` marks entries whose collation weight does not fit
  directly in a `u64`; those entries are resolved through `map_long_rune`.
  This chunk does not contain `LONG_RUNE` sentinels.
- `map_long_rune(r: usize) -> u128` maps a small set of special code points to
  long 128-bit collation sequences. It is not directly exercised by entries in
  this chunk, but it is part of the same `char_weight` data path.
- `CollatorUtf8Mb40900AiCi` is a type alias for
  `CollatorUca<data_0900::Unicode0900>`, making this table the weight source for
  the `Utf8Mb40900AiCi` collation selected through `match_template_collator!`.

## Control Flow

The chunk has no local control flow: it is a literal section of a static Rust
array. Runtime control enters it indirectly:

1. Higher-level collation dispatch maps `Collation::Utf8Mb40900AiCi` to
   `CollatorUtf8Mb40900AiCi`.
2. `CollatorUca<T>` implements the common UCA collation operations for any
   `UnicodeVersion` provider.
3. `CollatorUca<data_0900::Unicode0900>::char_weight(ch)` delegates to
   `Unicode0900::char_weight(ch)`.
4. `Unicode0900::char_weight` casts `ch` to a `usize`, bounds-checks against
   `UNICODE_CI_TABLE.len()`, reads `UNICODE_CI_TABLE[r]`, expands
   `LONG_RUNE` sentinels through `map_long_rune`, and returns the result as a
   `u128`.
5. For characters with code points `0x2120B..0x25AD0`, the lookup lands in this
   chunk and returns one of these monotonic `u64` weights.

The returned `u128` is consumed by three key `CollatorUca` operations:

- `write_sort_key` decodes UTF-8 with `next_utf8_char`, repeatedly emits the
  low 16-bit chunks of the weight as big-endian `u16` values, then shifts the
  weight by 16 bits until zero.
- `sort_compare` decodes both strings, skips characters whose weight is zero,
  compares weights chunk by chunk from low 16-bit units upward, and returns the
  first ordering difference.
- `sort_hash` decodes UTF-8, hashes each 16-bit weight unit directly, and uses
  the same zero-weight skip semantics as sort-key generation.

For this chunk's values, the low 16-bit unit is always `0xFB84` and the next
unit varies from `0x920A` through `0xDACF`. Because the common UCA code compares
and emits low chunks first, all entries in this segment share the first emitted
unit and are distinguished by the next unit.

## State And Persistence Behavior

This chunk is immutable process memory. It has no dynamic allocation, no
interior mutability, no persistence layer, no I/O, and no side effects. Its
state behavior is still important because it defines deterministic persisted
query semantics:

- SQL comparison results for strings containing code points in this range depend
  on these exact constants.
- Sort keys generated for indexes, ordering, and coprocessor evaluation depend
  on this data remaining stable across builds.
- Hashing for collation-aware equality/grouping paths depends on the same weight
  decomposition as comparison.
- Any regenerated or manually edited table value can change ordering equality or
  range boundaries for existing data containing CJK Extension B characters.

Because the array is compiled into the binary, updates require rebuilding TiKV
components that include `tidb_query_datatype`. There is no runtime reload or
configuration switch for this segment.

## Dependencies And Integration Points

- The file imports `super::UnicodeVersion` from the `utf8mb4_uca` module and
  fulfills that trait for `Unicode0900`.
- `utf8mb4_uca/mod.rs` defines `CollatorUca<T>`, the `UnicodeVersion` trait,
  and the public aliases `CollatorUtf8Mb4UnicodeCi` and
  `CollatorUtf8Mb40900AiCi`.
- `codec/collation/mod.rs` exports the `Collator` trait and maps
  `Utf8Mb40900AiCi` to `CollatorUtf8Mb40900AiCi` through
  `match_template_collator!`.
- The common collation path depends on `CharsetUtf8mb4`, `next_utf8_char`,
  `BufferWriter`, `Hasher`, and `Ordering` handling supplied elsewhere in the
  collation module.
- The data file comment says it was created from the Unicode UCA allkeys source
  at `https://www.unicode.org/Public/UCA/4.0.0/allkeys-4.0.0.txt`; this chunk is
  therefore best treated as generated data derived from an external Unicode
  ordering table rather than hand-authored source.

## Risks And Edge Cases

- Generated-data drift is the main risk. A single wrong constant in this chunk
  would silently alter ordering or hashing for one CJK Extension B code point.
  Since the values are monotonic, accidental insertion, deletion, or line-wrap
  damage would shift every later code point and be much more severe than a local
  typo.
- The table layout relies on exact positional indexing by Unicode scalar value.
  This chunk starts at index `0x2120B`, not at a locally declared range marker,
  so review and generation tooling need to validate counts, not just visible
  value patterns.
- The constants in this segment all share low 16-bit unit `0xFB84`. Any
  comparator or sort-key consumer that incorrectly assumes the first emitted
  16-bit unit is enough to distinguish weights would collapse the entire range.
  The current `CollatorUca` implementation continues shifting and comparing
  later units, so it avoids that collapse.
- The `Unicode0900::char_weight` bounds check uses `if r > UNICODE_CI_TABLE.len()`
  before indexing `UNICODE_CI_TABLE[r]`. If a valid Rust `char` has code point
  exactly equal to the table length (`0x2CEA1`), the check would not take the
  fallback path and the index would be out of bounds. This is outside this
  chunk's table values but directly relevant to the same lookup path.
- Characters above the table length use a computed fallback weight rather than a
  generated table entry. Ordering continuity around the table boundary should be
  tested because this chunk's visible monotonic pattern is only one part of the
  full table.
- `#[rustfmt::skip]` protects the generated table from normal formatting, but it
  also means style tools will not normalize or reveal unusual spacing. Validation
  should use scripts or generation checks rather than human visual inspection.
- The file name and exported type refer to `0900`, while the source comment
  references UCA 4.0.0 input. That may be an established compatibility choice,
  but it is a useful audit point when reconciling TiDB/MySQL collation
  expectations against the embedded generation source.

## Test Signals

- Compare and sort strings containing representative characters from the start,
  middle, and end of this chunk: `U+2120B`, an interior code point such as
  `U+23500`, and `U+25AD0`. Expected order should match the monotonic table
  order.
- Generate sort keys for adjacent code points in the segment and assert that the
  shared `0xFB84` unit is followed by the increasing distinguishing unit.
- Hash tests should confirm that adjacent characters in this range do not collide
  merely because they share the first emitted `0xFB84` unit.
- Regression tests should compare `sort_compare(a, b, false)` with bytewise
  comparison of `sort_key(a)` and `sort_key(b)` for sampled values in this
  range.
- Boundary tests should include the previous code point before the chunk
  (`U+2120A`), the first chunk code point (`U+2120B`), the last chunk code point
  (`U+25AD0`), and the next code point (`U+25AD1`) to catch off-by-one or shifted
  generated table data.
- A generated-table integrity check should verify that the number of constants
  before this chunk is 135,691 and that this chunk contains 18,630 constants.
- Lookup tests should cover high Unicode values around `UNICODE_CI_TABLE.len()`,
  especially `0x2CEA0`, `0x2CEA1`, and `0x2CEA2`, to exercise the table/fallback
  boundary and expose the exact-length bounds-check edge case.
