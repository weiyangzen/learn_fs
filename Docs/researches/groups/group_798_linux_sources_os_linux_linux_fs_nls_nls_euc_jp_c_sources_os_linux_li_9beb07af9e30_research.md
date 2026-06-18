# Group Research: group_798_linux_sources_os_linux_linux_fs_nls_nls_euc_jp_c_sources_os_linux_li_9beb07af9e30

Scope: `Docs/research_subset_a.md`, specifically the listed `sources/os/linux/linux` NLS and fsnotify files. Every listed source file was read completely. The listed files were also verified byte-identical to their corresponding `sources/os/linux/linux-stable` copies.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_euc-jp.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_euc-jp.c

Purpose: Linux NLS module for Japanese EUC-JP. Unlike generated single-byte NLS modules, this converter loads the existing `cp932` NLS table and translates between Unicode, Shift-JIS/CP932, and EUC-JP forms.

Core structures and data:
- `static struct nls_table *p_nls` holds the loaded `cp932` backend.
- Shift-JIS range macros classify JIS X 0208, JIS X 0201 kana, user-defined characters, IBM extensions, and NEC/IBM extensions.
- EUC-JP range macros classify normal EUC bytes, SS2 kana, SS3 G3 blocks, and user-defined ranges.
- `sjisibm2euc_map`, `euc2sjisibm_jisx0212_map`, and `euc2sjisibm_g3upper_map` handle IBM extension mappings outside the simple SJIS/EUC arithmetic conversions.

Important behavior:
- `uni2char()` delegates Unicode-to-CP932 conversion to `cp932`, then rewrites returned Shift-JIS bytes into EUC-JP.
- `char2uni()` parses EUC-JP into temporary Shift-JIS bytes and delegates final decoding to `cp932`.
- SS2/SS3 cases can consume or emit 2 or 3 EUC bytes, with explicit output and input bound checks.
- `init_nls_euc_jp()` loads `cp932`, copies its case tables into this table, and registers charset `"euc-jp"`.

Dependencies and interfaces:
- Implements `struct nls_table` callbacks `uni2char` and `char2uni`.
- Requires `load_nls("cp932")`; init fails with `-EINVAL` if unavailable.
- Returns `-ENAMETOOLONG` for output/input length problems and `-EINVAL` for invalid or unsupported encodings.

Design notes and risks:
- The byte arithmetic relies on exact range predicates and table sizes.
- `sjisibm2euc()` assumes callers already classified the bytes as IBM Shift-JIS.
- Unsupported EUC JIS X 0212 characters deliberately fail instead of substituting a placeholder.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_euc-jp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-1.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_iso8859-1.c

Purpose: Generated Linux NLS module for ISO 8859-1 / Latin-1, described as Western European Languages.

Core structures and data:
- `charset2uni[256]` maps byte values directly to Unicode U+0000 through U+00FF.
- `page00[256]` maps Unicode page 0 back to byte values.
- `page_uni2charset[256]` only maps page 0; all other pages are unmapped.
- `charset2lower` and `charset2upper` implement ASCII and Latin-1 byte-level casing.

Important behavior:
- `uni2char()` does a page-based reverse lookup and emits one byte.
- `char2uni()` maps one byte through `charset2uni`.
- Both paths treat `0x0000`/`0x00` as an unmapped sentinel, so NUL is rejected by the common generated logic.

Dependencies and interfaces:
- Self-contained `struct nls_table` implementation.
- Module lifecycle is `register_nls()` / `unregister_nls()` for charset `"iso8859-1"`.

Design notes and risks:
- Low control-flow complexity; behavior is almost entirely table-driven.
- Exact mapping only: no normalization, transliteration, or fallback substitution.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-13.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_iso8859-13.c

Purpose: Generated Linux NLS module for ISO 8859-13 / Latin-7, described as Baltic.

Core structures and data:
- `charset2uni[256]` contains Baltic Latin letters and punctuation such as curly quotes.
- Reverse lookup pages include `page00`, `page01`, and `page20`.
- Case tables include ISO 8859-13 extended letter pairs and ASCII casing.

Important behavior:
- `uni2char()` emits one byte for exact represented Unicode code points.
- `char2uni()` consumes one byte and rejects zero-valued table entries.
- Registers charset `"iso8859-13"`.

Dependencies and interfaces:
- Standard generated NLS table module using `linux/nls.h`.
- No subordinate charset is loaded.

