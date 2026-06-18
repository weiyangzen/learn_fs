# Research: subset-b-005722

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_euc-jp.c -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_euc-jp.c

## Purpose

This file implements the Linux NLS table for Japanese `euc-jp` by translating through the existing `cp932` table. It is not a generated Unicode mapping table by itself; it is a conversion adapter that maps EUC-JP byte sequences to Shift-JIS/CP932 byte sequences, calls the loaded CP932 NLS callbacks, and maps CP932 output back to EUC-JP. The implementation includes support for JIS X 0208, JIS X 0201 kana, user-defined characters, IBM extensions, and NEC/IBM extension remapping according to the referenced OSF/JVC EUC/SJIS conversion specification.

## Important APIs, Types, and Functions

The module-level dependency is `static struct nls_table *p_nls`, loaded with `load_nls("cp932")` during init. The registered `struct nls_table table` exposes `.charset = "euc-jp"`, `.uni2char`, and `.char2uni`; the case-folding tables are borrowed from the CP932 table.

Key macros classify and translate byte ranges: `IS_SJIS_LOW_BYTE`, `IS_SJIS_JISX0208`, `IS_SJIS_JISX0201KANA`, `IS_SJIS_UDC_LOW`, `IS_SJIS_UDC_HI`, `IS_SJIS_IBM`, `IS_SJIS_NECIBM`, `MAP_SJIS2EUC`, `SS2`, `SS3`, `IS_EUC_BYTE`, `IS_EUC_JISX0208`, `IS_EUC_JISX0201KANA`, `IS_EUC_UDC_LOW`, `IS_EUC_UDC_HI`, and `MAP_EUC2SJIS`.

Static tables `sjisibm2euc_map`, `euc2sjisibm_jisx0212_map`, and `euc2sjisibm_g3upper_map` handle IBM extension areas that are not simple arithmetic transforms. Helper functions `sjisibm2euc()`, `euc2sjisibm_jisx0212()`, `euc2sjisibm_g3upper()`, `euc2sjisibm()`, and `sjisnec2sjisibm()` isolate those special cases.

## Control Flow

`uni2char()` first delegates Unicode-to-CP932 conversion to `p_nls->uni2char()`. One-byte CP932 kana output is expanded to `SS2` plus kana. Two-byte output is optionally normalized from NEC/IBM extension rows to IBM extension rows, then transformed into EUC-JP: user-defined low rows map arithmetically, user-defined high rows become a three-byte `SS3` sequence, IBM extensions are table-mapped to two or three bytes, and ordinary JIS X 0208 rows use the standard SJIS-to-EUC arithmetic conversion. Unrecognized two-byte CP932 output returns `-EINVAL`.

`char2uni()` performs the inverse. ASCII bytes pass through as JIS X 0201 Roman. EUC two-byte sequences are decoded as kana, user-defined low rows, or JIS X 0208. `SS3` three-byte sequences handle high user-defined rows and IBM extension tables; other JIS X 0212-like input is rejected. After translating to a temporary CP932 byte sequence, the function calls `p_nls->char2uni()` and returns the number of EUC bytes consumed.

## State and Persistence Behavior

The file has one persistent module reference, `p_nls`, which is loaded at init and unloaded at exit. Static mapping tables are read-only. There is no per-mount mutable state, but conversion behavior is persistent for any filesystem using the `euc-jp` NLS table, so mapping changes affect filename interoperability.

## Dependencies and Integration Points

The file depends on the Linux NLS core, errno values, module lifecycle macros, and the CP932 NLS module. `init_nls_euc_jp()` loads CP932, borrows its case tables, and calls `register_nls()`. `exit_nls_euc_jp()` unregisters EUC-JP and unloads CP932. Filesystems interact only through the generic `struct nls_table` callbacks.

## Risks

The main risk is semantic drift in the many byte-range formulas and extension tables. Off-by-one errors in index calculations can remap large ranges. `sjisibm2euc()` computes an array index from lead/trail bytes and relies on callers to restrict inputs to IBM ranges. `char2uni()` returns `-EINVAL` rather than `-ENAMETOOLONG` for some truncated multibyte paths, which is observable behavior. Changes must preserve CP932 dependency handling so the borrowed case tables remain valid.

## Test Signals

Build the module with CP932 enabled, load/unload it, and verify `register_nls("euc-jp")` succeeds only when CP932 is available. Conversion tests should cover ASCII, JIS X 0201 kana, JIS X 0208 punctuation/kana/kanji, `SS3` high user-defined rows, IBM extensions from both G3 upper and JIS X 0212 maps, NEC/IBM special rows, invalid lead/trail bytes, and truncated two- and three-byte sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_euc-jp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-1.c -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-1.c

## Purpose

This generated NLS module registers the ISO 8859-1 / Latin-1 single-byte charset. It maps each byte directly to the same Unicode code point in `U+0000..U+00FF` and provides exact reverse mappings for filesystems that need Western European filename conversion.

## Important APIs, Types, and Functions

`charset2uni[256]` is a one-entry-per-byte `wchar_t` decode table. `page00[256]` is the reverse Unicode page for `U+00xx`, and `page_uni2charset[256]` points only page 0 at `page00`. `charset2lower[256]` and `charset2upper[256]` fold ASCII and Latin-1 uppercase/lowercase pairs. `uni2char()` encodes one byte from the reverse page; `char2uni()` decodes one byte from `charset2uni`. The `struct nls_table` is registered as `iso8859-1`.

## Control Flow

`uni2char()` rejects zero output space with `-ENAMETOOLONG`, indexes the reverse page with the high and low bytes of `wchar_t`, writes a single output byte when the table entry is nonzero, and returns `-EINVAL` for unmapped code points. `char2uni()` indexes `charset2uni[*rawstring]`, rejects `0x0000`, and returns one consumed byte.

## State and Persistence Behavior

All tables are `static const` and read-only. The only module state is registration in the NLS registry between `init_nls_iso8859_1()` and `exit_nls_iso8859_1()`. Mapping changes affect persisted filenames on filesystems mounted with this charset.

## Dependencies and Integration Points

The file depends on `linux/nls.h`, errno definitions, and module infrastructure. Filesystems use it through the NLS registry and the callbacks in `struct nls_table`.

## Risks

