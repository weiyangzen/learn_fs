# subset-b-005708 research

Grouped research for Linux native language support tables under `sources/distributed-fs/ceph-client/fs/nls`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-greek.c -->
# sources/distributed-fs/ceph-client/fs/nls/mac-greek.c

## Purpose
`mac-greek.c` implements the Linux NLS module for the classic Macintosh Greek single-byte code page. It translates between 8-bit on-disk or user-facing bytes and Unicode `wchar_t` code points for filesystems that select the `macgreek` charset. The file is almost entirely generated lookup data plus the standard NLS adapter functions and module registration hooks.

## Important APIs, types, and functions
The core data is `charset2uni[256]`, which maps each byte value to Unicode. The upper half includes Greek capital and lowercase letters, Greek tonos/dialytika variants, mathematical symbols, punctuation, `0x20ac`, and compatibility characters; zero entries mark unmappable bytes. Reverse conversion uses page tables `page00`, `page01`, `page03`, `page20`, `page21`, and `page22`, referenced through `page_uni2charset[256]` by Unicode high byte.

`uni2char()` validates `boundlen`, selects the relevant page table from the Unicode high byte, and returns either one output byte or `-EINVAL`/`-ENAMETOOLONG`. `char2uni()` indexes `charset2uni` and rejects mappings whose result is `0x0000`. `charset2lower` and `charset2upper` provide byte-level case folding for consumers using `nls_tolower()`/`nls_toupper()`. `table` is a `struct nls_table` with `.charset = "macgreek"`, the conversion callbacks, and case tables. `init_nls_macgreek()` and `exit_nls_macgreek()` register and unregister the table.

## Control flow
Module load calls `register_nls(&table)` from `init_nls_macgreek()`. Filesystem code later resolves `"macgreek"` through `load_nls()` in `nls_base.c` and calls the table callbacks. Byte-to-Unicode conversion is direct: the input byte indexes `charset2uni`, and a zero Unicode result is treated as invalid. Unicode-to-byte conversion splits the `wchar_t` into high and low bytes, uses the high byte to find a reverse page, then uses the low byte to fetch the output byte. The reverse page value `0x00` is also treated as unmapped, so Unicode NUL is not convertible through this table.

## State and persistence behavior
The module has no persistent or mutable runtime data beyond the `struct nls_table` linkage maintained by the NLS registry. All translation tables are `static const`; conversion calls are stateless and deterministic. Loading pins the module through the registry owner reference, and unloading removes the table from the global list.

## Dependencies and integration points
This file depends on Linux module, kernel, string, errno, and NLS headers. It integrates with the common NLS registry provided by `nls_base.c` and with filesystem clients such as FAT/VFAT that translate filenames through `struct nls_table`. The Unicode data license block indicates generated source from Unicode charset tables, so regeneration must preserve exact mapping semantics and license text.

## Risks and test signals
The main risks are table accuracy, especially for Greek-specific bytes, reverse mapping collisions, and the convention that `0x0000`/`0x00` means invalid rather than a valid NUL mapping. Case-folding tables must match Macintosh Greek expectations or case-insensitive filename lookup can regress. Useful tests load `nls_macgreek`, round-trip representative Greek letters and accented forms, verify invalid bytes or missing Unicode mappings return `-EINVAL`, confirm `boundlen == 0` returns `-ENAMETOOLONG`, and exercise case-insensitive VFAT lookup using Greek names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-greek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-iceland.c -->
# sources/distributed-fs/ceph-client/fs/nls/mac-iceland.c

## Purpose
`mac-iceland.c` provides the NLS implementation for the classic Macintosh Icelandic code page, registered as `maciceland`. It maps single-byte Macintosh Icelandic filename characters to Unicode and back for filesystem code that requests this charset.

## Important APIs, types, and functions
`charset2uni[256]` maps bytes to Unicode. The ASCII/control range is identity-like except for byte zero being represented as invalid, while the high range carries Latin letters and symbols needed by Mac Icelandic, including Icelandic/Nordic characters, typographic punctuation, mathematical symbols, ligatures, `0x0178`, `0x2044`, and `0x20ac`. Reverse mappings are split across `page00`, `page01`, `page02`, `page03`, `page20`, `page21`, `page22`, `page25`, and `pagef8`, with `page_uni2charset` pointing only at populated Unicode pages.

