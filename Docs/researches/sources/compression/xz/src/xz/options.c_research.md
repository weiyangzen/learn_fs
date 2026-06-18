# Research: sources/compression/xz/src/xz/options.c
## sources/compression/xz/src/xz/options.c

Purpose: Parses filter-specific option strings for Delta, BCJ, LZMA1, and LZMA2 old-style filter options.

Important APIs and functions: Public parsers are `options_delta()`, `options_bcj()`, and `options_lzma()`, each returning an allocated liblzma option struct. Internal `parse_options()` splits comma-separated `name=value` entries, validates option names, maps string values or bounded integer values, and dispatches to filter-specific setters. `set_delta()`, `set_bcj()`, and `set_lzma()` mutate option structs. `error_lzma_preset()` handles invalid preset strings.

Control flow: `args.c` invokes these functions when parsing `--delta`, BCJ filters, `--lzma1`, and `--lzma2`, then passes returned option pointers to `coder_add_filter()`. `coder.c` owns eventual filter-chain cleanup for dynamically allocated filter options.

State and persistence: Functions allocate option structs with `xmalloc()` and return ownership to the filter chain. There is no static parser state.

Dependencies and integration points: Uses liblzma option constants and `lzma_lzma_preset()`, `str_to_uint64()` for numeric parsing, and `message_fatal()` for validation failures. Complements newer `--filters` string parsing handled directly in `coder.c` through liblzma.

Risks: The generic parser does not support escaping or quoted commas. Optional filter arguments with null/empty strings keep defaults. LZMA `lc + lp <= 4` is validated here; other semantic validation occurs later through liblzma memory usage or encoder init. Returned allocations must remain valid for the lifetime of the filter chain.

Test signals: Cover empty option strings, missing values, invalid option names, invalid map values, bounds for delta distance, BCJ start offset, LZMA dict/lc/lp/pb/nice/depth, preset `0-9` and `e`, bad preset modifiers, and `lc + lp` overflow.
