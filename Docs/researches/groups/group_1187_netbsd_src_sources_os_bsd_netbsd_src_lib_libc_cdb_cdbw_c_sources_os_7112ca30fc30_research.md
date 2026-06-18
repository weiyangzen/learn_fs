# Group Research: group_1187_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_cdb_cdbw_c_sources_os_7112ca30fc30

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Every listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/cdb/cdbw.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/cdb/cdbw.c

Build-side writer for NetBSD constant database files. It stores copied key/data pairs, rejects duplicate keys, and emits an `NBCDB` file containing a minimal perfect hash table plus concatenated data.

Key behavior:
- `cdbw_open`, `cdbw_close` manage the writer state, key hash chains, and data arrays.
- `cdbw_put_data` appends copied data blobs and caps total data and counts to 32-bit output limits.
- `cdbw_put_key` hashes keys with `mi_vector_hash`, detects exact duplicates by three hash values plus byte comparison, and grows an internal power-of-two hash table.
- `cdbw_output` builds a 3-uniform hypergraph, repeatedly seeds and peels it until acyclic, assigns `g[]` values, then serializes the database.
- `cdbw_stable_seeder` plus the nbtool fallback division helpers make deterministic host-tool output possible.

Notable details:
- The graph algorithm stores vertex degree and XOR of incident edge ids instead of full incidence lists.
- The generated hash maps a key through three vertices and uses the assigned `g[]` values modulo the data-entry count to recover the data index.
- Output uses little-endian fields and compact 1/2/4-byte tables depending on size.
- Write calls treat short writes as failure rather than retrying.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/cdb/cdbw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/Makefile.inc

Libc build fragment for the Citrus internationalization subsystem.

Key behavior:
- Adds the Citrus source directory to `.PATH`.
- Reads the i18n module shared-library major version and defines `I18NMODULE_MAJOR` for `citrus_module.c`.
- Adds core Citrus sources, locale-category loaders, converter/mapper/database helpers, and ctype support to libc.
- Adds include paths for shared `_strtol.h`/`_strtoul.h` templates and locale internals.
- Suppresses format-truncation warnings for `citrus_iconv.c` and `citrus_csmapper.c`, both of which assemble bounded path/key strings.

This file defines the compilation surface for the non-module Citrus runtime embedded in libc.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_aliasname_local.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_aliasname_local.h

Small internal helper header for locale/encoding alias handling.

Key behavior:
- `__unaliasname(dbname, alias, buf, bufsize)` performs a case-sensitive `_lookup_simple` query.
- `__isforcemapping(name)` checks whether a name equals `/force` case-insensitively through `_bcs_strcasecmp`.

Dependencies:
- Expects Citrus lookup aliases and BCS string comparison macros from surrounding includes.
- Used by locale category loaders that need alias resolution without exposing public API.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_aliasname_local.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_bcs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_bcs.c

Implements basic character set string helpers used throughout Citrus parsing.

Key behavior:
- Case-insensitive string compare and bounded compare using `_bcs_toupper`.
- Whitespace and non-whitespace skipping, with both unbounded and length-tracked variants.
- Truncates trailing whitespace in a bounded buffer.
- Destructively lowercases or uppercases C strings using BCS conversions.

These routines intentionally avoid locale-sensitive `ctype(3)` behavior so parser behavior is stable while loading locale data.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_bcs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_bcs.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_bcs.h

Declares and defines inline predicates/conversions for the POSIX-like basic character set.

Key behavior:
- Inline predicates for blank, EOL, space, digit, upper, lower, alpha, alnum, and xdigit.
- Inline uppercase/lowercase transforms that do not accept EOF.
- Declarations for BCS string comparison, whitespace scanners, case conversion, and BCS-only `strtol`/`strtoul`.

Notable detail:
- The header explicitly distinguishes these helpers from `ctype.h`: they operate on `uint8_t` characters and are not locale-dependent.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_bcs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_bcs_strtol.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_bcs_strtol.c

Instantiates NetBSD's shared `_strtol.h` template for BCS-only signed long parsing.