Design notes and risks:
- Sparse punctuation mappings in Unicode page 0x20 must stay synchronized with `page_uni2charset`.
- Canonically equivalent or decomposed Unicode forms are not accepted.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-13.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-14.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_iso8859-14.c

Purpose: Generated Linux NLS module for ISO 8859-14 / Latin-8, described as Celtic.

Core structures and data:
- `charset2uni[256]` maps Celtic/Welsh-related Latin letters including dotted consonants and W/Y variants.
- Reverse mappings use `page00`, `page01`, and `page1e`.
- Case tables cover ASCII and charset-specific extended letters.

Important behavior:
- `uni2char()` performs exact page lookup and emits one byte.
- `char2uni()` maps one byte to Unicode and rejects zero-valued mappings.
- Registers charset `"iso8859-14"`.

Dependencies and interfaces:
- Self-contained NLS module with standard registration callbacks.
- No runtime-loaded backend.

Design notes and risks:
- Sparse page 0x1e reverse mappings make table synchronization important.
- Conversion logic is still the common one-byte generated pattern.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-14.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-15.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_iso8859-15.c

Purpose: Generated Linux NLS module for ISO 8859-15 / Latin-9, Western European Languages with Euro.

Core structures and data:
- `charset2uni[256]` resembles Latin-1 but replaces selected positions with Euro, OE/oe, S/s caron, Z/z caron, and Y diaeresis.
- Reverse mappings use `page00`, `page01`, and `page20`.
- Case tables include Latin-9 extended case pairs.

Important behavior:
- `uni2char()` exact-maps supported Unicode values to one byte.
- `char2uni()` consumes one byte and rejects zero-valued table entries.
- Registers charset `"iso8859-15"`.

Dependencies and interfaces:
- Standard generated `nls_table` module.
- No external NLS backend.

Design notes and risks:
- Euro sign U+20AC is handled through sparse page 0x20.
- No Unicode normalization or fallback behavior exists.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-15.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-2.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_iso8859-2.c

Purpose: Generated Linux NLS module for ISO 8859-2 / Latin-2, described as Slavic/Central European Languages.

Core structures and data:
- `charset2uni[256]` maps Central European Latin extended letters and diacritics.
- Reverse maps include `page00`, `page01`, and `page02`.
- Case tables encode charset-specific upper/lower pairs.

Important behavior:
- `uni2char()` performs exact reverse lookup and returns one byte or an errno.
- `char2uni()` consumes one byte and rejects zero-valued mappings.
- Registers charset `"iso8859-2"`.

Dependencies and interfaces:
- Self-contained generated NLS table.
- Module init/exit only register and unregister the table.

Design notes and risks:
- Reverse table value `0xff` is valid for U+02D9; only `0x00` is the unmapped sentinel.
- The generated helper cannot encode Unicode NUL.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-3.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_iso8859-3.c

Purpose: Generated Linux NLS module for ISO 8859-3 / Latin-3, described as Esperanto, Galician, Maltese, and Turkish.

Core structures and data:
- `charset2uni[256]` has explicit `0x0000` gaps for undefined byte positions.
- Reverse mappings include `page00`, `page01`, and `page02`.
- Case tables preserve undefined byte slots as zero.

Important behavior:
- `uni2char()` emits one byte for exact represented Unicode code points.
- `char2uni()` rejects undefined bytes and NUL through the zero-sentinel convention.
- Registers charset `"iso8859-3"`.

Dependencies and interfaces:
- Standard self-contained NLS registration.

Design notes and risks:
- This charset has more undefined byte slots than Latin-1/2.
- Consumers using case tables directly must account for zero entries on undefined bytes.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-4.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_iso8859-4.c

Purpose: Generated Linux NLS module for ISO 8859-4 / Latin-4, described as old Baltic charset.

Core structures and data:
- `charset2uni[256]` covers Baltic and Nordic Latin extended letters.
- Reverse mappings include `page00`, `page01`, and `page02`.
- `charset2lower` and `charset2upper` provide byte-level case conversion.

Important behavior:
- `uni2char()` maps exact Unicode code points back to one byte.
- `char2uni()` returns one-byte consumption for mapped entries and `-EINVAL` for zero mappings.
- Registers charset `"iso8859-4"`.

Dependencies and interfaces:
- Self-contained generated NLS table.
- No runtime-loaded backend.

