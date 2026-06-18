# subset-b-005709 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp437.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp437.c

Purpose: Implements the Linux NLS single-byte translation module for DOS codepage 437, described in the module metadata as United States/Canada. It provides exact byte-to-Unicode and Unicode-to-byte mappings for filesystems that mount with `iocharset=cp437` or otherwise request this NLS table.

Important APIs/types/functions: The file defines `charset2uni[256]` for byte-to-`wchar_t` conversion, Unicode reverse pages `page00`, `page01`, `page03`, `page20`, `page22`, `page23`, and `page25`, `page_uni2charset[256]` as the high-byte dispatch table, byte folding tables `charset2lower[256]` and `charset2upper[256]`, callbacks `uni2char()` and `char2uni()`, and a `struct nls_table` named `table` with `.charset = "cp437"`. Module lifecycle is `init_nls_cp437()` calling `register_nls(&table)` and `exit_nls_cp437()` calling `unregister_nls(&table)`.

Control flow: `uni2char()` rejects zero output space with `-ENAMETOOLONG`, splits the Unicode scalar into high and low bytes, indexes `page_uni2charset[ch]`, and writes one output byte only when a nonzero reverse-table entry exists; otherwise it returns `-EINVAL`. `char2uni()` indexes `charset2uni[*rawstring]`, rejects `0x0000` as unmapped, and returns one consumed byte. Initialization only registers the static table; exit unregisters it.

State and persistence behavior: All conversion data is static read-only module data. Runtime state is limited to registration in the kernel NLS registry while the module is loaded. There is no persistent storage, allocation, locking, or mutable per-mount state in the file.

Dependencies and integration points: Depends on `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>`. It integrates with the VFS/filesystem NLS layer through `struct nls_table`, `register_nls()`, `unregister_nls()`, `module_init()`, and `module_exit()`. The table provides byte-level case folding for callers that perform case-insensitive legacy-name handling.

Risks: Reverse mappings use `0x00` as the sentinel for "unmapped", so U+0000 and any byte whose forward mapping is zero cannot round-trip through these callbacks. The file trusts callers to pass at least one input byte to `char2uni()`; `boundlen` is not checked there because this is a fixed-width single-byte table. Because mappings are exact only, Unicode compatibility variants, decomposition, and best-fit conversions are intentionally unsupported. Test changes must preserve reciprocal table entries, especially for CP437 box drawing, math, Greek, and Latin-1 symbols.

Test signals: Build the NLS module, load it, and request `cp437` through a filesystem or direct NLS lookup. Table tests should iterate all nonzero `charset2uni` entries, confirm `uni2char(charset2uni[b]) == b` where the reverse table defines an exact mapping, confirm unmapped Unicode returns `-EINVAL`, and check `boundlen <= 0` returns `-ENAMETOOLONG`. Case-fold tests should verify ASCII A-Z/a-z and notable CP437 accented pairs in `charset2lower`/`charset2upper`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp437.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp737.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp737.c

Purpose: Implements the Linux NLS translation module for DOS codepage 737, a Greek single-byte character set. It lets filesystem name conversion code translate between on-disk CP737 bytes and Unicode `wchar_t` values using exact mapping tables generated from Unicode charset data.

Important APIs/types/functions: The module contains `charset2uni[256]`, reverse pages `page00`, `page03`, `page20`, `page22`, and `page25`, `page_uni2charset[256]`, `charset2lower[256]`, `charset2upper[256]`, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp737"`. Lifecycle hooks are `init_nls_cp737()` and `exit_nls_cp737()`, wired through `module_init` and `module_exit`.

Control flow: Conversion is a direct table lookup. `uni2char()` validates output capacity, derives `ch` and `cl` from the Unicode value, selects the reverse page by high byte, and returns one byte on a nonzero table hit or `-EINVAL` otherwise. `char2uni()` maps one input byte through `charset2uni` and rejects zero mappings. Module initialization registers the table; unload unregisters it.

State and persistence behavior: The file has only static const mapping data plus the registered NLS table. The only runtime state is the presence of the table in the kernel NLS registry while the module is loaded. It does not allocate memory, write storage, or persist configuration.