Key behavior:
- Defines `BCS_ONLY`, `_FUNCNAME` as `_bcs_strtol`, and integer bounds as `LONG_MIN`/`LONG_MAX`.
- Overrides `isspace`, `isdigit`, `isalpha`, and `isupper` to use Citrus BCS predicates.
- Includes `_strtol.h` from the common libc stdlib code.

Purpose:
- Provides locale-independent numeric parsing for Citrus config, DB text, and module version parsing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_bcs_strtol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_bcs_strtoul.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_bcs_strtoul.c

Instantiates NetBSD's shared `_strtoul.h` template for BCS-only unsigned long parsing.

Key behavior:
- Defines `BCS_ONLY`, `_FUNCNAME` as `_bcs_strtoul`, and max value as `ULONG_MAX`.
- Redirects character classification macros to BCS predicates.
- Supports nbtool configuration includes.

Purpose:
- Used where Citrus parses unsigned fields from portable text formats, such as pivot costs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_bcs_strtoul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_csmapper.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_csmapper.c

High-level character-set mapper resolver. It opens direct charset mappers or builds pivoted mapper chains.

Key behavior:
- Maintains a global `_citrus_mapper_area` for `_PATH_CSMAPPER`.
- Resolves source and destination charset aliases through `charset.alias`.
- Returns a persistent `mapper_none` instance when source and destination resolve to the same charset.
- Attempts direct mapper lookup by `src/dst`.
- If direct lookup fails and pivoting is allowed, finds the lowest-cost pivot using compiled `charset.pivot.pvdb` or text `charset.pivot`.
- Opens pivot chains via `mapper_serial` with `src/pivot,pivot/dst`.

Dependencies:
- Uses Citrus lookup, DB, mapper, mmap, BCS, endian helpers, and process-wide rwlock protection for the singleton none mapper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_csmapper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_csmapper.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_csmapper.h

Thin public/internal wrapper that aliases charset mapper operations to generic mapper operations.

Key behavior:
- Defines `_citrus_csmapper` as `_citrus_mapper`.
- Maps close, convert, state init, and trait accessors directly to `_citrus_mapper_*`.
- Declares `_citrus_csmapper_open`.
- Defines `_CITRUS_CSMAPPER_F_PREVENT_PIVOT` to disable pivot-chain fallback.

This header keeps charset-specific naming while reusing the generic mapper ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_csmapper.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype.c

Runtime loader and dispatcher setup for Citrus ctype encoding modules.

Key behavior:
- Defines `_citrus_ctype_default` using the built-in default `NONE` ctype ops.
- In dynamic builds, `_citrus_ctype_open` loads an i18n module unless the encoding is default.
- `_initctypemodule` resolves the module's ctype getops symbol, copies ops, patches missing ABI v1/v2 functions with fallback shims, validates required methods, and initializes module closure.
- `_citrus_ctype_close` uninitializes and unloads non-default modules.
- In non-dynamic builds, only the default ctype is accepted.

Important contract:
- The file enforces `_CITRUS_CTYPE_ABI_VERSION` compatibility and shields older modules with fallback implementations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype.h

Inline API wrapper around a `_citrus_ctype_rec` dispatch table.

Key behavior:
- Declares open/close and the external `_citrus_ctype_default`.
- Provides inline wrappers for multibyte and wide-character operations: `mblen`, `mbrlen`, `mbrtowc`, `mbsrtowcs`, `mbsnrtowcs`, `mbstowcs`, `mbtowc`, `wcrtomb`, `wcsrtombs`, `wcsnrtombs`, `wcstombs`, `wctomb`, `btowc`, and `wctob`.
- Asserts required ops before dispatch.

Notable detail:
- `mbsnrtowcs` and `wcsnrtombs` pass the ctype record itself, not only closure, matching the v3 ABI/fallback shape.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype_fallback.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype_fallback.c

Compatibility implementations for newer ctype ABI operations when older modules lack them.

