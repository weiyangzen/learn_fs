# Group Research: group_1617_plan9_sources_os_plan9_plan9_sys_src_cmd_tcs_gbk_c_sources_os_plan9_dea00396f436

Scope verified against `Docs/research_subset_a.md`: this group is under included source tree `sources/os/plan9/plan9`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/gbk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/gbk.c

This file is the static GBK-to-Unicode mapping payload for Plan 9's `tcs` converter. It contains no conversion control flow beyond including `gbk.h` and defining `long tabgbk[]`.

Key contents:
- `tabgbk[]` has 32,016 entries, exactly matching `GBKMAX - GBKMIN` for the byte-pair interval `[0x8140, 0xFE50)`.
- Each table index corresponds to a packed GBK two-byte code minus `GBKMIN`.
- Non-negative entries are Unicode/Plan 9 rune values; `-1` marks invalid, unassigned, or unsupported GBK byte-pair slots.
- The table includes CJK ideographs, punctuation, fullwidth forms, kana, Greek, Cyrillic, box-drawing, compatibility ideographs, radicals, and many extended GBK assignments.

Important details:
- Actual GBK input/output logic lives in `conv_gbk.c`; that code indexes `tabgbk[c - GBKMIN]` for input and builds a reverse `tab[]` map from `tabgbk[]` for output.
- Because output reverse mapping is built by assigning `tab[tabgbk[i-GBKMIN]] = i`, duplicate Unicode values in this data would resolve to the later GBK code point.
- The table is dense over the numeric GBK range, not compacted by valid lead/trail-byte classes, so invalid holes remain explicit `-1` values.
- The source is data-heavy and appears generated or imported from a character-set mapping source.

Filesystem relevance:
- Indirect: supports text transcoding for files and streams handled by `tcs`; it is not filesystem implementation code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/gbk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/gbk.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/gbk.h

This header exposes the GBK table range and table symbol used by the `tcs` GBK converter.

Key contents:
- `GBKMIN` is `0x8140`.
- `GBKMAX` is `0xFE50`.
- `extern long tabgbk[];` declares the mapping array defined in `gbk.c`.

Important details:
- The range is treated as half-open by `conv_gbk.c`: valid table lookup requires `c >= GBKMIN && c < GBKMAX`.
- The required table length is therefore `GBKMAX - GBKMIN`, which matches the 32,016 initializer entries in `gbk.c`.
- The header does not describe byte validity itself; it only bounds the numeric packed-code table.

Filesystem relevance:
- Indirect: part of `tcs` character conversion support for file/stream text data.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/gbk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/hdr.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/hdr.h

This is the shared internal header for Plan 9's `tcs` character-set converter. It defines global state, converter descriptors, function pointer types, common buffers, error sentinels, and portability macros.

Key contents:
- Declares global flags and counters: `squawk`, `clean`, `file`, `verbose`, `ninput`, `noutput`, `nrunes`, and `nerrors`.
- Defines converter capability flags: `From`, `Table`, and `Func`.
- Defines `struct convert` with converter name, description text, flags, data pointer, and function pointer.
- Declares converter registry `convert[]` and lookup helper `conv(char *, int)`.
- Defines input/output function pointer types and the `outtable`, `utf_*`, and `isoutf_*` interfaces.
- Defines shared block size `N = 10000`, global rune/output buffers, bad-map values, and `ESC`.
- Provides `OUT(out, r, n)` to dispatch either table-based or function-based output conversion.
- Provides Plan 9 versus hosted-C macros for error printing, unused values, and process exit.

Important details:
- `OUT` is central glue: input converters emit batches of runes and let the selected output converter decide whether to use `outtable()` or an output function.
- `BADMAP` is Unicode replacement character `0xFFFD`; `BYTEBADMAP` is `'?'` for byte-oriented fallbacks.
- The header assumes many globals are defined elsewhere in the `tcs` program, especially `tcs.c` and converter modules.
- For non-Plan 9 builds, it maps diagnostics to `fprintf(stderr, ...)` and exits through `exit(n)`.

Filesystem relevance:
- Indirect: provides common text-conversion plumbing for command-line conversion of file and stream contents.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/hdr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/html.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/html.c

This file implements the `html` input and output converter for `tcs`, translating between HTML character references/entities and Plan 9 runes.

Key behavior:
- Defines `Hchar { char *s; Rune r; }` and a static `byname[]` table of named HTML entities mapped to rune values.
- Uses leading `_` in entity names to mean "recognize this spelling on input, but do not generate it on output"; examples include common nonstandard aliases.
- `html_init()` copies `byname` to `byrune`, strips leading underscores for input lookup, suppresses those entries from output generation by setting their `byrune` rune to `Runeerror`, and sorts both lookup arrays.
- `findbyname()` binary-searches entity names to decode `&name;`.
- `findbyrune()` binary-searches rune values to choose a named entity for output.
- `html_in()` reads UTF input with `Bgetrune()`, recognizes `&name;`, decimal numeric references, and lowercase hexadecimal numeric references beginning `&#x`, then emits runes through `OUT`.
- `html_out()` writes ASCII runes directly, emits known non-ASCII runes as named entities, and falls back to decimal numeric references for other non-ASCII runes.

Important details:
- The comment says `&lt;`, `&gt;`, `&quot;`, and `&amp;` are intentionally omitted, but the table still includes `lt`, `gt`, `quot`, and `amp`; output behavior is governed by the sorted `byrune` table and ASCII fast path, so ASCII `<`, `>`, `"`, and `&` are written directly.
- Input entity scanning stops on semicolon or whitespace and uses a 100-byte buffer; malformed or unknown references are copied through as literal UTF text.
- Numeric reference parsing requires the final semicolon to remain present after `strtol`; out-of-range or negative values are treated as bad references and copied literally.
- Output uses `Biobuf` because generated entity strings can exceed the normal UTF bytes-per-rune size.
- `html_out()` initializes a new `Biobuf` on fd 1 for each call and flushes at the end of the batch.

Filesystem relevance:
- Indirect: converts HTML-encoded text in files or streams; no filesystem APIs beyond standard fd-based I/O.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/html.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/jis.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/jis.h

This header contains macro utilities for Japanese character-set conversion between JIS X 0208 coordinate bytes and Microsoft Shift-JIS byte pairs.

Key contents:
- `J2S(_h, _l)` transforms valid JIS X 0208 high/low bytes into Shift-JIS bytes.
- `S2J(_h, _l)` transforms valid Shift-JIS high/low bytes back into JIS X 0208 bytes.
- `ISJKANA(_b)` identifies JIS X 0201 halfwidth katakana bytes in `0xA0..0xDF`.
- `CANS2JH(_h)`, `CANS2JL(_l)`, and `CANS2J(_h, _l)` validate Shift-JIS lead/trail bytes usable for conversion.
- `CANJ2SB(_b)` and `CANJ2S(_h, _l)` validate JIS X 0208 graphic-set bytes in `0x21..0x7E`.

Important details:
- The conversion macros mutate their arguments in place; callers must pass modifiable byte variables, not expressions with side effects.
- The macros encode the Shift-JIS discontinuities around `0x7F` and `0xA0..0xDF`.
- `CANS2JH` excludes halfwidth-katakana bytes even though they are in the wider high-byte area.
- The comments document intended preconditions: `J2S` and `S2J` expect already validated input ranges.
- The macro style uses comma expressions and multi-statement blocks, matching old Plan 9 C conventions.

Filesystem relevance:
- Indirect: supports Japanese text conversion for file and stream contents handled by `tcs`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/jis.h -->