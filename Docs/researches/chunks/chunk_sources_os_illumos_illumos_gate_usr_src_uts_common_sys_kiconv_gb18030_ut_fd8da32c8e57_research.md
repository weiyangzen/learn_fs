# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h lines 33003-40491

## Scope

This report covers only lines 33003-40491 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h` for learn_fs subset A (`Docs/research_subset_a.md`). I read the requested 7,489-line range completely and used adjacent context only to identify the enclosing table declaration, type definition, and neighboring chunk boundaries.

The entire chunk is inside `static kiconv_table_array_t kiconv_gbk4_utf8[]`, the kernel-only GB18030 four-byte-sequence to UTF-8 mapping table that begins at line 24027 and closes much later at line 63449. This chunk contains no standalone declarations, functions, macros, preprocessor branches, or table closing braces.

## APIs And Data Structures

This chunk contributes 7,489 complete `kiconv_table_array_t` initializer rows:

- First row: key `0x81379034` maps to UTF-8 bytes `E2 92 B8` (`U+24B8`).
- Last row: key `0x82338932` maps to UTF-8 bytes `E4 8F 8A` (`U+43CA`).
- The rows are all packed four-byte GB18030 keys mapped to three-byte UTF-8 payloads.

The entry type is defined outside this file in `sys/kiconv_cck_common.h` as `uint32_t key; uchar_t u8[4];`. Every row in this chunk initializes the first three bytes of `u8`; the fourth byte is zero-filled by static aggregate initialization. The full-table count contract is the top-of-file `KICONV_GBK4_UTF8_MAX (39421)`, not redefined in this chunk.

## Control Flow

There is no executable C control flow in this chunk: no functions, branches, loops, calls, allocation, locking, or I/O. Runtime behavior is indirect through the kernel iconv code that consumes `kiconv_gbk4_utf8[]`.

The relevant conversion flow is external to the chunk:

1. GB18030 validation macros in `sys/kiconv_sc.h` define valid byte classes for four-byte sequences: second and fourth bytes are digits `0x30-0x39`, and the third byte is `0x81-0xfe`.
2. Converter code packs a validated four-byte GB18030 sequence into the table key format used here.
3. Shared lookup support declared as `kiconv_binsearch()` in `sys/kiconv_cck_common.h` depends on sorted table keys.
4. On a match, the stored `u8` bytes are emitted according to the UTF-8 length derived by common kiconv code from the first byte.
5. Invalid input handling, replacement-character policy, output-capacity errors, and buffer advancement are implemented in the conversion routines, not in this data range.

## State And Dependencies

The chunk is immutable static kernel data under the file's surrounding `_KERNEL` guard. It has no mutable state and no per-conversion state.

Direct dependencies visible from adjacent context:

- `kiconv_gbk4_utf8[]` declaration at line 24027.
- `kiconv_table_array_t` from `uts/common/sys/kiconv_cck_common.h`.
- `KICONV_GBK4_UTF8_MAX` from this header's top-level constants.
- GB18030 byte-shape macros and plane constants from `uts/common/sys/kiconv_sc.h`.
- Header export through `uts/common/sys/Makefile`.
- Reverse-direction data is separate in `sys/kiconv_utf8_gb18030.h`.

## Data Shape

Mechanical checks over the requested range found:

- Exact rows: 7,489.
- Syntax anomalies: none; every line is a complete table initializer row.
- Key ordering: strictly increasing, with no duplicate or descending keys.
- UTF-8 code point ordering: increasing throughout the chunk.
- Unicode gaps: expected sparse ranges are present around symbol/radical/CJK-extension blocks; these are mapping-table sparsity, not control-flow gaps.

Visible key-prefix spans:

- `0x8137...`: lines 33003-34108, 1,106 rows, `U+24B8..U+299F`, keys `0x81379034..0x8137FE39`.
- `0x8138...`: lines 34109-35368, 1,260 rows, `U+29A0..U+2E90`, keys `0x81388130..0x8138FE39`.
- `0x8139...`: lines 35369-36628, 1,260 rows, `U+2E91..U+34A2`, keys `0x81398130..0x8139FE39`.
- `0x8230...`: lines 36629-37888, 1,260 rows, `U+34A3..U+3993`, keys `0x82308130..0x8230FE39`.
- `0x8231...`: lines 37889-39148, 1,260 rows, `U+3994..U+3E86`, keys `0x82318130..0x8231FE39`.
- `0x8232...`: lines 39149-40408, 1,260 rows, `U+3E87..U+4375`, keys `0x82328130..0x8232FE39`.
- `0x8233...`: lines 40409-40491, 83 rows, `U+4376..U+43CA`, keys `0x82338130..0x82338932`.

## Risks And Cross-Chunk References

The main correctness risks are generated-data risks:

- Count drift: inserting or deleting rows anywhere in the full `kiconv_gbk4_utf8[]` table must keep `KICONV_GBK4_UTF8_MAX` aligned with the complete table.
- Sort-order drift: lookup relies on monotonic keys, so any manual edit must preserve order across chunk boundaries.
- UTF-8 payload drift: consumers trust these byte arrays; malformed triples would be copied directly to output.
- Boundary mistakes: this chunk starts and ends mid-table, so merge/report tooling must not infer a declaration or close brace inside this range.

Cross-chunk continuity:

- Previous chunk ends at line 33002 with key `0x81379033 -> E2 92 B7` (`U+24B7`); this chunk starts at line 33003 with the next row `0x81379034 -> E2 92 B8`.
- Next expected chunk should start at line 40492 with `0x82338933 -> E4 8F 8B` (`U+43CB`), immediately after this chunk's final `0x82338932 -> E4 8F 8A`.
- Later known chunk `47981-55469` remains in the same `kiconv_gbk4_utf8[]` table and continues the generated four-byte mapping data.