Dependencies and integration points: Uses the standard kernel module and NLS APIs from `<linux/module.h>`, `<linux/nls.h>`, and `<linux/errno.h>`. Filesystems that request `cp737` receive these callbacks for filename conversion and byte-level case folding. Greek uppercase/lowercase byte folds are encoded in the case tables, alongside ASCII folding.

Risks: `0x00` is both a byte value and the reverse-table sentinel, so NUL and holes in CP737 cannot be represented as successful conversions. `char2uni()` assumes a valid one-byte input buffer and ignores `boundlen`. Greek sigma and accented Greek mappings are exact table entries only; no normalization-aware or context-sensitive case behavior is attempted.

Test signals: Validate that the module registers as `cp737`, then round-trip all mapped Greek, ASCII, box-drawing, and symbol bytes through `char2uni()` and `uni2char()`. Negative tests should cover unmapped Unicode pages and zero output length. Case tests should exercise Greek alpha/Alpha ranges and ASCII.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp737.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp775.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp775.c

Purpose: Provides the Linux NLS module for DOS codepage 775, used for Baltic Rim character data. It translates single-byte CP775 filesystem names to Unicode and back with exact generated tables.

Important APIs/types/functions: Defines `charset2uni[256]`, reverse lookup pages `page00`, `page01`, `page20`, `page22`, and `page25`, `page_uni2charset[256]`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp775"`. `init_nls_cp775()` and `exit_nls_cp775()` register and unregister the table.

Control flow: `uni2char()` performs one-byte output conversion by checking `boundlen`, dispatching through `page_uni2charset` by Unicode high byte, and requiring a nonzero reverse entry. `char2uni()` reads one raw byte, translates through `charset2uni`, and fails on zero. Load/unload is linear registration logic.

State and persistence behavior: There is no mutable conversion state. The static mapping arrays and table live for the module lifetime; external state is only the NLS registry entry while loaded.

Dependencies and integration points: Integrates with kernel filesystems through `struct nls_table` and the NLS registry APIs in `<linux/nls.h>`. Its case tables support CP775-aware filename folding for Baltic Latin letters as well as ASCII.

Risks: Exact table semantics mean characters outside CP775 return `-EINVAL`, with no transliteration. The reverse mapping cannot encode byte `0x00` because zero marks missing entries. Case folding is byte-table based and should not be treated as full Unicode case mapping.

Test signals: Build and load the codepage module, confirm lookup by `cp775`, and run byte round-trips for Baltic accented letters, Latin-1 symbols, box-drawing characters, and ASCII. Include failure checks for unmapped Unicode, `boundlen == 0`, and case-fold expectations for Baltic-specific upper/lower byte pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp775.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp850.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp850.c

Purpose: Implements the Linux NLS module for DOS codepage 850, labeled Europe in the module description. It supports exact conversion between CP850 bytes and Unicode for legacy filesystem names.

Important APIs/types/functions: The file supplies `charset2uni[256]`, reverse pages `page00`, `page01`, `page20`, and `page25`, `page_uni2charset[256]`, byte case tables, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp850"`. `init_nls_cp850()` registers the table and `exit_nls_cp850()` unregisters it.

Control flow: The conversion callbacks are fixed-width single-byte lookups. `uni2char()` checks output room, chooses a Unicode page table, writes one byte for exact hits, and returns `-EINVAL` for holes. `char2uni()` maps `*rawstring` through `charset2uni` and treats zero as invalid. Module entry and exit only add/remove the table from the NLS registry.

State and persistence behavior: All mappings are static const data. No allocation or persistent writes occur; the only stateful effect is registration of the `cp850` NLS table during module lifetime.

Dependencies and integration points: Uses kernel module/NLS headers and error codes. Filesystems use this table when `cp850` is selected for on-disk names. `charset2lower` and `charset2upper` encode CP850-specific Latin accented case folding.

Risks: CP850 overlaps with CP437 in box-drawing regions but differs in extended Latin letters, so accidental table substitution can silently corrupt names. The implementation has no fallback for unmappable Unicode and no normalization. `char2uni()` relies on caller-provided input length validity.

