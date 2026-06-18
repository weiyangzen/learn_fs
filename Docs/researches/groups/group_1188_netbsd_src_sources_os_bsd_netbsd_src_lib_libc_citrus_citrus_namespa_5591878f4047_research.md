# Group Research: group_1188_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_citrus_citrus_namespa_5591878f4047

Scope checked against `Docs/research_subset_a.md`; all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Every source file listed for this group was read completely and summarized separately below.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_namespace.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_namespace.h

Read completely: 238 lines.

This header is the Citrus libc namespace indirection layer. It maps short internal symbols such as `_mapper_open`, `_stdenc_mbtowc`, `_region_peek32`, and `_index_t` onto exported/private `_citrus_*` names unless a component-specific `_CITRUS_*_NO_NAMESPACE` macro disables that remapping.

The file covers alias lookup, BCS helpers, csmapper, database and database factory APIs, lookup/esdb/hash helpers, mapper APIs and result constants, memstream/mmap helpers, pivot factory conversion, region helpers, standard encoding APIs and state constants, and basic Citrus integer types. It has no executable logic, but it determines the symbol names seen by all modules that include it.

Important interactions: most files in this group include it before using shorthand helpers. If a module defines a `_NO_NAMESPACE` macro inconsistently, it can silently change which symbol names are referenced at compile time.

Security/reliability notes: no direct runtime attack surface. Its main risk is ABI/symbol confusion, especially because it remaps both function-like names and type/constant names.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_namespace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_none.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_none.c

Read completely: 590 lines.

This implements the built-in `NONE` ctype and stdenc modules, effectively a byte-preserving single-byte encoding. The ctype half implements `mblen`, `mbrlen`, `mbrtowc`, `mbsrtowcs`, `mbsnrtowcs`, `mbtowc`, `wcrtomb`, `wcsrtombs`, `wcsnrtombs`, `wcstombs`, `wctomb`, `btowc`, and `wctob`. The stdenc half exposes the same behavior through Citrus standard-encoding callbacks.

Key behavior: `MB_CUR_MAX` is 1, states are always initial/stateless, bytes map to wide characters via `(unsigned char)`, and wide characters are only encodable if they fit in 8 bits. Invalid wide characters return `EILSEQ`; too-small output buffers in stdenc return `E2BIG`; incomplete input returns the conventional `(size_t)-2` for restartable interfaces.

Important interactions: `_citrus_stdenc_default` in `citrus_stdenc.c` uses `_citrus_NONE_stdenc_ops` and `_citrus_NONE_stdenc_traits`. The header `citrus_none.h` exports those operation tables.

Security/reliability notes: this is a low-complexity fallback encoding. The conversion functions consistently guard 8-bit bounds before writing. The logic relies on callers providing valid result pointers, as enforced only by convention or `_DIAGASSERT` in some paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_none.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_none.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_none.h

Read completely: 36 lines.

This header declares the `NONE` module operation tables: `_citrus_NONE_ctype_ops`, `_citrus_NONE_stdenc_ops`, and `_citrus_NONE_stdenc_traits`.

It is consumed by the standard encoding loader for the built-in default encoding and by `citrus_none.c` users that need the static operation descriptors. It contains only declarations and an include guard.

Security/reliability notes: no direct runtime behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_none.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_pivot_factory.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_pivot_factory.c

Read completely: 231 lines.

This file compiles text pivot mapping data into the Citrus pivot DB format. It parses input lines of the form `source target value`, strips comments beginning with `#`, groups rows by source encoding name, stores target/value mappings in per-source database factories, then serializes a top-level `_CITRUS_PIVOT_MAGIC` DB containing per-source `_CITRUS_PIVOT_SUB_MAGIC` sub-DBs.

Key functions: `find_src` creates or finds a source entry and DB factory; `convert_line` tokenizes and validates one line; `dump_db` serializes nested DB regions; `_citrus_pivot_factory_convert` streams all input lines, builds the DB, and writes the serialized region.

Important interactions: uses `_citrus_db_factory`, `_citrus_region`, BCS token helpers, and magic strings from `citrus_pivot_file.h`. This is a build/tooling-side converter rather than an iconv runtime mapper.