Design notes and risks:
- Some spacing diacritics live on Unicode page 2.
- There is no multibyte parsing or stateful conversion.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-5.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_iso8859-5.c

Purpose: Generated Linux NLS module for ISO 8859-5, described as Cyrillic.

Core structures and data:
- `charset2uni[256]` maps byte range `0xa1` onward to Cyrillic and related symbols, including U+2116.
- Reverse maps include `page00`, `page04`, and `page21`.
- Case tables map Cyrillic uppercase/lowercase byte ranges and preserve nonletters.

Important behavior:
- `uni2char()` exact-maps Unicode to ISO 8859-5 bytes.
- `char2uni()` consumes one byte and rejects zero-valued mappings.
- Registers charset `"iso8859-5"`.

Dependencies and interfaces:
- Standard generated NLS table module.

Design notes and risks:
- U+2116 maps through page 0x21 to byte `0xf0`.
- Cyrillic casing is byte-table-based and only covers representable characters.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-6.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_iso8859-6.c

Purpose: Generated Linux NLS module for ISO 8859-6, described as Arabic.

Core structures and data:
- `charset2uni[256]` maps Arabic punctuation, letters, and Arabic-Indic digits.
- Byte `0x30` through `0x39` map to U+0660 through U+0669, not ASCII digits.
- Reverse mappings include `page00` and `page06`.
- Case tables are mostly identity or zero because this charset has no upper/lowercase distinction.

Important behavior:
- `uni2char()` exact-maps Unicode page 0 and page 6 values to one byte.
- `char2uni()` rejects undefined slots and NUL.
- Registers charset `"iso8859-6"`.

Dependencies and interfaces:
- Self-contained generated NLS table.

Design notes and risks:
- The digit mapping is surprising for code expecting ASCII digit Unicode from byte `0x30`.
- Many high-byte positions are undefined and return `-EINVAL`.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-7.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_iso8859-7.c

Purpose: Generated Linux NLS module for ISO 8859-7, described as Modern Greek.

Core structures and data:
- `charset2uni[256]` maps Greek letters, tonos/dialytika characters, and selected punctuation.
- Reverse maps include `page00`, `page02`, `page03`, and `page20`.
- Case tables map Greek uppercase/lowercase byte values.

Important behavior:
- `uni2char()` emits one byte for exactly represented Unicode code points.
- `char2uni()` maps one byte and rejects zero-valued entries.
- Registers charset `"iso8859-7"`.

Dependencies and interfaces:
- Standard generated NLS implementation.

Design notes and risks:
- Sparse reverse mappings cover modifier letters and U+2015.
- Some Greek byte positions are undefined and fail byte-to-Unicode conversion.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-7.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-9.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_iso8859-9.c

Purpose: Generated Linux NLS module for ISO 8859-9 / Latin-5, described as Turkish.

Core structures and data:
- `charset2uni[256]` is close to Latin-1 but replaces selected positions with Turkish G/g breve, I dot/dotless, and S/s cedilla.
- Reverse mappings include `page00` and `page01`.
- Case tables include Turkish-specific byte case mappings.

Important behavior:
- `uni2char()` exact-maps supported Unicode values to one byte.
- `char2uni()` consumes one byte and rejects zero-valued mappings.
- Registers charset `"iso8859-9"`.

Dependencies and interfaces:
- Self-contained `nls_table` module.

Design notes and risks:
- Turkish-specific letters are sparse page 1 mappings, not custom code.
- Case tables are byte-oriented and not general Unicode locale-sensitive casing.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_iso8859-9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_koi8-r.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_koi8-r.c

Purpose: Generated Linux NLS module for KOI8-R, described as Russian.

Core structures and data:
- `charset2uni[256]` maps ASCII, box drawing, mathematical symbols, and Cyrillic letters.
- Reverse maps include `page00`, `page04`, `page22`, `page23`, and `page25`.
- Case tables provide KOI8-R byte-level Cyrillic casing and identity handling for graphics characters.

Important behavior:
- `uni2char()` performs exact Unicode-to-KOI8-R lookup.
- `char2uni()` maps one byte and rejects zero-valued entries.
- Registers charset `"koi8-r"`.

Dependencies and interfaces:
- Self-contained generated NLS table.

Design notes and risks:
- KOI8-R’s graphics characters explain the broader reverse page coverage.
- Unicode NUL and unmapped code points are rejected by the zero-sentinel convention.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_koi8-r.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_koi8-ru.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_koi8-ru.c