The `char2uni()` zero check means byte `0x00` is treated as invalid in this NLS callback even though the decode table stores `U+0000`; callers must not expect embedded NUL filename characters. `uni2char()` also uses a zero reverse-table entry as "unmapped", so `U+0000` is not encodable through this path. Case-folding tables are byte-level and not full Unicode normalization.

## Test Signals

Build/load/unload the module, verify all nonzero `U+0001..U+00FF` values round-trip, verify `U+0100` returns `-EINVAL`, verify zero-length output returns `-ENAMETOOLONG`, and check ASCII plus accented Latin-1 case-folding entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-13.c -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-13.c

## Purpose

This generated NLS module registers ISO 8859-13 / Latin-7 for Baltic languages. It provides a single-byte mapping for the common ASCII/C1 range plus Baltic letters, punctuation, and quote/dash symbols used by the ISO 8859-13 standard.

## Important APIs, Types, and Functions

`charset2uni[256]` decodes byte values to Unicode. Reverse tables `page00`, `page01`, and `page20` encode mappings for Latin-1-style characters, extended Latin letters, and selected punctuation such as quotation marks and dashes. `page_uni2charset` dispatches Unicode high bytes `0x00`, `0x01`, and `0x20`. `charset2lower` and `charset2upper` encode byte-level case pairs for the charset. `uni2char()`, `char2uni()`, and the registered `struct nls_table` follow the standard single-byte NLS pattern.

## Control Flow

Encoding indexes `page_uni2charset[ch][cl]` and emits one byte if nonzero. Decoding indexes `charset2uni[*rawstring]` and rejects zero mappings. There are no multibyte paths or allocations.

## State and Persistence Behavior

Tables are immutable and shared by all callers. Module state is limited to `register_nls()` and `unregister_nls()`. The mapping defines persistent filename interpretation for mounts configured with `iso8859-13`.

## Dependencies and Integration Points

The module integrates with the kernel NLS registry under `.charset = "iso8859-13"`. It depends on generated Unicode mapping tables and the generic NLS callback ABI.

## Risks

Sparse `page20` punctuation entries must remain exact because typographic punctuation is easy to confuse with ASCII substitutes. Zero entries are validity markers, not character values. Byte-level case tables must match ISO 8859-13 encoded pairs and avoid introducing mappings for unassigned bytes.

## Test Signals

Round-trip ASCII, Baltic letters from `page01`, punctuation from `page20`, and invalid Unicode pages. Exercise byte values whose decode table contains zero if present, and verify lower/upper tables for Latvian/Lithuanian/Estonian accented pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-13.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-14.c -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-14.c

## Purpose

This generated NLS module registers ISO 8859-14 / Latin-8, a Celtic-oriented single-byte charset. It covers ASCII, common Latin characters, extended Celtic letters, and selected Latin Extended Additional characters.

## Important APIs, Types, and Functions

`charset2uni[256]` contains the byte-to-Unicode map. Reverse pages `page00`, `page01`, and `page1e` map Unicode pages 0, 1, and `0x1e` back to one-byte ISO 8859-14 values. `charset2lower` and `charset2upper` describe byte-oriented case folding. `uni2char()` and `char2uni()` are the standard generated one-byte callbacks. The module registers `.charset = "iso8859-14"`.

## Control Flow

`uni2char()` checks output capacity, chooses a reverse page from the Unicode high byte, and emits a single byte when the page entry is nonzero. `char2uni()` reads one input byte and rejects zero-valued decode entries. Module init/exit only register and unregister the table.

## State and Persistence Behavior

All translation and case tables are read-only. The only runtime state is NLS registry membership. Existing on-disk filenames encoded with this charset depend on these stable table values.

## Dependencies and Integration Points

The module uses Linux NLS APIs, errno values, and module macros. Filesystems request it by charset name and receive the callback table through the NLS core.

## Risks

The `page1e` reverse table covers less common precomposed Latin letters; accidental omission can make valid Celtic filenames unencodable. Case-folding table entries for extended letters are easy to misalign because they are byte-coded rather than Unicode-codepoint-coded. NUL is intentionally invalid in conversion callbacks.

## Test Signals

Compile/load testing should be paired with round trips for Welsh/Irish/Scottish Gaelic characters, `page1e` letters, ASCII, invalid Unicode pages, zero-length buffers, and upper/lower pairs in the high half of the charset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-14.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-15.c -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-15.c

## Purpose

This generated NLS module registers ISO 8859-15 / Latin-9, a Western European single-byte charset closely related to ISO 8859-1 but with replacements such as the Euro sign and additional French/Finnish letters.

## Important APIs, Types, and Functions

`charset2uni[256]` maps bytes to Unicode. Reverse pages `page00`, `page01`, and `page20` encode Latin-1-style characters, extended Latin replacements, and selected punctuation/currency symbols, including Euro. `page_uni2charset` dispatches those pages. `charset2lower` and `charset2upper` provide byte-level case folding. The registered table uses `.charset = "iso8859-15"`.

## Control Flow

The conversion logic is generated single-byte NLS logic: `uni2char()` rejects insufficient output, emits one reverse-table byte for exact mappings, and returns `-EINVAL` otherwise; `char2uni()` decodes one byte and rejects zero mappings.

## State and Persistence Behavior

There is no mutable conversion state. Tables are read-only and module lifetime is represented by NLS registration. Persistent filenames using Latin-9 rely on exact values for bytes that differ from Latin-1.

## Dependencies and Integration Points

The file integrates with filesystems through `register_nls()` and the NLS callback ABI. It depends on Linux module, errno, and NLS headers.

## Risks

Confusing ISO 8859-15 with ISO 8859-1 is the dominant risk; bytes such as the Euro sign and ligature/letter replacements must remain distinct. Sparse reverse-page entries use zero as "unmapped", so tests must distinguish a missing mapping from byte zero.

## Test Signals

Round-trip ASCII, ordinary Western European accents, Euro, OE/oe, Y-diaeresis, and characters that differ from Latin-1. Verify invalid Unicode pages, `U+0000`, and no-space output failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-15.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-2.c -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-2.c

## Purpose

This generated NLS module registers ISO 8859-2 / Latin-2 for Central and Eastern European languages. It provides exact single-byte mappings for ASCII, selected Latin-1 symbols, and extended Latin characters used by Slavic and Central European alphabets.

