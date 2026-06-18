# sources/compression/xz/src/liblzma/common/block_decoder.c

Purpose: streaming decoder for an XZ Block body after its Block Header has been decoded, including raw filter chain output, Block Padding, and integrity Check validation.

Important APIs/types/functions: internal `lzma_block_coder`, helper `is_size_valid()`, `block_decode()`, `block_decoder_end()`, `lzma_block_decoder_init()`, and public `lzma_block_decoder()`.

Control flow: `block_decode()` limits input/output passed to the raw decoder based on known or maximum compressed/uncompressed sizes, updates running sizes, updates the check over produced output unless ignored, validates size consistency at stream end, stores actual sizes back into `lzma_block`, consumes zero padding until compressed size is four-byte aligned, finalizes and reads/verifies the Check field, and returns `LZMA_STREAM_END`.

State and persistence: per-coder state tracks nested raw decoder, block pointer, size counters/limits, check state, check read position, sequence, and `ignore_check`. It mutates the caller's `lzma_block` sizes and raw check.

Dependencies/integration: includes `filter_decoder.h` and `check.h`. Used by streaming and single-call Block decoders; caller usually obtains `block->filters` from `block_header_decoder.c`.

Risks: limit arithmetic prevents VLI overflow and over-read/over-output; regressions can become parsing vulnerabilities. Unsupported checks are read but not verified. `ignore_check` is available for block version >=1 and weakens integrity validation by design.

Test signals: Block decode tests for known/unknown sizes, padding errors, check mismatch, unsupported/ignored checks, filter chain errors, and streaming with small input/output buffers.