The public surface is the `struct nls_table table` for `"maciceland"`. `uni2char()` and `char2uni()` are the standard one-byte generated NLS callbacks. `charset2lower` and `charset2upper` encode byte-preserving case conversion. `init_nls_maciceland()` registers the table at module init, and `exit_nls_maciceland()` unregisters it.

## Control flow
On module initialization, the table is inserted into the global NLS table list. Consumers obtain it by name and call `char2uni()` while decoding byte strings or `uni2char()` while encoding Unicode. `char2uni()` performs one array lookup and rejects `0x0000`. `uni2char()` rejects empty output buffers, derives `ch = uni >> 8` and `cl = uni & 0xff`, looks up the page, then writes one byte only if the page exists and the entry is nonzero.

## State and persistence behavior
The file keeps no dynamic state. All charset, reverse, and casefold tables are immutable. Runtime state is limited to module registration in `nls_base.c`; there is no on-disk persistence and no caching inside this module.

## Dependencies and integration points
The module uses the Linux NLS ABI from `<linux/nls.h>` and returns kernel errno values from `<linux/errno.h>`. It integrates with NLS loading by charset name and with filesystems that store or expose filenames in Mac Icelandic. Its behavior must remain compatible with `nls_base.c` registry locking and module owner pinning.

## Risks and test signals
High-risk areas are exact byte assignments for Icelandic-specific letters, reverse mappings for symbols outside page 00, and case table correctness for accented Latin letters. Because zero in reverse pages signals unmapped, accidental valid mappings to byte zero cannot be represented. Test signals include module load/unload, known byte-to-Unicode vectors for Icelandic characters such as eth/thorn and accented vowels, reverse vectors from Unicode to bytes, case-insensitive comparisons, invalid Unicode page rejection, and buffer-size error behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-iceland.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-inuit.c -->
# sources/distributed-fs/ceph-client/fs/nls/mac-inuit.c

## Purpose
`mac-inuit.c` implements the `macinuit` NLS table for Macintosh Inuit/Inuktitut text. It is a single-byte charset adapter that maps high-byte values to Unicode Canadian Aboriginal Syllabics code points and selected Latin/symbol characters, enabling filename conversion when a filesystem is configured for this legacy Macintosh encoding.

## Important APIs, types, and functions
`charset2uni[256]` is the forward byte-to-Unicode table. The high half prominently maps into Unicode pages `0x14`, `0x15`, and `0x16` for syllabics, with additional punctuation, trademark/copyright symbols, `0x0141`, and `0x0142`. Reverse conversion uses `page00`, `page01`, `page14`, `page15`, `page16`, `page20`, and `page21` through `page_uni2charset`.

The conversion callbacks are the generated `uni2char()` and `char2uni()` functions. `uni2char()` enforces a one-byte output buffer, rejects missing reverse pages or zero entries, and returns one byte on success. `char2uni()` rejects entries that map to `0x0000`. `table` registers `.charset = "macinuit"` with conversion and byte-case tables. `init_nls_macinuit()` and `exit_nls_macinuit()` are the module lifecycle hooks.

## Control flow
The module follows the common NLS table pattern. Initialization registers the table; consumers load it by the `macinuit` name; each conversion is a stateless table lookup. Unlike multibyte encodings, there is no shift state, lead-byte handling, combining logic, or normalization. Case conversion is table based and byte oriented; most syllabic bytes map to themselves because the charset does not have ASCII-like upper/lower pairs for those symbols.

## State and persistence behavior
There is no mutable file-local state. Mapping data and case tables are `static const`, and all persistence remains in the filesystem using this translation layer. Registry state is external in the NLS core and only changes at module load/unload.

## Dependencies and integration points
The file depends on the NLS module ABI and is loaded through the same `load_nls()` path as other charset modules. It can be used by FAT/VFAT-style filename conversion or any kernel user of `struct nls_table`. Because it includes Unicode-generated data and license text, maintainers should regenerate it from authoritative tables rather than manually edit individual code points.