## Important APIs, Types, and Functions

`charset2uni[256]` maps bytes to Unicode. Reverse pages `page00`, `page01`, and `page02` map Unicode pages `0x00`, `0x01`, and selected spacing modifier letters back to charset bytes. `charset2lower` and `charset2upper` encode byte-level case folding for ASCII and Latin-2-specific pairs. `uni2char()`, `char2uni()`, and the `struct nls_table` registered as `iso8859-2` implement the NLS ABI.

## Control Flow

Encoding and decoding are one-byte table lookups with `-ENAMETOOLONG` for zero output capacity and `-EINVAL` for missing mappings. There are no dynamic allocations, locks, or multibyte branches.

## State and Persistence Behavior

The module stores immutable generated tables and registers/unregisters them at module load/unload. The table values are effectively persistent compatibility data for filenames encoded as ISO 8859-2.

## Dependencies and Integration Points

The file depends on kernel module/NLS headers and is consumed by filesystem charset conversion code through the generic NLS registry.

## Risks

Central European accented letters have many similar-looking precomposed Unicode values; table drift can silently corrupt filenames. Case tables must match byte positions, not Unicode ordering. The zero-entry sentinel excludes NUL conversion.

## Test Signals

Validate round trips for Polish, Czech, Slovak, Hungarian, Slovenian/Croatian letters, spacing modifier entries in `page02`, invalid Unicode pages, empty output buffers, and high-byte case-fold pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-3.c -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-3.c

## Purpose

This generated NLS module registers ISO 8859-3 / Latin-3 for Esperanto, Maltese, Galician, and older Turkish usage. It is a single-byte translation table with several undefined byte positions represented as invalid mappings.

## Important APIs, Types, and Functions

`charset2uni[256]` contains byte-to-Unicode values and explicit zero holes for undefined charset bytes. Reverse pages `page00`, `page01`, and `page02` provide exact Unicode-to-byte mappings. `charset2lower` and `charset2upper` encode ASCII and Latin-3 case folding, including zero entries for unassigned high-half bytes. `uni2char()`, `char2uni()`, and the `iso8859-3` `struct nls_table` are the exported behavior.

## Control Flow

`uni2char()` performs a capacity check and emits exactly one byte when the selected reverse table has a nonzero entry. `char2uni()` decodes one byte and rejects entries that are `0x0000`. Module init/exit only add or remove the NLS table.

## State and Persistence Behavior

All mapping state is static and read-only. Runtime persistence is limited to the table being registered with the NLS core.

## Dependencies and Integration Points

The module is integrated through Linux NLS and filesystem charset conversion. It has no dependency on other NLS modules.

## Risks

Undefined ISO 8859-3 byte slots are represented by zero and must not be accidentally made valid. Some case-table entries for dotted/dotless and Esperanto/Maltese letters are non-obvious, so byte-position tests matter more than visual inspection.

## Test Signals

Round-trip Esperanto, Maltese, and Turkish-era Latin-3 letters, assert undefined bytes fail decode, assert unmapped Unicode fails encode, and validate case mappings for the high-half charset-specific letters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-4.c -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-4.c

## Purpose

This generated module registers ISO 8859-4 / Latin-4, an older Baltic charset. It supplies single-byte filename conversion tables for ASCII plus Baltic and Nordic extended Latin letters.

## Important APIs, Types, and Functions

`charset2uni[256]` decodes bytes. `page00`, `page01`, and `page02` reverse selected Unicode pages to byte values. `charset2lower` and `charset2upper` implement byte-level folding. `uni2char()`, `char2uni()`, and the `iso8859-4` table provide the NLS interface.

## Control Flow

Conversion is a single table lookup in each direction. `uni2char()` checks `boundlen`, dispatches by Unicode high byte, and returns one byte or `-EINVAL`. `char2uni()` decodes one byte and treats zero as invalid.

## State and Persistence Behavior

The generated arrays are read-only. The module only mutates global NLS registry state when loaded or unloaded.

## Dependencies and Integration Points

The code depends on kernel NLS infrastructure and integrates with any filesystem that requests `iso8859-4`.

## Risks

ISO 8859-4 overlaps visually with other Latin/Baltic sets but has different byte assignments. Case tables and reverse pages must be validated against the exact standard, not inferred from neighboring ISO-8859 files.

## Test Signals

Round-trip Baltic/Nordic characters, verify spacing marks in `page02`, check high-half case folding, reject unmapped Unicode and NUL, and build-test the generated initializers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-5.c -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-5.c

## Purpose

This generated NLS module registers ISO 8859-5 for Cyrillic. It maps one-byte Cyrillic charset values to Unicode Cyrillic code points and provides exact reverse conversion for filesystem names.

## Important APIs, Types, and Functions

`charset2uni[256]` is the decode table. Reverse pages `page00`, `page04`, and `page21` map common symbols, Cyrillic characters, and one symbol page entry back to bytes. `charset2lower` and `charset2upper` perform byte-level folding for Cyrillic upper/lower pairs. The registered table uses `.charset = "iso8859-5"`.

## Control Flow

The generated `uni2char()` and `char2uni()` callbacks use one-byte table lookup and standard NLS errno returns. No multibyte logic or allocation exists.

## State and Persistence Behavior

Tables are immutable and shared. Module persistence is only the NLS registry entry. Charset table values define persistent filename interpretation for ISO 8859-5 mounts.

## Dependencies and Integration Points

The module integrates with Linux filesystems through the NLS registry and depends only on core kernel module/NLS headers.

## Risks

Cyrillic mappings around `U+0400..U+045F` and byte-level case-folding offsets must remain exact. Using zero as the invalid sentinel means `U+0000` cannot be encoded or decoded.

## Test Signals

Round-trip Russian and broader Cyrillic letters, validate Cyrillic case folding, test unmapped Unicode pages, and check module registration lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-6.c -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-6.c

## Purpose

This generated module registers ISO 8859-6 for Arabic. It is a single-byte NLS table for Arabic letters and marks, with many unassigned positions represented as invalid mappings.

## Important APIs, Types, and Functions

`charset2uni[256]` decodes bytes. Reverse pages `page00` and `page06` map common symbols and Arabic Unicode page entries back to byte values. `charset2lower` and `charset2upper` are effectively identity/ASCII-oriented because Arabic has no simple case folding. `uni2char()`, `char2uni()`, and the `iso8859-6` table implement the NLS ABI.