Security/reliability notes: parsing is bounded by `LINE_MAX` stack buffers and `snprintf`. Numeric parsing rejects trailing nonnumeric data. `dump_db` allocates serialized subregions and transfers ownership into the DB factory; it frees only the most recent temporary pointer on failure, so review of `_db_factory_add_by_s` ownership semantics is important when changing this path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_pivot_factory.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_pivot_factory.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_pivot_factory.h

Read completely: 36 lines.

This header declares `_citrus_pivot_factory_convert(FILE *, FILE *)`, the converter entry point implemented by `citrus_pivot_factory.c`.

It wraps the prototype in `__BEGIN_DECLS`/`__END_DECLS` for C++ compatibility and has no other logic.

Security/reliability notes: no direct runtime behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_pivot_factory.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_pivot_file.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_pivot_file.h

Read completely: 35 lines.

This header defines the serialized pivot database magic strings: `_CITRUS_PIVOT_MAGIC` as `CSPIVOT\0` and `_CITRUS_PIVOT_SUB_MAGIC` as `CSPIVSUB`.

It is shared between pivot DB writers and readers so the nested DB layers can validate file type.

Security/reliability notes: no executable code. Correct magic validation in consumers depends on these constants remaining synchronized with generated DB files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_pivot_file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_prop.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_prop.c

Read completely: 467 lines.

This implements the Citrus module property-string parser. It parses named properties according to a caller-provided hint table, supports booleans, strings, characters, and unsigned numeric ranges, and invokes type-specific callbacks for parsed values.

Key pieces: `_citrus_prop_object_t` stores the temporary value; generated integer readers handle decimal/octal/hex with cutoff checks; `_citrus_prop_read_character_common` supports C-style escapes; `_citrus_prop_read_str` supports quoted and unquoted strings; `_citrus_prop_parse_element` matches a symbol against hints and handles comma-separated value/range lists; `_citrus_prop_parse_variable` drives the whole stream.

Important interactions: BIG5 and HZ use this parser for runtime encoding variables; additional Citrus modules can define their own hint tables. It depends on `_memstream` and BCS classification rather than libc locale-sensitive parsing.

Security/reliability notes: numeric readers avoid accumulator overflow by cutoff/cutlim checks. String allocation grows in fixed chunks. The parser rejects unknown property names and malformed separators. Since callbacks receive parsed data directly and may allocate nested structures, callback failure paths are important to audit in the module using the parser.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_prop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_prop.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_prop.h

Read completely: 91 lines.

This header defines the property parser public interface. It declares `_citrus_prop_type_t`, callback typedefs for booleans, strings, character ranges, and numeric ranges, the `_citrus_prop_hint_t` table format, helper macros for hint entries, and `_citrus_prop_parse_variable`.

Important interactions: modules build static hint arrays with `_CITRUS_PROP_HINT_*` macros, then pass module-local context to the parser. Numeric and character properties use callbacks that receive a start and end value, allowing compact range syntax.

Security/reliability notes: no runtime code here, but the callback signatures define ownership and trust boundaries: string callback arguments are temporary parser-owned strings and must not be retained without copying unless the implementation guarantees lifetime.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_prop.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_region.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_region.h

Read completely: 108 lines.

This header defines `_citrus_region`, a pointer-plus-size view over a memory buffer, and inline helpers to initialize it, get the base pointer and length, bounds-check subranges, compute offsets, peek 8/16/32-bit values, and construct subregions.

Important interactions: mapped DB files, generated DB regions, mapper tables, pivot files, and memstreams all use this region abstraction. Multi-byte peeks copy with `memcpy`, avoiding unaligned-load issues; callers handle byte order explicitly where needed.

Security/reliability notes: `_citrus_region_check` uses `ofs + sz` directly, which can wrap on size_t overflow. Most callers use trusted or previously bounded offsets, but new file-format consumers should prefer an overflow-safe check pattern before deriving subregions from untrusted data.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_region.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_stdenc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_stdenc.c

