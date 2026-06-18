# Group Research: group_1038_linux_stable_sources_os_linux_linux_stable_fs_nls_mac_greek_c_sourc_3b1f15ab6ab6

Scope checked against `Docs/research_subset_a.md`: `sources/os/linux/linux-stable` is included. All 11 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-greek.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/mac-greek.c

This file implements the Linux NLS module for the classic Macintosh Greek codepage, registered under charset name `macgreek`.

It is a generated charset translation table module. `charset2uni[256]` maps every single-byte Mac Greek value to Unicode, with ASCII/control bytes preserved for `0x00` through `0x7f` and Greek letters, Greek tonos/dialytika forms, punctuation, symbols, and a few Latin-1 characters in the high half. Reverse conversion is handled through sparse Unicode page tables: `page00`, `page01`, `page03`, `page20`, `page21`, and `page22`, referenced by `page_uni2charset[256]`.

The conversion callbacks follow the common NLS table pattern:
- `uni2char()` checks output capacity, indexes `page_uni2charset` by Unicode high byte, and returns `-ENAMETOOLONG` or `-EINVAL` when the output byte cannot be represented.
- `char2uni()` indexes `charset2uni` by input byte and treats Unicode `0x0000` as unmappable, so NUL is not converted as a normal character.
- `struct nls_table table` binds these callbacks plus `charset2lower` and `charset2upper`.

The case-conversion tables are filled with `0xff` values rather than meaningful ASCII/Greek fold mappings, which means this module primarily provides byte/Unicode translation and should not be expected to implement useful case folding.

Module lifecycle is standard: `init_nls_macgreek()` calls `register_nls(&table)`, `exit_nls_macgreek()` calls `unregister_nls(&table)`, and the file declares `MODULE_DESCRIPTION("NLS Codepage macgreek")` with `Dual BSD/GPL` license. The file also carries the Unicode, Inc. data permission notice.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-greek.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-iceland.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/mac-iceland.c

This file implements the Linux NLS module for Macintosh Icelandic, registered as charset `maciceland`.

The core data is generated mapping state. `charset2uni[256]` maps Mac Icelandic bytes to Unicode, preserving the lower ASCII range and mapping high bytes to accented Latin characters, Icelandic-specific letters such as eth/thorn, mathematical symbols, punctuation, the Euro sign, and the Apple private-use character `0xf8ff`. Reverse lookup is organized into sparse Unicode page arrays: `page00`, `page01`, `page02`, `page03`, `page20`, `page21`, `page22`, `page25`, and `pagef8`.

The module uses the usual NLS single-byte conversion callbacks:
- `uni2char()` maps Unicode to one output byte through `page_uni2charset`; it fails on zero capacity or unmappable code points.
- `char2uni()` maps one input byte to a `wchar_t`; byte values mapped to `0x0000` are treated as invalid.
- The NLS table binds these callbacks and the static case tables.

The high-byte mapping is close to Mac Roman but swaps in Icelandic coverage: for example `0xdc`/`0xdd`/`0xde`/`0xdf` cover uppercase/lowercase eth and thorn, while the table keeps common Mac symbol mappings like `0xf0 -> 0xf8ff`. `charset2lower` and `charset2upper` are both initialized with `0xff` throughout, so there is no practical case-folding behavior exposed through this table.

The lifecycle functions register and unregister the table with the kernel NLS registry. Metadata declares `NLS Codepage maciceland`, `Dual BSD/GPL`, and includes the Unicode data permission notice.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-iceland.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-inuit.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/mac-inuit.c

This file implements the Linux NLS module for Macintosh Inuit, registered as `macinuit`.

The table targets Canadian Aboriginal Syllabics/Inuktitut byte mappings. `charset2uni[256]` maps ASCII/control bytes directly and maps most high bytes into Unicode ranges `0x1400` through `0x1676`, with a few common punctuation/symbol entries such as bullet, paragraph sign, copyright, trademark, en/em dash, quotes, and Polish L-with-stroke entries at `0xfe`/`0xff`. Reverse conversion is sparse across Unicode pages `page00`, `page01`, `page14`, `page15`, `page16`, `page20`, and `page21`.

