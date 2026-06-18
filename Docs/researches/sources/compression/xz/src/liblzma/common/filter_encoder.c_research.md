<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_encoder.c -->
# sources/compression/xz/src/liblzma/common/filter_encoder.c

Purpose: Maps Filter IDs to encoder-specific functions and exposes raw encoder initialization, support checks, memory usage, property encoding, and multithreaded block-size hints.

Important APIs/data: `encoders[]` maps supported filter IDs to init, memory usage, optional block-size, property-size, fixed property-size, and property-encode callbacks. Public APIs include `lzma_filter_encoder_is_supported()`, `lzma_filters_update()`, `lzma_raw_encoder()`, `lzma_raw_encoder_memusage()`, `lzma_mt_block_size()`, `lzma_properties_size()`, and `lzma_properties_encode()`. Internal `lzma_raw_encoder_init()` delegates to common chain initialization.

Control flow: Raw encoder init validates through `filter_common.c` and reverses the filter order for efficient encoding. `lzma_filters_update()` validates a new filter chain, builds a reversed copy, and calls the active coder update callback. `lzma_mt_block_size()` returns the maximum filter-specific block-size recommendation or `UINT64_MAX` when no hint is available. Property helpers distinguish unsupported valid IDs from programming errors and handle fixed-size versus callback-sized properties.

State/dependencies: Static table only. Depends on LZMA, LZMA2, simple BCJ, and Delta encoder modules. Public stream state is installed through `lzma_next_strm_init()` with `LZMA_RUN`, `LZMA_SYNC_FLUSH`, and `LZMA_FINISH`.

Risks/tests: Table accuracy is central. Tests should cover compile-time feature combinations, update callbacks with reversed chains, property size/encode failures, unsupported IDs, invalid options, and LZMA2 block-size hints for threaded encoding.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_encoder.c -->
