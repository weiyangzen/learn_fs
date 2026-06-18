# Group Research: group_1681_reactos_sources_windows_reactos_drivers_filesystems_ext2_src_nls_nl_b29db67eae4f

Scope: `Docs/research_subset_a.md`, specifically the listed ReactOS Ext2 NLS source files under `sources/windows/reactos/drivers/filesystems/ext2/src/nls`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp852.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp852.c

Purpose: Generated Linux-style NLS module for DOS/OEM code page 852, used for Central European filename character conversion in the ReactOS Ext2 driver copy.

Core structures and data:
- `charset2uni[256]` maps every CP852 byte to Unicode, with ASCII/control identity mappings, Central European Latin letters, box drawing, block elements, and spacing diacritics.
- Reverse lookup pages `page00`, `page01`, `page02`, and `page25` map Unicode pages 0x00, 0x01, 0x02, and 0x25 back to single CP852 bytes.
- `page_uni2charset[256]` dispatches Unicode high bytes to those reverse pages, leaving other pages unmapped.
- `charset2lower[256]` and `charset2upper[256]` implement byte-level case folding for ASCII plus CP852-specific Latin letters.

Important behavior:
- `uni2char()` splits a Unicode `wchar_t` into high/low bytes, selects a reverse page, emits one byte when the page entry is nonzero, returns `-ENAMETOOLONG` for no output room, and returns `-EINVAL` for unmapped Unicode.
- `char2uni()` directly indexes `charset2uni[*rawstring]`, rejects `0x0000`, and returns one consumed byte.
- The registered `struct nls_table` charset name is `"cp852"` with no alias.

Dependencies and interfaces:
- Uses Linux kernel/NLS headers and APIs: `struct nls_table`, `register_nls()`, `unregister_nls()`, `module_init`, `module_exit`, and `THIS_MODULE`.
- No external NLS backend, allocation, locks, filesystem I/O, or mutable runtime state beyond NLS registration.

Design notes and risks:
- The zero sentinel means Unicode NUL and byte 0x00 are not converted successfully by the callbacks.
- `char2uni()` does not check `boundlen`; correctness depends on the NLS caller passing at least one byte.
- The generated arrays are positional and not declared `const`, so accidental edits or writes can silently corrupt filename conversion and case folding.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp852.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp855.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp855.c

Purpose: Generated NLS module for DOS/OEM code page 855, a Cyrillic code page, wired into the ReactOS Ext2 driver's Linux-style NLS interface.

Core structures and data:
- `charset2uni[256]` maps ASCII/control bytes directly and maps high bytes to Cyrillic letters, box drawing, block elements, `U+2116` numero sign, and selected punctuation.
- Reverse pages `page00`, `page04`, `page21`, and `page25` support Unicode-to-CP855 lookup for Latin/punctuation, Cyrillic, numero sign, and drawing/block glyphs.
- `page_uni2charset[256]` points only those Unicode high pages at populated reverse arrays.
- `charset2lower` and `charset2upper` encode CP855's alternating Cyrillic case pairs plus ASCII case folding.

Important behavior:
- `uni2char()` performs exact one-byte reverse mapping through `page_uni2charset`; unmapped entries and zero results return `-EINVAL`.
- `char2uni()` consumes one byte and rejects `charset2uni` entries equal to zero.
- The module registers charset `"cp855"` with no alias.

Dependencies and interfaces:
- Standard Linux NLS module pattern using `<linux/nls.h>` and errno-style negative returns.
- Module lifecycle is limited to `register_nls(&table)` and `unregister_nls(&table)`.

Design notes and risks:
- CP855's case tables are data-critical because many Cyrillic upper/lower byte pairs are not contiguous in simple ASCII style.
- Reverse mapping depends on exact page dispatch; a wrong `page04` or `page21` pointer would reject or misencode whole Unicode ranges.
- No normalization or transliteration is attempted; only exact Unicode mappings are accepted.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp855.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp857.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp857.c

Purpose: Generated NLS module for DOS/OEM code page 857, covering Turkish-oriented Latin characters for Ext2 filename conversion.

Core structures and data:
- `charset2uni[256]` includes Latin-1-like accented letters, Turkish `U+0130`, `U+0131`, `U+011E`, `U+011F`, `U+015E`, `U+015F`, box drawing, and several explicit `0x0000` undefined slots.
- Reverse pages `page00`, `page01`, and `page25` map supported Unicode back to CP857.
- `charset2lower` and `charset2upper` include ASCII and Turkish-specific case pairs, with zeros preserved for undefined bytes.