The conversion functions are the same single-byte NLS pattern used by the other generated tables. `uni2char()` rejects insufficient output space and Unicode code points not present in the reverse page table. `char2uni()` returns the mapped Unicode value for one byte and reports `-EINVAL` for entries mapped to `0x0000`.

A notable difference from most neighboring Mac files is the case table content: `charset2lower` is filled with `0xff`, while `charset2upper` is filled with `0xfe`. These are not useful alphabetic folds for the syllabics repertoire; consumers should treat this module as a charset translator, not a locale-aware case mapper.

The file registers with `register_nls(&table)` in `init_nls_macinuit()` and unregisters in `exit_nls_macinuit()`. Module metadata identifies it as `NLS Codepage macinuit`, with `Dual BSD/GPL` license and the Unicode data permission notice.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-inuit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-roman.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/mac-roman.c

This file implements the Linux NLS module for classic Macintosh Roman, registered as `macroman`.

It is a generated mapping module for the base Mac Roman repertoire. `charset2uni[256]` preserves the lower ASCII/control range and maps high bytes to Western European accented Latin letters, punctuation, mathematical symbols, the Euro sign, Apple private-use `0xf8ff`, and ligatures `U+FB01`/`U+FB02`. Reverse lookup spans Unicode pages `page00`, `page01`, `page02`, `page03`, `page20`, `page21`, `page22`, `page25`, `pagef8`, and `pagefb`.

The implementation surface is the usual NLS table contract:
- `uni2char()` maps a Unicode `wchar_t` to a one-byte codepage value via `page_uni2charset`.
- `char2uni()` maps one input byte through `charset2uni`.
- Both reject unmappable values with `-EINVAL`; `uni2char()` also returns `-ENAMETOOLONG` for zero output capacity.
- `struct nls_table table` exposes the callbacks and case tables under `.charset = "macroman"`.

This is the broadest Mac table in this group because it includes the extra ligature reverse page `pagefb`. Like the related generated Mac modules, `charset2lower` and `charset2upper` are filled with `0xff`, so the file does not provide meaningful case conversion even though the fields are wired into the table.

The module uses standard init/exit registration and declares `MODULE_DESCRIPTION("NLS Codepage macroman")`, `MODULE_LICENSE("Dual BSD/GPL")`, and the Unicode data permission notice.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-roman.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-romanian.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/mac-romanian.c

This file implements the Linux NLS module for Macintosh Romanian, registered as `macromanian`.

The file is a generated single-byte charset translation table. `charset2uni[256]` is mostly Mac Roman-like, but it replaces some high-byte entries with Romanian-specific letters: `U+0102/U+0103`, `U+0218/U+0219`, and `U+021A/U+021B` are present in the high range. Reverse conversion uses sparse Unicode page arrays `page00`, `page01`, `page02`, `page03`, `page20`, `page21`, `page22`, `page25`, and `pagef8`.

The conversion mechanics match the other generated NLS modules. `uni2char()` performs a reverse page lookup from Unicode to one byte, bounds-checks output length, and reports unmappable characters. `char2uni()` maps one byte to Unicode and treats `0x0000` table entries as invalid. The exported NLS table supplies these callbacks plus lower/upper tables to the common NLS framework.

The table differs from `mac-roman.c` mainly by Romanian byte assignments and by not carrying the `pagefb` ligature reverse table. The case tables are all `0xff`, so any caller needing case-insensitive matching should not rely on this module for Romanian case folding.

Lifecycle and metadata are standard: `init_nls_macromanian()` registers, `exit_nls_macromanian()` unregisters, and the module is described as `NLS Codepage macromanian` under `Dual BSD/GPL`, with the Unicode data permission notice.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-romanian.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-turkish.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/mac-turkish.c

This file implements the Linux NLS module for Macintosh Turkish, registered as `macturkish`.

The generated mapping is based on Mac Roman with Turkish-specific assignments. `charset2uni[256]` maps high bytes to Western European characters plus Turkish letters such as `U+011E/U+011F`, `U+0130/U+0131`, and `U+015E/U+015F`. It also contains the Apple private-use mapping `0xf0 -> 0xf8ff` and a Turkish-specific private-use value `0xf5 -> 0xf8a0`. Reverse lookup uses `page00`, `page01`, `page02`, `page03`, `page20`, `page21`, `page22`, `page25`, and `pagef8`.