Read completely: 199 lines.

This file implements opening and closing Citrus standard-encoding modules. It defines `_citrus_stdenc_default` backed by `NONE`, and, when `_I18N_DYNAMIC` is enabled, dynamically loads encoding modules, resolves their `stdenc_getops` entry point, validates the operation table, allocates traits, and calls the module initializer.

Key behavior: opening `"NONE"` returns the singleton default object. Dynamic modules get their own `_citrus_stdenc` with copied ops and traits. Older ABI operation tables are patched by assigning a default `get_state_desc` that returns `EOPNOTSUPP`.

Important interactions: used by `iconv_std` to open source and destination encodings from ESDB records. Includes `citrus_none.h` for the default encoding and `citrus_module.h` for dynamic loading.

Security/reliability notes: the loader validates required callbacks before use and unwinds partially initialized objects through `_citrus_stdenc_close`. Dynamic module loading makes module path/name control security-sensitive outside this file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_stdenc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_stdenc.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_stdenc.h

Read completely: 148 lines.

This is the standard-encoding public/internal API header. It defines generic state-description IDs and states, includes `citrus_stdenc_local.h` for structures and callback types, declares open/close/default symbols, and provides inline wrappers for all core operations.

Key wrappers: `_citrus_stdenc_init_state`, `_citrus_stdenc_mbtocs`, `_citrus_stdenc_cstomb`, `_citrus_stdenc_mbtowc`, `_citrus_stdenc_wctomb`, `_citrus_stdenc_put_state_reset`, state-size and max-byte accessors, and `_citrus_stdenc_get_state_desc`.

Important interactions: encoding modules implement the callback table expected here; iconv modules consume these wrappers. The namespace header aliases shorter `_stdenc_*` names onto these functions.

Security/reliability notes: wrappers rely on `_DIAGASSERT` for null callback validation and then dispatch directly. Release builds depend on prior validation in `_citrus_stdenc_open`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_stdenc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_stdenc_local.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_stdenc_local.h

Read completely: 153 lines.

This header defines the standard-encoding ABI: getops function signatures, declaration/operation-table generation macros, callback typedefs, ABI version `0x00000002`, `_citrus_stdenc_ops`, `_citrus_stdenc_traits`, and `_citrus_stdenc`.

The macros `_CITRUS_STDENC_DECLS` and `_CITRUS_STDENC_DEF_OPS` are used by each encoding module to produce consistent static function prototypes and operation tables. The ABI v2 addition is `eo_get_state_desc`.

Important interactions: `citrus_stdenc_template.h` implements the macro-generated functions for most multibyte modules; `citrus_stdenc.c` validates and stores these ops.

Security/reliability notes: this is an ABI boundary. Incompatible callback signatures or wrong `lenops`/version handling can corrupt calls across dynamically loaded modules. One typedef contains a spelling typo `__reatrict`, but it is in a typedef declaration context and mirrors the source as read.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_stdenc_local.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_stdenc_template.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_stdenc_template.h

Read completely: 206 lines.

This non-standalone template implements the standard-encoding module wrapper functions for concrete encodings. A module defines `_FUNCNAME`, `_ENCODING_INFO`, `_ENCODING_STATE`, `_ENCODING_MB_CUR_MAX`, and state-dependent hooks, then includes this header.

Generated behavior: `stdenc_getops` validates ABI version and ops length, `stdenc_init` allocates encoding info and calls module init, `stdenc_uninit` calls module uninit and frees closure, wrappers dispatch to module-private `mbrtowc_priv`, `wcrtomb_priv`, `stdenc_wctocs`, and `stdenc_cstowc`, and state reset/state description are delegated or defaulted based on module flags.

Important interactions: included by BIG5, DECHanyu, EUC, EUCTW, GBK2K, HZ, ISO2022, and JOHAB after each module defines its private state machine.

Security/reliability notes: this centralizes allocation and ABI-copy behavior. It assumes module-private functions observe the restartable conversion contract and that `nresult` is non-null. Failures in module init free the allocated closure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_stdenc_template.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_types.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_types.h

Read completely: 41 lines.