Key behavior:
- `btowc` fallback converts one byte through `mbrtowc` with a fresh private state.
- `wctob` fallback converts a wide char through `wcrtomb` and succeeds only if exactly one byte is produced.
- `mbsnrtowcs` fallback loops over a bounded byte input using `mbrtowc`.
- `wcsnrtombs` fallback loops over bounded wide input using `wcrtomb`, preserving state if the output buffer is too small.

Notable details:
- Uses stack storage sized as `mbstate_t` for private state.
- Returns standard restartable conversion result counts and `(size_t)-1` on conversion error.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype_fallback.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype_fallback.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype_fallback.h

Declares fallback ctype functions used to bridge older module ABI versions.

Key behavior:
- Declares ABI v2 fallbacks: `_citrus_ctype_btowc_fallback`, `_citrus_ctype_wctob_fallback`.
- Declares ABI v3 fallbacks: `_citrus_ctype_mbsnrtowcs_fallback`, `_citrus_ctype_wcsnrtombs_fallback`.

This header is included by ctype local definitions and the dynamic module initialization logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype_fallback.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype_local.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype_local.h

Internal ABI definition for Citrus ctype modules.

Key behavior:
- Defines getops naming macros, module declaration macros, and ops-table construction macro.
- Declares all function pointer typedefs for ctype operations.
- Defines `_CITRUS_CTYPE_ABI_VERSION` as `0x00000003`.
- Documents ABI evolution: v2 added `btowc`/`wctob`; v3 added `mbsnrtowcs`/`wcsnrtombs`.
- Defines `_citrus_ctype_ops_rec` and `_citrus_ctype_rec`.
- Sets default ctype name/header/ops to `NONE` / `citrus_none.h`.

Purpose:
- This is the contract every Citrus ctype module must implement or be adapted to by fallbacks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype_local.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype_template.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype_template.h

Reusable template implementation for encoding-specific ctype modules.

Key behavior:
- Requires caller-defined macros for function naming, encoding info/state types, state packing/unpacking, state dependency, and encoding-specific private conversion routines.
- Implements common `mbtowc`, `mbrtowc`, `mbsrtowcs`, `mbsnrtowcs`, `mbstowcs`, `wcrtomb`, `wcsrtombs`, `wcsnrtombs`, `wcstombs`, `wctomb`, `btowc`, and `wctob` behavior.
- Handles restartable state through `_RESTART_BEGIN`/`_RESTART_END`, using either caller-provided private state or method-specific internal state.
- Supports state-dependent encodings with reset-sequence emission before null conversions.
- Provides `ctype_getops`, `ctype_init`, and `ctype_uninit` template implementations.
- Verifies `_ENCODING_STATE` alignment is compatible with locale multibyte state storage.