## Control Flow

Encoding uses Unicode high-byte dispatch and emits one byte for nonzero reverse entries. Decoding indexes one byte in `charset2uni` and rejects zero. Module init/exit register and unregister the table.

## State and Persistence Behavior

The generated tables are static and read-only. No runtime state is held beyond NLS registry membership.

## Dependencies and Integration Points

The file depends on the Linux NLS core and is consumed by filesystems through `register_nls()`.

## Risks

Unassigned bytes in ISO 8859-6 must remain invalid. The module performs no bidirectional shaping or normalization; it only maps encoded characters. Callers expecting Arabic presentation handling must do it elsewhere.

## Test Signals

Round-trip Arabic letters and punctuation in `page06`, verify unassigned byte failures, verify no unexpected case changes beyond ASCII tables, and exercise short output buffer and unmapped Unicode failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-7.c -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-7.c

## Purpose

This generated NLS module registers ISO 8859-7 for Modern Greek. It maps Greek single-byte filenames to Unicode and supports exact reverse conversion for the covered Greek and punctuation characters.

## Important APIs, Types, and Functions

`charset2uni[256]` decodes the byte set. Reverse pages `page00`, `page02`, `page03`, and `page20` cover Latin/symbol bytes, spacing modifier characters, Greek code points, and selected punctuation. `charset2lower` and `charset2upper` encode Greek and ASCII byte-level case pairs. The registered table is `.charset = "iso8859-7"`.

## Control Flow

The conversion callbacks are generated one-byte lookups. `uni2char()` rejects insufficient output or absent reverse mappings; `char2uni()` rejects zero decode entries and consumes one byte.

## State and Persistence Behavior

All mapping arrays are constant. Runtime state is only module registration with the NLS core.

## Dependencies and Integration Points

The module depends on Linux NLS infrastructure and integrates with filesystem charset conversion under `iso8859-7`.

## Risks

Greek tonos/dialytika characters and punctuation page entries are easy to confuse with other Greek encodings. Case folding is byte-based and does not implement full Unicode Greek casing rules.

## Test Signals

Round-trip Greek uppercase/lowercase, accented Greek characters, punctuation from `page20`, invalid byte/table holes, invalid Unicode pages, and case-folding entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-9.c -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-9.c

## Purpose

This generated module registers ISO 8859-9 / Latin-5 for Turkish. It is mostly Latin-1-compatible but replaces selected Icelandic letters with Turkish dotted/dotless I and G/S variants.

## Important APIs, Types, and Functions

`charset2uni[256]` is the byte-to-Unicode table. Reverse pages `page00` and `page01` map Latin and Turkish extended letters back to bytes. `charset2lower` and `charset2upper` encode ASCII and Turkish high-byte case pairs. `uni2char()`, `char2uni()`, and the `iso8859-9` table provide the NLS callbacks.

## Control Flow

Encoding and decoding are one-byte generated lookups. Missing reverse entries and zero decode entries return `-EINVAL`; no output capacity returns `-ENAMETOOLONG`.

## State and Persistence Behavior

Tables are static constants. The module only registers/unregisters the NLS table and has no per-consumer state.

## Dependencies and Integration Points

The module is used by filesystems through the Linux NLS registry under `iso8859-9`.

## Risks

Turkish dotted/dotless I case behavior is charset-specific and not equivalent to locale-aware Unicode casing. Confusing ISO 8859-9 with ISO 8859-1 corrupts high-byte Turkish letters.

## Test Signals

Round-trip Turkish `Ğ/ğ`, `İ/i`, `Ş/ş`, dotless `ı`, ASCII, and Latin-1 overlap. Validate case tables and failure for unmapped Unicode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_iso8859-9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_koi8-r.c -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_koi8-r.c

## Purpose

This generated NLS module registers KOI8-R for Russian. It maps KOI8-R bytes to Unicode Cyrillic, line-drawing, and symbol characters and provides exact reverse lookup for filesystem filename conversion.

## Important APIs, Types, and Functions

`charset2uni[256]` decodes bytes. Reverse pages `page00`, `page04`, `page22`, `page23`, and `page25` encode Latin/symbol, Cyrillic, mathematical, box drawing, and block/line drawing mappings. `charset2lower` and `charset2upper` implement KOI8-R byte-level case folding. `uni2char()`, `char2uni()`, and the registered `koi8-r` table implement the NLS interface.

## Control Flow

The callbacks are one-byte table lookups with standard NLS failure modes. Module init/exit register and unregister the generated table.

## State and Persistence Behavior

Translation data is immutable. Persistent effects are indirect: mounted filesystems using KOI8-R interpret on-disk names through these tables.

## Dependencies and Integration Points

The file depends on Linux NLS/module headers and integrates through `register_nls()` under `koi8-r`.

## Risks

KOI8-R includes box drawing and Cyrillic code points with non-obvious byte order. Table changes can break round-trip compatibility with legacy filesystems. Case folding must preserve KOI8-specific byte positions.

## Test Signals

Round-trip Russian Cyrillic, `Ё/ё`, box-drawing symbols, invalid Unicode pages, zero-length output, and high-byte case-fold pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_koi8-r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_koi8-ru.c -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_koi8-ru.c

## Purpose

This file registers KOI8-RU for Belarusian by wrapping the existing `koi8-u` NLS table and overriding the small set of bytes/code points that differ. It avoids duplicating a full generated mapping table.

## Important APIs, Types, and Functions

`static struct nls_table *p_nls` stores the loaded `koi8-u` table. `uni2char()` special-cases Unicode `U+040E` and `U+045E` to bytes `0xBE` and `0xAE`, while delegating most work to `p_nls->uni2char()`. `char2uni()` is intended to special-case the corresponding input bytes and otherwise delegate. The registered table is `.charset = "koi8-ru"` and borrows `charset2upper`/`charset2lower` from KOI8-U during init.

## Control Flow

Initialization loads `koi8-u`, installs its case tables, and registers KOI8-RU. Exit unregisters and unloads KOI8-U. Encoding checks output capacity, handles the two Belarusian short-U code points, suppresses two KOI8-U box-drawing mappings by returning 0, and delegates other values. Decoding reads a byte and either maps a special byte to `U+040E`/`U+045E` or delegates to KOI8-U.