Test signals: Verify `cp850` registration, round-trip all mapped high-bit European Latin bytes, and compare known CP850-specific letters against expected Unicode values. Confirm unmapped Unicode returns `-EINVAL`, zero output space returns `-ENAMETOOLONG`, and case tables preserve ASCII plus accented pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp850.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp852.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp852.c

Purpose: Provides the Linux NLS module for DOS codepage 852, covering Central and Eastern European Latin scripts. It is an exact single-byte conversion table for legacy filesystem filename encoding.

Important APIs/types/functions: Defines `charset2uni[256]`, reverse pages `page00`, `page01`, `page02`, and `page25`, `page_uni2charset[256]`, `charset2lower[256]`, `charset2upper[256]`, conversion callbacks `uni2char()` and `char2uni()`, and `struct nls_table table` with `.charset = "cp852"`. `init_nls_cp852()` and `exit_nls_cp852()` handle NLS registry lifecycle.

Control flow: `uni2char()` uses the Unicode high byte to choose a reverse page, then the low byte for a single output byte. It returns `-ENAMETOOLONG` if output capacity is zero and `-EINVAL` for missing mappings. `char2uni()` performs the forward lookup and rejects zero. Module load and unload call the standard register/unregister helpers.

State and persistence behavior: Static tables are immutable. The file keeps no dynamic state and persists nothing. The only externally visible state is whether the `cp852` table is currently registered.

Dependencies and integration points: Depends on Linux module and NLS APIs. It plugs into filesystem name conversion through `struct nls_table`, and the case folding arrays encode CP852-specific Central/Eastern European upper/lower byte pairs.

Risks: CP852 uses Latin Extended-A/B mappings, so stale or incorrectly generated `page01`/`page02` reverse tables can cause asymmetric conversion. Byte-level case folding is not a substitute for Unicode locale-sensitive behavior. Unmapped characters fail instead of being approximated.

Test signals: Exercise registration as `cp852`, round-trip Czech/Polish/Hungarian-style accented letters present in the high-bit table, and verify page coverage for Unicode pages 00, 01, 02, and 25. Negative tests should cover unmapped Cyrillic/Greek inputs, insufficient output length, and known case-fold pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp852.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp855.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp855.c

Purpose: Implements the Linux NLS translation module for DOS codepage 855, a Cyrillic codepage. It maps CP855 bytes to Unicode Cyrillic characters and back for legacy filesystem name handling.

Important APIs/types/functions: Provides `charset2uni[256]`, reverse pages `page00`, `page04`, `page21`, and `page25`, `page_uni2charset[256]`, byte case tables, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp855"`. `init_nls_cp855()` registers with the NLS layer, and `exit_nls_cp855()` unregisters.

Control flow: `uni2char()` checks output capacity, selects a reverse table using the Unicode high byte, and writes a single byte for a nonzero exact entry. `char2uni()` consumes one byte and returns the corresponding `wchar_t` unless the mapping is zero. The module init/exit paths contain no additional branching.

State and persistence behavior: Conversion state is entirely static and read-only. Runtime mutation is limited to the kernel NLS registry entry during the loaded module lifetime.

Dependencies and integration points: Uses `<linux/nls.h>` and module infrastructure. Filesystem drivers can request `cp855`; once loaded, the callbacks and Cyrillic case tables are used by generic NLS-aware filename conversion paths.

Risks: CP855's Cyrillic upper/lower pairs are byte-specific and differ from CP866, so using the wrong Cyrillic module changes both conversion and case folding. Exact-only conversion rejects unsupported Unicode and cannot normalize composed characters. The reverse tables use zero as an unmapped sentinel.

Test signals: Verify lookup by `cp855`, round-trip Cyrillic bytes across Unicode page 04, and test the encoded Cyrillic case pairs. Include error tests for missing output space, unmapped Unicode, and byte zero behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp855.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp857.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp857.c

Purpose: Supplies the Linux NLS module for DOS codepage 857, the Turkish single-byte codepage. It converts between CP857 on-disk bytes and Unicode for filesystem names.