Notable details:
- Conversion loops preserve source pointers until success rules require publishing them.
- Stateful output conversion restores state if an output buffer cannot fit the next multibyte sequence.
- Some legacy comments note limitations, such as `ctype_mbsinit` checking `state.chlen == 0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype_template.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db.c

Reader for Citrus compiled key/value database files.

Key behavior:
- `_citrus_db_open` validates magic, header, entry offset, and entry-directory bounds over a mapped region.
- `_citrus_db_lookup` hashes a key, walks collision chains, verifies key length and bytes, and returns a region for matching data.
- Locator support allows repeated lookup of duplicate/colliding entries.
- String and 8/16/32-bit typed lookup helpers validate data size and decode big-endian integer values.
- `_citrus_db_get_number_of_entries` and `_citrus_db_get_entry` provide sequential access.

Format:
- Uses `_citrus_db_file.h` big-endian on-disk header/entry records.
- Data/key regions are borrowed from the mapped database; caller must keep the underlying mapping alive.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db.h

Public internal interface for Citrus compiled DB readers.

Key behavior:
- Forward-declares `_citrus_db`.
- Defines `_citrus_db_locator` with saved hash value and next offset.
- Declares open, close, raw lookup, string lookup, typed lookup, entry count, and indexed entry retrieval.
- Provides `_citrus_db_locator_init`.

This header is consumed by lookup, ESDB, pivot, and locale category loaders.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_factory.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_factory.c

Builder/serializer for Citrus compiled database files.

Key behavior:
- `_citrus_db_factory_create/free` manage a queue of entries and aggregate key/data sizes.
- Add helpers accept raw regions, strings, and 8/16/32-bit integer values encoded in network byte order.
- `_citrus_db_factory_calc_size` computes a 16-byte-aligned serialized size.
- `_citrus_db_factory_serialize` builds a fixed-size hash directory, resolves collisions with linked entry chains, writes header/entry records, and copies key/data tables.

Format details:
- Header stores magic, entry count, and entry offset.
- Entry records store hash value, next offset, key offset/size, and data offset/size.
- Data records are padded to 16-byte alignment.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_factory.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_factory.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_factory.h

Interface for constructing serialized Citrus DB regions.

Key behavior:
- Declares opaque `_citrus_db_factory`.
- Defines `_citrus_db_hash_func_t`.
- Declares create/free, add raw/string/typed entries, size calculation, and serialization.

This is used by tools that compile text lookup data into DB form.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_factory.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_file.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_file.h

On-disk structure definitions for Citrus compiled DB files.

Key contents:
- Documents layout: header, entry directory, key table, data table.
- Defines `_CITRUS_DB_MAGIC_SIZE`, `_CITRUS_DB_HEADER_SIZE`, and packed header record.
- Defines packed entry record with hash, next offset, key offset/size, and data offset/size.
- Defines `_CITRUS_DB_ENTRY_SIZE` as 24.

All multi-byte fields are interpreted by reader/writer code as big-endian/network order.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_hash.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_hash.c

Standard Citrus DB hash function.

Key behavior:
- `_citrus_db_hash_std` iterates a region byte by byte.
- Lowercases bytes through BCS before hashing, making hash values case-insensitive for basic letters.
- Uses a classic nibble-shift hash with high-nibble folding.

The hash is shared by DB builders and readers, so serialized DB lookup depends on this exact function.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_hash.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_hash.h

Declares the standard Citrus DB hash function.

Key behavior:
- Exposes `_citrus_db_hash_std(void *, struct _citrus_region *)`.

Used by compiled lookup DBs, ESDB files, pivot DBs, and locale category DBs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_hash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_esdb.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_esdb.c

Encoding Scheme Database loader.

Key behavior:
- `_citrus_esdb_alias` resolves encoding aliases through `_PATH_ESDB/esdb.alias`.
- `_citrus_esdb_open` resolves aliases, finds an ESDB filename through `esdb.dir`, maps it, and converts the DB into `_citrus_esdb`.
- `conv_esdb` validates magic/version, reads encoding name, optional variable string, charset count, optional invalid character, and per-charset csid/name pairs.
- `_citrus_esdb_close` frees allocated strings and charset arrays.
- `_citrus_esdb_get_list` merges alias and directory entries, lowercases names, removes duplicates, and returns a dynamically allocated list.

Dependencies:
- Uses Citrus lookup for alias/dir text or compiled lookup DBs and Citrus DB for actual ESDB content.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_esdb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_esdb.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_esdb.h

Data structures and API for loaded Encoding Scheme Database records.

Key contents:
- `_citrus_esdb_charset` holds a charset id and charset name.
- `_citrus_esdb` holds encoding name, optional variable payload, charset count/list, and optional invalid wide character.
- Declares alias, open, close, list-free, and list-enumeration functions.

Used by encoding/conversion setup code to map names to module/charset metadata.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_esdb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_esdb_file.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_esdb_file.h

Symbol definitions for ESDB compiled database files.

Key contents:
- Magic: `ESDB\0\0\0\0`.
- Symbol names for version, encoding, variable, number of charsets, invalid character, charset name prefix, and charset id prefix.
- Current version constant `0x00000001`.

These constants must match ESDB compiler output and `citrus_esdb.c` lookup keys.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_esdb_file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_fix_grouping.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_fix_grouping.h

Compatibility helper for locale grouping strings.

Key behavior:
- Defines portable locale grouping value range: 0..126 and no-further-grouping value 127.
- If platform `CHAR_MAX` differs from 127, `_citrus_fixup_char_max_md` rewrites byte value 127 in grouping strings to `CHAR_MAX`.
- If `CHAR_MAX` already equals 127, the fixup macro is a no-op.

Used by numeric and monetary locale loaders after reading compiled grouping strings.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_fix_grouping.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_hash.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_hash.c

String hash adapter for Citrus in-memory hash tables.

Key behavior:
- `_citrus_string_hash_func` wraps a C string in a `_region`.
- Uses `_db_hash_std` and reduces modulo caller-provided hash size.

Used by mapper and iconv caches so in-memory cache keys share the same case-folded basic-character hash family.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_hash.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_hash.h

Macro wrapper around BSD `LIST` hash tables plus a string hash declaration.

Key behavior:
- Defines macros for entry fields, fixed-size hash-head structs, init, remove, insert, and linear bucket search.
- Declares `_citrus_string_hash_func`.

Used by Citrus mapper/iconv shared-object caches.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_hash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_iconv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_iconv.c

Runtime loader and cache for Citrus iconv conversion modules.

Key behavior:
- Initializes a process-wide shared converter cache and unused LRU-like tail queue.
- `ICONV_MAX_REUSE` controls the maximum number of unused shared converters, unless running setugid.
- Resolves source/destination aliases through `iconv.alias`.
- Rejects resolved names containing `/`.
- Looks up `src/dst` in `iconv.dir`, falling back to `*`.
- Loads the converter module, resolves iconv getops, validates ABI v2, and initializes shared converter state.
- `_citrus_iconv_open` creates a per-use context from shared state.
- `_citrus_iconv_close` uninitializes context and returns shared state to the cache or evicts it.

Concurrency:
- Uses a libc rwlock around cache initialization, lookup, reference counts, and eviction.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_iconv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_iconv.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_iconv.h

Public internal wrapper for Citrus iconv handles.

Key behavior:
- Declares `_citrus_iconv_open` and `_citrus_iconv_close`.
- Includes local ABI definitions.
- Defines `_CITRUS_ICONV_F_HIDE_INVALID`.
- Provides inline `_citrus_iconv_convert` dispatch to the module's `io_convert`.

The actual conversion implementation is module-provided; this header supplies the stable call surface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_iconv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_iconv_local.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_iconv_local.h

Internal ABI for Citrus iconv modules.

Key contents:
- Defines getops naming/declaration macros and ops-table construction macro.
- Declares function pointer typedefs for shared init/uninit, context init/uninit, and conversion.
- Defines `_citrus_iconv_ops` with ABI version, shared/context lifecycle, and conversion function.
- Sets `_CITRUS_ICONV_ABI_VERSION` to 2.
- Defines `_citrus_iconv_shared`, including cache linkage, module handle, use count, closure, and conversion name.
- Defines per-open `_citrus_iconv` context with shared pointer and closure.

This is the binary contract consumed by dynamically loaded iconv modules.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_iconv_local.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_ctype.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_ctype.c

Locale loader for `LC_CTYPE`.

Key behavior:
- Builds path `<root>/<name>/LC_CTYPE`.
- Maps the locale file and passes it to `_rune_load`.
- On successful load, updates global libc ctype/multibyte pointers:
  - `__mb_cur_max`
  - `_ctype_tab_`
  - `_tolower_tab_`
  - `_toupper_tab_`
  - legacy `_ctype_` when enabled
- Uses NetBSD `nb_lc_template_decl.h` and `nb_lc_template.h` for locale category lifecycle boilerplate.

Unlike other locale categories in this group, `LC_CTYPE` is loaded through runetype data rather than the generic Citrus DB/fallback template.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_ctype.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_messages.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_messages.c

Locale loader for `LC_MESSAGES`.

Key behavior:
- Defines the category prefix and uses the generic Citrus locale template.
- `_citrus_LC_MESSAGES_uninit` frees yes/no expressions and strings.
- Normal DB initialization reads `yesexpr`, `noexpr`, `yesstr`, and `nostr` string values from a Citrus DB.
- Fallback initialization reads the same values line-by-line from a plain memory stream.
- Category DB path is `LC_MESSAGES/SYS_LC_MESSAGES`; magic is `CtrsME10`.

Error handling:
- Any missing/malformed field releases already allocated strings and returns `EFTYPE`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_messages.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_messages.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_messages.h

Constants for `LC_MESSAGES` compiled locale data.

Key contents:
- Magic `CtrsME10`.
- Version symbol and version value `0x00000001`.
- Field symbols: `yesexpr`, `noexpr`, `yesstr`, `nostr`.

Consumed by `citrus_lc_messages.c` and locale-generation tools.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_messages.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_monetary.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_monetary.c

Locale loader for `LC_MONETARY`.

Key behavior:
- Defines string fields for currency symbols, decimal/thousands separators, grouping, and signs.
- Defines char fields for fractional digits, symbol placement, spacing, and sign positions.
- Normal DB initialization reads string fields and 8-bit integer fields from Citrus DB.
- Fallback initialization reads line-oriented text, parses numeric char fields via `_bcs_strtol`, and validates range 0..127.
- Applies grouping fixups via `_CITRUS_FIXUP_CHAR_MAX_MD` or `__fix_locale_grouping_str`.
- Frees all allocated string fields on uninit or failure.
- Category DB path is `LC_MONETARY`; magic is `CtrsMO10`.

This loader populates NetBSD's `_MonetaryLocale`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_monetary.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_monetary.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_monetary.h

Constants for `LC_MONETARY` compiled locale data.

Key contents:
- Magic `CtrsMO10`.
- Version symbol/value.
- Symbol names for all monetary strings and numeric char fields, including international variants.

These names are matched exactly by the monetary loader's key tables.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_monetary.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_numeric.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_numeric.c

Locale loader for `LC_NUMERIC`.

Key behavior:
- Loads `decimal_point`, `thousands_sep`, and `grouping`.
- Normal path reads strings from a Citrus DB.
- Fallback path reads three lines from a memory stream.
- Applies grouping conversion through `_CITRUS_FIXUP_CHAR_MAX_MD` or `__fix_locale_grouping_str`.
- Frees all allocated fields on uninit/failure.
- Category DB path is `LC_NUMERIC`; magic is `CtrsNU10`.

This loader populates NetBSD's `_NumericLocale`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_numeric.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_numeric.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_numeric.h

Constants for `LC_NUMERIC` compiled locale data.

Key contents:
- Magic `CtrsNU10`.
- Version symbol/value.
- Field symbols: `decimal_point`, `thousands_sep`, `grouping`.

Used by `citrus_lc_numeric.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_numeric.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_template.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_template.h

