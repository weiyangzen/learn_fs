# Group Research: group_1040_linux_stable_sources_os_linux_linux_stable_fs_nls_nls_euc_jp_c_sour_1bbb113bf68a

Scope: `Docs/research_subset_a.md`, specifically the listed `sources/os/linux/linux-stable` NLS and fsnotify files. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_euc-jp.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_euc-jp.c

Purpose: Linux NLS module for Japanese EUC-JP. Unlike most single-byte NLS table files, this module is a converter layered on top of the existing `cp932` NLS implementation, translating between Unicode and Shift-JIS/CP932 first and then between Shift-JIS and EUC-JP.

Core structures and data:
- `static struct nls_table *p_nls` holds the loaded `cp932` backend.
- Macros classify Shift-JIS byte ranges: JIS X 0208, JIS X 0201 kana, user-defined character ranges, IBM extended ranges, and NEC/IBM extension ranges.
- Macros classify EUC-JP byte sequences: normal EUC bytes, SS2 kana, SS3 G3 block, and user-defined ranges.
- `sjisibm2euc_map`, `euc2sjisibm_jisx0212_map`, and `euc2sjisibm_g3upper_map` encode IBM extended character conversions that are not expressible by the simple arithmetic SJIS/EUC transforms.

Important behavior:
- `uni2char()` delegates Unicode-to-byte conversion to `cp932`, then rewrites returned Shift-JIS bytes into EUC-JP. It handles one-byte kana by adding SS2, two-byte JIS X 0208 arithmetic conversion, UDC low/high ranges, IBM extensions, and NEC/IBM extension normalization.
- `char2uni()` parses EUC-JP input into a temporary Shift-JIS sequence and delegates final byte-to-Unicode conversion to `cp932`. It rejects unsupported JIS X 0212 or invalid EUC forms with `-EINVAL`.
- SS3-based high UDC and IBM extended sequences may consume or emit 3 EUC bytes, so both conversion directions include explicit bound checks.
- `init_nls_euc_jp()` loads `cp932`, copies its upper/lower tables into the public `nls_table`, then registers charset `"euc-jp"`.
- `exit_nls_euc_jp()` unregisters the table and unloads `cp932`.

Dependencies and interfaces:
- Implements the kernel `struct nls_table` callbacks `uni2char` and `char2uni`.
- Depends on `load_nls("cp932")`; failure to load that charset makes module init return `-EINVAL`.
- Uses Linux errno semantics: `-ENAMETOOLONG` for output buffer exhaustion and `-EINVAL` for invalid/unrepresentable encodings.

Design notes and risks:
- The conversion code is byte-arithmetic-heavy and relies on static table sizes and range macros matching the CP932/EUC mapping assumptions.
- `sjisibm2euc()` indexes into `sjisibm2euc_map` after the caller classifies the bytes as IBM Shift-JIS; callers must preserve that precondition.
- Unsupported EUC JIS X 0212 characters deliberately fail instead of substituting a GETA marker, as shown by the commented-out fallback in `char2uni()`.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_euc-jp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-1.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-1.c

Purpose: Generated Linux NLS module for ISO 8859-1 / Latin-1, described as Western European Languages.

Core structures and data:
- `charset2uni[256]` maps every byte value to the identical Unicode code point from U+0000 through U+00FF.
- `page00[256]` maps Unicode page 0 back to the identical byte values.
- `page_uni2charset[256]` only points page 0 at `page00`; all other pages are unmapped.
- `charset2lower[256]` and `charset2upper[256]` implement ASCII and Latin-1 case folding.

Important behavior:
- `uni2char()` rejects zero-length output buffers with `-ENAMETOOLONG`, looks up the Unicode high byte as a page selector, and emits exactly one byte for mapped nonzero entries.
- `char2uni()` maps one input byte through `charset2uni` and rejects byte `0x00` because the table value is `0x0000`.
- The module registers charset `"iso8859-1"` with both case tables.

Dependencies and interfaces:
- Standard `struct nls_table` implementation; no external NLS backend is loaded.
- Module init and exit are simple `register_nls()` / `unregister_nls()` wrappers.

Design notes and risks:
- The zero-entry-as-unmapped convention means NUL cannot be converted by `char2uni()` or `uni2char()` even though the mapping table contains it.
- Because Latin-1 is a direct byte-to-Unicode mapping for nonzero bytes, this file is mostly table data and is low in control-flow complexity.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-13.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-13.c

