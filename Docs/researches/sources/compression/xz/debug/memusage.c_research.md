<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/memusage.c -->
# sources/compression/xz/debug/memusage.c

Purpose: prints encoder and decoder memory usage for a hard-coded raw LZMA1 filter chain.

Important APIs/types/functions: initializes `lzma_options_lzma`, builds a `lzma_filter` array, calls `lzma_raw_encoder_memusage` and `lzma_raw_decoder_memusage`.

Control flow: no input processing; `main` constructs options with a 1.5 GiB dictionary and BT4 match finder, queries memory usage, prints byte counts, and exits.

State and persistence: no persistent state.

Dependencies and integration: depends on liblzma raw-filter memory accounting. It is a debug probe for memory limit and option validation behavior.

Risks: hard-coded extreme dictionary size may return values not representative of normal presets. It does not check for `UINT64_MAX` error returns from memory-usage APIs.

Test signals: compare printed values to expected memory formulae or regressions when liblzma memory accounting changes.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/memusage.c -->