## Risks and test signals
The risk profile is dominated by table correctness for syllabic code points and reverse page coverage. Missing reverse entries make Unicode names impossible to encode even if byte-to-Unicode decoding works. Test coverage should include representative byte ranges that map to pages 14, 15, and 16; round-trip checks for syllabic characters; invalid Unicode inputs outside populated pages; ASCII passthrough except NUL; and module lifecycle registration. Filesystem tests should create, lookup, and compare names containing syllabics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-inuit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-roman.c -->
# sources/distributed-fs/ceph-client/fs/nls/mac-roman.c

## Purpose
`mac-roman.c` is the NLS module for the classic Macintosh Roman charset, registered as `macroman`. It is the general Western Macintosh single-byte mapping used for legacy filenames and metadata conversion in filesystems that request this code page.

## Important APIs, types, and functions
`charset2uni[256]` maps bytes to Unicode and includes Western Latin accents, typographic punctuation, currency symbols, mathematical operators, Greek pi/omega symbols, Apple private-use style entries in page `0xf8`, and ligatures in page `0xfb`. Reverse mapping is larger than many sibling files: `page00`, `page01`, `page02`, `page03`, `page20`, `page21`, `page22`, `page25`, `pagef8`, and `pagefb` are reachable through `page_uni2charset`.

`uni2char()` and `char2uni()` are the generated callback pair used by `struct nls_table`. `charset2lower` and `charset2upper` define Mac Roman byte case folding. `table` binds `.charset = "macroman"` to those callbacks. `init_nls_macroman()` registers the table, and `exit_nls_macroman()` unregisters it.

## Control flow
Load-time control flow is only module registration. Runtime conversion is table driven: byte input becomes Unicode with one indexed read; Unicode input becomes a byte by splitting the code point into a page selector and offset. The reverse path only succeeds when `page_uni2charset[ch]` exists and its entry for `cl` is nonzero. All successful conversions consume or produce exactly one byte.

## State and persistence behavior
The module stores no per-mount or per-call state. It relies on static immutable mapping tables and the external global NLS registry. It does not persist data; it only interprets byte sequences supplied by filesystem code.

## Dependencies and integration points
The file plugs into the generic Linux NLS registry and is likely to be used by FAT/VFAT and other legacy-media paths when `iocharset=macroman` or equivalent configuration is requested. It depends on `nls_base.c` for registration, module pinning, lookup by charset name, and unload handling.

## Risks and test signals
Mac Roman has broad symbol coverage, so reverse pages beyond basic Latin are easy to regress during regeneration. Case-folding must be checked for accented Latin bytes, not just ASCII. The NLS convention that byte zero is invalid means embedded NUL is not representable. Useful tests include known Mac Roman mapping vectors, round trips for accents, ligatures, and page `0xf8`/`0xfb` entries, case-insensitive filename comparison, invalid Unicode rejection, and error behavior for too-small output buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-roman.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-romanian.c -->
# sources/distributed-fs/ceph-client/fs/nls/mac-romanian.c

## Purpose
`mac-romanian.c` implements the Macintosh Romanian NLS table, registered as `macromanian`. It adapts the Mac Roman-style Western charset layout for Romanian-specific characters, allowing single-byte filename conversion to and from Unicode.

## Important APIs, types, and functions
Forward mapping is held in `charset2uni[256]`. The high-byte range resembles Mac Roman but includes Romanian-specific code points such as `0x0103` and `0x0219` in positions where the base Roman table maps other Western characters. Reverse conversion uses `page00`, `page01`, `page02`, `page03`, `page20`, `page21`, `page22`, `page25`, and `pagef8`. The file provides generated byte case tables for NLS case operations.

The functional API is `uni2char()`, `char2uni()`, `init_nls_macromanian()`, and `exit_nls_macromanian()`. The `struct nls_table table` sets `.charset = "macromanian"` and points to the generated conversion and case tables.

## Control flow
The module registers its table at initialization and unregisters it at exit. Consumers do not call file-local functions directly; they receive the `struct nls_table` from `load_nls()`. Conversion then flows through single array lookups. `char2uni()` reads `charset2uni[*rawstring]`; `uni2char()` looks up the Unicode page and byte within the reverse table. Both paths return one on success and negative errno on invalid or oversized conditions.