This header defines Citrus scalar types: `_citrus_wc_t`, `_citrus_index_t`, and `_citrus_csid_t` as `uint32_t`, plus `_CITRUS_CSID_INVALID` as all-ones.

These types are the common representation for wide-character values, mapping indices, and character-set IDs across stdenc, mapper, and iconv modules.

Security/reliability notes: no executable logic. The fixed 32-bit width is central to file-format and ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_big5.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_big5.c

Read completely: 514 lines.

This module implements BIG5 ctype and stdenc support. It keeps a 256-entry cell table marking legal lead rows and trailing columns, plus a sorted list of excluded code ranges parsed from optional module variables.

Key behavior: `row` and `col` numeric property ranges set lead/trail byte classes; `excludes` ranges reject otherwise valid code points. If variable parsing is absent or fails, it falls back to Big5-1984 defaults: rows `0xA1-0xFE`, columns `0x40-0x7E` and `0xA1-0xFE`. `mbrtowc_priv` buffers up to 2 bytes and returns restart/error statuses; `wcrtomb_priv` validates width, row/column, and exclusions before writing.

Important interactions: uses `citrus_prop` for variable parsing and shared ctype/stdenc templates for exported APIs.

Security/reliability notes: excludes are appended in increasing non-overlapping order; invalid ranges return `EINVAL`. Conversion resets partial state on illegal sequences. Fallback-on-parse-failure is compatibility-oriented but means malformed variables do not necessarily fail module initialization.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_big5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_big5.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_big5.h

Read completely: 37 lines.

This header declares BIG5 module getops entry points for ctype and standard encoding via `_CITRUS_CTYPE_GETOPS_FUNC(BIG5)` and `_CITRUS_STDENC_GETOPS_FUNC(BIG5)`.

Security/reliability notes: declaration-only ABI surface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_big5.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_dechanyu.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_dechanyu.c

Read completely: 443 lines.

This module implements DEC Hanyu ctype and stdenc support. It is a mostly tableless 1-, 2-, or 4-byte state machine with a special `HANYUBIT` marker for the Hanyu extension sequence.

Key behavior: bytes `<=0x7F` are single-byte. Lead bytes are `0xA1-0xFE`; trail bytes are `0x21-0x7E` after clearing bit 7. A leading `0xC2 0xCB` sequence marks extended Hanyu data. `mbrtowc_priv` preserves partial input in `_DECHanyuState`; `wcrtomb_priv` emits ASCII, normal two-byte sequences, or four-byte Hanyu sequences. Standard-encoding conversion maps these forms into csid/index planes 0 through 4.

Important interactions: no external tables or variables; exports through ctype/stdenc templates.

Security/reliability notes: state transitions validate each saved byte before continuing. Illegal states return `EINVAL`; malformed sequences return `EILSEQ`; incomplete reads return `(size_t)-2`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_dechanyu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_dechanyu.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_dechanyu.h

Read completely: 37 lines.

This header declares DECHanyu ctype and standard-encoding getops entry points.

Security/reliability notes: declaration-only ABI surface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_dechanyu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_euc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_euc.c

Read completely: 437 lines.

This module implements configurable EUC ctype and stdenc support. Encoding variables supply four byte counts, four bit masks, and a global mask that determine character-set selection and wide-character construction.

Key behavior: `_citrus_EUC_parse_variable` reads counts and bit values from the module variable string, requiring each count to be 1 through 4. `_citrus_EUC_cs` classifies the first byte into G0/G1/SS2/SS3. `mbrtowc_priv` buffers up to three bytes and constructs a wide value by applying masks/bits. `wcrtomb_priv` finds the matching charset bits, emits SS2/SS3 prefixes when needed, and writes the configured number of bytes.

Important interactions: this module relies entirely on ESDB-provided variables for correctness; it exports through ctype/stdenc templates.

Security/reliability notes: variable parsing rejects missing or malformed fields with `EFTYPE`. The tableless conversion path bounds output length with `n < i` checks. Callers must ensure the variable string is NUL-terminated or otherwise safe for the parser’s `while (*v)` style scanning.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_euc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_euc.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_euc.h