Purpose: Linux NLS wrapper for KOI8-RU, described as Belarusian, implemented as a small delta on top of `koi8-u`.

Core structures and data:
- `static struct nls_table *p_nls` stores the loaded `koi8-u` backend.
- Public `nls_table` registers charset `"koi8-ru"` with custom `uni2char` and `char2uni`.
- Case tables are copied from the loaded `koi8-u` table at init.

Important behavior:
- `uni2char()` handles the few KOI8-RU differences: U+040E maps to `0xbe`, U+045E maps to `0xae`, and U+255D/U+256C return `0` in the special branch; other values delegate to `koi8-u`.
- `char2uni()` has a notable condition: when `(*rawstring & 0xef) != 0xae`, it returns U+040E or U+045E based on bit `0x10`; otherwise it delegates to `koi8-u`.
- `init_nls_koi8_ru()` loads `koi8-u`, inherits case tables, and registers this wrapper.
- `exit_nls_koi8_ru()` unregisters and unloads the base charset.

Dependencies and interfaces:
- Requires the `koi8-u` NLS module to be loadable.
- Exposes standard `struct nls_table` callbacks.

Design notes and risks:
- This file relies on `koi8-u` for almost all behavior.
- The `char2uni()` condition is suspicious relative to the “differ only on two characters” comment; changes need careful testing.
- Returning `0` from `uni2char()` is unusual compared with the generated modules’ negative errno behavior.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_koi8-ru.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_koi8-u.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_koi8-u.c

Purpose: Generated Linux NLS module for KOI8-U, described as Ukrainian.

Core structures and data:
- `charset2uni[256]` maps ASCII, graphics characters, Cyrillic letters, and Ukrainian-specific letters.
- Reverse maps include `page00`, `page04`, `page22`, `page23`, and `page25`.
- `charset2lower` and `charset2upper` implement KOI8-U byte-level case conversion.

Important behavior:
- `uni2char()` exact-maps Unicode through sparse reverse pages.
- `char2uni()` consumes one byte for nonzero mappings and rejects zero entries.
- Registers charset `"koi8-u"`.

Dependencies and interfaces:
- Self-contained NLS module.
- Serves as the runtime backend for `nls_koi8-ru.c`.

Design notes and risks:
- Supports line/box drawing and mathematical symbols in addition to Cyrillic.
- Differences from KOI8-R are concentrated around Ukrainian-specific Cyrillic and upper-byte graphics slots.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_koi8-u.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_ucs2_data.h -->
# File Research: sources/os/linux/linux/fs/nls/nls_ucs2_data.h

Purpose: Header declaring shared UCS-2 uppercase conversion table data for NLS UCS-2 helpers.

Core structures and data:
- Defines `struct UniCaseRange` with `wchar_t start`, `wchar_t end`, and `signed char *table`.
- Declares `NlsUniUpperTable[512]`.
- Declares `NlsUniUpperRange[]`.

Important behavior:
- Contains no executable logic.
- Provides the declaration boundary between `nls_ucs2_utils.c` and inline consumers in `nls_ucs2_utils.h`.

Dependencies and interfaces:
- Uses `wchar_t`; included through `nls_ucs2_utils.h`.

Design notes and risks:
- `table` is a non-const `signed char *` even though range table entries point at static data; this is part of the existing source contract.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_ucs2_data.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_ucs2_utils.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_ucs2_utils.c

Purpose: Defines and exports compressed UCS-2 uppercase conversion tables shared by in-kernel Unicode/NLS users.

Core structures and data:
- `NlsUniUpperTable[512]` provides signed uppercase offsets for low Unicode code points.
- `UniCaseRangeU03a0`, `UniCaseRangeU0430`, `UniCaseRangeU0490`, `UniCaseRangeU1e00`, and `UniCaseRangeUff40` cover Greek, Cyrillic, extended Cyrillic, extended Latin/Greek, and fullwidth Latin ranges.
- `NlsUniUpperRange[]` lists those ranges and ends with a zeroed sentinel.

Important behavior:
- No conversion functions are defined here; inline logic lives in `nls_ucs2_utils.h`.
- `EXPORT_SYMBOL_GPL` exports the table and range list.
- Module metadata identifies this as `"NLS UCS-2"`.

Dependencies and interfaces:
- Includes `nls_ucs2_utils.h`.
- Code/data lineage comments reference CIFS Unicode support.

