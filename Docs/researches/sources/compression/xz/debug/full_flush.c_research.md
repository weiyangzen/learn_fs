<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/full_flush.c -->
# sources/compression/xz/debug/full_flush.c

Purpose: debug encoder that creates an `.xz` stream while issuing multiple `LZMA_FULL_FLUSH` actions around fixed-size input chunks.

Important APIs/types/functions: global `lzma_stream strm`, `FILE *file_in`, helper `encode(size_t size, lzma_action action)`, `lzma_lzma_preset`, `lzma_stream_encoder`, `lzma_code`, and `lzma_end`.

Control flow: `main` opens an optional input file, builds an LZMA2+CRC32 stream encoder using preset 1, then calls `encode` with zero-length and small chunk sizes followed by `LZMA_FINISH`. `encode` refills input while `size > 0`, runs `lzma_code` with `LZMA_RUN` until chunk completion, flushes generated output, and asserts expected return codes.

State and persistence: stream state persists globally across multiple flush calls; output is written to stdout. No durable state is stored.

Dependencies and integration: depends on liblzma streaming encoder and `sysdefs.h` `my_min`.

Risks: `fopen` is not checked for failure. `size` is decremented by requested bytes rather than `fread` bytes, intentionally testing stream behavior but fragile on short reads. Write errors are ignored.

Test signals: resulting stream should decompress successfully and preserve input prefix covered by requested chunks; useful for regression checks around `LZMA_FULL_FLUSH`.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/full_flush.c -->