Read completely: 37 lines.

This header declares EUC ctype and standard-encoding getops entry points.

Security/reliability notes: declaration-only ABI surface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_euc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_euctw.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_euctw.c

Read completely: 430 lines.

This module implements EUC-TW ctype and stdenc support for ASCII and CNS-11643 planes. It uses fixed byte-class rules with no module variables.

Key behavior: ASCII is 1 byte, CNS plane 1 is two high-bit bytes, and planes 2 through 7 are four bytes using SS2 followed by a plane selector `0xA2-0xA7` and two high-bit bytes. Wide characters carry a plane marker in the high byte (`'G'` through `'M'`). Standard-encoding csid is the high-byte plane marker and index is the lower 7-bit row/column value.

Important interactions: exports through ctype/stdenc templates.

Security/reliability notes: output conversion validates buffer size before writing. Input conversion resets state on illegal sequences. One notable quirk is the `restart` path in `mbrtowc_priv`, which sets `*nresult = (size_t)-1` while returning 0, unlike the usual `(size_t)-2` incomplete marker used by most other restartable modules.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_euctw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_euctw.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_euctw.h

Read completely: 37 lines.

This header declares EUCTW ctype and standard-encoding getops entry points.

Security/reliability notes: declaration-only ABI surface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_euctw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_gbk2k.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_gbk2k.c

Read completely: 476 lines.

This module implements GBK/GB18030-style GBK2K ctype and stdenc support. It supports 1-byte ASCII, 2-byte GBK sequences, and optionally 4-byte surrogate-form sequences depending on module variables.

Key behavior: lead bytes are `0x81-0xFE`, trail bytes are `0x40-0x7E` or `0x80-0xFE`, and 4-byte sequences use decimal surrogate bytes `0x30-0x39` in positions 2 and 4. The variable parser scans for `2byte` to force `mb_cur_max = 2`; otherwise max is 4. Standard encoding classifies ASCII as csid 0, EUC-like G1 as csid 1, extended 2-byte as csid 2, and 4-byte GBKUCS as csid 3.

Important interactions: exports through ctype/stdenc templates and uses BCS case-insensitive matching for variables.

Security/reliability notes: conversion uses a small fixed 4-byte state buffer and checks each pushed byte class before completion. On `EILSEQ`, `mbrtowc_priv` does not reset `psenc->chlen`, unlike some peer modules; callers that retry after errors should explicitly reinitialize state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_gbk2k.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_gbk2k.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_gbk2k.h

Read completely: 37 lines.

This header declares GBK2K ctype and standard-encoding getops entry points.

Security/reliability notes: declaration-only ABI surface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_gbk2k.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_hz.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_hz.c

Read completely: 728 lines.

This module implements configurable HZ ctype and stdenc support. HZ is state-dependent: escape sequences switch active GL/GR graphic sets, and character interpretation depends on the active escape entry.

Key structures: `graphic_t` records charset, row/column length, and owning escape; `escape_t` links an escape character to GL/GR graphics and its escape set; `_HZEncodingInfo` owns two escape lists plus selected ASCII/GB2312 graphics; `_HZState` stores partial bytes and the active escape.

Key behavior: module variables are parsed with `citrus_prop`, defining escape set `0` and `1` entries with `CH`, `GL`, and `GR` properties. `mbrtowc_priv` handles `~` escapes, line continuation, GL/GR selection, active-set switching, and row/column range validation. `wcrtomb_priv` selects or switches the active escape before output. `put_state_reset` emits a reset escape to the initial set when needed.

Important interactions: uses `citrus_prop` callbacks to allocate escape and graphic nodes; exports through ctype/stdenc templates.

Security/reliability notes: parser-owned allocations are freed by `_citrus_HZ_encoding_module_uninit`. The module is sensitive to malformed variable strings because missing initial escapes can leave `INIT0(ei)` null and later state initialization asserts/depends on it. Conversion functions return `EINVAL` for impossible internal state and `EILSEQ` for invalid byte sequences.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_hz.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_hz.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_hz.h