Important behavior:
- `uni2char()` emits exactly one byte for exact mappings and fails with `-EINVAL` for unmapped Unicode.
- `char2uni()` rejects undefined byte positions because their forward table entries are `0x0000`.
- The registered charset name is `"cp857"` with no alias.

Dependencies and interfaces:
- Self-contained `struct nls_table` module using the same Linux NLS callback contract as the neighboring generated codepage files.
- No runtime dependency on another charset.

Design notes and risks:
- Turkish dotted/dotless I behavior is represented only by byte lookup tables, not by locale-aware Unicode case logic.
- Undefined byte slots affect both conversion and case tables; consumers using casefold arrays directly may see zero for those positions.
- The single-byte callback skeleton cannot encode Unicode NUL because zero is the unmapped sentinel.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp857.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp860.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp860.c

Purpose: Generated NLS module for DOS/OEM code page 860, primarily Portuguese, with standard DOS graphics and mathematical symbols.

Core structures and data:
- `charset2uni[256]` maps high bytes to Portuguese accented Latin letters, DOS line/box drawing characters, Greek/math symbols, block glyphs, and punctuation such as `U+20A7`.
- Reverse pages include `page00`, `page03`, `page20`, `page22`, `page23`, and `page25`.
- `page_uni2charset[256]` dispatches Latin/punctuation, Greek, superscript/currency, math, technical symbol, and box/block pages.
- Case tables fold ASCII and the CP860 Latin accented pairs; Greek/math/box glyphs mostly remain identity or zero when undefined.

Important behavior:
- `uni2char()` performs exact one-byte reverse lookup through the page dispatch table.
- `char2uni()` indexes `charset2uni` and rejects `0x0000`.
- The NLS table is registered as `"cp860"` with no alias.

Dependencies and interfaces:
- Standard generated Linux NLS module shape; only NLS registration/unregistration touches global framework state.
- No Ext2 metadata logic appears in this file; it supplies conversion callbacks consumed by filesystem code elsewhere.

Design notes and risks:
- CP860's reverse mapping spans more Unicode pages than many Latin codepages because of Greek and math symbols inherited from DOS glyph sets.
- Case folding is byte-oriented and cannot implement Unicode normalization or decomposition.
- Generated table drift can make filenames fail to round-trip between on-disk bytes and Unicode names.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp860.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp861.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp861.c

Purpose: Generated NLS module for DOS/OEM code page 861, supporting Icelandic-specific characters plus the common DOS graphics repertoire.

Core structures and data:
- `charset2uni[256]` maps high bytes to Icelandic/Nordic Latin letters including eth/thorn variants, accented vowels, DOS line drawing, block elements, Greek/math symbols, and `U+0192`.
- Reverse pages `page00`, `page01`, `page03`, `page20`, `page22`, `page23`, and `page25` cover Latin extended, Greek, math, technical, and graphics mappings.
- `charset2lower` and `charset2upper` encode Icelandic case relationships in CP861 byte space.

Important behavior:
- `uni2char()` rejects absent reverse pages and zero entries; successful conversions always emit one byte.
- `char2uni()` returns one byte consumed for valid mappings and rejects zero-valued entries.
- The module registers charset `"cp861"` with no alias.

Dependencies and interfaces:
- Uses the common Linux kernel NLS table interface and module macros.
- No external conversion backend is loaded.

Design notes and risks:
- Icelandic letters such as eth and thorn are table-driven; incorrect case tables can break case-insensitive filename comparisons.
- The reverse dispatch includes sparse pages, so omitted initializer entries rely on C zero-fill.
- `char2uni()` lacks an internal input-length guard and assumes its caller provides a valid byte pointer.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp861.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp862.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp862.c

Purpose: Generated NLS module for DOS/OEM code page 862, used for Hebrew byte-to-Unicode conversion with DOS graphics symbols.

Core structures and data:
- `charset2uni[256]` maps bytes `0x80-0x9a` to Hebrew letters `U+05D0..U+05EA`, then maps remaining high bytes to Latin punctuation, currency, box drawing, Greek/math symbols, and block glyphs.
- Reverse pages include `page00`, `page01`, `page03`, `page05`, `page20`, `page22`, `page23`, and `page25`.
- `page05` is the Hebrew reverse page mapping Unicode Hebrew letters back to CP862 bytes.
- Case tables are mostly ASCII/symbol identity; Hebrew has no upper/lower case folding.

