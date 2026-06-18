# Group Research: group_596_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__d9805474b1ac

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. The listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euckr_utf8.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euckr_utf8.h

## Purpose
Defines the kernel EUC-KR to UTF-8 conversion table used by illumos kiconv CCK conversion support. The file is generated/static data rather than procedural code: it maps 16-bit EUC-KR code values to UTF-8 byte arrays.

## Main Interfaces
- Include guard: `_SYS_KICONV_EUCKR_UTF8_H`.
- Kernel-only section: all conversion data is visible only under `_KERNEL`.
- `KICONV_EUCKR_UTF8_MAX` is defined as `8227`, matching the full number of table entries.
- `static kiconv_table_array_t kiconv_euckr_utf8[]` stores the mapping rows.

The table type is defined in `kiconv_cck_common.h` as a `uint32_t key` plus `uchar_t u8[4]`. This file relies on that type being included before this header.

## Data Layout
The file contains CDDL, Sun copyright, and Unicode data-file permission notices, followed by the kernel table.

The first row is a sentinel/fallback-style mapping:

- `0x0000 -> EF BF BD`, the UTF-8 replacement character.

The actual EUC-KR mappings start at `0xA1A1` and end at `0xFDFE`. The early ranges cover punctuation, mathematical symbols, currency/sign marks, fullwidth ASCII, Hangul jamo, roman numerals, Greek, box drawing, units, circled/parenthesized forms, hiragana/katakana, Cyrillic, and Hangul syllable ranges. The later ranges are mostly CJK ideograph mappings encoded as UTF-8 byte triples.

Sun-specific modifications are visible in the table comments for:

- `0xA2E6 -> E2 82 AC`, Euro currency symbol.
- `0xA2E7 -> C2 AE`, registered mark.

Complete-table validation from the full file:

- Source lines: 8,316.
- Declared entries: 8,227.
- Parsed initializer entries: 8,227.
- First key: `0x0000`.
- Last key: `0xFDFE`.
- Duplicate keys: none.
- Key ordering: strictly ascending.
- UTF-8 initializer widths: 171 two-byte mappings and 8,056 three-byte mappings.
- Invalid UTF-8 byte-shape initializers found: none.

Rows with two explicit UTF-8 bytes rely on normal C zero-initialization for the remaining `u8[4]` slots.

## Control Flow
There is no executable control flow in this header. Runtime conversion behavior is supplied by the kiconv code that includes or otherwise consumes this sorted `kiconv_table_array_t` data:

1. EUC-KR bytes are validated and combined into a table key by caller-side conversion logic.
2. The sorted table can be searched using the shared CCK table-search helpers.
3. Matching `u8` bytes are copied to the UTF-8 output buffer.
4. Invalid or missing mappings are handled by caller-side error/replacement policy, not by this table.

## Dependencies And Relationships
- `kiconv_cck_common.h` supplies `kiconv_table_array_t` and shared CCK conversion helper declarations.
- `usr/src/uts/common/sys/Makefile` lists this header alongside related kiconv conversion tables.
- Adjacent conversion data headers include `kiconv_uhc_utf8.h`, `kiconv_gb18030_utf8.h`, `kiconv_big5_utf8.h`, `kiconv_hkscs_utf8.h`, and reverse-direction UTF-8-to-encoding tables.
- Textual search in this checkout found `kiconv_euckr_utf8` and `KICONV_EUCKR_UTF8_MAX` only in this header, so consumers may be generated, conditionally built, or included through broader kiconv module patterns not visible as direct symbol references.

## Risks And Invariants
- The table must remain sorted by `key`; binary-search consumers depend on monotonic ordering.
- `KICONV_EUCKR_UTF8_MAX` must continue to match the initializer count. It currently does.
- The `static` table in a header gives each including translation unit a private copy; this is likely intentional for the kiconv table-header pattern but is a footprint concern if included broadly.
- Manual edits are high risk because almost all semantics are encoded in data rows. Validation should check count, sorted keys, duplicate keys, and UTF-8 byte validity.
- Two-byte mappings depend on zero-fill of the remaining `u8[4]` array elements, so consumers must not assume every row has three explicit payload bytes.
- The table maps keys only; it does not validate EUC-KR byte legality or enforce output-buffer policy.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euckr_utf8.h -->