Read completely: 37 lines.

This header declares HZ ctype and standard-encoding getops entry points.

Security/reliability notes: declaration-only ABI surface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_hz.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iconv_none.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iconv_none.c

Read completely: 128 lines.

This module implements a no-op iconv converter that copies bytes from input to output. Shared and per-context initialization store no closure. `convert` copies `min(*inbytes, *outbytes)` bytes, updates byte counts, reports zero invalids, and returns `E2BIG` if output space was insufficient.

Important interactions: exports iconv getops via `_CITRUS_ICONV_DEF_OPS(iconv_none)` and `_citrus_iconv_none_iconv_getops`.

Security/reliability notes: the copy itself is bounded by `len`. However, the pointer advancement in `_citrus_iconv_none_iconv_convert` uses `in += len` and `out += len`, which advances the local pointer-to-pointer variables rather than `*in` and `*out`. The byte counters are decremented, but caller-visible buffer pointers are not advanced. This looks like a functional bug with possible retry-loop consequences for callers expecting normal iconv pointer updates.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iconv_none.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iconv_none.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iconv_none.h

Read completely: 36 lines.

This header declares the `iconv_none` getops entry point with `_CITRUS_ICONV_GETOPS_FUNC(iconv_none)`.

Security/reliability notes: declaration-only ABI surface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iconv_none.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iconv_std.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iconv_std.c

Read completely: 585 lines.

This module implements the standard Citrus iconv engine. It opens source and destination ESDB records, opens their standard encodings, builds lists of usable charset mappers between source and destination charsets, then converts input by decoding to csid/index, mapping, and encoding to output.

Key functions: `open_csmapper` restricts composed mappers to stateless 1:1 mappings; `open_dsts` and `open_srcs` build sorted mapper lists by normalization cost; `do_conv` tries destination mappers and reports non-identical/no-corresponding cases; shared/context init allocate encodings and per-context state storage; `convert` handles reset calls, saves/restores encoding state around errors, tracks invalid counts, and optionally emits destination invalid replacement characters.

Important interactions: depends on ESDB, stdenc, mapper/csmapper, memstream, and Citrus iconv ABI. It is the bridge tying most files in this group into actual iconv behavior.

Security/reliability notes: state save/restore is a strong error-recovery pattern. Mapper initialization rejects stateful or non-1:1 mappers. Context allocation computes `(src_state + dst_state) * 2 + context`; if new encodings ever expose very large state sizes, overflow hardening would be prudent. The `err_norestore` label is present but unused.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iconv_std.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iconv_std.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iconv_std.h

Read completely: 36 lines.

This header includes `citrus_iconv_std_local.h` and declares `_CITRUS_ICONV_GETOPS_FUNC(iconv_std)`.

Security/reliability notes: declaration-only ABI surface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iconv_std.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iconv_std_local.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iconv_std_local.h

Read completely: 81 lines.

This header defines private data structures for `iconv_std`: per-encoding handles plus live/saved states, destination mapper records, source mapper records, shared converter state, and per-context state.

Important fields: `_citrus_iconv_std_shared` owns source/destination standard encodings, source charset mapping list, and invalid replacement policy; `_citrus_iconv_std_context` owns the per-call mutable encoding state wrappers.

Security/reliability notes: no executable code. The separation between shared immutable mapping state and per-context mutable conversion state is important for thread-safety and reentrancy.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iconv_std_local.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iso2022.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iso2022.c

Read completely: 1349 lines.

This module implements ISO-2022 ctype and stdenc support. It is a configurable, state-dependent escape-sequence engine with G0-G3 designation, GL/GR invocation, single-shift handling, optional 8-bit behavior, and recommended charset placement.

Key structures: `_ISO2022Charset` records charset type/final/intermediate/version; `_ISO2022State` stores current G sets, GL/GR/single-shift selectors, a partial escape buffer, and initialization flags; `_ISO2022EncodingInfo` stores recommendation arrays, initial G sets, max charset policy, and flags.

