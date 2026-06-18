# Group Research: group_184_9front_sources_os_plan9_9front_sys_src_cmd_tcs_html_c_sources_os_pla_90d9170d0a7f

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Each listed source file was read completely. Verification used full-file reads plus `wc -l`/`sha256sum` and symbol/reference scans across `sys/src/cmd/tcs`.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/html.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/html.c

## Purpose
Implements the `tcs` HTML character reference codec. It converts HTML named and numeric character references to Plan 9 `Rune` values on input and emits non-ASCII runes as HTML entities or decimal numeric references on output.

## Key Elements
Defines `Hchar { char *s; Rune r; }` and a 2004-entry `byname[]` table of HTML entity names to Unicode scalar values. Names beginning with `_` are accepted after stripping the underscore but are not generated.

Runtime lookup is initialized by `html_init()`, which copies `byname` into `byrune`, sorts by name for input lookup, sorts by rune for output lookup, suppresses nonstandard names for generation, and resolves duplicate entity names for the same rune by keeping the shortest generated name. The file has 440 duplicate rune values in the entity table, so this duplicate-elimination step is central to stable output.

Functions:
- `hnamecmp`, `hrunecmp`, `hlencmp`: `qsort` comparators for name, rune, and name length.
- `html_init`: one-time table normalization and sorting.
- `findbyname`: binary-searches named references.
- `findbyrune`: binary-searches generated entity names by rune.
- `html_in`: reads UTF input through `Biobuf`, decodes `&name;`, `&#decimal;`, and `&#xhex;` forms, preserves invalid references literally, and calls `fixsurrogate`.
- `html_out`: writes ASCII runes raw, non-ASCII runes as named entities when available, otherwise as `&#decimal;`.

## Dependencies
Uses Plan 9 headers `u.h`, `libc.h`, `bio.h`, plus local `hdr.h` and `conv.h`. It depends on global conversion buffers/macros such as `runes`, `N`, `OUT`, `Runeerror`, `Runeself`, and `fixsurrogate`. `tcs.c` registers this file through two `convert[]` entries named `html`, one for `html_in` and one for `html_out`.

## Behavior/Risks
Input decoding intentionally refuses to turn references for ASCII syntax characters `<`, `>`, `&`, `"`, and `'` into raw characters; when a reference resolves to one of those characters, it re-emits the original reference text instead. This avoids introducing literal HTML syntax during "from HTML" conversion.

Malformed references are not dropped: the parser emits the original buffered bytes and preserves a consumed semicolon when present. Numeric references reject trailing garbage and negative values, but do not otherwise validate Unicode scalar range before assigning to `Rune`.

`html_out` only escapes non-ASCII runes. ASCII `<`, `>`, `&`, quotes, and apostrophes are written raw, so this is an encoding converter, not a general HTML escaper.

## Verification
Read completely: 2246 lines, 43604 bytes. SHA-256: `aaef031586249c31c6f07709993a1088c57dc3218018396f2a14181bcd1866f7`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/html.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/jis.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/jis.h

## Purpose
Provides macro helpers for converting between JIS X 0208 byte pairs and Microsoft Shift-JIS byte pairs, plus byte-range predicates used by the Japanese converters.

## Key Elements
Defines in-place transformation macros:
- `J2S(_h, _l)`: mutates a valid JIS X 0208 high/low byte pair into Shift-JIS form, including the Shift-JIS skipped byte ranges.
- `S2J(_h, _l)`: mutates a valid Shift-JIS pair into JIS X 0208 form.
- `ISJKANA(_b)`: detects JIS X 0201 katakana range `0xa0..0xdf`.
- `CANS2JH`, `CANS2JL`, `CANS2J`: validate Shift-JIS lead/trail bytes before conversion.
- `CANJ2SB`, `CANJ2S`: validate 94-character-set JIS bytes.

## Dependencies
Included by `conv_jis.c`, which uses `CANS2J`/`S2J` to parse Shift-JIS and mixed JIS input, and `J2S` to emit Shift-JIS output from kuten table indexes.

## Behavior/Risks
The transform macros mutate their arguments multiple times and assume simple lvalue integer variables. Passing expressions with side effects would be unsafe. The comments state callers must pass bytes already in valid range; the range predicates are separate and must be used by callers before conversion.

The macros operate on arithmetic byte values, not typed `uchar *` despite the comments saying pointer-like names. They are compact and old-style, so misuse can produce subtle conversion errors.

## Verification
Read completely: 107 lines, 2873 bytes. SHA-256: `b6d54e880597d35bc4971dd8ceb89073028b357591c6e4ab2899a314b172db9b`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/jis.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/ksc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/ksc.c