Purpose: Generated Linux NLS module for ISO 8859-13 / Latin-7, described as Baltic.

Core structures and data:
- `charset2uni[256]` maps bytes to Unicode, with Baltic-specific Latin extended code points and punctuation such as U+201C/U+201D/U+201E/U+2019.
- Reverse maps are split across `page00`, `page01`, and `page20`, selected through `page_uni2charset`.
- `charset2lower` and `charset2upper` include case conversion for the ISO 8859-13 extended letters in addition to ASCII.

Important behavior:
- `uni2char()` maps exact Unicode characters back to one-byte ISO 8859-13 values and returns `-EINVAL` when the page or code point is not represented.
- `char2uni()` consumes one byte and rejects table entries equal to zero.
- The registered charset name is `"iso8859-13"`.

Dependencies and interfaces:
- Standard generated NLS table module using `linux/nls.h`.
- No runtime dependencies beyond NLS core registration.

Design notes and risks:
- Several Unicode punctuation mappings live outside page 0/1 and are handled via `page20`; additions must preserve the sparse page table pattern.
- The exact-mapping rule excludes decomposed or compatibility-equivalent Unicode forms.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-13.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-14.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-14.c

Purpose: Generated Linux NLS module for ISO 8859-14 / Latin-8, described as Celtic.

Core structures and data:
- `charset2uni[256]` maps ISO 8859-14 bytes to Unicode, including Welsh and Celtic-related letters such as dotted consonants and W/Y variants.
- Reverse maps include `page00`, `page01`, and `page1e` for Latin Extended Additional characters.
- `page_uni2charset[256]` references page 0, page 1, and page 0x1e while leaving other pages unmapped.
- Case tables cover ASCII and the charset-specific extended letters.

Important behavior:
- `uni2char()` emits one byte for exact mappings only and rejects unmapped Unicode with `-EINVAL`.
- `char2uni()` returns one consumed byte for mapped values and rejects zero-valued mappings.
- The registered charset name is `"iso8859-14"`.

Dependencies and interfaces:
- Standard `nls_table` module with no subordinate charset.
- Module lifecycle is only `register_nls()` and `unregister_nls()`.

Design notes and risks:
- The file carries historical attribution to Rhys Jones / Swansea University Computer Society and a Unicode source note.
- Sparse reverse mappings across page 0x1e make this less trivial than Latin-1, but the conversion logic remains the common generated one-byte pattern.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-14.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-15.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-15.c

Purpose: Generated Linux NLS module for ISO 8859-15 / Latin-9, described as Western European Languages with Euro.

Core structures and data:
- `charset2uni[256]` resembles Latin-1 but replaces selected positions with Euro, OE/oe, S/s caron, Z/z caron, and Y diaeresis mappings.
- Reverse mappings are in `page00`, `page01`, and `page20`.
- Case tables include the extended Latin-9 letters and ASCII case conversion.

Important behavior:
- `uni2char()` performs page-based exact reverse lookup and emits one byte.
- `char2uni()` maps one byte to Unicode and rejects zero-valued entries.
- The registered charset name is `"iso8859-15"`.

Dependencies and interfaces:
- Standard `struct nls_table` callbacks and module registration.
- No external charset backend.

Design notes and risks:
- Euro sign U+20AC is represented through the sparse page 0x20 reverse map.
- The implementation intentionally does no normalization, transliteration, or fallback substitution.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-15.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-2.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-2.c

Purpose: Generated Linux NLS module for ISO 8859-2 / Latin-2, described as Slavic/Central European Languages.

Core structures and data:
- `charset2uni[256]` maps bytes to Latin Extended-A letters and diacritics used by Central European languages.
- Reverse maps include `page00`, `page01`, and `page02`, because exact mappings include spacing diacritics in Unicode page 2.
- `charset2lower` and `charset2upper` encode the charset-specific case pairs.

Important behavior:
- `uni2char()` performs exact page lookup and returns one output byte or an errno.
- `char2uni()` consumes one byte and rejects zero-valued mappings.
- The registered charset name is `"iso8859-2"`.

Dependencies and interfaces:
- Self-contained NLS table module using generated lookup arrays.
- Module init/exit only register and unregister the table.

Design notes and risks:
- Reverse mapping includes `0xff` for U+02D9, showing that the lookup arrays may use byte `0xff` as a valid result, while `0x00` is the unmapped sentinel.
- The common conversion helper cannot encode Unicode NUL.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-3.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-3.c

