# Group Research: illumos kiconv public/kernel encoding headers

Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`. This grouped report covers exactly the five requested files under `usr/src/uts/common/sys`.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_ja_jis_to_unicode.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_ja_jis_to_unicode.h

## Role

Kernel-only Japanese JIS-family to Unicode mapping header for illumos `kiconv_ja` conversions. It is almost entirely static lookup data plus two small compatibility macros for Microsoft-flavored mappings.

## Structure

- Lines 1-66: CDDL header, Sun copyright, Unicode data permission notice, and note that Sun modified the Unicode data.
- Lines 68-78: include guard, C++ linkage wrapper, includes of `<sys/kiconv.h>` and `<sys/kiconv_ja.h>`, then `_KERNEL` gating.
- Line 80: defines local `NODEST` as `KICONV_JA_REPLACE`; unmapped table cells therefore yield U+FFFD replacement, not `KICONV_JA_NODEST`.
- Lines 85-118: `kiconv_ja_jisx0201roman_to_ucs2[]`, a 128-entry direct table for JIS X 0201 Roman/control bytes 0x00-0x7f. It mostly maps byte values to the same UCS-2 code point.
- Lines 120-136: `kiconv_ja_jisx0201kana_to_ucs2[]`, a 63-entry table for JIS X 0201 half-width kana 0xa1-0xdf to Unicode U+FF61-U+FF9F.
- Lines 138-2394: `kiconv_ja_jisx0208_to_ucs2[]`, a dense 94x94-style JIS X 0208 mapping table. It starts with punctuation, symbols, Greek/Cyrillic, kana, box drawing, vendor rows, then kanji. Undefined positions use `NODEST`. Later rows include private-use sequential mappings such as U+E000 and above for vendor/private areas.
- Lines 2396-4653: `kiconv_ja_jisx0212_to_ucs2[]`, a second 94x94-style table for JIS X 0212 supplemental mappings. Early rows are sparse with many `NODEST` entries, then extended Latin/Greek/Cyrillic and large CJK ranges, ending with compatibility/private-use rows.
- Lines 4655-4674: `KICONV_JA_CNV_JISMS_TO_U2(id, u, c1, c2)` macro. It initializes `u` to `KICONV_JA_NODEST` and applies a small set of EUCJP-MS/CP932 overrides for JIS X 0208 coordinates: `(0x21,0x41)->0xff5e`, `(0x21,0x42)->0x2225`, `(0x21,0x5d)->0xff0d`, `(0x21,0x71)->0xffe0`, `(0x21,0x72)->0xffe1`, and `(0x22,0x4c)->0xffe2`.
- Lines 4676-4685: `KICONV_JA_CNV_JIS0212MS_TO_U2(id, u, c1, c2)` macro. It initializes `u` to `KICONV_JA_NODEST` and maps EUCJP-MS/CP932 JIS X 0212 coordinate `(0x22,0x43)` to `0xffe4`.
- Lines 4687-4695: undefines `NODEST`, closes `_KERNEL`, C++ wrapper, and guard.

## Dependencies And Consumers

- Depends on `kiconv_ja_ucs2_t`, `KICONV_JA_REPLACE`, `KICONV_JA_NODEST`, `KICONV_JA_TBLID_EUCJP_MS`, and `KICONV_JA_TBLID_CP932` from `kiconv_ja.h`.
- `kiconv_ja_ucs2_t` is `ushort_t`, so all lookup results are 16-bit. This fits the UCS-2-oriented Japanese conversion path in this header.
- The arrays are declared `static const` in a header, so every translation unit including it gets private read-only copies. This is consistent with generated kiconv mapping headers but increases object size.
- The data is consumed by Japanese kernel conversion code that indexes by normalized JIS row/cell or byte offsets. Bounds checks must live in callers; the tables themselves do not validate indices.

## Important Behaviors

- Regular table misses use U+FFFD replacement via `NODEST`, whereas the Microsoft override macros use `KICONV_JA_NODEST` (0xffff) to signal "no override." Callers must distinguish these meanings.
- The X 0201 Roman table maps byte 0x5c to U+005C rather than a yen sign. Any yen/backslash policy is handled elsewhere or through other mapping tables.
- The X 0201 kana table is offset-based; callers must subtract the start byte 0xa1 before indexing.
- The X 0208 and X 0212 tables are arranged in 94-cell rows using comments like `/* 16 01 */`; callers normally subtract 0x21 from each JIS byte and compute `row * 94 + cell`.
- CP932/EUCJP-MS compatibility mappings are not embedded by rewriting the main tables. They are exposed as explicit coordinate overrides, making standard and Microsoft behavior share the same base data.

## Risks And Gotchas

- The file is data-heavy and generated-data-like. Manual edits are risky because one shifted entry corrupts all later row/cell mappings.
- `NODEST` is a temporary macro with a generic name, but the file undefines it before exit. Include-order issues are low as long as no code relies on `NODEST` after including this header.
- The `KICONV_JA_CNV_*` macros are multi-statement macros without `do { } while (0)`. They should be used only in statement contexts where the expanded `if` chain cannot break surrounding `else` binding.
- Because the static arrays are header-local, duplicate inclusion in multiple C files can duplicate large constants. This is a size tradeoff, not a runtime mutability issue.

## Research Notes

Read completely: 4695 lines, 179489 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_ja_jis_to_unicode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_ko.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_ko.h

## Role

Kernel-only Korean encoding helper macros for EUC-KR, UHC, and Korean user-defined area handling in illumos `kiconv`.

## Structure

- Lines 1-22: CDDL header and Sun copyright.
- Lines 24-33: include guard, C++ linkage wrapper, and `_KERNEL` gating.
- Line 36: `KICONV_KO_IS_EUCKR_BYTE(b)` validates an EUC-KR byte in the 0xa1-0xfe range.
- Lines 39-43: UHC byte validators. First byte is 0x81-0xfe. Second byte is 0x41-0x5a, 0x61-0x7a, or 0x81-0xfe.
- Lines 46-56: constants for Korean user-defined areas in EUC-KR: segment 1 `0xc9a1-0xc9fe`, segment 2 `0xfea1-0xfefe`, segment bytes `0xc9` and `0xfe`, offset range `0xa1-0xfe`, range size `0x5e`, and conversion offsets `0xf65f`/`0xf6bd`.
- Lines 59-62: corresponding Unicode private-use/UDA range constants: UCS-4 `0xf700-0xf7bb`, UTF-8 scalar-packed `0xef9c80-0xef9ebb`.
- Lines 65-69: `KICONV_KO_IS_UDC_IN_EUC(v)` detects whether a packed EUC-KR two-byte value falls in either UDC segment.
- Lines 72-74: `KICONV_KO_IS_UDC_IN_UTF8(v)` detects whether a packed UTF-8 value falls in the Korean UDA range.
- Lines 76-82: closes `_KERNEL`, C++ wrapper, and guard.

## Dependencies And Consumers

- This header does not include `<sys/kiconv.h>` itself. It assumes consumers include any needed base kiconv definitions separately.
- The UDC macros operate on packed integer representations, not byte pointers. For example, EUC-KR bytes must be combined into values such as `0xc9a1`.
- The UTF-8 constants are packed byte sequences in an integer, matching the style used elsewhere in kiconv tables.

## Important Behaviors

- UHC second-byte validation intentionally includes ASCII letter ranges and the high-byte range, excluding punctuation gaps such as 0x5b-0x60 and 0x7b-0x80.
- EUC-KR validation accepts only graphic EUC bytes 0xa1-0xfe; ASCII handling is outside these macros.
- The Korean UDA mapping spans two EUC rows of 94 entries each, totaling `0xbc` code positions, mapped to U+F700 through U+F7BB.

## Risks And Gotchas

- Macro arguments are evaluated more than once in range checks like `KICONV_KO_IS_UDC_IN_EUC(v)`. Callers should pass side-effect-free expressions.
- Because there are no parentheses around each `&&` subexpression inside `KICONV_KO_IS_UHC_2nd_BYTE`, standard C precedence still gives the intended meaning, but the macro relies on that precedence.
- The header is public under `sys/` but meaningful only under `_KERNEL`; userland inclusion yields only guards and C++ wrappers.

## Research Notes

Read completely: 82 lines, 2690 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_ko.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_latin1.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_latin1.h

## Role

Kernel-only single-byte Western encoding conversion tables for illumos `kiconv`. It supports CP1252, ISO 8859-1, ISO 8859-15, and CP850 in both directions against UTF-8.

## Structure

- Lines 1-66: CDDL header, Sun copyright, Unicode data permission notice, and modification note.
- Lines 68-77: include guard, C++ linkage wrapper, include of `<sys/kiconv.h>`, then `_KERNEL` gating.
- Lines 79-88: comments describe `to_u8_tbl`; indices are source byte minus 0x80 and each entry stores up to three UTF-8 bytes. Invalid entries have a first byte that maps to an invalid size in the shared UTF-8 byte-count table.
- Lines 90-618: `static const kiconv_to_utf8_tbl_comp_t to_u8_tbl[4][128]`.
- Lines 91-221: CP1252 to UTF-8 entries for 0x80-0xff. Undefined CP1252 C1 slots 0x81, 0x8d, 0x8f, 0x90, and 0x9d are encoded as `{ 0xFE, 0xFE, 0xFE }`.
- Lines 222-352: ISO 8859-1 to UTF-8 entries for 0x80-0xff, including C1 controls as C2 80 through C2 9F and Latin-1 supplement characters.
- Lines 353-483: ISO 8859-15 to UTF-8 entries. It differs from ISO 8859-1 at standard Latin-9 replacement positions such as 0xa4 euro, 0xa6/0xa8 S caron pairs, 0xb4/0xb8 Z caron pairs, and 0xbc/0xbd OE pairs.
- Lines 484-618: CP850 to UTF-8 entries, including accented Latin letters, box-drawing characters, block elements, and DOS code page symbols.
- Lines 620-627: comments describe `to_sb_tbl`; each entry stores a packed 24-bit UTF-8 byte sequence and an 8-bit single-byte result, sorted by UTF-8 key for binary search.
- Lines 628-1141: `static const kiconv_to_sb_tbl_comp_t to_sb_tbl[4][128]`.
- Lines 629-758: UTF-8 to CP1252. It includes sorted mappings for Latin-1 supplement, CP1252 punctuation, euro, trademark, and padding sentinel entries `{ 0xFFFFFF, 0x00 }` for undefined byte positions.
- Lines 759-889: UTF-8 to ISO 8859-1. This maps C1 controls and Latin-1 supplement UTF-8 forms back to bytes 0x80-0xff.
- Lines 890-1018: UTF-8 to ISO 8859-15. The table omits replaced Latin-1 characters that ISO 8859-15 does not encode and includes euro/OE/caron mappings.
- Lines 1019-1141: UTF-8 to CP850. The table covers Latin, box-drawing, and block symbols used by CP850.
- Lines 1143-1149: closes `_KERNEL`, C++ wrapper, and guard.

## Dependencies And Consumers

- Depends on `kiconv_to_utf8_tbl_comp_t` and `kiconv_to_sb_tbl_comp_t` from `kiconv.h`.
- The forward table is indexed by conversion id and source byte offset. In `usr/src/uts/common/os/kiconv.c`, conversion paths use `to_u8_tbl[id][k]` and `u8_number_of_bytes[first_byte]` to decide how many bytes to emit.
- Reverse conversion paths binary-search `to_sb_tbl[id]` by packed UTF-8 value. The comments and table ordering are part of that contract.
- Tables are `static const` in a header, so included translation units receive private read-only copies.

## Important Behaviors

- Only bytes 0x80-0xff are represented. ASCII bytes 0x00-0x7f are handled directly by converter logic, not by these tables.
- CP1252 invalid bytes use `0xfe` sentinel bytes in `to_u8_tbl`, while reverse CP1252 uses `0xffffff` sentinels at the end of the sorted table. Consumers must preserve this convention.
- ISO 8859-1 is treated as a full 0x80-0xff byte-to-Unicode mapping, including C1 controls, rather than rejecting the 0x80-0x9f range.
- The packed UTF-8 keys are byte sequences, not Unicode scalar values. For example, euro is represented as `0xe282ac`.

## Risks And Gotchas

- `to_sb_tbl` must remain sorted by packed UTF-8 key for binary search. A single out-of-order edit can make valid characters unconvertible.
- The two table families encode invalid/unassigned entries differently. Treating `0xfe` and `0xffffff` as equivalent without considering direction would be wrong.
- The table id ordering is implicit: CP1252, ISO 8859-1, ISO 8859-15, CP850. Callers must use matching ids.
- Because arrays are header-local, including this file from multiple C files duplicates approximately 34 KB of table source data in object form.

## Research Notes

Read completely: 1149 lines, 33868 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_latin1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_sc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_sc.h

## Role

Kernel-only Simplified Chinese byte validation and boundary constants for GBK, GB2312, and GB18030 conversion logic in illumos `kiconv`.

## Structure

- Lines 1-22: CDDL header and Sun copyright.
- Lines 24-33: include guard, C++ linkage wrapper, and `_KERNEL` gating.
- Line 36: `KICONV_SC_IS_GBK_1st_BYTE(c)` accepts first bytes 0x81-0xfe.
- Lines 39-40: `KICONV_SC_IS_GBK_2nd_BYTE(c)` accepts 0x40-0x7e or 0x80-0xfe.
- Line 43: `KICONV_SC_IS_GB18030_2nd_BYTE(c)` accepts decimal digit bytes 0x30-0x39 for four-byte GB18030 sequences.
- Line 46: `KICONV_SC_IS_GB18030_3rd_BYTE(c)` accepts 0x81-0xfe.
- Lines 49-50: `KICONV_SC_IS_GB18030_4th_BYTE(c)` aliases the four-byte second-byte digit rule.
- Lines 53-60: `KICONV_SC_GET_GB_LEN(v, l)` sets `l` to 4, 2, or 1 based on whether high 16 or high 8 bits are present in a packed GB value.
- Line 62: `KICONV_SC_IS_GB2312_BYTE(b)` accepts 0xa1-0xfe.
- Lines 65-69: constants for the Unicode plane-1/GB18030 arithmetic boundary: U+10000, its UTF-8 packed bytes `0xf0908080`, and GB18030 sequence `0x90308130`.
- Lines 71-77: closes `_KERNEL`, C++ wrapper, and guard.

## Dependencies And Consumers

- This header has no includes. It relies only on basic integer comparisons and is intended to be included after any broader kiconv declarations needed by the consumer.
- The length macro assumes a packed integer representation where one-byte, two-byte, and four-byte GB sequences occupy low-order bytes.
- Plane-1 constants are used by GB18030 arithmetic conversion for Unicode code points at and above U+10000.

## Important Behaviors

- The first/second byte validators labeled GBK are also used for the two-byte subset of GB18030.
- Four-byte GB18030 validation has the pattern first byte 0x81-0xfe, second digit 0x30-0x39, third 0x81-0xfe, fourth digit 0x30-0x39.
- `KICONV_SC_GET_GB_LEN` is a statement macro that assigns to an output lvalue rather than returning a value.

## Risks And Gotchas

- `KICONV_SC_GET_GB_LEN(v, l)` lacks `do { } while (0)`, so it is unsafe in some `if/else` contexts unless wrapped by the caller.
- The length macro evaluates `v` more than once. Side-effect expressions would be problematic.
- The byte validators do not cast to unsigned. If callers pass signed `char` values with negative representation, validation can fail unexpectedly unless values are normalized to unsigned/integer byte range.

## Research Notes

Read completely: 77 lines, 2429 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_sc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_tc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_tc.h

## Role

Kernel-only Traditional Chinese byte validation and user-defined area constants for Big5 and EUC-TW/CNS 11643 conversion logic in illumos `kiconv`.

## Structure

- Lines 1-22: CDDL header and Sun copyright.
- Lines 24-33: include guard, C++ linkage wrapper, and `_KERNEL` gating.
- Line 36: `KICONV_TC_IS_BIG5_1st_BYTE(v)` accepts first bytes 0x81-0xfe.
- Lines 39-40: `KICONV_TC_IS_BIG5_2nd_BYTE(v)` accepts 0x40-0x7e or 0xa1-0xfe.
- Line 43: `KICONV_TC_EUCTW_MBYTE` defines 0x8e as the CNS 11643 plane 2-16 introducer byte.
- Line 46: `KICONV_TC_EUCTW_PMASK` defines 0xa0 as the plane-number mask.
- Lines 49-50: `KICONV_TC_IS_EUCTW_1st_BYTE(v)` accepts either 0x8e or a valid EUC byte via shared `KICONV_IS_VALID_EUC_BYTE(v)`.
- Lines 53-57: `KICONV_TC_IS_VALID_EUCTW_SEQ(ib)` validates an EUC-TW byte pointer based on caller-provided `isplane1` and `plane_no` variables. Plane 1 checks byte 1; planes 2-16 check bytes 2 and 3 after the 0x8e introducer and plane byte.
- Lines 59-65: constants for EUC-TW user-defined Unicode range: planes 12/13/14/16 map to U+F0000 through a UTF-8 packed range `0xf3b08080-0xf3b8a88f`.
- Lines 67-73: closes `_KERNEL`, C++ wrapper, and guard.

## Dependencies And Consumers

- Depends on `KICONV_IS_VALID_EUC_BYTE(v)` from the shared kiconv headers, but does not include that header itself.
- `KICONV_TC_IS_VALID_EUCTW_SEQ(ib)` depends on local variables named `isplane1` and `plane_no` in the caller's scope. This is an implicit macro contract.
- The sequence macro reads bytes from `ib + 1`, `ib + 2`, and `ib + 3`; buffer-length checks must be completed by the caller before use.

## Important Behaviors

- Big5 second byte permits two disjoint ranges, deliberately excluding 0x7f-0xa0.
- EUC-TW plane 1 can be represented as two valid EUC bytes. Planes 2-16 use the multibyte introducer 0x8e followed by a plane byte and two EUC bytes.
- The UDA constants describe a Unicode supplementary private-use range, so conversions using them require UTF-8 packed values larger than three bytes.

## Risks And Gotchas

- `KICONV_TC_IS_VALID_EUCTW_SEQ` is not self-contained; it will not compile unless `isplane1` and `plane_no` exist in scope.
- The sequence macro can read past available input if caller length checks are wrong.
- Byte-validation macros evaluate arguments more than once in some cases and should receive side-effect-free expressions.
- As with the other small regional headers, userland inclusion sees no functional declarations because all definitions are gated by `_KERNEL`.

## Research Notes

Read completely: 73 lines, 2221 bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_tc.h -->