The operational code is the shared NLS generated skeleton. `uni2char()` maps Unicode back to one byte through sparse pages and enforces output capacity. `char2uni()` maps one byte to Unicode and rejects null mappings. The `nls_table` binds `.charset = "macturkish"`, the callbacks, and static case arrays.

The reverse mapping includes Turkish letters in `page01` and the private-use `pagef8` entry, making it different from the base Mac Roman table even though much of the punctuation and Latin mapping is shared. As with the other Mac generated modules here, `charset2lower` and `charset2upper` are filled with `0xff`, so Turkish dotted/dotless-I case behavior is not implemented by these tables.

The file registers/unregisters through the kernel NLS registry and declares `MODULE_DESCRIPTION("NLS Codepage macturkish")`, `Dual BSD/GPL`, and the Unicode data permission notice.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/mac-turkish.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_ascii.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_ascii.c

This file implements the minimal Linux NLS module for ASCII, registered as charset `ascii`.

The module contains a 128-entry `charset2uni` table for `0x00` through `0x7f`, a `page00` reverse table for Unicode page 0, and ASCII case-conversion tables. Unlike the Mac generated modules in this group, `charset2lower` and `charset2upper` contain real ASCII folding for `A-Z` and `a-z`.

The conversion callbacks are simple:
- `uni2char()` indexes `page_uni2charset` by the high Unicode byte and returns a one-byte ASCII value only if the reverse table entry is nonzero.
- `char2uni()` maps the input byte through `charset2uni`; because the table only has explicit data for ASCII range, high-byte use would be outside the intended charset contract.
- Both callbacks reject `0x0000` as an ordinary character because zero table entries are used as “unmapped.”

`struct nls_table table` wires the charset name, conversion callbacks, and case maps. `init_nls_ascii()` registers the table; `exit_nls_ascii()` unregisters it. Module metadata declares `NLS ASCII (United States)` and `Dual BSD/GPL`.

This file is the straightforward single-byte baseline used when filesystems request ASCII-only name conversion.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_ascii.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_base.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_base.c

This file is the core Linux filesystem Native Language Support implementation. It provides UTF conversion helpers, NLS table registration/loading, and the built-in fallback default table.

The UTF-8/UTF-32 path uses `utf8_table[]` to validate sequence length, bit masks, minimum encoded value, `UNICODE_MAX`, and surrogate exclusion. `utf8_to_utf32()` returns the number of consumed bytes or `-EILSEQ`/`-EOVERFLOW`. `utf32_to_utf8()` emits UTF-8 for a scalar value, rejects invalid Unicode and surrogate code points, and returns `-EOVERFLOW` when the output buffer is too small.

The UTF-8/UTF-16 helpers support native, little-endian, and big-endian UTF-16 through `put_utf16()` and `get_utf16()`. `utf8s_to_utf16s()` converts UTF-8 input to UTF-16 code units and emits surrogate pairs for non-BMP values. `utf16s_to_utf8s()` converts UTF-16 strings to UTF-8, skips malformed surrogate input, and stops when a valid character no longer fits in the output buffer.

The NLS registry is a global linked list rooted at `tables`, protected by `nls_lock`. `__register_nls()` inserts a table after checking for double registration, `unregister_nls()` removes a table, `find_nls()` matches by charset or alias while taking a module reference, `load_nls()` invokes module autoloading with `nls_%s`, and `unload_nls()` drops the module reference. `load_nls_default()` attempts `CONFIG_NLS_DEFAULT` and falls back to `default_table`.

The built-in `default_table` is an identity-style 8-bit mapping for Unicode page 0, with ASCII case folding for the alphabetic ASCII range. It uses the same `uni2char()` and `char2uni()` skeleton as generated modules, but spans all `0x00`-`0xff` byte values in `charset2uni` and `page00`.