Purpose: Generated Linux NLS module for ISO 8859-3 / Latin-3, described as Esperanto, Galician, Maltese, and Turkish.

Core structures and data:
- `charset2uni[256]` maps ISO 8859-3 bytes to Unicode and has explicit `0x0000` gaps for undefined byte positions.
- Reverse maps include `page00`, `page01`, and `page02`.
- Case conversion tables include defined Latin-3 case pairs and zeros for undefined byte positions.

Important behavior:
- `uni2char()` emits one byte for exact mapped Unicode values.
- `char2uni()` rejects bytes whose `charset2uni` entry is `0x0000`, including undefined bytes and NUL.
- The registered charset name is `"iso8859-3"`.

Dependencies and interfaces:
- Standard NLS registration with self-contained generated tables.

Design notes and risks:
- This charset has more undefined byte slots than Latin-1/2; callers should expect `-EINVAL` for those bytes.
- Lower/upper tables preserve undefined slots as zero, which can matter for consumers using case tables directly.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-4.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-4.c

Purpose: Generated Linux NLS module for ISO 8859-4 / Latin-4, described as old Baltic charset.

Core structures and data:
- `charset2uni[256]` covers Baltic and Nordic Latin extended letters.
- Reverse maps include `page00`, `page01`, and `page02`.
- `charset2lower` and `charset2upper` provide one-byte case transforms for the charset.

Important behavior:
- `uni2char()` maps exact Unicode code points back to one byte using `page_uni2charset`.
- `char2uni()` returns one-byte consumption for mapped entries and `-EINVAL` for zero mappings.
- The registered charset name is `"iso8859-4"`.

Dependencies and interfaces:
- Self-contained NLS table, no runtime-loaded backend.

Design notes and risks:
- Like ISO 8859-2, some reverse mappings for spacing diacritics live on Unicode page 2.
- The file has generated-table complexity only; no multibyte parsing or stateful conversion exists.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-5.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-5.c

Purpose: Generated Linux NLS module for ISO 8859-5, described as Cyrillic.

Core structures and data:
- `charset2uni[256]` maps byte range `0xa1` onward to Cyrillic and related symbols, including U+2116.
- Reverse maps include `page00`, `page04`, and `page21`.
- Case tables map Cyrillic uppercase/lowercase byte ranges and preserve nonletters.

Important behavior:
- `uni2char()` uses exact reverse lookup and emits one byte.
- `char2uni()` consumes one byte and rejects zero mappings.
- The registered charset name is `"iso8859-5"`.

Dependencies and interfaces:
- Standard generated NLS table module.

Design notes and risks:
- U+2116 maps through page 0x21 to byte `0xf0`.
- Cyrillic case folding is byte-table-based, not Unicode-general; it only covers characters representable in the charset.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-6.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-6.c

Purpose: Generated Linux NLS module for ISO 8859-6, described as Arabic.

Core structures and data:
- `charset2uni[256]` maps Arabic punctuation, letters, and Arabic-Indic digits. Notably byte `0x30` through `0x39` map to U+0660 through U+0669 rather than ASCII digits.
- Reverse maps include `page00` and `page06`.
- Case conversion tables are mostly identity or zero because Arabic has no upper/lowercase distinction in this charset.

Important behavior:
- `uni2char()` exact-maps Unicode page 0 and 6 characters to one byte.
- `char2uni()` rejects undefined slots and NUL.
- The registered charset name is `"iso8859-6"`.

Dependencies and interfaces:
- Self-contained generated NLS table.

Design notes and risks:
- The ASCII digit byte range is intentionally mapped to Arabic-Indic Unicode digits by the table; consumers expecting ASCII digits from bytes `0x30`-`0x39` would be surprised.
- Many high-byte positions are undefined and return `-EINVAL`.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-7.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-7.c

Purpose: Generated Linux NLS module for ISO 8859-7, described as Modern Greek.

Core structures and data:
- `charset2uni[256]` maps Greek letters, Greek tonos/dialytika characters, and selected punctuation.
- Reverse maps include `page00`, `page02`, `page03`, and `page20`.
- Case tables map Greek uppercase/lowercase byte values and preserve nonletters.

