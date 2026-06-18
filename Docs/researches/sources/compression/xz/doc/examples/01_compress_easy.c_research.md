<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/doc/examples/01_compress_easy.c -->
# sources/compression/xz/doc/examples/01_compress_easy.c

Purpose: documented sample showing multi-call `.xz` compression from stdin to stdout with `lzma_easy_encoder`.

Important APIs/types/functions: `get_preset`, `init_encoder`, `compress`, `lzma_stream`, `LZMA_STREAM_INIT`, `lzma_easy_encoder`, `lzma_code`, `LZMA_RUN`, `LZMA_FINISH`, and `lzma_end`.

Control flow: parse preset `0-9` plus optional `e`, initialize CRC64 preset encoder, loop reading input and calling `lzma_code`, flush output when the output buffer fills or stream ends, handle liblzma errors explicitly, then close stdout.

State and persistence: one `lzma_stream` holds encoder state; stdin/stdout are the only data channels.

Dependencies and integration: primary public API example for applications embedding liblzma.

Risks: intended as sample code, not a full CLI. It is careful with read/write errors, but uses stdio buffering and single-threaded flow only.

Test signals: compile with `-llzma`, compress a file, and validate with `xz -t` or decompression comparison.
<!-- END_FILE_RESEARCH: sources/compression/xz/doc/examples/01_compress_easy.c -->
