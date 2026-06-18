# sources/compression/zstd/examples/multiple_streaming_compression.c

Purpose: demonstrates streaming compression of multiple files while reusing input/output buffers and a `ZSTD_CCtx`.

Important types/functions: `resources`, `createResources_orDie`, `freeResources`, `compressFile_orDie`, `main`, `ZSTD_CStreamInSize`, `ZSTD_CStreamOutSize`, `ZSTD_CCtx_setParameter`, `ZSTD_CCtx_reset`, and `ZSTD_compressStream2`.

Control flow: resources are allocated once at compression level 7 with checksum enabled. Each file opens input/output, resets only the compression session while keeping sticky parameters, reads chunks of recommended input size, chooses `ZSTD_e_continue` or `ZSTD_e_end`, loops until the chunk is consumed or the frame ends, writes produced output, then closes files. Output filename buffer grows as needed.

State and persistence: buffers and CCtx persist across files; context session state is reset before each file. Outputs are `<input>.zst`.

Dependencies/integration: public streaming compression API, `common.h`, examples Makefile. It illustrates the sticky-parameter contract of `ZSTD_CCtx_reset(..., ZSTD_reset_session_only)`.

Risks: the loop uses `read < toRead` to detect the last chunk, which is correct for regular fread EOF patterns but means a read error must be caught by `fread_orDie`. Output names are appended blindly. Any fatal helper exits the whole multi-file run.

Test signals: multiple files, empty file, files exactly equal to `ZSTD_CStreamInSize()`, checksum verification via decompression, and reuse behavior after compressing several files.