Important behavior:
- `uni2char()` emits one byte for exactly represented Unicode code points and rejects unmapped inputs.
- `char2uni()` maps one byte to Unicode and rejects zero-valued table entries.
- The registered charset name is `"iso8859-7"`.

Dependencies and interfaces:
- Standard generated NLS implementation.

Design notes and risks:
- The file includes sparse reverse mappings for modifier letters and U+2015, so not all Greek-related Unicode input is accepted.
- Some Greek code points are undefined in the byte table; byte-to-Unicode can fail on those byte positions.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-7.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-9.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-9.c

Purpose: Generated Linux NLS module for ISO 8859-9 / Latin-5, described as Turkish.

Core structures and data:
- `charset2uni[256]` is close to ISO 8859-1 but replaces selected Icelandic positions with Turkish G/g breve, I dot/dotless, and S/s cedilla.
- Reverse mappings include `page00` and `page01`.
- Case tables include Turkish-specific byte case mappings such as dotted/dotless I behavior within the charset.

Important behavior:
- `uni2char()` exact-maps supported Unicode code points to one byte.
- `char2uni()` consumes one byte and rejects zero-valued mappings.
- The registered charset name is `"iso8859-9"`.

Dependencies and interfaces:
- Self-contained `nls_table` module.

Design notes and risks:
- The Turkish-specific letters are sparse page 1 mappings, not special-case code in the conversion functions.
- Case tables are byte-oriented and should not be assumed to implement locale-sensitive Unicode casing outside this charset.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_iso8859-9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_koi8-r.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_koi8-r.c

Purpose: Generated Linux NLS module for KOI8-R, described as Russian.

Core structures and data:
- `charset2uni[256]` maps ASCII, box drawing symbols, mathematical symbols, and Cyrillic letters.
- Reverse maps include `page00`, `page04`, `page22`, `page23`, and `page25`.
- Case tables provide KOI8-R byte-level Cyrillic casing and identity handling for graphics characters.

Important behavior:
- `uni2char()` performs exact Unicode-to-KOI8-R lookup and emits one byte.
- `char2uni()` maps one byte to Unicode and rejects zero-valued entries.
- The registered charset name is `"koi8-r"`.

Dependencies and interfaces:
- Self-contained generated NLS table.

Design notes and risks:
- KOI8-R includes many line drawing and block characters, which explains the larger reverse page coverage compared with ISO 8859 files.
- It uses the same zero sentinel pattern; Unicode NUL and unmapped graphics/code points are rejected.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_koi8-r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_koi8-ru.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_koi8-ru.c

Purpose: Linux NLS wrapper for KOI8-RU, described as Belarusian, implemented as a small delta on top of `koi8-u`.

Core structures and data:
- `static struct nls_table *p_nls` stores the loaded `koi8-u` backend.
- The public `nls_table` defines charset `"koi8-ru"` and custom `uni2char`/`char2uni` callbacks.
- Case tables are copied from the underlying `koi8-u` table at init time.

Important behavior:
- `uni2char()` checks the few Unicode values where KOI8-RU differs from KOI8-U. U+040E maps to byte `0xbe`, U+045E maps to `0xae`, and U+255D/U+256C return 0 in the special branch; other cases delegate to `koi8-u`.
- `char2uni()` has a suspicious-looking branch: when `(*rawstring & 0xef) != 0xae`, it returns U+040E or U+045E based on bit `0x10`; otherwise it delegates to `koi8-u`.
- `init_nls_koi8_ru()` loads `koi8-u`, inherits its case tables, and registers the wrapper.
- `exit_nls_koi8_ru()` unregisters and unloads the base charset.

Dependencies and interfaces:
- Requires the `koi8-u` NLS module to be loadable.
- Exposes normal `nls_table` callbacks to NLS core.

Design notes and risks:
- The file is intentionally tiny and relies on `koi8-u` for almost all behavior.
- The `char2uni()` condition differs from the comment's “two characters” wording; the current expression sends most bytes into the special mapping branch and only delegates for bytes matching the masked pattern. This should be treated carefully if audited or modified.
- Returning `0` from `uni2char()` for U+255D/U+256C is not the usual negative errno pattern used by generated modules.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_koi8-ru.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_koi8-u.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_koi8-u.c

Purpose: Generated Linux NLS module for KOI8-U, described as Ukrainian.