## Purpose
Defines the KS C 5601 to Unicode mapping table used by the Korean EUC converter.

## Key Elements
Includes `ksc.h` and defines `long tabksc5601[]`, a compressed mapping table for the 94x94 KS C 5601 codeset. The file comments document the index formula: for KS C 5601 code point `(n, m)`, lookup index is `(n - 33) * 94 + (m - 33)`.

The table starts with punctuation/symbol mappings such as `0x3000`, includes Hangul and Hanja ranges, uses `-1` for unmapped slots, and ends with a terminal `0` sentinel. `int ksc5601max = sizeof(tabksc5601)/sizeof(tabksc5601[0])-1` excludes that sentinel from converter iteration and bounds checks.

## Dependencies
Declared in `ksc.h` and consumed by `conv_ksc.c`. `ukscproc` indexes `tabksc5601` for EUC-K input and treats `< 0` entries as unknown mappings. `uksc_out` builds the reverse `tab[]` lookup by scanning `0..ksc5601max-1`.

## Behavior/Risks
This file is pure table data with no executable control flow besides the global `ksc5601max` initializer. Converter correctness depends on the table order exactly matching the `(row,column)` indexing formula. A misplaced row changes both input decoding and reverse output encoding.

Unmapped slots are represented as `-1`; `conv_ksc.c` increments conversion errors and emits `BADMAP`/`BYTEBADMAP` unless clean mode suppresses output. The terminal zero is not part of the logical table because `ksc5601max` subtracts one.