## State and Persistence Behavior

The module holds a runtime reference to KOI8-U in `p_nls`. There are no generated local tables and no per-consumer state. Persistent filename interpretation depends on both this adapter and the loaded KOI8-U table.

## Dependencies and Integration Points

The file depends on another NLS module (`koi8-u`) and on the NLS registry. Filesystems see a normal `struct nls_table` for `koi8-ru`.

## Risks

The `char2uni()` condition is a high-risk area: the code checks `((*rawstring & 0xef) != 0xae)` before mapping to the two special Unicode values, which is counterintuitive for a two-byte override pattern where only `0xAE` and `0xBE` should be special. Regression tests should pin this behavior or detect it as a bug against the intended KOI8-RU mapping. Returning `0` from `uni2char()` for selected box-drawing code points is also unusual because NLS callbacks normally return a byte count or negative errno.

## Test Signals

Load KOI8-U and KOI8-RU together, test `U+040E`/`U+045E` to `0xBE`/`0xAE`, test decode of `0xAE` and `0xBE`, test ordinary KOI8-U delegated bytes, test the suppressed `U+255D`/`U+256C` behavior, and verify unload releases the dependent NLS table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_koi8-ru.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_koi8-u.c -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_koi8-u.c

## Purpose

This generated NLS module registers KOI8-U for Ukrainian. It extends KOI8-R-style Cyrillic coverage with Ukrainian-specific letters while retaining symbol and line-drawing mappings.

## Important APIs, Types, and Functions

`charset2uni[256]` decodes KOI8-U bytes. Reverse pages `page00`, `page04`, `page22`, `page23`, and `page25` map Unicode pages for common symbols, Cyrillic, math, box drawing, and drawing/block symbols back to bytes. `charset2lower` and `charset2upper` encode KOI8-U byte-level case pairs. The registered table uses `.charset = "koi8-u"`.

## Control Flow

`uni2char()` and `char2uni()` are one-byte table lookups with the standard generated NLS sentinel handling. Init and exit register and unregister the NLS table.

## State and Persistence Behavior

All mapping data is immutable. The table can also be a dependency for `koi8-ru`, so unloading order matters through NLS reference handling.

## Dependencies and Integration Points

The file integrates through the Linux NLS registry and may be loaded directly by filesystems or indirectly by the KOI8-RU adapter.

## Risks

Ukrainian Cyrillic overrides must not be confused with KOI8-R or KOI8-RU. Box-drawing and symbol pages need exact reverse mappings for round trips. Case-folding is charset-byte-specific.

## Test Signals

Round-trip Ukrainian-specific letters, Russian overlap, box-drawing symbols, delegated use by KOI8-RU, invalid Unicode pages, and upper/lower case table behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_koi8-u.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_ucs2_data.h -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_ucs2_data.h

## Purpose

This header declares the shared data contract for UCS-2 uppercase conversion helpers. It exposes the compressed uppercase delta tables implemented in `nls_ucs2_utils.c` and consumed by inline functions in `nls_ucs2_utils.h`.

## Important APIs, Types, and Functions

`struct UniCaseRange` stores a start code point, end code point, and signed-char delta table. `extern signed char NlsUniUpperTable[512]` declares the base table for low Unicode values. `extern const struct UniCaseRange NlsUniUpperRange[]` declares the range table for sparse higher Unicode blocks.

## Control Flow

The header has no executable flow. Runtime lookup happens in `UniToupper()` by first indexing `NlsUniUpperTable` for values below its size and then scanning `NlsUniUpperRange`.

## State and Persistence Behavior

The header declares global uppercase data but owns no storage. Consumers rely on the data being linked from `nls_ucs2_utils.c`.

## Dependencies and Integration Points

It is included by `nls_ucs2_utils.h`. The type uses `wchar_t`, so consumers must include headers that define it before or through the utility header.

## Risks

The data contract assumes signed-char deltas are sufficient for every represented uppercase mapping. Any new range whose delta does not fit signed char would require a format change. Header and implementation must remain in sync.

## Test Signals

Build users that include the header, verify exported symbols resolve, and test uppercase conversion through `UniToupper()` for low-table and range-table values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_ucs2_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_ucs2_utils.c -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_ucs2_utils.c

## Purpose

This file provides exported UCS-2 uppercase conversion data derived from CIFS/server Unicode helpers. It is data-heavy support code for filesystems that need Windows-style or UCS-2 case-insensitive filename handling.

## Important APIs, Types, and Functions

`NlsUniUpperTable[512]` is an exported signed-char delta table for low Unicode values, including ASCII and Latin ranges. Range arrays `UniCaseRangeU03a0`, `UniCaseRangeU0430`, `UniCaseRangeU0490`, `UniCaseRangeU1e00`, and `UniCaseRangeUff40` cover Greek, Cyrillic, extended Cyrillic, extended Latin/Greek, and fullwidth Latin ranges. `NlsUniUpperRange[]` stitches those arrays into a sentinel-terminated table of `struct UniCaseRange`. Both `NlsUniUpperTable` and `NlsUniUpperRange` are exported with `EXPORT_SYMBOL_GPL`.

## Control Flow

There are no callable functions in this file beyond module metadata. Lookup control flow is implemented by inline consumers in the header: add the signed delta from the base table or from the first matching range table.

## State and Persistence Behavior

The exported tables are global static storage for the module/built-in kernel image. They are not mutated at runtime. Since the arrays define case-insensitive comparison behavior, changes can affect persistent filename lookup semantics for filesystems that depend on them.

## Dependencies and Integration Points

The file includes filesystem, module, slab, unaligned, and local UCS-2 utility headers. It integrates with any GPL kernel code that uses `UniToupper()`/`UniStrupr()` or directly references the exported tables.

## Risks

Signed-char deltas must be exact and within range. Range boundaries and sentinel order are critical because consumers scan ranges linearly. Case mapping is uppercase-only and compressed; it is not a full Unicode case-folding engine.

## Test Signals

Build/link tests should verify exported symbols. Functional tests should uppercase ASCII, Latin-1, Greek, Cyrillic, extended Latin, and fullwidth Latin values, and verify unmapped characters remain unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_ucs2_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_ucs2_utils.h -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_ucs2_utils.h