Core structures and data:
- `charset2uni[256]` maps ASCII, graphics characters, Cyrillic letters, and Ukrainian-specific letters such as Ukrainian Ye, I, Yi, and Ghe with upturn.
- Reverse maps include `page00`, `page04`, `page22`, `page23`, and `page25`.
- `charset2lower` and `charset2upper` implement KOI8-U byte-level case conversion.

Important behavior:
- `uni2char()` exact-maps Unicode code points through sparse reverse page tables.
- `char2uni()` returns one consumed byte for nonzero mappings and rejects zero entries.
- The registered charset name is `"koi8-u"`.

Dependencies and interfaces:
- Self-contained NLS table module; also serves as the runtime backend for `nls_koi8-ru.c`.

Design notes and risks:
- Like KOI8-R, it supports line/box drawing characters and mathematical symbols in addition to Cyrillic letters.
- Differences from KOI8-R are concentrated in the upper byte table around Ukrainian-specific Cyrillic and some graphics slots.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_koi8-u.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_ucs2_data.h -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_ucs2_data.h

Purpose: Header declaring shared UCS-2 uppercase conversion table data for NLS UCS-2 helpers.

Core structures and data:
- Defines `struct UniCaseRange` with `wchar_t start`, `wchar_t end`, and a signed offset `table`.
- Declares `NlsUniUpperTable[512]`, the base uppercase offset table.
- Declares `NlsUniUpperRange[]`, the range table used for Unicode pages beyond the base table.

Important behavior:
- This header contains no executable logic; it is a declaration boundary between `nls_ucs2_utils.c` and inline consumers in `nls_ucs2_utils.h`.

Dependencies and interfaces:
- Uses `wchar_t`; callers include this through `nls_ucs2_utils.h`.

Design notes and risks:
- The `table` pointer is non-const `signed char *` even though the exported range table points at static data; this matches existing usage but should be preserved carefully for ABI/source compatibility.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_ucs2_data.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_ucs2_utils.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_ucs2_utils.c

Purpose: Defines and exports compressed UCS-2 uppercase conversion tables shared by in-kernel Unicode/NLS users.

Core structures and data:
- `NlsUniUpperTable[512]` provides signed offsets for low Unicode code points, especially ASCII/Latin ranges.
- `UniCaseRangeU03a0`, `UniCaseRangeU0430`, `UniCaseRangeU0490`, `UniCaseRangeU1e00`, and `UniCaseRangeUff40` hold signed offsets for Greek, Cyrillic, extended Cyrillic, extended Latin/Greek, and fullwidth Latin.
- `NlsUniUpperRange[]` lists those ranges and terminates with a zeroed sentinel.

Important behavior:
- There are no conversion functions in this C file; logic lives in `nls_ucs2_utils.h`.
- The tables are exported with `EXPORT_SYMBOL_GPL` for use by other GPL-compatible kernel code.
- Module metadata identifies this as `"NLS UCS-2"` with GPL license.

Dependencies and interfaces:
- Includes `nls_ucs2_utils.h`, which in turn uses the declarations from `nls_ucs2_data.h`.
- Origin comments indicate code/data lineage from CIFS Unicode support.

Design notes and risks:
- The signed offset encoding is compact but fragile: consumers add the signed offset to the input code point.
- Range boundaries and table lengths must stay synchronized; the sentinel is how `UniToupper()` knows to stop.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_ucs2_utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_ucs2_utils.h -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_ucs2_utils.h

Purpose: Inline UCS-2 string utility and uppercase conversion helpers, originally derived from CIFS Unicode handling.

Core structures and definitions:
- Defines Windows private-use remappings for reserved filename characters: `UNI_ASTERISK`, `UNI_QUESTION`, `UNI_COLON`, `UNI_GRTRTHAN`, `UNI_LESSTHAN`, `UNI_PIPE`, and `UNI_SLASH`.
- Provides inline string functions: `UniStrcat`, `UniStrchr`, `UniStrcmp`, `UniStrcpy`, `UniStrlen`, `UniStrnlen`, `UniStrncat`, `UniStrncmp`, `UniStrncmp_le`, `UniStrncpy`, `UniStrncpy_le`, and `UniStrstr`.
- Provides `UniToupper()` and `UniStrupr()` unless `UNIUPR_NOUPPER` is defined.

