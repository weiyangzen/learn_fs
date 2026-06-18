<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_decoder.c -->
# sources/compression/xz/src/liblzma/common/stream_decoder.c

Purpose: Implements the single-threaded `.xz` Stream decoder state machine.

Important APIs/types: `lzma_stream_coder` owns sequence, nested Block decoder, `lzma_block` options, Stream Flags, `lzma_index_hash`, memory limit/usage, check reporting flags, concatenation flags, buffer position, and a shared header buffer. Public `lzma_stream_decoder()` wraps internal `lzma_stream_decoder_init()`.

Control flow: `SEQ_STREAM_HEADER` reads and validates the Header, reports check notifications if requested, and sets Block check type. `SEQ_BLOCK_HEADER` distinguishes Index Indicator from Block Header and collects full Block Header. `SEQ_BLOCK_INIT` decodes filter options, applies ignore-check, calculates raw decoder memory, enforces memlimit, initializes the Block decoder, and frees temporary filter options. `SEQ_BLOCK_RUN` forwards data/output to the Block decoder and appends observed size pairs to `lzma_index_hash`. `SEQ_INDEX` decodes and verifies Index hash. `SEQ_STREAM_FOOTER` verifies Backward Size and Stream Flags. `SEQ_STREAM_PADDING` handles concatenated Streams and four-byte padding alignment.

State and persistence: The nested Block decoder and Index hash persist across calls. `memusage` is updated only after a valid filter chain is known, so `lzma_memusage()` does not expose `UINT64_MAX` from bad options. `first_stream` converts bad magic in later Streams from format error to data error.

Dependencies/integration: Depends on Block decoder, filter decoder memory usage, Stream Header/Footer helpers, `index_hash.c`, and `lzma_next_coder` callbacks (`end`, `get_check`, `memconfig`).

Risks/tests: Error classification, memlimit retry at `SEQ_BLOCK_INIT`, Index/hash verification, and concatenated padding are critical. Tests should cover all check-reporting flags, unknown filters, low memlimit, unsupported checks, corrupt Block/Header/Footer/Index, concatenated Streams with padding, and `LZMA_FINISH` behavior.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_decoder.c -->