## Purpose

This header provides inline UCS-2 string utility functions and uppercase conversion helpers for kernel filesystems. Its semantics mirror C string routines but operate on `wchar_t`/little-endian UCS-2 units.

## Important APIs, Types, and Functions

The header defines private-use Unicode constants for Windows-reserved filename characters such as `UNI_ASTERISK`, `UNI_QUESTION`, `UNI_COLON`, `UNI_GRTRTHAN`, `UNI_LESSTHAN`, `UNI_PIPE`, and `UNI_SLASH`. Inline routines include `UniStrcat`, `UniStrchr`, `UniStrcmp`, `UniStrcpy`, `UniStrlen`, `UniStrnlen`, `UniStrncat`, `UniStrncmp`, `UniStrncmp_le`, `UniStrncpy`, `UniStrncpy_le`, `UniStrstr`, `UniToupper`, and `UniStrupr`.

## Control Flow

The string helpers use simple NUL-terminated loops analogous to libc routines. The `_le` variants convert little-endian `__le16` values with endian helpers. `UniToupper()` first uses `NlsUniUpperTable` for low code points, then scans `NlsUniUpperRange` until the input falls within a range or passes all ranges. `UniStrupr()` walks a little-endian string in place, uppercasing each code unit.

## State and Persistence Behavior

The header contains inline code only. It mutates caller-provided buffers for copy, concat, strncpy, and uppercase-in-place operations. It assumes NUL-terminated UCS-2 input unless a length-limited function is used.

## Dependencies and Integration Points

It depends on byteorder helpers, `linux/types.h`, `linux/nls.h`, `linux/unicode.h`, and `nls_ucs2_data.h`. Filesystems can include it to share NTFS/CIFS-style UCS-2 string behavior.

## Risks

Most routines do not know destination buffer sizes beyond the explicit `n` parameters, so callers must guarantee space. `UniStrnlen()` increments before checking the limit, matching its local implementation but requiring careful caller interpretation. `UniStrncpy_le()` names suggest little-endian output but uses `__le16_to_cpu()` while writing to `wchar_t *`, so type expectations should be checked by consumers. `UniToupper()` is uppercase-only and does not implement locale-sensitive or full Unicode case folding.

## Test Signals

Unit tests should cover empty strings, exact-length bounded operations, unterminated inputs guarded by length, substring matches at start/middle/end, little-endian comparisons/copies, uppercase of ASCII/Greek/Cyrillic/fullwidth ranges, and reserved-character private-use constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_ucs2_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_utf8.c -->
# Research: sources/distributed-fs/ceph-client/fs/nls/nls_utf8.c

## Purpose

This module registers UTF-8 as an NLS charset so filesystems can use the same `struct nls_table` interface as legacy byte encodings. Unlike the generated ISO/KOI tables, it delegates conversion to generic UTF helpers.

## Important APIs, Types, and Functions

`identity[256]` is initialized at module load and used for both `.charset2lower` and `.charset2upper`, meaning byte-level case conversion is disabled. `uni2char()` calls `utf32_to_utf8()`. `char2uni()` calls `utf8_to_utf32()` and rejects code points above `MAX_WCHAR_T`. The registered table uses `.charset = "utf8"`.

## Control Flow

`uni2char()` checks output capacity, encodes one `wchar_t` to UTF-8, writes `?` and returns `-EINVAL` on encode failure, and otherwise returns the byte count. `char2uni()` decodes a UTF-8 sequence from bounded input, writes `?` and returns `-EINVAL` if decoding fails or the result is too large for `wchar_t`, and otherwise returns bytes consumed.

## State and Persistence Behavior

The only mutable module state is `identity[256]`, initialized once before registration. There is no per-consumer state. UTF-8 filenames persist according to the kernel UTF helper behavior.

## Dependencies and Integration Points

The file depends on Linux NLS and Unicode conversion helpers. It integrates with filesystems through the NLS registry under `utf8`.

## Risks

The fallback writes `?` on invalid conversion while still returning an error; callers must not consume the fallback as success. Identity case tables mean no Unicode case folding is provided. `MAX_WCHAR_T` bounds make this table dependent on the kernel's `wchar_t` width.

## Test Signals

Round-trip ASCII, two-, three-, and four-byte UTF-8 within `MAX_WCHAR_T`, invalid byte sequences, truncated sequences, too-small output buffers, and case-table identity behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_utf8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/Kconfig -->
# Research: sources/distributed-fs/ceph-client/fs/notify/Kconfig

## Purpose

This Kconfig file defines the top-level `FSNOTIFY` symbol and includes the dnotify, inotify, and fanotify configuration submenus.

## Important APIs, Types, and Functions

`config FSNOTIFY` is a non-prompted boolean with `def_bool n`. The file then sources `fs/notify/dnotify/Kconfig`, `fs/notify/inotify/Kconfig`, and `fs/notify/fanotify/Kconfig`.

## Control Flow

Kconfig evaluation starts with a disabled internal `FSNOTIFY` symbol. Subsystems such as DNOTIFY or FANOTIFY select it when enabled.

## State and Persistence Behavior

The only persistent output is kernel configuration state. No runtime code is present.

## Dependencies and Integration Points

This file is the build-configuration integration point for filesystem notification support. It controls whether common fsnotify objects from the sibling Makefile are compiled.

## Risks

Because `FSNOTIFY` has no user prompt and defaults off, notification backends must remember to `select FSNOTIFY`. Missing a sourced submenu would silently hide a backend.

## Test Signals

Run Kconfig/config generation with DNOTIFY, INOTIFY, and FANOTIFY toggles, confirm enabling each selects `FSNOTIFY`, and confirm disabling all leaves common fsnotify code out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/Makefile -->
# Research: sources/distributed-fs/ceph-client/fs/notify/Makefile

## Purpose

This Makefile wires the common fsnotify core and notification backend subdirectories into the kernel build.

## Important APIs, Types, and Functions

`obj-$(CONFIG_FSNOTIFY)` builds `fsnotify.o`, `notification.o`, `group.o`, `mark.o`, and `fdinfo.o`. `obj-y` always descends into `dnotify/`, `inotify/`, and `fanotify/`, leaving their own Makefiles to decide whether backend objects are built.

