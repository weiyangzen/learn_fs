# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_uhc_utf8.h lines 1-8453

## Scope

- Repository subset: `Docs/research_subset_a.md`; `sources/os/illumos/illumos-gate` is in scope.
- Source span read completely: lines 1-8453 of `usr/src/uts/common/sys/kiconv_uhc_utf8.h`.
- This is chunk 1 of an oversized generated-style kernel conversion header. It covers the file preamble, guards, exported table-size macro, start of the UHC-to-UTF-8 table, and the first 8,373 table rows.
- The chunk ends inside the `kiconv_uhc_utf8[]` initializer. Line 8453 is key `0xB296`; adjacent line 8454 continues with key `0xB297`, so later chunks own the remaining rows and syntactic closure.

## APIs And Public Surface

- The header is guarded by `_SYS_KICONV_UHC_UTF8_H`, wrapped for C++ with `extern "C"`, and all conversion declarations in this span are gated by `_KERNEL`.
- The only macro defined in this chunk is `KICONV_UHC_UTF8_MAX (17047)`, documented as the maximum mapping number from UHC to UTF-8.
- The primary object introduced here is `static kiconv_table_array_t kiconv_uhc_utf8[] = { ... }`.
- No functions, callbacks, structs, or external symbols are defined. Because the array is `static` in a header, each including translation unit can receive its own private copy.
- The table element type is not defined in this file. It comes from `kiconv_cck_common.h` as a `uint32_t key` plus `uchar_t u8[4]`.

## Data Layout Visible In This Chunk

- Each mapping row uses a UHC code-unit key and a UTF-8 byte initializer in `u8`.
- The first row is a sentinel/fallback-style entry: key `0x0000` maps to `EF BF BD`, with the comment `Hold entry for non-identical conv`.
- Verified chunk statistics for lines 1-8453:
  - 8,373 mapping rows.
  - First key `0x0000`; last key `0xB296`.
  - No duplicate keys and no non-ascending keys in this span.
  - 170 rows have two explicit UTF-8 bytes, from `0xA1A4` through `0xACF1`.
  - 8,203 rows have three explicit UTF-8 bytes.
- The `u8[4]` backing array means omitted initializer bytes are zero-filled. Consumers must use conversion logic that understands UTF-8 length rather than assuming every row has exactly three explicit bytes.
- The early table body maps UHC extension keys beginning at `0x8141` to Hangul UTF-8 syllables. The key order follows UHC lead/trail-byte ordering, including gaps where byte values are not valid UHC trail bytes.
- Around the KS X 1001-compatible ranges, the table includes non-Hangul symbols as well as Hangul: punctuation, mathematical symbols, arrows, fullwidth ASCII forms, jamo, Roman numerals, Greek, box drawing, units, circled characters, hiragana/katakana, Cyrillic, and related compatibility characters. These are the visible source of the two-byte UTF-8 rows in this chunk.
- Near line 8024 the table reaches `0xB041`; near the chunk end it continues through the Hangul run to `0xB296 -> EC BF 80`.

## Control Flow

- There is no executable control flow in this chunk. It is compile-time initializer data plus preprocessor structure.
- Runtime conversion behavior is provided elsewhere by kiconv/CCK conversion code that includes this header and searches or indexes `kiconv_uhc_utf8[]`.
- The data is sorted by key in this span, which is an important invariant for table-driven lookup implementations, especially binary search.

## State And Dependencies

- State is static read-mostly conversion data compiled into kernel code paths that include this header under `_KERNEL`.
- Direct type dependencies visible from surrounding illumos headers:
  - `kiconv_table_array_t` from `kiconv_cck_common.h`.
  - `uint32_t` and `uchar_t` from kernel/common type headers included before this header by consumers.
  - Korean encoding validation helpers in `kiconv_ko.h`, including UHC first-byte and second-byte validity macros.
- Related generated-style reverse mapping data exists in `kiconv_utf8_uhc.h`, with `KICONV_UTF8_UHC_MAX (17047)` and a `static kiconv_table_t kiconv_utf8_uhc[]`.
- `usr/src/uts/common/sys/Makefile` exports both `kiconv_uhc_utf8.h` and `kiconv_utf8_uhc.h`.
- File-level licensing in this chunk includes the illumos CDDL header, Sun copyright, and Unicode data permission notice.

## Risks And Invariants

- Data integrity is the main risk. A single wrong key, byte literal, deletion, or insertion can silently corrupt Korean UHC conversion.
- `KICONV_UHC_UTF8_MAX` must match the complete table row count across all chunks. The complete local file has 17,047 rows from `0x0000` through `0xFDFE`, matching the macro, but this chunk contributes only the first 8,373 rows.
- Key ordering must remain strictly ascending for lookup consumers that depend on sorted tables.
- The table mixes UHC extension Hangul, KS X 1001-style symbol mappings, and common Hangul mappings. Reviewers should avoid treating the file as a contiguous algorithmic Hangul-only range.
- Invalid byte-sequence handling is not implemented in this header; it depends on external Korean encoding validators and conversion routines.
- The `static` table-in-header pattern can increase text/data footprint if included by multiple translation units, but it also keeps the mapping private to each consumer.
- The chunk is syntactically incomplete by design: it opens the header and array but does not close the initializer, `_KERNEL`, `extern "C"`, or include guard.

## Cross-Chunk References

- Later chunks must continue from line 8454 with key `0xB297` and preserve the sorted table sequence.
- Later chunks own the remaining rows through final key `0xFDFE`, the terminating `};`, and the closing preprocessor guards.
- Per-file merge should reconcile all chunk row counts against `KICONV_UHC_UTF8_MAX (17047)` and the companion reverse table size in `kiconv_utf8_uhc.h`.
- No final per-file report was created for this chunk.