Important behavior:
- `uni2char()` supports exact one-byte mappings through the reverse page table; no shaping, bidi processing, or normalization is performed.
- `char2uni()` maps one byte and rejects zero entries.
- The module registers `"cp862"` with no alias.

Dependencies and interfaces:
- Standard self-contained Linux NLS table, using `register_nls()` and `unregister_nls()` for lifecycle.
- No Hebrew-specific runtime library dependency exists; all behavior is static table lookup.

Design notes and risks:
- Hebrew text direction and presentation are outside this module; it only maps byte values to Unicode code points.
- Sparse reverse pages and zero sentinels make undefined bytes and Unicode NUL invalid.
- Filename equality behavior depends on the byte-level case tables, which intentionally do not fold Hebrew letters.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp862.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp863.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp863.c

Purpose: Generated NLS module for DOS/OEM code page 863, a Canadian French code page with DOS graphics and symbols.

Core structures and data:
- `charset2uni[256]` maps high bytes to French accented letters, currency/punctuation, `U+2017`, box drawing, block elements, and Greek/math symbols.
- Reverse lookup pages are `page00`, `page01`, `page03`, `page20`, `page22`, `page23`, and `page25`.
- `charset2lower` and `charset2upper` fold ASCII plus the CP863 Latin accented letters.

Important behavior:
- `uni2char()` returns one encoded byte for exact reverse mappings and `-EINVAL` for unmapped code points.
- `char2uni()` consumes one byte and rejects `0x0000` table values.
- The registered charset is `"cp863"` with no alias.

Dependencies and interfaces:
- Implements the common Linux `struct nls_table` callback surface.
- No mutable conversion state exists after module registration.

Design notes and risks:
- Some CP863 byte values map to symbols rather than Latin letters, so reverse table page coverage extends into Greek/math and box drawing Unicode pages.
- The byte-level case tables are not equivalent to Unicode locale-aware folding.
- Generated table order is critical; a shifted initializer would corrupt many mappings without changing control flow.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp863.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp864.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp864.c

Purpose: Generated NLS module for DOS/OEM code page 864, covering Arabic-oriented byte mappings, Arabic presentation forms, Arabic-Indic digits, punctuation, and DOS graphics.

Core structures and data:
- `charset2uni[256]` maps ASCII/control bytes, selected DOS graphics, Arabic punctuation (`U+060C`, `U+061B`, `U+061F`), Arabic-Indic digits `U+0660..U+0669`, tatweel/shadda, and many Arabic presentation forms in the `U+FE7D..U+FEFC` range.
- Reverse pages include `page00`, `page03`, `page06`, `page22`, `page25`, and `pagefe`.
- `page06` maps Arabic punctuation/digits/marks back to CP864.
- `pagefe` maps Arabic presentation forms back to CP864 byte values.
- Case tables are mostly identity/zero because Arabic has no upper/lower case; ASCII still folds normally.

Important behavior:
- `uni2char()` is exact and one-byte only; it does not compose/decompose Arabic presentation forms.
- `char2uni()` rejects undefined byte positions where the forward table stores `0x0000`.
- The registered charset is `"cp864"` with no alias.

Dependencies and interfaces:
- Self-contained Linux-style NLS table module.
- No shaping engine, bidi engine, or external charset backend is involved.

Design notes and risks:
- CP864 maps many bytes to Arabic presentation-form code points rather than base Arabic letters, so normalization differences can make Unicode inputs unencodable.
- Several forward table positions are undefined; those bytes fail conversion instead of substituting replacement characters.
- The reverse dispatch has a long mostly-null `page_uni2charset[256]` with a late `pagefe` entry; preserving high-page alignment is essential.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp864.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp865.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp865.c

Purpose: Generated NLS module for DOS/OEM code page 865, a Nordic code page used for single-byte filename conversion.

Core structures and data:
- `charset2uni[256]` maps high bytes to Scandinavian/Nordic Latin characters, currency/punctuation, box drawing, block glyphs, Greek/math symbols, and common DOS symbols.
- Reverse pages are `page00`, `page01`, `page03`, `page20`, `page22`, `page23`, and `page25`.
- `charset2lower` and `charset2upper` provide ASCII and Nordic accented-letter byte folding.

