# Group Research: group_796_linux_sources_os_linux_linux_fs_nls_mac_greek_c_sources_os_linux_lin_86e762b77566

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`. This grouped report covers the requested Linux NLS charset conversion modules and the shared NLS base implementation.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-greek.c -->
# File Research: sources/os/linux/linux/fs/nls/mac-greek.c

Implements the `macgreek` NLS codepage module.

Key behavior:
- Provides generated Unicode Organization mapping tables for the Mac Greek single-byte charset.
- `charset2uni[256]` maps each input byte to Unicode; bytes `0x00` and any table entries mapped to `0x0000` are treated as invalid by `char2uni()`.
- Reverse conversion is sparse through `page_uni2charset[]`, with populated Unicode pages `00`, `01`, `03`, `20`, `21`, and `22`.
- `uni2char()` returns `-ENAMETOOLONG` if no output byte fits and `-EINVAL` when a Unicode code point has no exact Mac Greek byte.
- Registers `struct nls_table` with charset name `macgreek`.

Important interactions:
- Loaded by the NLS core through `register_nls()` / `unregister_nls()`.
- Exposes generated `charset2lower` and `charset2upper` tables, but this file’s case maps are placeholder-like rather than a rich Greek case-folding implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-greek.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-iceland.c -->
# File Research: sources/os/linux/linux/fs/nls/mac-iceland.c

Implements the `maciceland` NLS codepage module.

Key behavior:
- Provides generated Mac Iceland byte-to-Unicode and Unicode-to-byte mappings.
- The forward map covers ASCII plus Mac Iceland extended Latin, punctuation, math symbols, Icelandic letters, the Apple private-use glyph `0xf8ff`, and related modifier marks.
- Reverse lookup uses populated Unicode pages `00`, `01`, `02`, `03`, `20`, `21`, `22`, `25`, and `f8`.
- `char2uni()` rejects bytes mapping to `0x0000`; `uni2char()` only accepts exact reverse mappings.
- Registers charset name `maciceland`.

Important interactions:
- Follows the standard Linux NLS module shape used by filesystem filename conversion.
- Case conversion tables are generated data supplied through `struct nls_table`, not computed dynamically.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-iceland.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-inuit.c -->
# File Research: sources/os/linux/linux/fs/nls/mac-inuit.c

Implements the `macinuit` NLS codepage module.

Key behavior:
- Provides generated mappings for a Mac Inuit charset centered on Canadian Aboriginal Syllabics.
- The extended byte range maps heavily into Unicode pages `14`, `15`, and `16`, with some Latin, punctuation, and symbol entries.
- Reverse lookup is sparse through pages `00`, `01`, `14`, `15`, `16`, `20`, and `21`.
- Uses the common one-byte conversion callbacks:
  - `char2uni()` maps one byte to one Unicode value.
  - `uni2char()` maps one Unicode value to one byte only when the reverse table has an exact entry.
- Registers charset name `macinuit`.

Important interactions:
- The generated lower/upper tables are unusual: broad placeholder-style values dominate rather than normal ASCII-style case folding.
- Consumers should treat this module primarily as exact charset conversion data.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-inuit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-roman.c -->
# File Research: sources/os/linux/linux/fs/nls/mac-roman.c

Implements the `macroman` NLS codepage module.

Key behavior:
- Provides generated Mac Roman mappings for ASCII, Western European Latin characters, punctuation, math symbols, ligatures, and the Apple private-use glyph.
- Reverse lookup includes pages `00`, `01`, `02`, `03`, `20`, `21`, `22`, `25`, `f8`, and `fb`; page `fb` handles `fb01` and `fb02` ligatures.
- `uni2char()` encodes only exact Unicode-to-byte mappings and returns `-EINVAL` otherwise.
- `char2uni()` decodes a single byte and rejects `0x0000`.
- Registers charset name `macroman`.

Important interactions:
- This is the base Mac Roman variant that the Icelandic, Romanian, and Turkish modules resemble structurally.
- Used by filesystem NLS users that need legacy Mac Roman filename translation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-roman.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-romanian.c -->
# File Research: sources/os/linux/linux/fs/nls/mac-romanian.c

Implements the `macromanian` NLS codepage module.

Key behavior:
- Provides generated mappings for Mac Romanian, mostly Mac Roman-compatible with Romanian-specific substitutions.
- Includes Romanian code points such as `0102/0103`, `0218/0219`, and `021a/021b`.
- Reverse lookup uses pages `00`, `01`, `02`, `03`, `20`, `21`, `22`, `25`, and `f8`.
- Conversion callbacks are exact one-byte mappings with `-ENAMETOOLONG` for no output space and `-EINVAL` for unmappable Unicode or invalid decoded bytes.
- Registers charset name `macromanian`.

Important interactions:
- Shares the same Linux NLS module registration path and conversion contract as the other generated Mac codepages.
- Case mapping data is table-supplied, not locale-sensitive logic.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-romanian.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-turkish.c -->
# File Research: sources/os/linux/linux/fs/nls/mac-turkish.c

Implements the `macturkish` NLS codepage module.

Key behavior:
- Provides generated mappings for Mac Turkish.
- Extends the Mac Roman-style table with Turkish-specific characters including `011e/011f`, `0130/0131`, and `015e/015f`.
- Includes a private-use mapping at `0xf8a0` and the Apple private-use glyph `0xf8ff`.
- Reverse lookup uses pages `00`, `01`, `02`, `03`, `20`, `21`, `22`, `25`, and `f8`.
- Registers charset name `macturkish`.

Important interactions:
- Supplies exact byte/Unicode conversion through the shared `struct nls_table` interface.
- No multibyte state exists; every conversion consumes or emits exactly one byte on success.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/mac-turkish.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_ascii.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_ascii.c

Implements the `ascii` NLS codepage module.

Key behavior:
- Defines a 7-bit ASCII `charset2uni` table for bytes `0x00` through `0x7f`; bytes above `0x7f` default to `0x0000` and are invalid.
- Reverse lookup is only populated for Unicode page `00`.
- `uni2char()` returns one byte for exact ASCII mappings except NUL, and rejects unmappable values.
- `char2uni()` rejects byte `0x00` because it maps to `0x0000`.
- Provides ASCII lower/upper case conversion tables for `A-Z` and `a-z`.
- Registers charset name `ascii`.

Important interactions:
- Used as a minimal NLS table for filesystems needing strict ASCII filename conversion.
- Module lifecycle is standard `register_nls()` on init and `unregister_nls()` on exit.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_ascii.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_base.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_base.c

Implements the shared Linux native language support registry and UTF conversion helpers.

Key behavior:
- Maintains a global linked list of `struct nls_table` entries protected by `nls_lock`.
- `__register_nls()` adds a table and rejects duplicate/already-linked registrations.
- `unregister_nls()` removes a registered table.
- `find_nls()` searches by charset or alias and pins the owning module with `try_module_get()`.
- `load_nls()` requests `nls_<charset>` modules on demand.
- `unload_nls()` drops the module reference.
- `load_nls_default()` tries `CONFIG_NLS_DEFAULT`, falling back to the built-in `default_table`.
- Implements UTF helpers:
  - `utf8_to_utf32()`
  - `utf32_to_utf8()`
  - `utf8s_to_utf16s()`
  - `utf16s_to_utf8s()`
- UTF validation rejects overlong encodings, surrogate code points, and code points above `0x10ffff`.

Important interactions:
- Exports NLS registry and UTF conversion symbols for filesystem code and charset modules.
- The built-in `default_table` is a single-byte identity-style table for bytes `0x01` through `0xff`, with ASCII-style case maps.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_base.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_cp1250.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_cp1250.c

Implements the `cp1250` Windows Central European NLS codepage module.

Key behavior:
- Provides generated Windows CP1250 mappings for Central European and Slavic Latin characters.
- `charset2uni` includes undefined CP1250 bytes as `0x0000`, which `char2uni()` rejects.
- Reverse lookup uses pages `00`, `01`, `02`, `20`, and `21`.
- Case tables include ASCII and CP1250-specific upper/lower mappings for accented Latin letters.
- Registers charset name `cp1250`.

Important interactions:
- Used by filesystems that expose or consume CP1250-encoded filenames.
- Exact reverse mappings mean Unicode characters without a CP1250 byte fail instead of being approximated.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_cp1250.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_cp1251.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_cp1251.c

Implements the `cp1251` Windows Cyrillic NLS codepage module.

Key behavior:
- Provides generated Windows CP1251 mappings for Cyrillic plus punctuation and symbols.
- `charset2uni` maps Cyrillic uppercase/lowercase ranges directly in `0xc0-0xff`, with additional Cyrillic letters in `0x80-0xbf`.
- Reverse lookup uses pages `00`, `04`, `20`, and `21`.
- Case tables encode Cyrillic case conversion as well as ASCII case conversion.
- Registers charset name `cp1251`.

Important interactions:
- The module description names Bulgarian and Belarusian, but the table is the general Windows CP1251 charset.
- Like the other table modules, it performs no best-fit transliteration.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_cp1251.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_cp1255.c -->
# File Research: sources/os/linux/linux/fs/nls/nls_cp1255.c

Implements the `cp1255` Hebrew NLS codepage module, with an `iso8859-8` alias.

Key behavior:
- Provides CP1255 mappings for Hebrew letters, Hebrew marks, punctuation, and common Windows symbols.
- Forward map includes Hebrew Unicode page `05` entries and undefined bytes as `0x0000`.
- Reverse lookup uses pages `00`, `01`, `02`, `05`, `20`, and `21`.
- Registers charset name `cp1255` and alias `iso8859-8`.
- Declares `MODULE_ALIAS_NLS(iso8859-8)` so module autoload can satisfy that alias.

Important interactions:
- `find_nls()` in `nls_base.c` can match either `.charset` or `.alias`, so callers asking for `iso8859-8` can receive this table.
- The file describes both ISO-8859-8 and CP1255, but the actual table contains Windows CP1255-specific positions as well.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nls/nls_cp1255.c -->