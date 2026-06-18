# sources/compression/xz/src/liblzma/common/string_conversion.c Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/string_conversion.c -->
## sources/compression/xz/src/liblzma/common/string_conversion.c

### Purpose
`string_conversion.c` converts between user-facing filter-chain strings and `lzma_filter` arrays. It also lists supported filter names/options. This is the library-side counterpart of xz-style preset/filter syntax, but it avoids locale-sensitive parsing and keeps messages translatable by xz.

### Important APIs, Types, And Functions
`lzma_str_to_filters()` parses presets and explicit chains. `lzma_str_from_filters()` stringifies filter arrays. `lzma_str_list_filters()` produces help/listing text. Internal helpers include fixed-buffer string builder `lzma_str`, option metadata `option_map`, string-to-value maps, `parse_lzma12_preset()`, `parse_options()`, `parse_filter()`, `str_to_filters()`, and `strfy_filter()`. The static `filter_name_map` binds filter names to IDs, option sizes, parsers, and stringification ranges.

### Control Flow
Parsing skips leading spaces and treats digit or `-digit` input as an LZMA2 preset. Otherwise it parses up to four filters separated by spaces or `--`, allocates zeroed option structures, dispatches filter-specific parsers, validates `.xz`-allowed filters unless `LZMA_STR_ALL_FILTERS` is set, and optionally validates the chain with `lzma_validate_chain()`. Option parsing handles `name=value`, maps named values, parses decimal `uint32_t` without `strtoul()`, accepts KiB/MiB/GiB suffixes only for flagged options, writes fields by `offsetof`, and advances the input pointer for accurate error positions. Stringification walks filters, maps IDs back to names, optionally emits encoder/decoder options, and supports getopt-long syntax and no-space chain separators.

### State, Persistence, And Dependencies
All state is temporary except allocated filter options or returned strings, which the caller must later free through liblzma conventions. The output string uses a fixed 800-byte allocation. Dependencies include `filter_common.h`, filter feature macros, LZMA/delta/BCJ option types, `lzma_lzma_preset()`, `lzma_validate_chain()`, and allocator helpers.

### Integration Points
This API is used by applications that accept human-readable filter strings and by tools that need to print or list available filter chains. Compile-time feature macros determine which filters appear in `filter_name_map`.

### Risks
The fixed string buffer is intentionally not reallocated; adding filters/options without increasing `STR_ALLOC_SIZE` can trip `LZMA_PROG_ERROR`. Parsing allocates each filter options object before validation, so every error path must free partial results. `LZMA_STR_NO_VALIDATION` can return chains that later fail encoder/decoder initialization. Error messages are static strings; callers should use `error_pos` to report location.

### Test Signals
Tests should cover presets, explicit LZMA1/LZMA2 options, BCJ and delta options, multiplier suffix variants, duplicate commas, missing names/values, too-long names, unsupported flags, all stringification flags, NULL options for filters that allow/disallow them, and error-position accuracy.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/string_conversion.c -->
