<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/known_sizes.c -->
# sources/compression/xz/debug/known_sizes.c

Purpose: debug encoder that manually constructs an `.xz` stream whose block header records known compressed and uncompressed sizes.

Important APIs/types/functions: uses `lzma_lzma_preset`, `lzma_block`, `lzma_block_encoder`, `lzma_block_header_size`, `lzma_block_header_encode`, `lzma_index_init`, `lzma_index_append`, `lzma_index_encoder`, `lzma_stream_header_encode`, and `lzma_stream_footer_encode`.

Control flow: read up to 1 MiB of stdin into memory, encode a single LZMA2 block into an output buffer, backfill the block header, build and encode an index, synthesize stream flags/header/footer, then write the complete stream.

State and persistence: all encoding buffers and liblzma structures are process-local; output is emitted to stdout only.

Dependencies and integration: exercises lower-level block/index/container APIs instead of the high-level stream encoder.

Risks: output buffer is also 1 MiB and the comment admits overflow is possible for poorly compressible input near the limit. Many errors return `1` without diagnostics. It does not check `fread`/`fwrite` errors.

Test signals: generated output should pass `xz -t` and `xz --list` should show known block sizes; inputs close to the buffer limit are useful negative tests.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/known_sizes.c -->