Key behavior: `_citrus_ISO2022_parse_variable` parses tokens such as charset recommendations, `INITn=...`, `MAXn`, and flags (`8BIT`, `LS*`, `SS*`, `NOOLD`). `_ISO2022_sgetwchar` consumes shifts and escape sequences, updates designation state, and extracts wide-character encodings. `_citrus_ISO2022_mbrtowc_priv` manages restartable partial escape buffers. `_ISO2022_sputwchar` chooses a charset plane, emits designation/invocation sequences, and writes encoded bytes. `put_state_reset` emits a reset sequence by outputting NUL and dropping the final data byte.

Important interactions: exports through ctype/stdenc templates and is consumed by `iconv_std`. It uses only variable strings, no external mapping file in this source.

Security/reliability notes: the escape buffer is fixed at 7 bytes and the parser rejects too-long/incomplete sequences through restart or `EILSEQ`. Variable parsing allocates recommendation arrays and frees them only on parse failure; module uninit is empty, so successful initialization retains those arrays for module lifetime but does not release them on close. Comments note that output conversion mutates state before all buffer-size failures are known; callers such as `iconv_std` save/restore state around failures to compensate.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iso2022.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iso2022.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iso2022.h

Read completely: 37 lines.

This header declares ISO2022 ctype and standard-encoding getops entry points.

Security/reliability notes: declaration-only ABI surface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iso2022.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_johab.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_johab.c

Read completely: 395 lines.

This module implements JOHAB ctype and stdenc support for Korean encodings. It supports ASCII and two-byte Hangul, user-defined, and Hanja ranges.

Key behavior: helper predicates validate Hangul (`0x84-0xD3` lead), user-defined area (`0xD8` lead), and Hanja (`0xD9-0xDE` or `0xE0-0xF9` lead) with their allowed trail-byte ranges. `mbrtowc_priv` buffers one lead byte and completes with a validated trail byte. `wcrtomb_priv` emits ASCII or validated two-byte values. Standard encoding maps Hanja between JOHAB byte ranges and a linear 94-column index for csid 2.

Important interactions: no variables or external tables; exports through ctype/stdenc templates.

Security/reliability notes: buffer-size checks are simple and explicit. On illegal two-byte input, `mbrtowc_priv` returns `EILSEQ` without clearing `chlen`, so caller state handling after errors matters.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_johab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_johab.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_johab.h

Read completely: 37 lines.

This header declares JOHAB ctype and standard-encoding getops entry points.

Security/reliability notes: declaration-only ABI surface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_johab.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_646.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_646.c

Read completely: 259 lines.

This module implements an ISO-646 variant mapper for a fixed set of special ASCII code points: `#`, `$`, `@`, brackets, backslash, caret, grave, braces, vertical bar, and tilde. A description file supplies replacement values for those positions.

Key behavior: the variable string optionally starts with `!` to request backward mapping, followed by a file path relative to the mapper directory. `parse_file` memory-maps that file and reads one numeric mapping per special code. Forward conversion maps special ASCII through the table, passes other ASCII through, rejects `src >= 0x80`, and treats `INVALID` table entries as non-identical. Backward conversion reverses table entries, rejects ambiguous source special bytes, and treats non-ASCII as non-identical.

Important interactions: uses mapper ABI, memstream, mmap, and BCS helpers.

Security/reliability notes: path construction uses `PATH_MAX` and `snprintf`, but truncation is not explicitly detected. In `parse_file`, after `strtoul`, the code calls `_bcs_skip_ws(buf)` rather than skipping from the parse end pointer, which appears to make the trailing-content validation ineffective or inverted for normal numeric lines; this parser deserves targeted tests before format changes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_646.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_646.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_646.h

Read completely: 37 lines.

This header declares the mapper_646 getops entry point twice with `_CITRUS_MAPPER_GETOPS_FUNC(mapper_646)`.

Security/reliability notes: duplicate identical declarations are harmless in C but noisy; declaration-only ABI surface otherwise.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_646.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_none.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_none.c

Read completely: 111 lines.

This module implements the identity mapper. Initialization sets traits to stateless 1:1 conversion with no closure. Conversion writes `src` to `*dst` and returns `_CITRUS_MAPPER_CONVERT_SUCCESS`.

