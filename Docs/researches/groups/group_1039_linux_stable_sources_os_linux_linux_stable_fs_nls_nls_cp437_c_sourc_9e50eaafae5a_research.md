# Group Research: group_1039_linux_stable_sources_os_linux_linux_stable_fs_nls_nls_cp437_c_sourc_9e50eaafae5a

Scope verified against `Docs/research_subset_a.md`: `sources/os/linux/linux-stable` is included. All 16 listed `fs/nls` source files were read completely. These files are generated Linux kernel NLS codepage modules: each provides byte-to-Unicode tables, sparse Unicode-to-byte reverse tables, charset-local casefold tables, `uni2char`/`char2uni` callbacks, and module registration through `register_nls()`.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp437.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp437.c

Implements Linux NLS support for DOS/OEM codepage 437, described as United States/Canada. The file is a generated translation module based on Unicode Organization charset data and only exposes exact Unicode-to-charset mappings.

The main data path is `charset2uni[256]`, mapping each single-byte CP437 value to `wchar_t`. Bytes `0x00-0x7f` are mostly ASCII/control values, while `0x80-0xff` include Latin accented letters, currency symbols, Greek/math symbols, block drawing, and box drawing characters. Reverse mapping is implemented through sparse `pageXX[256]` tables for Unicode high-byte pages `00`, `01`, `03`, `20`, `22`, `23`, and `25`, referenced by `page_uni2charset`.

`uni2char()` rejects zero output space with `-ENAMETOOLONG`, indexes the reverse page by Unicode high and low bytes, returns `-EINVAL` when no exact mapping exists, and writes one byte on success. `char2uni()` maps one input byte through `charset2uni` and treats a resulting `0x0000` as invalid, so byte NUL/undefined mappings are not accepted as regular characters by this callback.

The module exports `struct nls_table table` with charset `"cp437"`, the two conversion callbacks, and CP437-specific `charset2lower`/`charset2upper` tables. Initialization registers the table; exit unregisters it. Module metadata is `NLS Codepage 437 (United States, Canada)` with `Dual BSD/GPL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp437.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp737.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp737.c

Implements Linux NLS support for DOS/OEM codepage 737, described as Greek. It follows the generated NLS table pattern with exact mappings only.

`charset2uni[256]` maps ASCII/control bytes directly for `0x00-0x7f`; the upper half maps primarily Greek uppercase/lowercase letters, Greek accented letters, and the common DOS line/box drawing range. Reverse Unicode lookup uses sparse pages `00`, `03`, `20`, `22`, and `25`, matching the file’s Greek, punctuation/math, and box-drawing coverage.

`uni2char()` is the standard generated lookup routine: it checks output capacity, splits `wchar_t` into page and offset, looks up `page_uni2charset`, returns one output byte for an exact mapping, and returns `-EINVAL` otherwise. `char2uni()` maps a byte through `charset2uni` and rejects mappings that resolve to `0x0000`.

The `nls_table` registers charset `"cp737"` and provides the local case conversion tables. The init/exit functions call `register_nls()` and `unregister_nls()`. Module metadata names `NLS Codepage 737 (Greek)` and uses `Dual BSD/GPL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp737.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp775.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp775.c

Implements Linux NLS support for codepage 775, described as Baltic Rim. It is a generated single-byte charset translation module.

The byte-to-Unicode table preserves ASCII/control mappings in the low half and maps the high half to Baltic Latin characters, punctuation/currency symbols, and DOS box/block drawing characters. Reverse mapping is split across Unicode pages `00`, `01`, `20`, `22`, and `25`, which reflects Latin-1, Latin Extended-A, punctuation/math, and box drawing coverage.

The conversion callbacks are the generated NLS template. `uni2char()` enforces `boundlen > 0`, then uses `page_uni2charset[ch][cl]` where available; zero table entries mean unmappable and return `-EINVAL`. `char2uni()` returns exactly one wide character unless the selected byte maps to `0x0000`.