Exports include UTF conversion functions and NLS registry APIs. Module metadata identifies this as `Base file system native language support` under `Dual BSD/GPL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_base.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp1250.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp1250.c

This file implements the Windows CP1250 NLS module for Slavic/Central European languages, registered as `cp1250`.

`charset2uni[256]` maps CP1250 bytes to Unicode, preserving ASCII/control values and mapping high bytes to Central European Latin characters, punctuation, currency/symbols, and combining-like spacing diacritics. Undefined CP1250 byte positions are represented by `0x0000`. Reverse conversion uses Unicode pages `page00`, `page01`, `page02`, `page20`, and `page21`.

The file provides meaningful case conversion tables. `charset2lower` and `charset2upper` preserve ASCII case folding and also map Central European uppercase/lowercase byte pairs where representable in CP1250. This makes it more useful for case-insensitive filename handling than the Mac tables in this group.

The conversion callbacks follow the NLS convention: one Unicode code point to one byte in `uni2char()`, one byte to one Unicode code point in `char2uni()`, with `-ENAMETOOLONG` on missing output capacity and `-EINVAL` for unmappable values.

Module lifecycle is standard: `init_nls_cp1250()` registers the table and `exit_nls_cp1250()` unregisters it. Metadata declares `NLS Windows CP1250 (Slavic/Central European Languages)` and `Dual BSD/GPL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp1250.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp1251.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp1251.c

This file implements the Windows CP1251 NLS module, described for Bulgarian and Belarusian and registered as `cp1251`.

`charset2uni[256]` maps CP1251 bytes to Unicode, with Cyrillic uppercase/lowercase ranges at `0xc0`-`0xff`, Cyrillic extensions in the `0x80` and `0xa0` ranges, and punctuation/symbol mappings such as Euro, quotes, dashes, bullet, trademark, and numero sign. Undefined bytes are encoded as `0x0000`. Reverse lookup is stored in `page00`, `page04`, `page20`, and `page21`.

The case tables are meaningful. `charset2lower` maps ASCII uppercase to lowercase and maps Cyrillic uppercase bytes to their lowercase byte equivalents. `charset2upper` performs the inverse for ASCII and Cyrillic, including special CP1251 Cyrillic letters in the upper control-extension range.

The conversion callbacks are the common NLS generated form. `uni2char()` does sparse reverse lookup and rejects unmappable Unicode values; `char2uni()` maps input bytes and rejects `0x0000` entries. The table exposes these callbacks as `.charset = "cp1251"`.

The module registers through `init_nls_cp1251()`, unregisters through `exit_nls_cp1251()`, and declares `MODULE_DESCRIPTION("NLS Windows CP1251 (Bulgarian, Belarusian)")` with `Dual BSD/GPL` license.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp1251.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp1255.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp1255.c

This file implements the Windows CP1255 Hebrew NLS module and also exposes alias `iso8859-8`.

`charset2uni[256]` maps CP1255 bytes to Unicode. The high range includes Hebrew points and punctuation (`U+05B0` through `U+05C3`), Hebrew letters (`U+05D0` through `U+05EA`), Yiddish ligature letters (`U+05F0` through `U+05F4`), New Sheqel sign, common Windows punctuation, and undefined slots as `0x0000`. Reverse lookup uses `page00`, `page01`, `page02`, `page05`, `page20`, and `page21`.

The NLS table differs from the other Windows files by declaring `.alias = "iso8859-8"` and `MODULE_ALIAS_NLS(iso8859-8)`, allowing module resolution by either CP1255 or ISO-8859-8 naming even though the table is CP1255-oriented.

The case tables preserve ASCII folding but Hebrew code points themselves have no uppercase/lowercase distinction. Many undefined/nonalphabetic high bytes map to `0x00`, while Hebrew byte ranges are effectively identity-preserved for upper/lower fields.

The conversion callbacks are standard: `uni2char()` maps one Unicode code point to one byte via sparse reverse pages, and `char2uni()` maps one byte to Unicode. Both treat unmapped entries as errors, with `uni2char()` also enforcing output capacity.

Lifecycle is standard registration/unregistration. Metadata declares `NLS Hebrew charsets (ISO-8859-8, CP1255)`, `Dual BSD/GPL`, and the NLS alias.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp1255.c -->