# sources/compression/xz/src/liblzma/common/block_encoder.c

Purpose: streaming encoder for an XZ Block body, excluding the Block Header but including compressed data padding and integrity Check output.

Important APIs/types/functions: internal `lzma_block_coder`, `block_encode()`, `block_encoder_end()`, `block_encoder_update()`, `lzma_block_encoder_init()`, and public `lzma_block_encoder()`.

Control flow: during `SEQ_CODE`, the raw encoder consumes input and produces compressed bytes; the wrapper tracks compressed/uncompressed sizes, guards against VLI overflow, and updates the selected check with consumed input. On `LZMA_STREAM_END` with `LZMA_FINISH`, it stores final sizes to `lzma_block`, emits zero Block Padding until the compressed size is four-byte aligned, finalizes and streams the Check field, copies raw check to the block, and returns `LZMA_STREAM_END`.

State and persistence: per-stream state holds nested raw encoder, caller block pointer, sequence, size counters, check position, and check state. It mutates `block->compressed_size`, `block->uncompressed_size`, and `block->raw_check`.

Dependencies/integration: includes `filter_encoder.h` and `check.h`. Higher-level stream encoders combine it with Block Header generation and Index construction.

Risks: callers must compute/encode the Block Header separately using final sizes or a reserved header strategy. `block_encoder_update()` only permits filter updates during payload coding. Unsupported check types prevent encoding because a valid Block cannot be produced.

Test signals: streaming Block encode/decode round trips, sync flush behavior, filter-update tests, VLI overflow boundaries, and check field validation.