Design notes and risks:
- Signed offset encoding is compact but fragile because consumers add offsets directly to code points.
- Range boundaries and table lengths must stay synchronized with the sentinel-scanning logic.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_ucs2_utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_ucs2_utils.h -->
# File Research: sources/os/linux/linux/fs/nls/nls_ucs2_utils.h

Purpose: Inline UCS-2 string utility and uppercase conversion helpers, derived from CIFS/server Unicode handling.

Core structures and definitions:
- Defines Windows private-use remappings for reserved filename characters: `UNI_ASTERISK`, `UNI_QUESTION`, `UNI_COLON`, `UNI_GRTRTHAN`, `UNI_LESSTHAN`, `UNI_PIPE`, and `UNI_SLASH`.
- Provides inline string helpers: `UniStrcat`, `UniStrchr`, `UniStrcmp`, `UniStrcpy`, `UniStrlen`, `UniStrnlen`, `UniStrncat`, `UniStrncmp`, `UniStrncmp_le`, `UniStrncpy`, `UniStrncpy_le`, and `UniStrstr`.
- Provides `UniToupper()` and `UniStrupr()` unless `UNIUPR_NOUPPER` is defined.

Important behavior:
- String helpers mirror C library style APIs over `wchar_t` / `__le16`-style UCS-2 code units.
- Little-endian variants convert via kernel byteorder helpers.
- `UniToupper()` first indexes `NlsUniUpperTable`, then scans `NlsUniUpperRange[]`.
- `UniStrupr()` uppercases a little-endian UCS-2 string in place.

Dependencies and interfaces:
- Includes byteorder helpers, Linux types, `linux/nls.h`, `linux/unicode.h`, and `nls_ucs2_data.h`.
- Depends on table definitions exported by `nls_ucs2_utils.c`.

Design notes and risks:
- Several helpers are unsafe C-style copy/concat functions with no destination capacity tracking.
- Operates on 16-bit code units and does not handle full Unicode scalar or surrogate-pair semantics.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_ucs2_utils.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_utf8.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_utf8.c

Purpose: Linux NLS module exposing UTF-8 through the same `nls_table` interface as legacy charsets.

Core structures and data:
- `identity[256]` is initialized at module load and used as both lower and upper case tables.
- Registers charset `"utf8"`.

Important behavior:
- `uni2char()` checks output length, calls `utf32_to_utf8()`, and writes `'?'` while returning `-EINVAL` on encode failure.
- `char2uni()` calls `utf8_to_utf32()`, rejects decode failures and values above `MAX_WCHAR_T`, stores `'?'` on failure, and returns the consumed byte count on success.
- `init_nls_utf8()` initializes identity case tables and registers the module.

Dependencies and interfaces:
- Uses kernel Unicode helpers `utf32_to_utf8()` and `utf8_to_utf32()`.
- Exposes standard NLS callbacks.

Design notes and risks:
- Case conversion is explicitly byte-identity, not Unicode-aware folding.
- Error paths write fallback question marks while returning errors, so callers must honor negative return codes.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_utf8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/Kconfig -->
# File Research: sources/os/linux/linux/fs/notify/Kconfig

Purpose: Top-level Kconfig entry point for fsnotify-related configuration.

Core contents:
- Defines hidden `config FSNOTIFY` with `def_bool n`.
- Sources `fs/notify/dnotify/Kconfig`, `fs/notify/inotify/Kconfig`, and `fs/notify/fanotify/Kconfig`.

Important behavior:
- `FSNOTIFY` is selected by concrete notification frontends rather than directly enabled here.

Dependencies and interfaces:
- Kconfig-only file; no runtime code.

Design notes and risks:
- New fsnotify frontend Kconfig files need to be sourced here to participate in configuration traversal.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/Makefile -->
# File Research: sources/os/linux/linux/fs/notify/Makefile

Purpose: Kbuild rules for the fsnotify subsystem directory.

Core contents:
- Builds `fsnotify.o`, `notification.o`, `group.o`, `mark.o`, and `fdinfo.o` when `CONFIG_FSNOTIFY` is enabled.
- Always descends into `dnotify/`, `inotify/`, and `fanotify/` using `obj-y`.

Important behavior:
- Shared fsnotify infrastructure is conditional on `CONFIG_FSNOTIFY`.
- Frontend subdirectories are traversed unconditionally; their own Makefiles gate objects by config.

Dependencies and interfaces:
- Kbuild-only file.