Important APIs/types/functions: Defines `charset2uni[256]`, reverse pages `page00`, `page01`, and `page25`, `page_uni2charset[256]`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp857"`. Registry lifecycle is handled by `init_nls_cp857()` and `exit_nls_cp857()`.

Control flow: `uni2char()` returns one byte after a successful reverse-page lookup and returns `-ENAMETOOLONG` or `-EINVAL` for no capacity or no exact mapping. `char2uni()` directly indexes `charset2uni` and returns one byte consumed if nonzero. Module load/unload register and unregister the static table.

State and persistence behavior: The module has immutable generated tables and no persistent state. Its only mutable effect is registration in the global NLS table list while loaded.

Dependencies and integration points: Integrates with Linux filesystem NLS consumers through `struct nls_table`. Turkish-specific Latin mappings and byte-level upper/lower tables are supplied to callers that need case-insensitive comparisons in this legacy encoding.

Risks: Turkish dotted/dotless I behavior is represented only by static byte tables, not full locale-aware Unicode casing. The source has several unmapped `0x0000` entries in `charset2uni`, so tests must distinguish intentional holes from accidental omissions. No best-fit conversion exists for characters outside CP857.

Test signals: Confirm `cp857` registration, round-trip Turkish letters such as dotted/dotless I and related Latin Extended values, and verify `charset2lower`/`charset2upper` pairs. Negative tests should include unmapped byte holes, unmapped Unicode, and zero output length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp857.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp860.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp860.c

Purpose: Implements the Linux NLS module for DOS codepage 860, labeled Portuguese. It supports exact single-byte translation between CP860 bytes and Unicode for legacy filesystem filename conversion.

Important APIs/types/functions: The module defines `charset2uni[256]`, reverse pages `page00`, `page03`, `page20`, `page22`, `page23`, and `page25`, `page_uni2charset[256]`, byte case-fold arrays, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp860"`. Lifecycle hooks are `init_nls_cp860()` and `exit_nls_cp860()`.

Control flow: `uni2char()` validates output length, performs high-byte reverse-page dispatch, emits one byte for an exact nonzero mapping, or fails with `-EINVAL`. `char2uni()` maps one byte through `charset2uni` and rejects zero. Init and exit are direct calls into the NLS registry.

State and persistence behavior: All data is static and immutable. There is no allocation, no persisted filesystem state, and no per-caller context; only module registration state changes.

Dependencies and integration points: Uses Linux module/NLS headers and error codes. Filesystem NLS users select this table with `cp860`; case folding is supplied through the CP860 `charset2lower` and `charset2upper` arrays.

Risks: CP860 differs from CP437/CP850 in Portuguese accented letters while retaining many graphical symbols; confusing these codepages can produce visually plausible but incorrect filenames. Exact lookup rejects missing Unicode, and NUL cannot be represented because zero is the unmapped marker.

Test signals: Round-trip Portuguese accented entries, ASCII, and graphical symbols. Validate `cp860` lookup, `-ENAMETOOLONG` on no output space, `-EINVAL` for unmapped Unicode, and byte-level case folding for Portuguese-specific pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp860.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp861.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp861.c

Purpose: Provides the Linux NLS module for DOS codepage 861, labeled Icelandic. It translates legacy CP861 bytes to Unicode and back for filesystem filename processing.

Important APIs/types/functions: Contains `charset2uni[256]`, reverse pages `page00`, `page01`, `page03`, `page20`, `page22`, `page23`, and `page25`, `page_uni2charset[256]`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp861"`. `init_nls_cp861()` registers the table; `exit_nls_cp861()` unregisters it.

Control flow: The callbacks perform fixed one-byte conversions. `uni2char()` checks `boundlen`, looks up the Unicode page and low byte, and returns one output byte or an error. `char2uni()` performs the forward byte lookup and treats a zero result as invalid. The module lifecycle is linear NLS registration.

State and persistence behavior: No mutable data is kept in the conversion path. Static tables are module-local; registration in the NLS subsystem is the only runtime state.

