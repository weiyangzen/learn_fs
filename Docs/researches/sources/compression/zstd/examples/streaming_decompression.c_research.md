# sources/compression/zstd/examples/streaming_decompression.c

Purpose: streaming decompression example that reads a file containing one or more concatenated zstd frames and writes decompressed bytes to stdout.

Important functions/APIs: `decompressFile_orDie`, `main`, `ZSTD_DStreamInSize`, `ZSTD_DStreamOutSize`, `ZSTD_createDCtx`, `ZSTD_decompressStream`, `ZSTD_freeDCtx`, and common IO helpers.

Control flow: open input and use stdout as output, allocate recommended buffers, create DCtx, read chunks, and while input remains call `ZSTD_decompressStream` into an output buffer and write produced bytes. It tracks `lastRet`; after EOF, empty input is rejected and nonzero `lastRet` means the final frame was truncated.

State and persistence: DCtx keeps streaming decompression state across calls and automatically resets at frame boundaries. Persistent effect is writing to stdout, which may be redirected by tests.

Dependencies/integration: public zstd streaming decompression API and `common.h`. The examples Makefile uses it for positive decompression and invalid-input negative tests.

Risks: closes `stdout` via `fclose_orDie(fout)`, which is acceptable for this standalone process but can surprise embedding/reuse. It intentionally rejects trailing non-zstd data at EOF. All errors terminate.

Test signals: decompress output from simple and streaming compression, concatenated frames, empty input must fail, invalid input must fail, truncated frame must report EOF before stream end.