## Control Flow

Kbuild conditionally adds common fsnotify objects when `CONFIG_FSNOTIFY=y`. Directory descent happens unconditionally for backend directories.

## State and Persistence Behavior

The file affects build artifacts only. It has no runtime state.

## Dependencies and Integration Points

It depends on Kbuild conventions and the Kconfig symbols defined in the notify tree. Backend object files depend on the common objects when their configs select `FSNOTIFY`.

## Risks

Adding a backend without selecting `FSNOTIFY` can compile backend code without the common support it expects. Removing a common object here breaks all backends.

## Test Signals

Build kernels with no notification backend, DNOTIFY only, FANOTIFY only, and combined backends; inspect built objects and link success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/dnotify/Kconfig -->
# Research: sources/distributed-fs/ceph-client/fs/notify/dnotify/Kconfig

## Purpose

This file exposes the legacy dnotify backend configuration option.

## Important APIs, Types, and Functions

`config DNOTIFY` is a prompted boolean, defaults to `y`, and selects `FSNOTIFY`. The help text describes directory-based per-file-descriptor notifications delivered via signals and notes that newer alternatives exist.

## Control Flow

Selecting DNOTIFY enables the common fsnotify core through `select FSNOTIFY` and lets the dnotify Makefile build `dnotify.o`.

## State and Persistence Behavior

Only kernel configuration state is affected. Runtime behavior is in `dnotify.c`.

## Dependencies and Integration Points

It integrates legacy userspace ABI support with the fsnotify core. The option is user-visible and defaults on for compatibility.

## Risks

Default-on legacy support increases attack surface unless distributions choose to disable it. Removing `select FSNOTIFY` would break the build or runtime integration.

## Test Signals

Generate configs with DNOTIFY enabled/disabled, confirm `CONFIG_FSNOTIFY` follows, and confirm `dnotify.o` is built only when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/dnotify/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/dnotify/Makefile -->
# Research: sources/distributed-fs/ceph-client/fs/notify/dnotify/Makefile

## Purpose

This Kbuild file compiles the dnotify backend object when `CONFIG_DNOTIFY` is enabled.

## Important APIs, Types, and Functions

The only rule is `obj-$(CONFIG_DNOTIFY) += dnotify.o`.

## Control Flow

Kbuild includes `dnotify.o` conditionally based on the Kconfig symbol.

## State and Persistence Behavior

The file has build-time effects only.

## Dependencies and Integration Points

It depends on `fs/notify/dnotify/Kconfig` and the top-level notify Makefile's directory descent.

## Risks

The rule is simple; risk is mainly accidental symbol rename or loss of conditional build coverage.

## Test Signals

Build with `CONFIG_DNOTIFY=y` and `n`, verifying object inclusion and absence respectively.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/dnotify/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/dnotify/dnotify.c -->
# Research: sources/distributed-fs/ceph-client/fs/notify/dnotify/dnotify.c

## Purpose

This file implements legacy dnotify directory notifications on top of fsnotify. Users register interest with `fcntl()` on a directory file descriptor and receive `SIGIO` notifications when matching child events occur.

## Important APIs, Types, and Functions

Global state includes `dir_notify_enable`, optional sysctl registration, `dnotify_struct_cache`, `dnotify_mark_cache`, and the singleton `dnotify_group`. `struct dnotify_mark` embeds `struct fsnotify_mark` and chains `struct dnotify_struct` registrations. `dnotify_recalc_inode_mask()` recomputes the aggregate mask. `dnotify_handle_event()` sends `SIGIO` and removes one-shot registrations. `dnotify_flush()` removes registrations on file close. `convert_arg()` maps userspace `DN_*` flags to internal `FS_*` masks. `attach_dn()` adds or merges a registration. `fcntl_dirnotify()` is the main registration entry point. `dnotify_init()` allocates caches and the fsnotify group.

## Control Flow

Registration rejects disabled sysctl state, zero masks remove existing watches, and non-directories return `-ENOTDIR`. Valid registrations pass `security_path_notify()`, allocate a dnotify struct and potentially a new mark, lock the fsnotify group, find or add the inode mark, check for an fd-close race with `fget_raw()`, set file ownership for signal delivery, attach or merge the registration, and recalculate masks.

On events, fsnotify calls `dnotify_handle_event()`. It ignores irrelevant non-directory events, locks the mark, scans all registrations, sends `send_sigio()` to matching owners, and frees one-shot registrations before recalculating the mark mask. `dnotify_flush()` performs close-time cleanup and detaches/free marks when the last registration disappears.

## State and Persistence Behavior

Runtime state is held in slab-allocated `dnotify_struct` nodes chained from a per-inode dnotify mark, plus the shared fsnotify group. State persists until one-shot event consumption, explicit zero-mask removal, fd close, or mark teardown. There is no on-disk persistence.

## Dependencies and Integration Points

The implementation depends on fsnotify backend APIs, signal ownership helpers, security hooks, sysctl when enabled, slab caches, spinlocks, and file descriptor lifetime rules. It exports behavior through `fcntl_dirnotify()` and `dnotify_flush()`.

## Risks

Concurrency around fd close and mark insertion is delicate; the group lock and mark spinlock must be preserved. One-shot removal while iterating the chain must update masks correctly. Signal-based delivery is lossy and legacy. `dir_notify_enable` sysctl changes can make registrations fail with `-EINVAL`.

## Test Signals

Test registration on directories and non-directories, zero-mask removal, one-shot and `DN_MULTISHOT` behavior, signal delivery for create/delete/modify/access/attrib/rename, close-time cleanup, concurrent close/register races, sysctl disable behavior, and security hook denial.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/dnotify/dnotify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/fanotify/Kconfig -->
# Research: sources/distributed-fs/ceph-client/fs/notify/fanotify/Kconfig

## Purpose

This Kconfig file exposes fanotify support and optional permission-event support.

## Important APIs, Types, and Functions

`config FANOTIFY` is a prompted boolean, defaults to `n`, selects `FSNOTIFY` and `EXPORTFS`, and describes file access notification with file descriptors. `config FANOTIFY_ACCESS_PERMISSIONS` depends on FANOTIFY, defaults `n`, and enables userspace permission decisions for access events.

## Control Flow