Important behavior:
- The string helpers use `wchar_t` / `__le16` style UCS-2 code units and generally mirror C library semantics with explicit comments.
- Little-endian variants convert through `__le16_to_cpu()` / `le16_to_cpu()` / `cpu_to_le16()` where applicable.
- `UniToupper()` first uses `NlsUniUpperTable` for code points below the table size, then scans `NlsUniUpperRange[]` and applies the signed offset for matching ranges.
- `UniStrupr()` uppercases a little-endian UCS-2 string in place.

Dependencies and interfaces:
- Includes byteorder helpers, Linux types, `linux/nls.h`, `linux/unicode.h`, and `nls_ucs2_data.h`.
- Depends on exported table definitions from `nls_ucs2_utils.c`.

Design notes and risks:
- These are unsafe C-style string helpers: destination capacity is not tracked for concat/copy functions except by the explicit `n` variants.
- The functions operate on 16-bit-style code units and do not handle full Unicode scalar values or surrogate-pair semantics.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_ucs2_utils.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_utf8.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_utf8.c

Purpose: Linux NLS module exposing UTF-8 through the same `nls_table` interface as legacy charsets.

Core structures and data:
- `identity[256]` is initialized at module load and assigned as both `charset2lower` and `charset2upper`, meaning no byte-level case conversion is performed.
- The registered charset is `"utf8"`.

Important behavior:
- `uni2char()` validates output buffer length, then calls `utf32_to_utf8()`. On failure it writes `'?'` to output and returns `-EINVAL`.
- `char2uni()` calls `utf8_to_utf32()`, rejects decode failures or code points above `MAX_WCHAR_T`, stores `'?'` in `*uni` on failure, and returns the consumed byte count on success.
- `init_nls_utf8()` initializes identity case tables and registers the module.

Dependencies and interfaces:
- Uses kernel Unicode helpers `utf32_to_utf8()` and `utf8_to_utf32()`.
- Exposes standard `struct nls_table` callbacks.

Design notes and risks:
- Case conversion is explicitly a no-op; consumers needing Unicode-aware case folding need separate logic.
- Error paths write fallback question mark values while returning an error, so callers should not ignore negative return codes.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_utf8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/notify/Kconfig

Purpose: Top-level Kconfig entry point for fsnotify-related kernel configuration.

Core contents:
- Defines `config FSNOTIFY` as `def_bool n`; it is selected by concrete notification features rather than user-selected directly here.
- Sources `fs/notify/dnotify/Kconfig`, `fs/notify/inotify/Kconfig`, and `fs/notify/fanotify/Kconfig`.

Important behavior:
- This file establishes fsnotify as a hidden base symbol for dnotify, inotify, and fanotify.

Dependencies and interfaces:
- Kconfig-only file; no runtime code.

Design notes and risks:
- Any new fsnotify frontend Kconfig should be sourced here to be visible in configuration traversal.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/notify/Makefile

Purpose: Build rules for the fsnotify subsystem directory.

Core contents:
- Builds `fsnotify.o`, `notification.o`, `group.o`, `mark.o`, and `fdinfo.o` when `CONFIG_FSNOTIFY` is enabled.
- Always descends into `dnotify/`, `inotify/`, and `fanotify/` via `obj-y`, letting subdirectory Makefiles decide based on config symbols.

Important behavior:
- Core fsnotify objects are conditional on `CONFIG_FSNOTIFY`.
- Frontend directories are included in the build traversal unconditionally.

Dependencies and interfaces:
- Kbuild-only file.

Design notes and risks:
- The multiline `obj-$(CONFIG_FSNOTIFY)` assignment is the central list for shared fsnotify infrastructure objects.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/dnotify/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/notify/dnotify/Kconfig

Purpose: Kconfig option for legacy dnotify support.

Core contents:
- Defines `config DNOTIFY` as a boolean user-visible option `"Dnotify support"`.
- Selects `FSNOTIFY`.
- Defaults to `y`.
- Help text describes dnotify as a directory-based per-file-descriptor file change notification system using signals, retained for compatibility despite better alternatives.

Important behavior:
- Enabling dnotify automatically enables fsnotify core.

Dependencies and interfaces:
- Kconfig-only.

Design notes and risks:
- Defaulting to `y` preserves compatibility for applications that still rely on dnotify.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/dnotify/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/dnotify/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/notify/dnotify/Makefile

Purpose: Build rule for dnotify implementation.

Core contents:
- Builds `dnotify.o` when `CONFIG_DNOTIFY` is enabled.

Important behavior:
- This subdirectory contributes code only if the dnotify Kconfig symbol is enabled.