## State and persistence behavior
All mapping state is immutable static data. The only mutable state is the table's linkage in the NLS registry and the module owner reference managed outside this file. There are no caches, locks, or persistent side effects in the module itself.

## Dependencies and integration points
The module depends on the standard kernel module and NLS headers and shares the common table structure with other generated Mac charset files. It integrates with filesystem mount options or charset lookups that request `macromanian`. It relies on `nls_base.c` for lookup, registration locking, and module reference management.

## Risks and test signals
The most important risks are confusing this table with `macroman` or `macturkish`, since the files have nearly identical structure but different high-byte Romanian mappings and case tables. Regeneration should be diffed against authoritative Unicode mapping data. Tests should include Romanian-specific bytes and reverse Unicode mappings, case folding for Romanian letters, ASCII passthrough, invalid mapping rejection, module load/unload, and filesystem create/lookup operations with Romanian names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-romanian.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-turkish.c -->
# sources/distributed-fs/ceph-client/fs/nls/mac-turkish.c

## Purpose
`mac-turkish.c` provides the Macintosh Turkish NLS module, registered as `macturkish`. It maps legacy single-byte Turkish Macintosh filenames to Unicode and encodes Unicode back to the charset where exact mappings exist.

## Important APIs, types, and functions
`charset2uni[256]` holds forward byte mappings. The table is Mac Roman-like in structure but differs for Turkish letters and related case pairs such as dotted/dotless I and other Turkish-specific Latin characters. Reverse conversion is split into `page00`, `page01`, `page02`, `page03`, `page20`, `page21`, `page22`, `page25`, and `pagef8`, selected through `page_uni2charset`.

`uni2char()` and `char2uni()` implement the NLS callback contract. The `charset2lower` and `charset2upper` arrays are especially important here because Turkish case behavior differs from simple ASCII assumptions. `table` registers the callbacks under `.charset = "macturkish"`. `init_nls_macturkish()` calls `register_nls()`, and `exit_nls_macturkish()` calls `unregister_nls()`.

## Control flow
On module load, registration makes the table discoverable. Runtime control flow is a one-character conversion path: byte-to-Unicode indexes `charset2uni`; Unicode-to-byte derives a reverse page and byte offset. Missing mappings and zero entries return `-EINVAL`, and an output bound of zero or less returns `-ENAMETOOLONG`. There is no multibyte parsing or locale-sensitive dynamic logic.

## State and persistence behavior
The file is stateless aside from module registration. Static tables are read-only and shared by all callers. No filesystem state is written by this module, and no conversion history is retained.

## Dependencies and integration points
It depends on `<linux/nls.h>` and the core registry in `nls_base.c`. Filesystems that support configurable NLS charsets use the `macturkish` table through `struct nls_table` callbacks and byte case helpers. The exact mapping comes from generated Unicode charset data, so integration compatibility is table-data compatibility rather than algorithm complexity.

## Risks and test signals
Turkish-specific case folding is the key behavioral risk. Incorrect upper/lower tables can break case-insensitive lookup even if round-trip conversion works. Other risks include accidentally inheriting values from Mac Roman during regeneration, missing reverse mappings for Turkish letters, and the invalid-NUL convention. Tests should cover dotted and dotless I byte mappings, other Turkish Latin letters, lower/upper table behavior, invalid Unicode pages, `boundlen` handling, module registration, and filename lookup on a case-insensitive filesystem path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/mac-turkish.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_ascii.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_ascii.c

## Purpose
`nls_ascii.c` implements the `ascii` NLS charset. It provides exact one-byte conversion for 7-bit ASCII plus control bytes, with no mappings for bytes `0x80` through `0xff`. This is the simplest loadable NLS table and serves filesystems that explicitly request ASCII conversion.

## Important APIs, types, and functions
`charset2uni[256]` contains entries only through `0x7f`; uninitialized trailing entries are zero and therefore invalid. `page00[256]` provides reverse mappings for Unicode page 0 values through `0x7f`, while `page_uni2charset[256]` points only to `page00`. `charset2lower` and `charset2upper` implement ASCII case folding for `A-Z` and `a-z`.