Generic Citrus locale category creation template.

Key behavior:
- Builds path `<root>/<name>/_CATEGORY_DB`.
- Maps the category file.
- Allocates category data storage.
- Attempts to open the mapped file as a Citrus DB with `_CATEGORY_MAGIC`.
- If DB open succeeds, calls `_PREFIX(init_normal)`.
- If DB open fails, binds a memory stream and calls `_PREFIX(init_fallback)`.
- Includes NetBSD `nb_lc_template.h` for the rest of category lifecycle logic.

Used by messages, monetary, numeric, and time loaders.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_template.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_template_decl.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_template_decl.h

Declaration companion for the generic Citrus locale template.

Key behavior:
- Includes `nb_lc_template_decl.h`.
- Declares category-specific `_PREFIX(init_normal)` and `_PREFIX(init_fallback)` inline functions expected by `citrus_lc_template.h`.

This header defines the required hooks each locale category implementation must provide.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_template_decl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_time.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_time.c

Locale loader for `LC_TIME`.

Key behavior:
- Defines a large key table for abbreviated/full weekday names, abbreviated/full month names, AM/PM strings, and date/time format strings.
- Normal DB initialization reads each string by symbol from Citrus DB and duplicates it into `_TimeLocale`.
- Fallback initialization reads values line-by-line in the same key order.
- Uninit frees every allocated string slot.
- Category DB path is `LC_TIME`; magic is `CtrsTI10`.

