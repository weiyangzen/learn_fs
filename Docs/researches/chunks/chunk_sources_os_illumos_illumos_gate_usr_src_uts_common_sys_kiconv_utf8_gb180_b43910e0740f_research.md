# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h lines 23675-37471

## Scope

This report covers only lines 23675-37471 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h` for learn_fs subset A (`Docs/research_subset_a.md`). I read the full requested range and used adjacent context only to identify the enclosing declarations, shared type definitions, and nearby conversion infrastructure.

The entire chunk is an interior slice of the kernel-only UTF-8-to-GB18030 mapping table:

- The file declares `KICONV_UTF8_GB18030_MAX` as `63361`.
- The enclosing array is `static kiconv_table_t kiconv_utf8_gb18030[]`, declared earlier under `#ifdef _KERNEL`.
- This chunk contributes 13,797 table entries and does not open or close the array.

## APIs And Exported Data

No callable API, macro, typedef, function pointer, or public kernel entry point is defined in this line range. The host-visible surface is data: packed UTF-8 keys and packed GB18030 values consumed by converter code that includes this header.

Each entry is a `kiconv_table_t` pair from `sys/kiconv_cck_common.h`:

- `key`: a UTF-8 byte sequence packed into a `uint32_t`.
- `value`: the GB18030 output sequence packed into a `uint32_t`.

The chunk starts with `0xE5B2A8 -> 0x8CFE` at line 23675 and ends with `0xE98A8C -> 0xE386` at line 37471. Decoding the packed UTF-8 bytes, this is the contiguous Unicode code point span U+5CA8 through U+928C. The adjacent previous line is U+5CA7, and the adjacent next line is U+928D, confirming this chunk is a middle segment of a larger ordered table.

## Control Flow

There is no local runtime control flow: no branches, loops, calls, allocation, locking, error handling, or state mutation occur in this chunk.

Runtime behavior is supplied by converter glue outside this range. Adjacent common declarations expose `kiconv_binsearch()` and UTF-8-to-CCK wrapper prototypes for tables of this shape. The practical invariant for this chunk is therefore ordering by `key`: the 13,797 entries are monotonically increasing by packed UTF-8 key, which supports binary-search based lookup. The mapped `value` field is not monotonic and must not be searched or range-inferred.

## State And Data Flow

This chunk contributes immutable static mapping state. Because the array is declared `static` in a header, storage is internal to any including translation unit rather than exported as one global object.

Data-flow semantics are one-way:

- Input to lookup is a validated UTF-8 sequence packed into a 24-bit value in a `uint32_t`.
- Successful lookup returns the packed GB18030 value in the table entry.
- Missing keys, invalid UTF-8, replacement policy, output-buffer sizing, and errno behavior are handled by converter code outside this table.

All 13,797 visible output values are four hex digits, so this slice maps to two-byte GB18030/GBK-compatible sequences only. Mechanical checks found no four-byte GB18030 values in the chunk, no malformed entry lines, no duplicate/decreasing keys, and no invalid two-byte GB18030 byte forms: first bytes are in `0x81`-`0xfe`, and second bytes avoid `0x7f` while staying in the valid `0x40`-`0x7e` or `0x80`-`0xfe` ranges.

The output values mix extension/private mapping ranges such as `0x8D40`-style assignments with standard-looking two-byte CJK values such as `0xD1D2`, `0xC1EB`, `0xB0B6`, and `0xE1B6`. This means callers must treat the table as authoritative per-entry mapping data, not as a formula from Unicode scalar position to GB18030 bytes.

## Dependencies

Direct dependencies visible from adjacent context:

- `_KERNEL` gates the table; non-kernel builds do not see this data.
- `kiconv_table_t` is defined in `sys/kiconv_cck_common.h` as `{ uint32_t key; uint32_t value; }`.
- The file header attributes the mapping data to Unicode data modified by Sun Microsystems.
- `uts/common/sys/Makefile` lists `kiconv_utf8_gb18030.h` among installed/common system headers.

Related converter context:

- `sys/kiconv_cck_common.h` declares `kiconv_binsearch()`, `kiconv_utf8_to_cck()`, and `kiconvstr_utf8_to_cck()` as common UTF-8-to-CCK conversion helpers.
- `uts/common/os/kiconv.c` registers `gb18030` as a normalized charset name with code id `9`.
- The reverse mapping lives in `kiconv_gb18030_utf8.h`; this chunk alone does not prove round-trip completeness.

Direct C references to `kiconv_utf8_gb18030` outside this header were not visible in the searched tree, so include-time/generated use should be checked when merging the final per-file report.

## Risks And Edge Cases

- Lookup correctness depends on sorted `key` order. Any duplicate, deletion, or out-of-order insertion can break binary-search behavior or silently select the wrong character.
- `KICONV_UTF8_GB18030_MAX` must continue to match the full table, not this chunk count.
- A single mistyped literal can corrupt path/name conversion under GB18030 locales without causing compile-time failure.
- Since the table is `static` in a header, each including translation unit can carry its own copy, increasing kernel text/data footprint if included broadly.
- The output values are all two-byte mappings in this range; callers still need separate handling for ASCII passthrough, four-byte GB18030 mappings in other chunks, invalid UTF-8, incomplete input, and replacement-character policy.
- The chunk maps a large contiguous Unicode range, but GB18030 output bytes are intentionally sparse and non-monotonic; compression or regeneration must preserve exact per-codepoint values.

## Cross-Chunk References

- Earlier chunks define the file prologue, licensing/provenance comments, header guards, `_KERNEL` gate, `KICONV_UTF8_GB18030_MAX`, and the start of `kiconv_utf8_gb18030[]`.
- The immediately preceding data line maps U+5CA7 (`0xE5B2A7`) to `0x8CFD`; this chunk begins at U+5CA8.
- The immediately following data line maps U+928D (`0xE98A8D`) to `0xE387`; later chunks continue the same table.
- The final per-file report should merge this middle-table segment with other chunks before drawing file-wide conclusions about total table size, closing guards, and complete UTF-8/GB18030 coverage.