The module registers charset `"cp775"` through `struct nls_table`, with codepage-specific lower/upper byte case maps. Module registration is handled by `init_nls_cp775()` and `exit_nls_cp775()`. Metadata describes `NLS Codepage 775 (Baltic Rim)` and declares `Dual BSD/GPL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp775.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp850.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp850.c

Implements Linux NLS support for codepage 850, described as Europe. The file supplies generated exact translation tables for a DOS/OEM Western European encoding.

`charset2uni[256]` maps low bytes to ASCII/control values and high bytes to Western European Latin letters, symbols, and DOS line/block drawing characters. Reverse Unicode pages are `00`, `01`, `20`, and `25`, covering Latin-1, limited Latin Extended-A, selected punctuation/currency, and box/block drawing.

`uni2char()` performs a sparse reverse-table lookup and returns `-ENAMETOOLONG` for no output capacity or `-EINVAL` for unmappable Unicode. `char2uni()` performs direct byte lookup and rejects mappings resolving to `0x0000`.

The registered `nls_table` is named `"cp850"` and includes charset-local lower/upper maps used by filesystems that need codepage-aware case behavior. Init and exit register/unregister this table. Metadata is `NLS Codepage 850 (Europe)` under `Dual BSD/GPL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp850.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp852.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp852.c

Implements Linux NLS support for codepage 852, described as Central/Eastern Europe. It is generated from Unicode charset tables with exact reverse mappings only.

The forward table maps ASCII/control bytes in the lower half and Central/Eastern European Latin characters in the upper half, including Latin Extended-A/B code points, plus box/block drawing characters. Reverse lookup pages are `00`, `01`, `02`, and `25`, matching Latin-1, Latin Extended-A, Latin Extended-B, and box drawing.

`uni2char()` follows the common sparse-page reverse lookup and reports `-EINVAL` when a Unicode character lacks an exact CP852 byte. `char2uni()` maps one byte through the forward table and treats `0x0000` as invalid.

The `nls_table` registers charset `"cp852"` with CP852-specific case maps. Init and exit are standard `register_nls()`/`unregister_nls()` wrappers. Module metadata says `NLS Codepage 852 (Central/Eastern Europe)` and `Dual BSD/GPL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp852.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp855.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp855.c

Implements Linux NLS support for codepage 855, described as Cyrillic. It provides generated single-byte conversion tables.

The forward table maps lower bytes to ASCII/control characters and the upper range to Cyrillic letters, selected symbols, and box/block drawing. Reverse Unicode coverage is sparse across pages `00`, `04`, `21`, and `25`, corresponding to Latin-1 symbols, Cyrillic, number/form symbols, and box drawing.

`uni2char()` checks output length, selects a reverse page from `page_uni2charset`, and returns `-EINVAL` when the table entry is zero. `char2uni()` maps one raw byte through `charset2uni` and rejects `0x0000`.

The module registers charset `"cp855"` with local byte casefold tables. Lifecycle is standard NLS module registration and unregistration. Metadata identifies `NLS Codepage 855 (Cyrillic)` and `Dual BSD/GPL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp855.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp857.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp857.c

Implements Linux NLS support for codepage 857, described as Turkish. It is a generated exact mapping module.

The byte-to-Unicode table maps ASCII/control values in the lower half and Turkish/Western Latin characters plus box drawing in the upper half. Reverse Unicode mappings are provided for pages `00`, `01`, and `25`, covering Latin-1, limited Latin Extended-A Turkish characters, and box/block drawing.

`uni2char()` uses the common two-level reverse lookup and returns one byte on success, `-ENAMETOOLONG` for no output buffer, or `-EINVAL` for unmappable Unicode. `char2uni()` maps one input byte and rejects a `0x0000` result.

