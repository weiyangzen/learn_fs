<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_decoder.c -->
# sources/compression/xz/src/liblzma/common/filter_decoder.c

Purpose: Maps Filter IDs to decoder-specific functions and exposes raw decoder initialization, support checks, memory usage, and property decoding.

Important APIs/data: The `decoders[]` table is built from compile-time macros and maps LZMA1/LZMA1EXT, LZMA2, BCJ filters, and Delta to init, memory, and properties-decode callbacks. Public functions include `lzma_filter_decoder_is_supported()`, `lzma_raw_decoder()`, `lzma_raw_decoder_memusage()`, and `lzma_properties_decode()`. Internal `lzma_raw_decoder_init()` feeds `filter_common.c`.

Control flow: `decoder_find()` scans the table. `lzma_raw_decoder_init()` delegates chain validation and initialization to `lzma_raw_coder_init()` with decoder order preserved. `lzma_properties_decode()` initializes `filter->options` to NULL for safe cleanup, rejects unknown IDs, accepts empty properties when no decode callback exists, and otherwise lets the filter-specific decoder allocate options.

State and dependencies: Static table only; no persistent runtime state. Depends on filter-specific headers for LZMA, LZMA2, simple BCJ, and Delta decoders.

Risks and tests: Compile-time feature combinations affect supported IDs. Tests should cover unsupported-but-valid IDs, invalid properties sizes, `options` cleanup behavior, memory usage for chains with simple filters, and raw decoding action support (`LZMA_RUN`, `LZMA_FINISH`).
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_decoder.c -->