Dependencies and integration points: Depends on kernel module and NLS APIs. It integrates with any filesystem using the kernel NLS layer and provides CP861-specific case folding for Icelandic letters plus common graphical symbols.

Risks: Icelandic letters such as eth/thorn must match CP861 byte positions; replacing with nearby CP437/CP865 tables would change filenames. Reverse tables cannot encode zero-valued mappings, and no Unicode normalization or fallback conversion is performed.

Test signals: Confirm registration under `cp861`, round-trip Icelandic-specific high-bit bytes, and verify ASCII/accented case folding. Include negative tests for unmapped Unicode pages and no output buffer capacity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp861.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp862.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp862.c

Purpose: Implements the Linux NLS module for DOS codepage 862, a Hebrew single-byte codepage. It enables exact conversion between CP862 filesystem bytes and Unicode Hebrew/Latin/symbol characters.

Important APIs/types/functions: Defines `charset2uni[256]`, reverse pages `page00`, `page01`, `page03`, `page05`, `page20`, `page22`, `page23`, and `page25`, `page_uni2charset[256]`, byte case tables, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp862"`. `init_nls_cp862()` and `exit_nls_cp862()` manage registration.

Control flow: `uni2char()` maps Unicode page 05 Hebrew entries and other covered pages back to one CP862 byte after checking output capacity. Missing pages or zero entries return `-EINVAL`. `char2uni()` maps one input byte to Unicode and rejects zero. Module init/exit only register and unregister.

State and persistence behavior: The module stores only static generated tables and has no persistence. Runtime state is the registered NLS table while loaded.

Dependencies and integration points: Uses Linux NLS and module infrastructure. Filesystems selecting `cp862` use these callbacks for names; Latin case folding is present, while Hebrew letters themselves do not have simple upper/lower byte pairs in this DOS codepage.

Risks: Right-to-left display ordering is outside this module; it only converts code points. Applications may misinterpret successful conversion as bidi handling. Exact mapping rejects Hebrew presentation variants and other Unicode forms not represented in CP862.

Test signals: Verify `cp862` lookup, round-trip Hebrew letters in Unicode page 05, and test shared box-drawing/symbol entries. Check that unsupported Hebrew marks or presentation forms fail with `-EINVAL` and that case tables do not unexpectedly alter Hebrew bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp862.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp863.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp863.c

Purpose: Provides the Linux NLS module for DOS codepage 863, labeled Canadian French. It maps CP863 bytes used in legacy filenames to Unicode and back with exact generated tables.

Important APIs/types/functions: Supplies `charset2uni[256]`, reverse pages `page00`, `page01`, `page03`, `page20`, `page22`, `page23`, and `page25`, `page_uni2charset[256]`, case-fold arrays, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp863"`. Module lifecycle is `init_nls_cp863()` and `exit_nls_cp863()`.

Control flow: `uni2char()` dispatches by Unicode high byte, requires a nonzero exact reverse mapping, and writes one output byte. `char2uni()` consumes one byte through `charset2uni` and fails on zero. Registration and unregistration are direct calls to NLS helpers.

State and persistence behavior: Static const tables are the only conversion data. The module keeps no per-filesystem state and writes nothing to persistent storage.

Dependencies and integration points: Integrates with the Linux NLS registry and filesystem callers through `struct nls_table`. Its case tables handle CP863 Canadian French accented byte pairs and ASCII.

Risks: CP863 repositions several French accented characters compared with CP850/CP437, so using the wrong table causes reversible but semantically wrong names. Exact-only reverse lookup fails for decomposed accents and other Unicode equivalents. NUL and unmapped table holes are invalid.

Test signals: Confirm `cp863` registration, round-trip Canadian French accented bytes, and test box-drawing/symbol entries inherited from DOS layouts. Validate expected failures for decomposed accent sequences and unmapped Unicode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp863.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp864.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp864.c

Purpose: Implements the Linux NLS module for DOS codepage 864, an Arabic codepage. It performs exact conversion between CP864 single-byte values and Unicode Arabic, Arabic presentation forms, Latin, and symbol code points for filesystem names.