The `nls_table` charset is `"cp857"`, with codepage-specific `charset2lower` and `charset2upper` tables. Init/exit register and unregister the table. Metadata is `NLS Codepage 857 (Turkish)` and `Dual BSD/GPL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp857.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp860.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp860.c

Implements Linux NLS support for codepage 860, described as Portuguese. This is a generated DOS/OEM charset module.

`charset2uni[256]` maps the lower half to ASCII/control values and the upper half to Portuguese/Western European Latin characters, DOS line/box drawing, Greek/math symbols, and block characters. Reverse Unicode pages are `00`, `03`, `20`, `22`, `23`, and `25`.

The conversion callbacks match the generated NLS model. `uni2char()` is exact-only and fails with `-EINVAL` for characters not represented in CP860. `char2uni()` performs direct byte lookup and rejects bytes whose forward mapping is `0x0000`.

The module registers charset `"cp860"` with local lower/upper byte maps and standard NLS init/exit routines. Metadata identifies `NLS Codepage 860 (Portuguese)` and `Dual BSD/GPL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp860.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp861.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp861.c

Implements Linux NLS support for codepage 861, described as Icelandic. It is generated from Unicode charset data and only supports exact reverse mappings.

The forward table maps low bytes to ASCII/control values and high bytes to Icelandic/Western Latin letters, DOS drawing characters, and symbols. Reverse Unicode pages are `00`, `01`, `03`, `20`, `22`, `23`, and `25`, reflecting Latin, Greek/math, symbol, and box-drawing coverage.

`uni2char()` checks `boundlen`, indexes the sparse reverse page table, and returns `-EINVAL` for unmappable Unicode. `char2uni()` returns one `wchar_t` from `charset2uni` unless that mapping is `0x0000`.

The registered charset is `"cp861"` with CP861 lower/upper case tables. Lifecycle is handled through `register_nls()` and `unregister_nls()`. Module metadata is `NLS Codepage 861 (Icelandic)` with `Dual BSD/GPL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp861.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp862.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp862.c

Implements Linux NLS support for codepage 862, described as Hebrew. It is a generated single-byte codepage module.

The forward table maps lower bytes to ASCII/control values. The upper range includes Hebrew letters, Latin/symbol entries, and DOS box/block drawing. Reverse lookup is sparse across pages `00`, `01`, `03`, `05`, `20`, `22`, `23`, and `25`; page `05` is the Hebrew block and is the file’s key differentiator.

`uni2char()` performs exact Unicode-to-byte conversion through `page_uni2charset` and returns `-EINVAL` for characters outside the supported mappings. `char2uni()` maps a raw byte to Unicode and rejects `0x0000`.

The `nls_table` registers charset `"cp862"` and includes local case tables, though Hebrew letters themselves are not case-paired. Init and exit register/unregister the table. Metadata is `NLS Codepage 862 (Hebrew)` and `Dual BSD/GPL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp862.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp863.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp863.c

Implements Linux NLS support for codepage 863, described as Canadian French. It follows the generated Linux NLS table structure.

The byte-to-Unicode table maps ASCII/control values directly and maps the high byte range to French/Western Latin letters, selected symbols, and DOS box/block drawing characters. Reverse Unicode pages are `00`, `01`, `03`, `20`, `22`, `23`, and `25`.

`uni2char()` enforces a positive output bound and uses sparse reverse tables for exact mappings. Missing reverse entries return `-EINVAL`. `char2uni()` maps one byte through `charset2uni` and rejects `0x0000`.

The module registers charset `"cp863"` with codepage-specific case conversion arrays. Standard module init/exit functions register and unregister the NLS table. Metadata identifies `NLS Codepage 863 (Canadian French)` and `Dual BSD/GPL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp863.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp864.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp864.c

Implements Linux NLS support for codepage 864, described as Arabic. It is a generated exact mapping table module.

Unlike most surrounding DOS codepages, CP864 maps some printable low-range bytes to Arabic-related symbols, including `0x25` to U+066A. The high byte range includes Arabic letters and presentation forms, plus Greek/math and box/block drawing entries. Reverse Unicode pages are `00`, `03`, `06`, `22`, `25`, and `fe`; page `06` covers Arabic, and page `fe` covers Arabic presentation forms.

`uni2char()` performs sparse exact reverse lookup and returns `-EINVAL` for unsupported Unicode. `char2uni()` maps one byte through the forward table and rejects `0x0000`, which also filters undefined CP864 byte positions.

The registered charset is `"cp864"` with byte-oriented lower/upper tables. Init and exit use the normal NLS registration lifecycle. Metadata is `NLS Codepage 864 (Arabic)` under `Dual BSD/GPL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp864.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp865.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp865.c

