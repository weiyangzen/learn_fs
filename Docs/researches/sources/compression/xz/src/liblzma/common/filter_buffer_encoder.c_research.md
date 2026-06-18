<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_buffer_encoder.c -->
# sources/compression/xz/src/liblzma/common/filter_buffer_encoder.c

Purpose: Implements `lzma_raw_buffer_encode()`, the single-call raw encoder wrapper for an already-specified filter chain.

Important APIs: The function validates buffer arguments, initializes a temporary raw encoder with `lzma_raw_encoder_init()`, runs the coder with `LZMA_FINISH`, frees it, and maps `LZMA_STREAM_END` to `LZMA_OK`.

Control flow and state: It keeps a local `in_pos` and snapshots `out_pos`. On successful stream end it leaves the new output position visible. On `LZMA_OK`, the output buffer was too small and becomes `LZMA_BUF_ERROR`; all other errors preserve the original output position.

Dependencies and integration: Depends on `filter_encoder.h`, the raw filter chain init path, and downstream filter encoders such as LZMA, BCJ, and Delta. It is commonly exercised by raw filter tests and higher-level single-shot wrappers.

Risks and tests: The main risks are accepting invalid `NULL`/size combinations and failing to roll back `out_pos` on errors. Tests should cover empty input, exact output capacity, undersized output, invalid chains, and custom allocator failures.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_buffer_encoder.c -->