Important APIs/types/functions: Defines `charset2uni[256]`, reverse pages `page00`, `page03`, `page06`, `page22`, `page25`, and `pagefe`, `page_uni2charset[256]`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp864"`. `init_nls_cp864()` registers and `exit_nls_cp864()` unregisters the table.

Control flow: `uni2char()` uses Unicode high-byte dispatch, notably including page 06 for Arabic and page FE for presentation forms, then writes a single byte for exact nonzero entries. `char2uni()` maps one raw byte to Unicode and rejects zero. Module init/exit simply update the NLS registry.

State and persistence behavior: The conversion tables are immutable module data. There is no dynamic allocation or persistent storage; the only runtime state is NLS registration.

Dependencies and integration points: Uses standard Linux module and NLS APIs. Filesystem NLS users selecting `cp864` receive these conversion callbacks and byte case tables. Arabic shaping, joining, and bidi processing are not integration responsibilities of this file.

Risks: CP864 includes Arabic presentation-form mappings, so replacing those with normalized base Arabic characters would break exact round-trip behavior. The source contains several unmapped bytes; tests must preserve intentional holes. The module does not perform shaping or bidirectional reordering, only codepoint conversion.

Test signals: Verify registration as `cp864`, round-trip Arabic base letters, presentation form entries from page FE, Latin symbols, and box-drawing bytes. Confirm unmapped bytes/Unicode return `-EINVAL` and no-output-space returns `-ENAMETOOLONG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp864.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp865.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp865.c

Purpose: Provides the Linux NLS module for DOS codepage 865, labeled Norwegian and Danish. It converts legacy CP865 filename bytes to Unicode and back.

Important APIs/types/functions: Contains `charset2uni[256]`, reverse pages `page00`, `page01`, `page03`, `page20`, `page22`, `page23`, and `page25`, `page_uni2charset[256]`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp865"`. `init_nls_cp865()` and `exit_nls_cp865()` implement module registry lifecycle.

Control flow: The callbacks are single-byte exact lookups. `uni2char()` validates output room, finds a reverse page from the Unicode high byte, and writes one byte if the table entry is nonzero. `char2uni()` reads one byte and rejects zero-valued mappings. Load/unload only register and unregister `table`.

State and persistence behavior: No conversion state changes at runtime. Static tables live in module memory; external mutable state is limited to the NLS registry entry.

Dependencies and integration points: Integrates with Linux filesystems through `<linux/nls.h>` and `struct nls_table`. Case folding covers ASCII plus CP865 Nordic letters used in legacy DOS filenames.

Risks: CP865 is close to CP437 but differs in Nordic letters, making copy/paste table changes risky. No normalization, decomposition, or fallback is performed. Reverse lookup cannot encode byte zero because zero denotes missing entries.

Test signals: Confirm `cp865` lookup, round-trip Norwegian/Danish letters and DOS graphical symbols, and validate upper/lower byte folds. Include negative tests for unmapped Unicode and zero output capacity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp865.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp866.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp866.c

Purpose: Implements the Linux NLS module for DOS codepage 866, labeled Cyrillic/Russian. It converts single-byte CP866 filenames to Unicode and back using exact mapping tables.

Important APIs/types/functions: Defines `charset2uni[256]`, reverse pages `page00`, `page04`, `page21`, `page22`, and `page25`, `page_uni2charset[256]`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp866"`. `init_nls_cp866()` registers the table and `exit_nls_cp866()` unregisters it.

Control flow: `uni2char()` checks for at least one output byte, selects the reverse table by Unicode high byte, and returns one byte for exact entries. Missing entries return `-EINVAL`. `char2uni()` maps one byte through `charset2uni` and fails on zero. Module lifecycle is standard NLS registration.

State and persistence behavior: The module has no mutable conversion state and persists nothing. Its only stateful effect is that the kernel can resolve `cp866` while the module is loaded.

Dependencies and integration points: Uses Linux module infrastructure and NLS APIs. Filesystem code uses the callbacks for CP866 names, with Cyrillic upper/lower folding in byte tables.