This loader is data-table driven and relies on `nb_lc_time_misc.h` index macros for field placement.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_time.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_time.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_time.h

Constants for `LC_TIME` compiled locale data.

Key contents:
- Magic `CtrsTI10`.
- Version symbol/value.
- Field symbols for weekdays, months, AM/PM, date/time formats, and AM/PM time format.

Used by `citrus_lc_time.c` and locale build tools.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_time.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lookup.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lookup.c

Unified sequential and keyed lookup interface over compiled `.db` files or plain text files.

Key behavior:
- `_citrus_lookup_seq_open` first tries `<name>.db`; if absent, falls back to plain `<name>`.
- DB mode maps the compiled lookup DB, opens it with magic `LOOKUP\0\0`, supports indexed iteration and locator-based repeated keyed lookup.
- Plain mode maps text, ignores comments beginning with `#`, trims whitespace, parses first token as key, and returns the rest as data.
- Supports optional case-insensitive keys by lowercasing stored search keys.
- `_citrus_lookup_simple` opens, performs one lookup, copies data into caller buffer, and closes.

Used heavily for alias files, `iconv.dir`, `mapper.dir`, ESDB directory files, and pivot data.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lookup.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lookup.h

Interface for Citrus lookup files.

Key behavior:
- Defines case-sensitive and case-ignore flags.
- Declares simple lookup, sequence open/rewind/next/keyed lookup/count/close.
- Provides `_citrus_lookup_alias`, which returns the original key if lookup fails.

