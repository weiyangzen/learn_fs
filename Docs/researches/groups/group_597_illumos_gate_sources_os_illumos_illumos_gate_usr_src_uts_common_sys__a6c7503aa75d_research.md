# Group Research: group_597_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__a6c7503aa75d

Scope: `Docs/research_subset_a.md`, source tree `sources/os/illumos/illumos-gate`. Both listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb2312_utf8.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb2312_utf8.h

## Purpose

`kiconv_gb2312_utf8.h` is a kernel-only illumos iconv data header for converting GB2312 encoded values to UTF-8 byte sequences. It contains no callable functions; its primary payload is a large static mapping table compiled only when `_KERNEL` is defined.

The file carries CDDL, Sun copyright, and Unicode data-file permission notices, with a Sun modification notice. It is guarded by `_SYS_KICONV_GB2312_UTF8_H` and wrapped in `extern "C"` for C++ consumers.

## Public Surface

Under `_KERNEL`, the file defines:

- `KICONV_GB2312_UTF8_MAX (8179)`: the declared number of mapping entries.
- `static uchar_t kiconv_gb2312_utf8[][3]`: a flat array of UTF-8 byte triples.

The table comment says the index is derived from `GB2312 - 0x2121`, so consumers must preserve the same GB2312 normalization/indexing convention used by the conversion implementation. The header itself does not validate input bytes or compute indexes.

## Data Layout

The table contains exactly 8,179 initializer rows, matching `KICONV_GB2312_UTF8_MAX`.

Observed table characteristics:

- 8,029 rows have three explicit bytes.
- 150 rows have two explicit bytes and rely on zero-initialization of the third byte.
- 729 rows map to UTF-8 replacement character `EF BF BD`, annotated as `/* -1 */` for unassigned/non-mappable positions.
- A small five-row private-use run appears near the end with `EE A0 90` through `EE A0 94`.
- The final row is `EF BF BD` with the comment `Hold entry for non-identical convsersion.`

The mapping starts with GB2312 symbol/punctuation-style entries, including ideographic punctuation, math symbols, fullwidth ASCII, kana, Greek/Cyrillic, pinyin/Bopomofo, and box drawing. The bulk of the file is CJK ideograph mappings encoded as UTF-8 triples.

## Control Flow

There is no executable control flow in this file. Runtime conversion behavior is entirely data-driven:

1. External kernel iconv code validates and normalizes GB2312 input.
2. It indexes into `kiconv_gb2312_utf8`.
3. It copies the resulting UTF-8 bytes to the destination buffer.
4. Missing or non-identical mappings are represented by replacement-character rows in this table.

Error handling, incomplete multibyte sequence handling, and output-buffer checks are not implemented here.

## Dependencies

The file assumes kernel/system typedefs are already available, especially `uchar_t`. It does not include headers directly.

Related integration points visible in the source tree:

- `uts/common/sys/Makefile` lists `kiconv_gb2312_utf8.h` among exported/generated kiconv headers.
- Adjacent CCK/kiconv headers provide related Chinese conversion tables and byte validation logic.
- Direct textual references to `kiconv_gb2312_utf8` outside this header were not found in the scanned tree, suggesting inclusion may be generated, indirect, or limited to build-specific conversion units.

## Risks And Invariants

Important invariants:

- `KICONV_GB2312_UTF8_MAX` must equal the initializer count.
- Replacement rows are meaningful placeholders and must not be removed just because they look repetitive.
- Two-byte UTF-8 rows depend on zero-filled padding.
- Table order and indexing convention must remain aligned with the consumer’s GB2312 index calculation.

Risks:

- Manual edits are high risk because semantic correctness depends on thousands of table entries.
- Because the array is `static` in a header, each including translation unit receives its own copy.
- The file does not self-describe valid GB2312 byte ranges; callers must perform validation elsewhere.
- The final “non-identical conversion” hold entry is part of the table contract and should be preserved even though it is not a normal character mapping.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb2312_utf8.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_ja.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_ja.h

## Purpose

`kiconv_ja.h` is the shared Japanese kernel iconv support header. It defines encoding table IDs, conversion helper macros, byte-classification predicates, NEC/IBM remapping logic, Japanese mapping typedefs, and compact static lookup vectors for JIS/SJIS transformations.

The file is guarded by `_SYS_KICONV_JA_H`, includes `<sys/kiconv.h>`, and uses C++ `extern "C"` wrapping.

## Public Surface

Encoding/table IDs:

- `KICONV_JA_TBLID_EUCJP`
- `KICONV_JA_TBLID_EUCJP_MS`
- `KICONV_JA_TBLID_SJIS`
- `KICONV_JA_TBLID_CP932`
- `KICONV_JA_MAX_MAPPING_TBLID`

Replacement/sentinel values:

- `KICONV_JA_DEF_SINGLE`
- `KICONV_JA_REPLACE (0xfffd)`
- `KICONV_JA_NODEST (0xffff)`
- surrogate range predicates `KICONV_JA_IFHISUR()` and `KICONV_JA_IFLOSUR()`

Conversion helper macros include:

- `KICONV_JA_RETERROR`
- `KICONV_JA_NGET`
- `KICONV_JA_NGET_REP_FR_MB`
- `KICONV_JA_NGET_REP_TO_MB`
- `KICONV_JA_NPUT`
- `KICONV_JA_GETU`
- `KICONV_JA_PUTU`
- UTF-8 BOM skip macros with and without conversion state

The macro layer assumes caller-local variables and labels such as `errno`, `rv`, `ret`, `next`, `ip`, `op`, `ileft`, `oleft`, `read_len`, `l`, `repnum`, and `kcd`.

## Byte Classification

The header defines predicates for:

- ASCII and C1 controls.
- EUC-JP codeset 1, codeset 2, codeset 3, UDC ranges, and JIS X 0208 row coverage.
- SJIS hankaku katakana, multibyte lead bytes, kanji lead bytes, supplemental kanji, UDC, IBM, NEC/IBM, and trail bytes.
- UTF-8 private-use/UDC range `0xe000` through `0xf8ff`.

These macros centralize byte-range policy for EUC-JP, EUC-JP-MS, SJIS, and CP932 conversion paths.

## Mapping Data

The file defines:

- `typedef ushort_t kiconv_ja_euc16_t`
- `typedef ushort_t kiconv_ja_ucs2_t`

It then provides six static mapping vectors:

- `kiconv_ja_sjtojis1`
- `kiconv_ja_sjtojis2`
- `kiconv_ja_jis208tosj1`
- `kiconv_ja_jis212tosj1`
- `kiconv_ja_jistosj2`
- `kiconv_ja_sjtoibmext`

These support direct conversion between SJIS byte positions and JIS row/cell values, plus IBM extension remapping. Invalid or unmappable vector entries use `0xff` or `0xffff` sentinels.

## NEC/IBM Remapping

`KICONV_JA_REMAP_NEC(dest)` translates selected NEC/IBM SJIS extension ranges into IBM code ranges. If the input is outside the accepted ranges, it sets `dest` to `0xffff`.

This macro mutates its argument repeatedly, so it must be called with a simple lvalue, not an expression with side effects.

## Dependencies And Integration

Direct dependency:

- `<sys/kiconv.h>` for common kiconv state/types and replacement definitions.

Observed related headers:

- `kiconv_ja_unicode_to_jis.h` includes this file and uses `KICONV_JA_NODEST`, table IDs, and `kiconv_ja_euc16_t`.
- `kiconv_ja_jis_to_unicode.h` includes this file and uses `KICONV_JA_REPLACE`, table IDs, and `kiconv_ja_ucs2_t`.
- `uts/common/sys/Makefile` exports `kiconv_ja.h`.

The helper macros call external conversion helpers such as `read_unicode()` and `write_unicode()` and depend on `kiconv_state_t` state for BOM processing.

## Control Flow

Unlike pure data-table headers, this file embeds control flow in macros. The macros decrement input/output counters, advance pointers, set `errno`, set `rv`, increment replacement counts, and jump to caller labels.

This makes the header tightly coupled to expected conversion-function structure. It reduces repeated boilerplate in the Japanese converters but makes misuse easy outside that context.

## Risks And Invariants

Important invariants:

- Table IDs must remain synchronized with companion Japanese mapping headers.
- Sentinel values `0xff`, `0xffff`, and `0xfffd` have distinct meanings and should not be collapsed.
- Byte-classification macros assume unsigned/`ushort_t`-style values; signed `char` inputs must be promoted safely before use.
- BOM macros mutate `inbuf` and `inleft`; callers must pass lvalue pointer/count variables.

Risks:

- Macro control flow depends on caller variables and labels, so refactoring callers can silently break these macros.
- `KICONV_JA_REMAP_NEC` mutates its argument and evaluates it many times.
- Static arrays in a header can duplicate storage in each including translation unit.
- The conversion tables are compact but opaque; changes should be validated with known EUC-JP, SJIS, CP932, surrogate, UDC, and BOM test vectors.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_ja.h -->