Dependencies and interfaces:
- Kbuild-only file.

Design notes and risks:
- No composite object list exists here; the implementation is a single C file.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/dnotify/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/dnotify/dnotify.c -->
# File Research: sources/os/linux/linux-stable/fs/notify/dnotify/dnotify.c

Purpose: Legacy directory notification implementation built on fsnotify. It supports `fcntl()`-based dnotify watches on directories and delivers events via `SIGIO`/poll notifications.

Core structures and globals:
- `dir_notify_enable` controls whether dnotify registration is accepted; when sysctl is enabled it is exposed as `fs/dir-notify-enable`.
- `dnotify_struct_cache` and `dnotify_mark_cache` are slab caches for per-watch and per-inode-mark state.
- `dnotify_group` is the single fsnotify group for dnotify.
- `struct dnotify_mark` wraps an `fsnotify_mark` plus a linked list of `struct dnotify_struct` entries for all file descriptors watching the inode.

Important behavior:
- `dnotify_recalc_inode_mask()` recalculates the aggregate inode event mask from all attached dnotify watch entries and updates fsnotify core masks.
- `dnotify_handle_event()` receives fsnotify inode events, filters non-directory cases, sends `SIGIO` to interested watchers, and removes one-shot watchers that lack `FS_DN_MULTISHOT`.
- `dnotify_flush()` removes the watch entry for a file descriptor on close and detaches/frees the fsnotify mark when the last watcher is gone.
- `convert_arg()` maps userspace `DN_*` flags to fsnotify `FS_*` masks, always including `FS_EVENT_ON_CHILD`.
- `attach_dn()` either appends a new watcher to the mark list or ORs a new mask into an existing watcher for the same owner/file.
- `fcntl_dirnotify()` is the registration entry point: it validates enablement, directory-ness, security policy, allocates state, handles fd-close races with `fget_raw()`, sets file ownership for signals, attaches the watcher, and handles cleanup paths.
- `dnotify_init()` creates caches, allocates the fsnotify group, and registers the sysctl.

Dependencies and interfaces:
- Externally callable functions include `dnotify_flush()` and `fcntl_dirnotify()`.
- Uses fsnotify backend mark/group APIs, Linux security hook `security_path_notify()`, and signal ownership helpers.

Concurrency and lifetime:
- Uses the fsnotify group lock and per-mark spinlock to coordinate mark list updates.
- Handles the race where a file descriptor is closed during registration by comparing `fget_raw(fd)` result against `filp`.
- One-shot watchers are freed during event delivery while holding the mark lock.

Design notes and risks:
- dnotify is compatibility code; Kconfig help explicitly points users toward superior alternatives.
- Watcher lifetime is tied to file descriptor ownership and close handling, so mistakes in ownership or flush paths can leak or prematurely remove notifications.
- The implementation relies on linked-list mutation under spinlock; changes should be made cautiously.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/dnotify/dnotify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/fanotify/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/notify/fanotify/Kconfig

Purpose: Kconfig options for fanotify support.

Core contents:
- `config FANOTIFY` enables filesystem-wide access notification, selects `FSNOTIFY` and `EXPORTFS`, and defaults to `n`.
- Help text explains that fanotify sends an open file descriptor to user-space listeners along with the event.
- `config FANOTIFY_ACCESS_PERMISSIONS` enables permission checking for fanotify listeners, depends on `FANOTIFY`, and defaults to `n`.

Important behavior:
- Basic fanotify support pulls in fsnotify core and exportfs support.
- Permission checking is separated so access-decision fanotify features can be disabled independently.

Dependencies and interfaces:
- Kconfig-only; informs conditional compilation in fanotify code elsewhere.

Design notes and risks:
- Permission checking has direct security implications and is opt-in, with help text recommending `N` if unsure.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/fanotify/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/fanotify/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/notify/fanotify/Makefile

Purpose: Build rule for fanotify implementation files.

Core contents:
- Builds `fanotify.o` and `fanotify_user.o` when `CONFIG_FANOTIFY` is enabled.

Important behavior:
- Fanotify is split between core event handling/allocation (`fanotify.o`) and user-facing syscall/read-response handling (`fanotify_user.o`, not in this work item).

Dependencies and interfaces:
- Kbuild-only file.