## Verification
Read completely: 988 lines, 72413 bytes. SHA-256: `26cfb392fdd22a5a33c8e70d196628d0a2385812dcd60edfce74999fdcc6773c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/ksc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/ksc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/ksc.h

## Purpose
Declares the KS C 5601 mapping table and its logical entry count for Korean conversion code.

## Key Elements
Exports:
- `extern long tabksc5601[];`
- `extern int ksc5601max;`

The comments state the table is indexed by kuten-style code position and that `ksc5601max` is the number of usable entries.

## Dependencies
Included by `ksc.c`, which defines the objects, and `conv_ksc.c`, which consumes them.

## Behavior/Risks
No include guard is present. The header contains only extern declarations, so repeated inclusion is not a storage-definition problem, but it relies on conventional single-definition behavior from `ksc.c`.

## Verification
Read completely: 2 lines, 112 bytes. SHA-256: `28b62139f19ffd46d9831973e95d3c95f6fd2b3cc34698bd3eafa8e90ce09440`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/ksc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/kuten208.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/kuten208.c

## Purpose
Defines the JIS X 0208 kuten-to-Unicode mapping table used by JIS, EUC-JP, and Shift-JIS converters.

## Key Elements
Includes `kuten208.h` and defines `long tabkuten208[KUTEN208MAX]`. The table has 8407 entries, matching `KUTEN208MAX`, indexed by the converter formula `hi * 100 + lo - 3232` after byte normalization.

Entries map JIS X 0208 kuten positions to Unicode code points. `-1` marks unmapped positions. Some entries are negative in the table family convention used by `conv_jis.c` to signal ambiguous mappings, though in this file the observed negative sentinel is `-1`.

## Dependencies
Declared in `kuten208.h`. Used by `conv_jis.c` for:
- `alljis`, `ms`, `ujis`, and `jis` input decoding.
- reverse-table initialization in `tab_init`.
- `jisjis_out`, `msjis_out`, and `ujis_out`.
Also referenced by `font/kmap.c` for font mapping generation.

## Behavior/Risks
This is pure data, but it is a critical shared table for multiple Japanese encodings. Input converters treat out-of-range indexes or `-1` entries as conversion errors. Output converters build a reverse `tab[]` by scanning all `KUTEN208MAX` entries, so duplicate Unicode mappings resolve to whichever table position is assigned last during the scan.

Any off-by-one change to `KUTEN208MAX` or row order would affect ISO-2022-JP, EUC-JP, and Shift-JIS behavior together.

## Verification
Read completely: 1055 lines, 59960 bytes. SHA-256: `08089fb28a6c852380cab4f5be938ee289689dfb47b9726f57c20dae13399f93`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/kuten208.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/kuten208.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/kuten208.h

## Purpose
Defines the fixed size and extern declaration for the JIS X 0208 kuten mapping table.

## Key Elements
Defines `KUTEN208MAX` as `8407` and declares `extern long tabkuten208[KUTEN208MAX];`.

## Dependencies
Included by `kuten208.c`, `conv_jis.c`, and `font/kmap.c`.

## Behavior/Risks
No include guard is present. The fixed maximum must remain synchronized with the initializer in `kuten208.c`; `conv_jis.c` uses it for bounds checks and reverse lookup construction.

## Verification
Read completely: 3 lines, 94 bytes. SHA-256: `952d40bfdf81091f24103eda3742ad5167a307e9a5588187e379bfb6c26788ce`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/kuten208.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/kuten212.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/kuten212.c

## Purpose
Defines the JIS X 0212 kuten-to-Unicode mapping table used for EUC-JP codeset 3 input.

## Key Elements
Includes `kuten212.h` and defines `long tabkuten212[KUTEN212MAX]`. The table has 7768 entries, matching `KUTEN212MAX`, indexed in `conv_jis.c` with the same kuten-style `hi * 100 + lo - 3232` formula for codeset 3 byte pairs.

The table maps JIS X 0212 positions to Unicode and uses `-1` for unmapped slots.

## Dependencies
Declared in `kuten212.h`. Used by `conv_jis.c` only on EUC-JP input when codeset 3 is selected by byte `0x8f`; there is no corresponding output path in this code for JIS X 0212.

## Behavior/Risks
This is input-only table data for supplementary Japanese characters. Invalid codeset 3 byte ranges are rejected before lookup; valid but unmapped kuten positions produce conversion errors and `BADMAP` unless clean mode suppresses replacement output.

Because there is no reverse output table for `tabkuten212`, characters decoded from JIS X 0212 may not round-trip back through the available JIS output encoders.

## Verification
Read completely: 975 lines, 55407 bytes. SHA-256: `3361e421d5a4dd2aa2131b0b652912c7de89d4e102cfe5b897cfdebe8af88c4f`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/kuten212.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/kuten212.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/kuten212.h

## Purpose
Defines the fixed size and extern declaration for the JIS X 0212 kuten mapping table.

## Key Elements
Defines `KUTEN212MAX` as `7768` and declares `extern long tabkuten212[KUTEN212MAX];`.

## Dependencies
Included by `kuten212.c` and `conv_jis.c`.

## Behavior/Risks
No include guard is present. The constant must stay synchronized with `tabkuten212` and with the bounds checks in the EUC-JP codeset 3 decoder.

## Verification
Read completely: 3 lines, 94 bytes. SHA-256: `afe90feb0cc7ec20cd2913acea35e772f0a584ebf1ec08b31d8cd4db2390316a`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/kuten212.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/misc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/misc.h

## Purpose
Defines multiple 256-entry single-byte character-set mapping tables used directly by the generic `tcs` table converter.

## Key Elements
Provides these `long[256]` tables:
- `tabatari`: ATARI-ST character set, ASCII identity in low half plus accented Latin, Hebrew, Greek, and symbols.
- `tabebcdic`: EBCDIC mapping with many `-1` unmapped slots and comments about compatibility substitutions.
- `tabmacroman`: Macintosh Standard Roman mapping, including ligatures and private-use-style Apple symbol `0xf7ff`.
- `tabnextstep`: NEXTSTEP encoding vector, including combining marks and two final `0xffff` entries.
- `tabps2`: IBM PS/2-style mapping with Latin, box drawing, and symbols.
- `tabsf1`, `tabsf2`: Finnish/Swedish ISO-646 variants with high-half unmapped entries.
- `tabtis620`: Thai TIS-620 mapping with unmapped gaps.
- `tabviet1`, `tabviet2`: Vietnamese VSCII variants with combining marks and precomposed Vietnamese letters.
- `tabviscii`: Vietnamese VISCII 1.1 mapping.

All tables were scanned as full 256-entry arrays after comment removal. Notable unmapped counts: `tabebcdic` 128, `tabsf1` 112, `tabsf2` 112, `tabtis620` 41, `tabviet1` 17, `tabviet2` 32. `tabatari`, `tabmacroman`, `tabnextstep`, `tabps2`, and `tabviscii` have no `-1` entries.

## Dependencies
These tables are registered in `tcs.c` as `Table` converters under names including `atari`, `ebcdic`, `macrom`, `next`, `sf1`, `sf2`, `tis-620`, `viet1`, `viet2`, and `vscii`.

## Behavior/Risks
Despite the `.h` suffix, this file defines storage, not just declarations. It must be included in exactly the intended compilation unit or duplicate definitions would result.

The generic table converter interprets `-1` as unmappable. Tables with compatibility substitutions, `0xffff`, combining marks, or private-use values may not round-trip cleanly through other encodings. Since these are direct byte-indexed tables, each array must remain exactly 256 logical entries.

## Verification
Read completely: 304 lines, 19274 bytes. SHA-256: `e2730f899d627a2bf27ceb510b2be52af45bef1dc26dffdf1899fb9e904f68ed`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/misc.h -->