Important interactions: useful as a mapper plugin where an explicit no-op mapping is needed. It exports through mapper ABI macros.

Security/reliability notes: no dynamic allocation and minimal attack surface. The convert function assumes `dst` is valid.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_none.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_none.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_none.h

Read completely: 36 lines.

This header declares the mapper_none getops entry point.

Security/reliability notes: declaration-only ABI surface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_none.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_serial.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_serial.c

Read completely: 263 lines.

This module implements two composite mapper plugins: serial and parallel. Both parse a comma-separated list of mapper names and open each mapper from the current mapper area.

Key behavior: serial conversion applies every mapper in order, feeding each output into the next. Parallel conversion tries each mapper against the original source and returns the first successful result; `ILSEQ` aborts immediately, while other failures continue until returning non-identical. Initialization rejects child mappers that are not stateless 1:1 converters.

Important interactions: uses `_mapper_open`, `_mapper_close`, mapper trait accessors, memstream parsing, and SIMPLEQ storage.

Security/reliability notes: `parse_var` trims mapper names into a `PATH_MAX` buffer with `snprintf` but does not detect truncation. In one error path after opening a child mapper with incompatible traits, it frees the link without closing `ml_mapper`, causing a resource leak on malformed composition definitions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_serial.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_serial.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_serial.h

Read completely: 37 lines.

This header declares mapper_serial and mapper_parallel getops entry points.

Security/reliability notes: declaration-only ABI surface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_serial.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_std.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_std.c

Read completely: 464 lines.

This module implements the standard binary-table mapper. It opens a mapped DB file, validates the `MAPPER\0\0` magic, reads the mapper `type`, and currently supports `rowcol` tables.

Key behavior: row/column metadata defines source component bit width, component ranges, destination unit width, invalid sentinel, and optional out-of-bounds/illegal-sequence extension. `rowcol_convert` decomposes the source index into row/column components, linearizes into a table offset, reads an 8/16/32-bit big-endian destination value, and returns success, non-identical, or illegal-sequence based on sentinel values.

Important interactions: uses `citrus_db` over an mmap-backed region, file-layout constants from `citrus_mapper_std_file.h`, local rowcol structures from `citrus_mapper_std_local.h`, and mapper ABI macros.

Security/reliability notes: it validates rowcol count, source bit width, destination unit width, and table size before conversion. Table-size multiplication uses `uint64_t`, reducing overflow risk. A likely validation bug exists in the optional extension block: after `_db_lookup_by_s` returns `ENOENT`, the code still checks `_region_size(&r) < sizeof(*eix)` before the `ret == 0` guard, using an uninitialized or stale region and potentially rejecting mapper files without the optional extension.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_std.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_std.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_std.h

Read completely: 38 lines.

This header includes `citrus_mapper_std_local.h` and declares the mapper_std getops entry point.

Security/reliability notes: declaration-only ABI surface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_std.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_std_file.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_std_file.h

Read completely: 75 lines.

This header defines the on-disk standard mapper DB format constants. It declares the magic string, DB symbol names (`type`, `info`, `table`, `rowcol_ext_ilseq`), the `rowcol` type string, current and compatibility row/column info structures, fixed structure sizes, row/column maximum, and out-of-bounds extension modes.

Important interactions: `citrus_mapper_std.c` reads these packed big-endian records from mapped DB regions.

Security/reliability notes: no executable logic. Because these structures are file-format ABI, changes require compatible readers or versioning.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_std_file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_std_local.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_std_local.h

Read completely: 70 lines.

This header defines private in-memory structures for mapper_std. It includes linear zones, rowcol mapper state, converter/uninit function pointer types, and the top-level `_citrus_mapper_std` object containing the mapped file region, DB handle, dispatch callbacks, and type-specific union.

Important interactions: consumed only by `citrus_mapper_std.c` through `citrus_mapper_std.h`.

Security/reliability notes: no executable code. The design keeps file-backed table data in `_citrus_region` and heap-allocated parsed row/column zone metadata in `rc_src_rowcol`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_std_local.h -->