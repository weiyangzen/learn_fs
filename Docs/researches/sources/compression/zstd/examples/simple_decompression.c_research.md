# sources/compression/zstd/examples/simple_decompression.c

Purpose: in-memory one-shot decompression example for frames with known content size. It validates that compressed data is zstd and that the frame declares its original size.

Important functions/APIs: `decompress`, `main`, `ZSTD_getFrameContentSize`, `ZSTD_decompress`, `ZSTD_CONTENTSIZE_ERROR`, `ZSTD_CONTENTSIZE_UNKNOWN`, `CHECK_ZSTD`, and common helpers.

Control flow: require one compressed file path, load it, query frame content size, reject non-zstd or unknown-size frames, allocate exact output size, decompress, verify returned size, print summary, and free buffers.

State and persistence: decompressed data is only in memory; no output file is written.

Dependencies/integration: public zstd simple decompression API and `common.h`. The examples Makefile uses it for positive and invalid-input negative tests.

Risks: rejects legitimate frames without content size. Whole-file compressed and decompressed buffers must fit in memory. It is a validator/demo, not a general decompressor.

Test signals: paired output from `simple_compression`, invalid uncompressed input must fail, zero-size frame must succeed, unknown content-size frames should be rejected with a clear check failure.