Design notes and risks:
- The multiline `obj-$(CONFIG_FSNOTIFY)` list is the central shared fsnotify object list.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/dnotify/Kconfig -->
# File Research: sources/os/linux/linux/fs/notify/dnotify/Kconfig

Purpose: Kconfig option for legacy dnotify support.

Core contents:
- Defines user-visible boolean `DNOTIFY`.
- Selects `FSNOTIFY`.
- Defaults to `y`.
- Help describes dnotify as directory-based per-fd notification using signals, retained for compatibility despite superior alternatives.

Important behavior:
- Enabling dnotify automatically enables fsnotify core.

Dependencies and interfaces:
- Kconfig-only file.

Design notes and risks:
- Defaulting to `y` preserves compatibility for applications still relying on dnotify.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/dnotify/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/dnotify/Makefile -->
# File Research: sources/os/linux/linux/fs/notify/dnotify/Makefile

Purpose: Kbuild rule for the dnotify implementation.

Core contents:
- Builds `dnotify.o` when `CONFIG_DNOTIFY` is enabled.

Important behavior:
- This subdirectory contributes code only under the dnotify config symbol.

Dependencies and interfaces:
- Kbuild-only file.

Design notes and risks:
- Implementation is a single C object.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/dnotify/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/dnotify/dnotify.c -->
# File Research: sources/os/linux/linux/fs/notify/dnotify/dnotify.c

Purpose: Legacy directory notification implementation built on fsnotify. It supports `fcntl()`-based directory watches tied to file descriptors and delivers events through `SIGIO`/poll notifications.

Core structures and globals:
- `dir_notify_enable` gates dnotify registration and may be exposed as `fs/dir-notify-enable` under sysctl.
- `dnotify_struct_cache` and `dnotify_mark_cache` allocate watcher and mark state.
- `dnotify_group` is the single fsnotify group used by dnotify.
- `struct dnotify_mark` wraps an `fsnotify_mark` plus a linked list of `struct dnotify_struct` watchers.

Important behavior:
- `dnotify_recalc_inode_mask()` recomputes aggregate inode interest from all linked dnotify watchers.
- `dnotify_handle_event()` filters non-directory cases, sends `SIGIO` to matching watchers, and removes one-shot watchers lacking `FS_DN_MULTISHOT`.
- `dnotify_flush()` removes a file descriptor’s watch on close and detaches/frees the mark when no watchers remain.
- `convert_arg()` translates userspace `DN_*` flags into fsnotify `FS_*` masks and always includes `FS_EVENT_ON_CHILD`.
- `attach_dn()` either appends a new watcher or ORs a new mask into an existing watcher for the same owner/file.
- `fcntl_dirnotify()` validates enablement, directory-ness, security policy, allocation, fd-close races, signal ownership, and mark attachment.
- `dnotify_init()` creates slab caches, allocates the fsnotify group, and registers sysctl state.

Dependencies and interfaces:
- Externally used functions include `dnotify_flush()` and `fcntl_dirnotify()`.
- Uses fsnotify mark/group APIs, `security_path_notify()`, file ownership helpers, and signal delivery helpers.

Concurrency and lifetime:
- Uses the fsnotify group lock and per-mark spinlock for watcher list mutation.
- Handles fcntl/close races by comparing `fget_raw(fd)` with the original `filp`.
- One-shot watchers are freed during event delivery under the mark lock.

Design notes and risks:
- Compatibility code with lifetime tied to file descriptor ownership.
- Linked-list mutation under spinlock and mark detach/free sequencing are the main correctness-sensitive paths.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/dnotify/dnotify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/fanotify/Kconfig -->
# File Research: sources/os/linux/linux/fs/notify/fanotify/Kconfig

Purpose: Kconfig options for fanotify support.

Core contents:
- `config FANOTIFY` enables filesystem-wide access notification, selects `FSNOTIFY` and `EXPORTFS`, and defaults to `n`.
- Help notes fanotify sends an open file descriptor to userspace listeners with events.
- `config FANOTIFY_ACCESS_PERMISSIONS` depends on `FANOTIFY`, enables listener permission decisions, and defaults to `n`.

Important behavior:
- Basic fanotify support pulls in fsnotify core and exportfs support.
- Permission checking is independently configurable.

Dependencies and interfaces:
- Kconfig-only file; controls fanotify compilation and feature availability elsewhere.