This header abstracts text-vs-compiled lookup storage for callers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lookup.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lookup_factory.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lookup_factory.c

Converter from plain lookup text to compiled Citrus lookup DB.

Key behavior:
- Reads input lines with `fgetln`.
- Strips comments and whitespace.
- Extracts the first token as key, lowercases it, and stores the rest of the line as data.
- Uses `_citrus_db_factory` with `_db_hash_std`.
- Serializes with lookup magic `LOOKUP\0\0` and writes the region to output.

Purpose:
- Build-time support for faster runtime lookup files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lookup_factory.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lookup_factory.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lookup_factory.h

Declaration for lookup-file compilation.

Key behavior:
- Declares `_citrus_lookup_factory_convert(FILE *out, FILE *in)`.

This is a small build/tool interface over `citrus_lookup_factory.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lookup_factory.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lookup_file.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lookup_file.h

File-format constant for compiled Citrus lookup DBs.

Key contents:
- Defines `_CITRUS_LOOKUP_MAGIC` as `LOOKUP\0\0`.

Used by lookup reader and factory serialization.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lookup_file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mapper.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mapper.c

Generic runtime loader/cache for Citrus mapper modules.

Key behavior:
- `_citrus_mapper_create_area` validates a mapper area by checking for `mapper.dir`, stores base directory, and initializes a fixed hash cache.
- `lookup_mapper_entry` maps `mapper.dir`, finds a mapper line, and splits it into module and variable arguments.
- `mapper_open` loads a module, resolves mapper getops, validates required ABI methods, allocates traits, and calls module init.
- `_citrus_mapper_open` caches mappers by map name with reference counts.
- `_citrus_mapper_open_direct` bypasses `mapper.dir`.
- `_citrus_mapper_close` decrements reference counts, removes cached entries at zero, and unloads modules.
- `_citrus_mapper_set_persistent` marks a mapper as never freed.

Concurrency:
- Uses a process-wide rwlock around area creation and cache/refcount mutation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mapper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mapper.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mapper.h

Public internal interface and inline dispatchers for Citrus mappers.

Key behavior:
- Declares mapper area creation, open, direct open, close, and persistent marking.
- Defines conversion result constants for success, non-identical mapping, source-more, destination-more, illegal sequence, and fatal errors.
- Provides inline wrappers for convert, init state, state size, source max, and destination max.
- Includes `citrus_mapper_local.h` for structure definitions.

This is the generic mapping API used by charset mapping and serial mapper composition.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mapper.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mapper_local.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mapper_local.h

Internal ABI definition for Citrus mapper modules.

Key contents:
- Getops naming/declaration macros and ops-table macro.
- Function pointer typedefs for init, uninit, convert, and state init.
- ABI version `0x00000001`.
- `_citrus_mapper_ops` with method pointers.
- `_citrus_mapper_traits` with state size and M:N source/destination suspension limits.
- `_citrus_mapper` runtime object with ops, closure, module handle, traits, cache link, refcount, and key.

This file defines the binary/plugin boundary for mapper modules.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mapper_local.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_memstream.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_memstream.c

Memory-backed stream helpers for parsing mapped files and regions.

Key behavior:
- `_citrus_memory_stream_getln` returns the next line region and advances position.
- `_citrus_memory_stream_matchline` scans for a key at the start of parsed non-comment lines and returns the data portion.
- `_citrus_memory_stream_chr` returns the region up to a delimiter and advances past it.
- `_citrus_memory_stream_skip_ws` consumes BCS whitespace.

Parsing rules:
- Comment delimiter is `#`.
- Matching trims trailing whitespace/newlines, skips leading whitespace, and compares first token case-sensitively or insensitively.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_memstream.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_memstream.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_memstream.h