`uni2char()` and `char2uni()` implement the standard single-byte NLS callbacks. `table` registers `.charset = "ascii"` with conversion and case tables. `init_nls_ascii()` and `exit_nls_ascii()` register and unregister the table with the NLS core.

## Control flow
The module initialization path calls `register_nls(&table)`. Consumers loading `"ascii"` then use the table callbacks. `char2uni()` indexes directly by input byte; because bytes above `0x7f` map to zero, they fail with `-EINVAL`. `uni2char()` accepts only Unicode values whose high byte points at `page00` and whose low byte maps to a nonzero output byte. A zero output buffer fails with `-ENAMETOOLONG`.

## State and persistence behavior
The file has no mutable state except its registration with the global NLS list. Translation tables are static constants and conversions are deterministic. No persistent filesystem metadata is changed here.

## Dependencies and integration points
The module depends on kernel module/NLS headers and the registry in `nls_base.c`. Filesystem clients use it by charset name and then call callbacks through `struct nls_table`, especially for filename conversion and byte case operations.

## Risks and test signals
The notable semantic detail is that `char2uni()` rejects byte `0x00`, and `uni2char()` rejects Unicode NUL, because zero also marks unmapped entries. Another risk is callers expecting ISO-8859-1 behavior for bytes above `0x7f`; this table intentionally rejects them. Tests should cover ASCII printable round trips, control-byte conversion except NUL behavior, rejection of high bytes, upper/lower ASCII case folding, `boundlen` errors, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_ascii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_base.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_base.c

## Purpose
`nls_base.c` is the core Linux filesystem Native Language Support implementation. It provides UTF-8/UTF-16 conversion helpers, maintains the global list of registered `struct nls_table` instances, supports module autoloading for charset names, and supplies the built-in `"default"` one-byte table used when `CONFIG_NLS_DEFAULT` cannot be loaded.

## Important APIs, types, and functions
The UTF helpers are `utf8_to_utf32()`, `utf32_to_utf8()`, `utf8s_to_utf16s()`, and `utf16s_to_utf8s()`, all exported. `struct utf8_table` describes UTF-8 sequence masks, minimum values, and shifts. Constants define `UNICODE_MAX`, `PLANE_SIZE`, and surrogate masks. `put_utf16()` and `get_utf16()` handle native, little-endian, and big-endian UTF-16 storage.

The registry APIs are `__register_nls()`, `unregister_nls()`, `load_nls()`, `unload_nls()`, and `load_nls_default()`. `find_nls()` searches by `.charset` or `.alias` and pins the owning module with `try_module_get()`. `tables` is the global linked list head, initialized to `default_table`, and `nls_lock` protects list mutation and lookup. `load_nls()` wraps lookup in `try_then_request_module(find_nls(charset), "nls_%s", charset)` so missing tables can be autoloaded.

The default table is a generated identity-style 8-bit mapping through `0xff`, with `charset2uni`, `page00`, reverse page pointers, and byte case tables. Its `struct nls_table` is named `"default"`.

## Control flow
UTF-8 decoding in `utf8_to_utf32()` walks `utf8_table`, accumulates continuation bits, rejects overlong encodings, values above `0x10ffff`, surrogate code points, incomplete sequences, and malformed continuation bytes. UTF-8 encoding in `utf32_to_utf8()` rejects invalid Unicode/surrogates, returns zero if the output pointer is NULL, and emits the shortest fitting sequence or `-EOVERFLOW`.

`utf8s_to_utf16s()` scans a NUL-terminated bounded UTF-8 input, decodes non-ASCII through `utf8_to_utf32()`, emits surrogate pairs for non-BMP code points when space permits, and stops when input, NUL, or output capacity ends. `utf16s_to_utf8s()` reads bounded UTF-16, stops at NUL, combines valid surrogate pairs, ignores unmatched low or invalid surrogate sequences, and stops rather than overflowing when encoded bytes do not fit.

Registration flow sets the module owner, checks that the table is not already linked, inserts at the head under `nls_lock`, and returns `-EBUSY` for duplicates. Unregister searches and unlinks under the same lock. Loading first searches the existing list, then asks kmod to request `nls_<charset>` if absent. Unloading decrements the module owner reference.