Design notes and risks:
- Permission checking is security-sensitive and defaults off, with help text recommending `N` if unsure.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/fanotify/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/fanotify/Makefile -->
# File Research: sources/os/linux/linux/fs/notify/fanotify/Makefile

Purpose: Kbuild rule for fanotify implementation files.

Core contents:
- Builds `fanotify.o` and `fanotify_user.o` when `CONFIG_FANOTIFY` is enabled.

Important behavior:
- Core event handling/allocation is in `fanotify.o`.
- User-facing syscall/read/response logic is in `fanotify_user.o`, outside this work item.

Dependencies and interfaces:
- Kbuild-only file.

Design notes and risks:
- Source layout changes must keep this object list synchronized.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/fanotify/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/notify/fanotify/fanotify.c -->
# File Research: sources/os/linux/linux/fs/notify/fanotify/fanotify.c

Purpose: Core fanotify backend logic for event filtering, allocation, merging, permission-response waiting, event destruction, and fsnotify operation hooks.

Core helper groups:
- Equality/hash helpers compare paths, fsids, file handles, FID events, name events, filesystem error events, and mount events.
- Merge helpers decide whether queued events can coalesce.
- Permission helpers wait for userspace access decisions.
- Event-mask helpers combine mark masks and ignore masks into outgoing user-visible fanotify masks.
- File-handle helpers encode exportfs file handles for FID-style reporting.
- Allocation/free helpers create and destroy path, permission, FID, name, filesystem-error, overflow, and mount event variants.

Important behavior:
- `fanotify_should_merge()` requires matching hash, event type, and pid, refuses directory/non-directory mixing, refuses rename/non-rename mixing, and then compares event-specific identity.
- `fanotify_merge()` scans at most `FANOTIFY_MAX_MERGE_EVENTS`, never merges permission events, and increments filesystem error counts on merged error events.
- `fanotify_get_response()` waits for permission event replies, handles signal cancellation, converts `FAN_ALLOW`/`FAN_DENY` plus optional errno to kernel returns, audits requested responses, and destroys the permission event.
- `fanotify_group_event_mask()` applies mark masks, ignore masks, fid/path/mount mode constraints, and strips/report flags according to legacy versus FID reporting mode.
- `fanotify_encode_fh_len()` and `fanotify_encode_fh()` use `exportfs_encode_fid()` and support inline or external file-handle storage; encode failures produce invalid handles for report fallback.
- `fanotify_alloc_event()` selects representation based on mask and group flags: permission path event, filesystem error event, name event, FID event, path event, or mount event.
- `fanotify_handle_event()` validates fanotify/fsnotify mask alignment with `BUILD_BUG_ON`, filters the event, prepares permission waits, obtains fsid for FID mode, allocates, queues/merges, waits for permission responses when needed, and finalizes waits.
- `fanotify_free_event()` dispatches cleanup by event type and releases paths, pids, external buffers, kmem-cache objects, mempool objects, or heap allocations.

Event model details:
- Path events store and refcount a `struct path`.
- Permission events are path events with response state, optional range info, and wait semantics.
- FID events store fsid plus encoded object file handle.
- Name events can store directory file handle, second directory file handle for rename, child file handle, and one or two names in a variable-sized allocation.
- Filesystem error events use a mempool and may carry an invalid file handle when no inode exists.
- Mount events carry a mount ID and are not mergeable.

Dependencies and interfaces:
- Implements `const struct fsnotify_ops fanotify_fsnotify_ops`.
- Uses fsnotify iteration, queueing, marks, wait handling, and overflow APIs.
- Uses exportfs, audit, memcg charging, ucounts, and fanotify-local definitions from `fanotify.h`.

Concurrency and lifetime:
- Queue merge hash insertion assumes `group->notification_lock`.
- Permission events transition through init, reported, canceled, and answered states.
- Mark and group resource accounting is released through fsnotify ops callbacks.
- Allocation paths take path and pid references and release them in paired free helpers.

Design notes and risks:
- Central fanotify machinery with direct userspace ABI impact.
- Permission handling is security-sensitive: permission event allocation failure denies access, while mark-deletion races intentionally allow the operation.
- Variable-sized name/FID event layout depends on exact helper ordering and size calculations.
- `BUILD_BUG_ON(HWEIGHT32(ALL_FANOTIFY_EVENT_BITS) != 24)` must be updated with event bit definition changes.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/notify/fanotify/fanotify.c -->