Important behavior:
- `uni2char()` emits one byte only when the Unicode page and low-byte entry map exactly to CP865.
- `char2uni()` consumes one byte and rejects zero-valued mappings.
- The NLS table registers charset `"cp865"` with no alias.

Dependencies and interfaces:
- Standard generated Linux NLS module with module init/exit wrappers.
- No external NLS dependency or filesystem-specific logic appears in the file.

Design notes and risks:
- CP865 differs subtly from neighboring DOS code pages in a few punctuation/letter slots; treating it as generic CP437-style graphics would break round trips.
- Sparse reverse pages use zero as the unmapped sentinel.
- Case-insensitive behavior is only as accurate as the generated byte-level case tables.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp865.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp866.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp866.c

Purpose: Generated NLS module for DOS/OEM code page 866, the common Russian Cyrillic DOS code page.

Core structures and data:
- `charset2uni[256]` maps `0x80-0xaf` to uppercase and lowercase Cyrillic ranges, keeps DOS line drawing in `0xb0-0xdf`, maps `0xe0-0xef` to remaining lowercase Cyrillic, and maps `0xf0-0xff` to Cyrillic variants and symbols.
- Reverse pages `page00`, `page04`, `page21`, `page22`, and `page25` support Latin/symbol, Cyrillic, numero sign, math, and box/block reverse mappings.
- `charset2lower` and `charset2upper` fold CP866 Cyrillic byte ranges as well as ASCII.

Important behavior:
- `uni2char()` returns a single CP866 byte for exact mappings and `-EINVAL` otherwise.
- `char2uni()` rejects byte 0x00 through the `0x0000` sentinel convention.
- The charset registers as `"cp866"` with no alias.

Dependencies and interfaces:
- Uses only Linux kernel NLS/module APIs.
- No runtime allocation or per-mount state.

Design notes and risks:
- CP866's Cyrillic mappings are comparatively regular, but the surrounding graphics and symbol pages still require exact table preservation.
- Case folding maps whole Cyrillic byte ranges, so table corruption can affect case-insensitive lookup semantics.
- As with the other generated modules, Unicode normalization and replacement fallback are absent.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp866.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp869.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp869.c

Purpose: Generated NLS module for DOS/OEM code page 869, a Greek code page.

Core structures and data:
- `charset2uni[256]` includes undefined high-byte holes, Greek capitals and lowercase letters, tonos/dialytika variants, punctuation, box drawing, and block characters.
- Reverse pages `page00`, `page03`, `page20`, and `page25` map Latin/punctuation, Greek, punctuation dashes/quotes, and drawing/block glyphs back to CP869.
- `charset2lower` and `charset2upper` encode Greek byte-level case pairs plus ASCII folding.

Important behavior:
- `uni2char()` accepts only exact Unicode-to-byte mappings; unmapped Greek forms or decomposed accents fail.
- `char2uni()` rejects bytes whose forward table entry is zero, including several undefined bytes in the `0x80` range.
- The module registers charset `"cp869"` with no alias.

Dependencies and interfaces:
- Standard Linux NLS callback implementation and module lifecycle.
- No external Greek normalization or locale handling is involved.

Design notes and risks:
- Greek precomposed accented forms are table entries; decomposed Unicode sequences do not round-trip through this module.
- Undefined high-byte positions must remain zero to avoid accepting invalid on-disk filename bytes.
- Case folding is byte-oriented and generated, not full Unicode case folding.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp869.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp874.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp874.c

Purpose: Generated NLS module for Windows/DOS code page 874, Thai, with a `tis-620` alias.

Core structures and data:
- `charset2uni[256]` maps ASCII/control bytes, selected punctuation in the `0x80-0x9f` range, Thai letters and marks `U+0E01..U+0E5B`, Thai baht sign `U+0E3F`, and undefined zero slots.
- Reverse pages `page00`, `page0e`, and `page20` map Latin/punctuation, Thai, and punctuation marks back to CP874.
- `charset2lower` and `charset2upper` mostly preserve bytes because Thai has no case; ASCII folding remains present.
- `table.alias` is `"tis-620"`, and `MODULE_ALIAS_NLS(tis-620)` advertises the alias.

Important behavior:
- `uni2char()` emits a single byte for exact CP874/TIS-620-compatible mappings.
- `char2uni()` rejects undefined bytes and NUL through zero-valued `charset2uni` entries.
- Module init registers charset `"cp874"`.