## State and persistence behavior
State is in-memory only. The global table list persists while the kernel runs and changes as NLS modules load or unload. The default table is always present. UTF conversion helpers keep no state between calls. There is no on-disk persistence, but filesystem-visible behavior depends on which NLS table is loaded and referenced by a mounted filesystem.

## Dependencies and integration points
This file is the integration point for all generated charset modules in `fs/nls`. It exports symbols used by filesystems and by other NLS modules. It depends on kernel module loading, spinlocks, byte-order helpers, errno conventions, and the `struct nls_table` ABI. Filesystems such as FAT/VFAT call `load_nls()`, store table pointers in superblock state, call conversion callbacks and case helpers, then call `unload_nls()` during teardown.

## Risks and test signals
The registry must avoid duplicate insertion, stale owner references, and races between lookup and unload. UTF conversion risks include accepting overlong UTF-8, surrogate values, truncated input, or writing past output bounds. The default table's zero-entry convention means NUL is invalid for callback conversion even though other bytes map identity-style. Tests should cover concurrent module load/unload, alias lookup, autoload request names, fallback through `load_nls_default()`, invalid UTF-8 sequences, surrogate handling, non-BMP UTF-16 pairs, endian modes, output capacity boundaries, and filesystem mount/unmount paths that load and release NLS tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp1250.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp1250.c

## Purpose
`nls_cp1250.c` implements the Windows CP1250 NLS table for Central European and Slavic languages. It converts single-byte CP1250 data to Unicode and exact Unicode mappings back to CP1250 for filesystem filename handling.

## Important APIs, types, and functions
`charset2uni[256]` maps CP1250 bytes to Unicode. The high range includes `0x20ac`, typographic punctuation, caron/breve/ogonek/double-acute marks, and Central European Latin letters such as L with stroke, S/Z/C/R variants, and other Slavic characters. Some CP1250 byte positions are `0x0000`, marking undefined bytes. Reverse mapping uses `page00`, `page01`, `page02`, `page20`, and `page21`.

`uni2char()` and `char2uni()` provide the generated callback pair. `charset2lower` and `charset2upper` encode CP1250-aware byte case folding. `table` registers `.charset = "cp1250"`. `init_nls_cp1250()` registers the table, and `exit_nls_cp1250()` unregisters it.

## Control flow
The lifecycle is standard for a loadable NLS module. At runtime, byte decoding is one `charset2uni` lookup with zero treated as invalid. Unicode encoding selects a reverse page by high byte, checks for a populated page and nonzero entry, writes the byte, and returns one. No normalization or best-fit substitution is attempted; the comments explicitly indicate exact Unicode-to-charset mappings only.

## State and persistence behavior
The module is stateless after registration. Static tables are immutable and shared. It does not persist data; filesystems persist bytes, while this table determines their interpretation for callers.

## Dependencies and integration points
The file depends on the Linux NLS module ABI and the `nls_base.c` registry. FAT/VFAT and similar filesystems can load `"cp1250"` as an on-disk or I/O charset, use conversion callbacks for filename translation, and use case tables during case-insensitive lookup.

## Risks and test signals
Central European case folding and undefined byte behavior are the main risks. CP1250 is often confused with ISO-8859-2; tests should verify Windows-specific positions such as euro and smart quotes as well as accented letters. Useful tests include known mapping vectors, undefined byte rejection, reverse mapping for page 01 and page 02 characters, upper/lower table validation, buffer bound errors, module lifecycle, and filesystem filename round trips for Polish, Czech, Slovak, Hungarian, and related names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp1250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp1251.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp1251.c

## Purpose
`nls_cp1251.c` provides the Windows CP1251 NLS table for Cyrillic-script languages. It maps CP1251 bytes to Unicode Cyrillic code points, punctuation, and symbols, and encodes exact Unicode matches back to one-byte CP1251.

## Important APIs, types, and functions
`charset2uni[256]` maps byte values to Unicode. The upper half contains Cyrillic letters in pages `0x04`, including Ukrainian/Belarusian/Serbian/Macedonian variants, plus punctuation such as smart quotes, dashes, `0x20ac`, `0x2116`, and `0x2122`. Reverse mapping uses `page00`, `page04`, `page20`, and `page21`.