Enabling FANOTIFY pulls in fsnotify and exportfs support. Enabling permission checking adds support for access-decision events used by scanners or storage managers.

## State and Persistence Behavior

Only kernel configuration state is affected. Runtime state is implemented in fanotify source files.

## Dependencies and Integration Points

The `EXPORTFS` select matters because fanotify can report file handles/FIDs. The permission option gates code paths that wait for userspace responses.

## Risks

Permission events expand the ability of userspace listeners to block file access and therefore have security and availability implications. Misconfigured dependencies would break FID reporting.

## Test Signals

Build with FANOTIFY off/on and with permissions off/on, confirm fsnotify/exportfs selections, and run fanotify permission-event tests only when the permission option is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/fanotify/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/fanotify/Makefile -->
# Research: sources/distributed-fs/ceph-client/fs/notify/fanotify/Makefile

## Purpose

This Kbuild file compiles the fanotify backend and userspace interface objects when FANOTIFY is enabled.

## Important APIs, Types, and Functions

The rule is `obj-$(CONFIG_FANOTIFY) += fanotify.o fanotify_user.o`.

## Control Flow

Kbuild includes both the core backend event code and user-facing syscall/file-descriptor code under the FANOTIFY config.

## State and Persistence Behavior

The file has build-time effects only.

## Dependencies and Integration Points

It depends on the top-level notify directory descent and `CONFIG_FANOTIFY` from Kconfig.

## Risks

Core and user-interface objects must be built together because they share types, caches, and group setup. Splitting the rule incorrectly would cause link or runtime failures.

## Test Signals

Build with FANOTIFY enabled and disabled, confirming both objects are present or absent together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/fanotify/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/fanotify/fanotify.c -->
# Research: sources/distributed-fs/ceph-client/fs/notify/fanotify/fanotify.c

## Purpose

This file is the core fanotify fsnotify backend. It filters fsnotify events against fanotify marks, allocates the appropriate fanotify event representation, merges compatible queued events, handles permission-event waits, and frees event/group/mark resources.

## Important APIs, Types, and Functions

Equality and hashing helpers include `fanotify_path_equal()`, `fanotify_hash_path()`, `fanotify_hash_fsid()`, `fanotify_fh_equal()`, `fanotify_hash_fh()`, `fanotify_fid_event_equal()`, `fanotify_info_equal()`, `fanotify_name_event_equal()`, and `fanotify_error_event_equal()`. `fanotify_should_merge()` and `fanotify_merge()` implement queue coalescing with `FANOTIFY_MAX_MERGE_EVENTS`.

Permission flow is handled by `fanotify_get_response()`. Event mask filtering is handled by `fanotify_group_event_mask()`. File-handle support is provided by `fanotify_encode_fh_len()` and `fanotify_encode_fh()`. Event identity decisions use `fanotify_report_child_fid()`, `fanotify_fid_inode()`, and `fanotify_dfid_inode()`.

Allocation paths include `fanotify_alloc_path_event()`, `fanotify_alloc_mnt_event()`, `fanotify_alloc_perm_event()`, `fanotify_alloc_fid_event()`, `fanotify_alloc_name_event()`, `fanotify_alloc_error_event()`, and the dispatcher `fanotify_alloc_event()`. Delivery is handled by `fanotify_handle_event()`. Free paths include `fanotify_free_group_priv()`, per-event-type free helpers, `fanotify_free_event()`, `fanotify_freeing_mark()`, and `fanotify_free_mark()`. The exported backend vtable is `fanotify_fsnotify_ops`.

## Control Flow

Fsnotify calls `fanotify_handle_event()`. The handler verifies compile-time mask equivalence with `BUILD_BUG_ON`, derives a user-visible event mask through `fanotify_group_event_mask()`, prepares user waits for permission events, obtains cached fsid for FID mode, allocates a matching event object, queues it with `fsnotify_insert_event()`, and for permission events waits in `fanotify_get_response()` until userspace allows, denies, supplies a custom errno, or the waiter is interrupted.

Mask filtering considers report mode (`FAN_REPORT_MNT`, path mode, FID mode), object availability, mark masks, ignore masks, and whether event flags should be visible to userspace. Allocation selects event type based on group flags and data: permission path events, filesystem error events, name/FID events for directory and rename reporting, plain FID events, path events, or mount-id events. Merge logic hashes comparable event identity and never merges permission or mount events.

## State and Persistence Behavior

Fanotify state is held in `fsnotify_group` private data, notification queues, merge hash buckets, memcg charging context, mempools for error events, refcounted paths, pids, file handles, and mark accounting. Permission events carry state transitions `FAN_EVENT_INIT`, `FAN_EVENT_REPORTED`, `FAN_EVENT_ANSWERED`, and `FAN_EVENT_CANCELED`. No data is persisted on disk; state persists until userspace reads/responds, queues merge, overflow handling occurs, or group/mark teardown frees resources.

## Dependencies and Integration Points

The file depends on the fsnotify backend ABI, exportfs file-handle encoding, fanotify internal types from `fanotify.h`, audit hooks, memcg charging, wait queues, pid references, mount/path/dentry/inode data extraction, and user namespace/ucount accounting. It is paired with `fanotify_user.o`, which creates groups, reads events, and supplies permission responses.

## Risks

Permission-event races are high risk: interruption before userspace reads the event, cancellation after reporting, and answer/wakeup races must preserve correct frees and access decisions. Event merging must not merge events that userspace needs to distinguish, especially directory-vs-file events, rename records, permission events, and events without stable file handles. FID encoding failures intentionally degrade to invalid handles for some events; filesystem exportfs behavior affects fanotify semantics. Memory allocation policy differs for unlimited queues and limited queues, with security implications for lost events and OOM behavior. Refcounting of paths, pids, external file-handle buffers, mempool objects, and ucounts must match allocation type.

## Test Signals

Exercise path, FID, directory-FID, name, target-FID, rename, mount, overflow, permission, pre-access, and filesystem-error events. Verify merge behavior for identical paths/FIDs/names/errors and non-merge behavior for permission, mount, directory flag changes, and rename distinctions. Test userspace allow/deny/custom-errno/audit responses, signal interruption, group teardown while waiting, file-handle encode failure, no-fsid or weak-fsid marks, memory pressure, memcg charging, and mark/group accounting on free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/notify/fanotify/fanotify.c -->