Inline API and struct definition for Citrus memory streams.

Key behavior:
- Defines `_citrus_memory_stream` with a region and current offset.
- Declares line/match/chr/skip helpers.
- Provides inline bind, bind pointer, rewind, tell, remainder, seek, getc, ungetc, peek, getregion, typed get8/get16/get32, and get-line-as-region helpers.

Notable detail:
- `_citrus_memory_stream_get8` checks for one byte but advances `ms_pos` by 2. This is unusual and may be a latent typo unless callers rely on 2-byte stepping; the surrounding get16/get32 advance by their natural sizes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_memstream.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mmap.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mmap.c

File mapping helper for Citrus data files.

Key behavior:
- `_citrus_map_file` opens a path read-only with `O_CLOEXEC`, verifies it is a regular file, maps it private/read-only, and initializes a region over the mapping.
- On failure, returns `errno` or `EOPNOTSUPP` and closes the fd.
- `_citrus_unmap_file` unmaps and clears a non-null mapped region.

Used throughout Citrus for locale files, lookup files, DBs, ESDBs, mapper/iconv metadata, and pivot data.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mmap.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mmap.h

Declaration header for Citrus file mapping helpers.

Key behavior:
- Declares `_citrus_map_file` and `_citrus_unmap_file`.

The region type is supplied by `citrus_region.h` through including code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_mmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_module.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_module.c

Dynamic i18n module loader for Citrus.

Key behavior:
- When `_I18N_DYNAMIC` is enabled, locates shared libraries named `lib<encname>.so.<major>[.<minor>]` in the i18n module directory.
- Determines search directory from `PATH_I18NMODULE` unless setugid, otherwise uses `_PATH_I18NMODULE`, with optional `MLIBDIR` rewriting.
- Parses and compares Dewey-style shared-library version suffixes.
- `_citrus_load_module` finds a compatible module with `I18NMODULE_MAJOR` and opens it with `dlopen`.
- `_citrus_find_getops` builds the symbol name `_citrus_<modname>_<ifname>_getops` and resolves it with `dlsym`.
- `_citrus_unload_module` calls `dlclose`.
- In non-dynamic builds, loading and getops lookup return failure/no-op.

Security/compatibility:
- Ignores environment override in setugid programs.
- Has a special m68k stack protector optimization attribute workaround.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_module.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_module.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_module.h

Interface for Citrus dynamic module handling.

Key behavior:
- Defines opaque `_citrus_module_t`.
- Declares `_citrus_find_getops`, `_citrus_load_module`, and `_citrus_unload_module`.

Used by ctype, mapper, and iconv runtime loaders.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_module.h -->