Implements Linux NLS support for codepage 865, described as Norwegian/Danish. It is a generated DOS/OEM charset module.

The forward table maps low bytes to ASCII/control values and high bytes to Nordic/Western Latin characters, DOS box/block drawing, Greek/math symbols, and related punctuation. Reverse Unicode pages are `00`, `01`, `03`, `20`, `22`, `23`, and `25`, very similar in shape to CP437/CP861 but with Nordic-specific byte assignments.

`uni2char()` checks buffer capacity and uses sparse reverse pages for exact mappings only. `char2uni()` maps one byte to a `wchar_t` and rejects `0x0000`.

The module registers charset `"cp865"` with CP865-specific casefold arrays. Init/exit call `register_nls()` and `unregister_nls()`. Metadata identifies `NLS Codepage 865 (Norwegian, Danish)` and `Dual BSD/GPL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp865.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp866.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp866.c

Implements Linux NLS support for codepage 866, described as Cyrillic/Russian. It is generated and exact-mapping-only.

The byte-to-Unicode table maps low bytes to ASCII/control values, high bytes mostly to Cyrillic uppercase/lowercase letters, plus selected symbols and box/block drawing. Reverse Unicode pages are `00`, `04`, `21`, `22`, and `25`, covering Latin-1 symbols, Cyrillic, number/form symbols, math, and drawing characters.

`uni2char()` performs the standard reverse lookup with `-ENAMETOOLONG` for no space and `-EINVAL` for unmappable Unicode. `char2uni()` maps one byte and rejects `0x0000`.

The `nls_table` charset is `"cp866"` and includes Cyrillic-aware byte case maps. Lifecycle functions register/unregister the table. Metadata is `NLS Codepage 866 (Cyrillic/Russian)` and `Dual BSD/GPL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp866.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp869.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp869.c

Implements Linux NLS support for codepage 869, described as Greek. It is a generated exact mapping module distinct from CP737 by its byte assignments and Greek coverage.

`charset2uni[256]` maps lower bytes to ASCII/control values and high bytes to Greek letters/diacritics, selected Latin/symbol entries, and DOS box/block drawing. Reverse Unicode pages are `00`, `03`, `20`, and `25`, covering Latin-1/symbols, Greek, punctuation, and box drawing.

`uni2char()` uses sparse reverse pages and returns `-EINVAL` for Unicode characters without an exact CP869 byte. `char2uni()` maps one raw byte and treats `0x0000` as invalid.

The registered table uses charset `"cp869"` with CP869 lower/upper maps. Init and exit use standard NLS registration. Metadata identifies `NLS Codepage 869 (Greek)` and `Dual BSD/GPL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp869.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp874.c -->
# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp874.c

Implements Linux NLS support for Thai codepage 874 and aliases it as TIS-620. This is the only file in the group that sets `.alias = "tis-620"` and emits `MODULE_ALIAS_NLS(tis-620)`.

The forward table maps ASCII/control bytes directly, marks several Windows-style undefined/control-extension positions as `0x0000`, maps selected punctuation in the `0x80-0x9f` area, and maps `0xa1-0xfb` primarily to Thai Unicode U+0E01 through U+0E5B. Reverse Unicode pages are `00`, `0e`, and `20`, corresponding to Latin-1/ASCII, Thai, and punctuation.

`uni2char()` follows the generated exact reverse lookup and returns `-EINVAL` for Unicode not present in CP874/TIS-620. `char2uni()` maps one byte through `charset2uni` and rejects undefined byte positions via the `0x0000` check.

The `nls_table` registers charset `"cp874"` with alias `"tis-620"` plus local lower/upper byte maps. Init/exit use `register_nls()` and `unregister_nls()`. Metadata is `NLS Thai charset (CP874, TIS-620)`, `Dual BSD/GPL`, and the TIS-620 NLS alias.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nls/nls_cp874.c -->