Dependencies and interfaces:
- Self-contained Linux NLS table with standard module registration.
- No Thai shaping, collation, or normalization support appears in the file.

Design notes and risks:
- The alias makes CP874 available to consumers requesting `tis-620`, but the table also includes Windows punctuation mappings outside strict simple Thai letter ranges.
- Undefined byte slots around C1 controls and Thai gaps intentionally fail.
- Case tables are not meaningful for Thai letters beyond identity mapping.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp874.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_euc-jp.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_euc-jp.c

Purpose: Linux-style NLS converter for Japanese EUC-JP in the ReactOS Ext2 source tree. Unlike the single-byte generated table files, this module loads the existing `cp932` NLS table and translates between Unicode and CP932/Shift-JIS first, then between Shift-JIS and EUC-JP.

Core structures and data:
- `static struct nls_table *p_nls` stores the loaded `cp932` backend.
- Macros classify Shift-JIS low bytes, JIS X 0208, JIS X 0201 kana, user-defined character ranges, IBM extended ranges, and NEC/IBM extension ranges.
- Macros classify EUC bytes, SS2 kana sequences, SS3 G3 sequences, and low/high user-defined ranges.
- `MAP_SJIS2EUC` and `MAP_EUC2SJIS` implement arithmetic conversion between the normal JIS X 0208 / UDC Shift-JIS and EUC coordinate systems.
- `sjisibm2euc_map` maps CP932 IBM extended byte pairs to EUC-JP two- or three-byte sequences.
- `euc2sjisibm_jisx0212_map` and `euc2sjisibm_g3upper_map` provide reverse lookup for IBM extended characters that cannot be converted by the simple arithmetic macros.

Important helper behavior:
- `sjisibm2euc()` converts IBM Shift-JIS extensions to EUC. Some entries become two-byte JIS X 0208 EUC sequences; others are emitted as SS3 plus two bytes.
- `euc2sjisibm_jisx0212()` binary-searches a sorted EUC-to-IBM map and returns a CP932 pair when found.
- `euc2sjisibm_g3upper()` maps upper G3 EUC extension blocks to CP932 extension pairs by computed index.
- `euc2sjisibm()` tries G3 upper mapping first, then the JIS X 0212 map.
- `sjisnec2sjisibm()` normalizes NEC/IBM Shift-JIS extension ranges into IBM extension byte pairs before EUC conversion.

Important conversion behavior:
- `uni2char()` first calls `p_nls->uni2char()` to encode Unicode as CP932/Shift-JIS.
- One-byte CP932 halfwidth kana `0xA1..0xDF` is rewritten as EUC SS2 followed by the kana byte, requiring two output bytes.
- Two-byte CP932 is converted by category: NEC/IBM normalization, UDC low arithmetic conversion, UDC high SS3 conversion, IBM extension map conversion, or normal JIS X 0208 arithmetic conversion.
- Invalid or unsupported CP932 results return `-EINVAL`; insufficient output room returns `-ENAMETOOLONG`.
- `char2uni()` parses EUC-JP into a temporary two-byte Shift-JIS buffer, then delegates Unicode conversion to `p_nls->char2uni()`.
- `char2uni()` handles ASCII/JIS X 0201 romaji as one byte, SS2 kana as two bytes, normal JIS X 0208 as two bytes, low UDC as two bytes, and SS3 high UDC/IBM extensions as three bytes.
- Unsupported JIS X 0212 or invalid SS3 sequences return `-EINVAL`; a commented-out GETA fallback is intentionally disabled.

Dependencies and interfaces:
- `init_nls_euc_jp()` loads `cp932` with `load_nls("cp932")`, copies its upper/lower case tables into this module's `table`, and registers charset `"euc-jp"`.
- `exit_nls_euc_jp()` unregisters the EUC-JP table and unloads the CP932 backend.
- The module has no alias and no standalone Unicode mapping tables for general characters; CP932 is a hard runtime dependency.