Design notes and risks:
- Any changes to fanotify source layout must keep this composite list synchronized.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/fanotify/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/fanotify/fanotify.c -->
# File Research: sources/os/linux/linux-stable/fs/notify/fanotify/fanotify.c

Purpose: Core fanotify event creation, filtering, merging, permission-response waiting, and destruction logic for the fsnotify backend.

Core helper groups:
- Identity and hash helpers compare and hash paths, fsids, file handles, name-event info, fid events, and filesystem error events.
- Merge helpers decide when queued events can be coalesced.
- Permission helpers wait for userspace responses to access-permission events.
- Event-mask helpers calculate which event bits a group should receive after mark masks and ignore masks are applied.
- File-handle helpers encode exportfs file handles for FID-style fanotify events.
- Allocation helpers create the different event object variants.
- Free helpers release resources for every event type and group/mark private state.

Important behavior:
- `fanotify_should_merge()` only merges events with the same hash, type, and pid, and refuses to merge directory and non-directory events or rename/non-rename combinations. It delegates equality by event type: path, fid, name, filesystem error, or mount event.
- `fanotify_merge()` limits merge scanning to `FANOTIFY_MAX_MERGE_EVENTS` and never merges permission events. For filesystem error events it increments `err_count` on merge.
- `fanotify_get_response()` waits on `access_waitq` for permission events, handles signal cancellation and races with userspace replies, converts `FAN_ALLOW`/`FAN_DENY` plus optional errno to kernel return values, audits when requested, and destroys the permission event before returning.
- `fanotify_group_event_mask()` combines all matching marks, applies ignore masks, enforces mode-specific requirements such as path availability, FID/dir availability, or mount-event type, and strips/report flags according to legacy vs FID modes.
- `fanotify_encode_fh_len()` and `fanotify_encode_fh()` use exportfs file handles for FID reports, support inline or external handle storage, hash handle contents for merge keys, and fall back to invalid file handles on encoding failure.
- `fanotify_alloc_event()` selects event representation based on mask and group flags: permission path events, filesystem error events, name events, FID events, path events, or mount events. It charges allocation to the monitoring group memcg and uses stronger allocation flags for unlimited queues.
- `fanotify_handle_event()` is the fsnotify callback. It validates compile-time mask equality with `BUILD_BUG_ON`, filters the event mask, prepares permission waits when needed, obtains fsid in FID mode, allocates the event, queues/merges it through fsnotify, waits for permission responses, and finalizes permission waits.
- `fanotify_free_event()` dispatches destruction based on event type and releases paths, pids, external file-handle buffers, kmem-cache objects, mempool error events, or heap allocations as appropriate.

Event model details:
- Path events hold a `struct path` and take a path reference.
- Permission events are path events with response state, optional range information, and wait semantics.
- FID events hold fsid plus an encoded object file handle.
- Name events can include directory file handle, second directory file handle for rename, child file handle, and one or two names in a variable-sized allocation.
- Filesystem error events use a mempool and may carry an invalid file handle when the error has no inode.
- Mount events carry a mount ID and are explicitly not mergeable.

Dependencies and interfaces:
- Implements `const struct fsnotify_ops fanotify_fsnotify_ops` with `.handle_event`, `.free_group_priv`, `.free_event`, `.freeing_mark`, and `.free_mark`.
- Uses fsnotify backend iteration, queueing, mark mask, wait, and overflow APIs.
- Uses exportfs for file-handle encoding, audit for permission response auditing, memcg charging, ucounts, and fanotify-local structures declared in `fanotify.h`.

Concurrency and lifetime:
- Event queue and merge hash operations assume `group->notification_lock` where required.
- Permission events have explicit state transitions: init, reported, canceled, answered.
- Mark and group resource accounting is released through the fsnotify ops callbacks.
- Allocation paths take references to paths and pids and release them in the matching free helpers.

Design notes and risks:
- The file is central fanotify machinery; small mask/filter changes can affect userspace ABI behavior.
- FID/name event layout is variable-sized and depends on exact ordering of encoded handles and names through `fanotify_info_*` helpers.
- Permission event handling is security-sensitive: failures to allocate permission events deny access by returning `-ENOMEM`, while races with mark deletion intentionally allow the operation.
- The compile-time `BUILD_BUG_ON(HWEIGHT32(ALL_FANOTIFY_EVENT_BITS) != 24)` is a guard that must be updated when event bit definitions change.

<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/notify/fanotify/fanotify.c -->