The generated callback pair is `uni2char()`/`char2uni()`. `charset2lower` and `charset2upper` provide byte-level Cyrillic case folding. `table` registers `.charset = "cp1251"`, and the module entry/exit functions are `init_nls_cp1251()` and `exit_nls_cp1251()`.

## Control flow
Initialization registers the NLS table. Runtime conversion is exact and table driven. `char2uni()` turns a byte into a Unicode value and returns `-EINVAL` for undefined entries. `uni2char()` looks up the reverse page for the Unicode high byte and emits one byte if present. Empty output buffers return `-ENAMETOOLONG`; missing mappings return `-EINVAL`.

## State and persistence behavior
No mutable local state is kept. All mapping and case data is static constant data. The only runtime state is the NLS registry linkage and module owner reference managed by `nls_base.c`.

## Dependencies and integration points
The module integrates with Linux filesystems through `struct nls_table`. It is loaded by charset name `"cp1251"` and can be used for on-disk or I/O filename translation. The comments identify the generated Unicode table source, and the module description notes Bulgarian and Belarusian but the table covers the CP1251 Cyrillic repertoire more broadly.

## Risks and test signals
Risks include incorrect Cyrillic case folding, undefined byte handling, and mixups with KOI8 or ISO Cyrillic tables. Because Cyrillic upper/lower pairs span byte ranges, case-table regressions can break case-insensitive lookup. Tests should cover basic Russian Cyrillic letters, Ukrainian/Belarusian-specific letters, punctuation/euro mappings, undefined byte `0x98`, reverse page `0x04`, case folding, module load/unload, and filesystem name round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp1251.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp1255.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp1255.c

## Purpose
`nls_cp1255.c` implements the Windows CP1255 Hebrew NLS table and also exposes an alias for `iso8859-8`. It maps Hebrew letters, Hebrew points/punctuation, and CP1255 symbols to Unicode and provides exact reverse mappings for filesystem charset conversion.

## Important APIs, types, and functions
`charset2uni[256]` maps bytes to Unicode. The high range includes euro and typographic punctuation, Hebrew sheqel sign, Hebrew vowel points in `0x05b0` and related ranges, Hebrew punctuation and ligatures around `0x05f0`, and Hebrew letters `0x05d0` through `0x05ea`. Several bytes are undefined and map to `0x0000`. Reverse mapping uses `page00`, `page01`, `page02`, `page05`, `page20`, and `page21`.

`uni2char()` and `char2uni()` are the conversion callbacks. `charset2lower` and `charset2upper` are effectively identity-like for Hebrew because Hebrew has no upper/lower case, while preserving ASCII case behavior. `table` registers `.charset = "cp1255"` and `.alias = "iso8859-8"`. The file also declares `MODULE_ALIAS_NLS(iso8859-8)` so module autoload can satisfy alias requests. `init_nls_cp1255()` and `exit_nls_cp1255()` manage registration.

## Control flow
Module initialization registers the table. `find_nls()` in `nls_base.c` can match either `"cp1255"` or the alias `"iso8859-8"` and pin the module. Conversion itself is a one-byte lookup. `char2uni()` rejects undefined bytes; `uni2char()` rejects missing reverse pages, zero reverse entries, or insufficient output buffer length.

## State and persistence behavior
The module has immutable static tables and no local mutable state. Alias and charset names are fields in the registered table. Persistence is external to filesystems storing bytes; this module supplies interpretation only while loaded and referenced.

## Dependencies and integration points
It depends on the NLS registry and module alias machinery. Integration points include filesystem charset options that request either CP1255 or ISO-8859-8 naming. The alias behavior is notable because lookup by alias is handled by `nls_base.c` before or after module autoload.

## Risks and test signals
Alias behavior is the unique risk compared with most generated one-byte modules: both `cp1255` and `iso8859-8` requests should resolve to the same table, and autoload metadata must match. Mapping risk includes undefined Hebrew-point positions, sheqel/euro/punctuation mappings, and right-to-left filename test coverage at higher layers. Tests should cover Hebrew letters and vowel points, undefined byte rejection, reverse page `0x05`, alias loading by `iso8859-8`, ASCII case behavior, module unload after both names, and filesystem filename round trips using Hebrew strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp1255.c -->