Design notes and risks:
- Failure to load `cp932` makes initialization return `-EINVAL`, so EUC-JP availability depends on the CP932 NLS module.
- The mapping helpers are dense and byte-arithmetic-heavy. Range macro correctness is critical because helper functions assume callers have classified bytes before indexing generated maps.
- `sjisibm2euc()` computes an index from Shift-JIS bytes; callers must only pass bytes satisfying `IS_SJIS_IBM`.
- `char2uni()` returns `-EINVAL` for truncated multibyte EUC input, while the single-byte generated modules generally have no comparable input-length checks.
- The public case tables are borrowed from CP932, so case behavior follows the backend rather than a separate EUC-specific table.
- Correctness is filename-critical: errors can make Japanese names fail lookup, fail round trip, or collide after conversion.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_euc-jp.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-1.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-1.c

Purpose: Generated NLS module for ISO 8859-1 / Latin-1, used as a one-byte Western European charset converter.

Core structures and data:
- `charset2uni[256]` is a direct byte-to-Unicode mapping from `U+0000` through `U+00FF`.
- `page00[256]` maps Unicode page 0 back to the same byte values.
- `page_uni2charset[256]` only points Unicode high byte 0 to `page00`; all other pages are zero-filled and unmapped.
- `charset2lower` and `charset2upper` fold ASCII and Latin-1 case pairs.

Important behavior:
- `uni2char()` emits one byte for nonzero page-0 reverse entries and returns `-EINVAL` for all other Unicode pages.
- `char2uni()` maps one input byte but rejects `0x0000`.
- The module registers charset `"iso8859-1"` with no alias.

Dependencies and interfaces:
- Standard Linux `struct nls_table` module with register/unregister lifecycle.
- No external dependencies or dynamic state.

Design notes and risks:
- Although ISO 8859-1 maps byte 0 to Unicode NUL in the data table, the callback treats zero as invalid because zero is also the unmapped sentinel.
- This file is low-complexity compared with other codepages, but the case tables still affect case-insensitive filename behavior.
- No Unicode normalization or fallback mapping is performed.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-1.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-13.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-13.c

Purpose: NLS module for ISO 8859-13 / Latin-7, a Baltic charset.

Core structures and data:
- `charset2uni[256]` maps ASCII/control bytes directly and maps high bytes to Baltic Latin letters, Latin punctuation, quotes, and `U+2019`.
- Reverse pages `page00`, `page01`, and `page20` map Unicode pages 0x00, 0x01, and 0x20 back to ISO 8859-13 bytes.
- `charset2lower` and `charset2upper` include Baltic extended-letter case pairs plus ASCII folding.

Important behavior:
- `uni2char()` performs exact one-byte reverse lookup and rejects unmapped Unicode.
- `char2uni()` consumes one byte and rejects zero-valued mappings.
- The registered charset is `"iso8859-13"` with no alias.

Dependencies and interfaces:
- Self-contained Linux NLS table implementation.
- Module init/exit only register and unregister the static table.

Design notes and risks:
- Several typographic punctuation characters live in Unicode page 0x20, so reverse dispatch must preserve `page20`.
- Exact mapping excludes decomposed diacritic forms.
- Zero sentinel behavior prevents Unicode NUL conversion.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-13.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-14.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-14.c

Purpose: Generated NLS module for ISO 8859-14 / Latin-8, a Celtic charset, with file attribution to Rhys Jones / Swansea University Computer Society.

Core structures and data:
- `charset2uni[256]` maps high bytes to Celtic/Welsh-related Latin letters, including dotted consonants, W/Y variants, and Latin Extended Additional characters.
- Reverse pages `page00`, `page01`, and `page1e` map Unicode page 0, Latin Extended-A, and Latin Extended Additional back to ISO 8859-14.
- `page_uni2charset[256]` includes the high-page `page1e` entry for `U+1E00..U+1EFF`.
- `charset2lower` and `charset2upper` fold ASCII plus charset-specific extended letters.

Important behavior:
- `uni2char()` emits one exact one-byte ISO 8859-14 value or fails with `-EINVAL`.
- `char2uni()` rejects the zero sentinel and returns one consumed byte otherwise.
- The registered charset name is `"iso8859-14"` with no alias.

Dependencies and interfaces:
- Standard generated Linux NLS module using `register_nls()` and `unregister_nls()`.
- No external backend or mutable runtime conversion state.

Design notes and risks:
- The `page1e` reverse table is essential for dotted-letter mappings and must stay aligned with Unicode high byte 0x1E.
- The file is table-dominated; all semantic conversion behavior is exact lookup, not normalization.
- Case-folding correctness depends entirely on the generated upper/lower byte tables.

<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-14.c -->