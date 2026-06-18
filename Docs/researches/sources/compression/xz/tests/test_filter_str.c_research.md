# sources/compression/xz/tests/test_filter_str.c

Purpose: tests string conversion APIs for liblzma filter chains: parsing, formatting, and listing filters.

Important functions and data: `test_lzma_str_to_filters()`, `test_lzma_str_from_filters()`, `test_lzma_str_list_filters()`, plus compile-time arrays of supported encoder, decoder, and combined filter names.

Control flow: parsing tests cover NULL inputs, unsupported flags, empty and invalid names, invalid option names/values, presets, `LZMA_STR_ALL_FILTERS`, `LZMA_STR_NO_VALIDATION`, chain length limits, options via `key=value`, BCJ and delta options, leading/trailing spaces, `--` separators, and binary multiplier suffixes. Formatting tests check bad inputs/flags, empty arrays, encoder/decoder/getopt/no-space modes, BCJ default option elision, too many filters, NULL required options, and bad IDs. Listing tests validate flag errors, filter-specific listing, and expected supported names by build configuration.

State and persistence: repeatedly allocates filter option arrays and output strings, then frees them with `lzma_filters_free()` and `free()`. No files are read.

Dependencies and integration: exercises public filter-string APIs, filter support macros, and option structs. It mirrors CLI `--filters=`-style parsing semantics.

Risks: error-position assertions are fragile but valuable because they lock parser diagnostics. Contains a noted weak substring check where `"arm"` can match longer names.

Test signals: detects parser grammar regressions, option validation errors, string formatting drift where exact output is promised, and listing omissions.