Risks: CP866 and CP855 are both Cyrillic but not interchangeable; byte positions and case folding differ. Exact mapping rejects unsupported Unicode and does not normalize Cyrillic variants. `char2uni()` relies on caller input buffer validity.

Test signals: Round-trip Russian Cyrillic uppercase and lowercase bytes, verify `charset2upper`/`charset2lower`, and confirm page 04 reverse mappings. Negative tests should cover unmapped Unicode pages, no output space, and byte zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp866.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp869.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp869.c

Purpose: Provides the Linux NLS module for DOS codepage 869, a Greek codepage. It maps between CP869 bytes and Unicode for legacy filesystem filename conversion.

Important APIs/types/functions: Supplies `charset2uni[256]`, reverse pages `page00`, `page03`, `page20`, and `page25`, `page_uni2charset[256]`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp869"`. Lifecycle hooks are `init_nls_cp869()` and `exit_nls_cp869()`.

Control flow: `uni2char()` performs capacity checking, high-byte reverse-page dispatch, nonzero entry validation, and one-byte output. `char2uni()` maps one byte to Unicode and rejects zero. Module entry/exit add and remove the NLS table.

State and persistence behavior: Static generated data is immutable. No heap state, per-mount context, or persistent data is maintained.

Dependencies and integration points: Integrates with the Linux NLS registry through `register_nls()` and `unregister_nls()`. Filesystems selecting `cp869` use these callbacks and Greek/ASCII byte case folding tables.

Risks: The table contains multiple unmapped high-bit byte positions, so exhaustive tests must allow intentional `0x0000` holes. CP869 differs from CP737 in Greek layout and symbols; using one for the other corrupts round-trip conversion. No context-sensitive final sigma or Unicode normalization is performed.

Test signals: Validate `cp869` registration, round-trip mapped Greek letters and punctuation, and assert `-EINVAL` for intentional byte holes or unsupported Unicode. Check ASCII and Greek case-fold table entries plus `boundlen <= 0` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp869.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp874.c -->
# sources/distributed-fs/ceph-client/fs/nls/nls_cp874.c

Purpose: Implements the Linux NLS module for Thai CP874/TIS-620. It provides exact single-byte conversion between Thai legacy bytes and Unicode for filesystem names and exposes `tis-620` as an alias.

Important APIs/types/functions: Defines `charset2uni[256]`, reverse pages `page00`, `page0e`, and `page20`, `page_uni2charset[256]`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, and `struct nls_table table` with `.charset = "cp874"` and `.alias = "tis-620"`. Lifecycle hooks are `init_nls_cp874()` and `exit_nls_cp874()`. Metadata includes `MODULE_DESCRIPTION("NLS Thai charset (CP874, TIS-620)")`, `MODULE_LICENSE("Dual BSD/GPL")`, and `MODULE_ALIAS_NLS(tis-620)`.

Control flow: `uni2char()` checks output capacity, selects reverse page 00, 0E, or 20 by Unicode high byte, and writes one byte for exact nonzero mappings. `char2uni()` maps one input byte and rejects zero. Loading registers the table under the main charset and alias; unloading unregisters it.

State and persistence behavior: The code uses immutable static mapping arrays and no dynamic state. Persistence is limited to the transient NLS registry entry while the module is loaded.

Dependencies and integration points: Uses Linux module, NLS, and errno APIs. Filesystems can request either `cp874` or `tis-620` and receive the same callbacks. Thai has no uppercase/lowercase distinction, so the case tables primarily preserve bytes and ASCII behavior rather than language-specific folding.

Risks: CP874 has many intentionally unmapped bytes in the 0x80-0x9f and trailing ranges; treating those as valid would change error behavior. The `tis-620` alias is part of the integration contract and should not be dropped. Thai normalization, combining-mark ordering, and rendering are outside this byte conversion module.

Test signals: Verify both `cp874` and `tis-620` lookup/module alias behavior, round-trip Thai characters in Unicode page 0E, and check special page 20 punctuation such as the ellipsis entry. Negative tests should cover unmapped byte holes, unsupported Unicode, and zero output length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nls/nls_cp874.c -->
